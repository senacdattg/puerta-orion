<template>
    <table class="tabla-usuarios">
      <thead>
        <tr class="">
          <th class="">Usuario</th>
          <th class="">Rol</th>
          <th class="">Acción</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td colspan="3" style="text-align: center; padding: 20px;">
            Cargando usuarios...
          </td>
        </tr>
        <tr v-else-if="error">
          <td colspan="3" style="text-align: center; padding: 20px; color: red;">
            Error: {{ error }}
          </td>
        </tr>
        <tr
          v-else
          v-for="(user, index) in filteredUsers"
          :key="user.id_usuario"
          :class="[
            'user-row',
            index % 2 === 0 ? 'user-row--even' : 'user-row--odd'
          ]"
        >
          <td class="user-name">{{ user.usuario }}</td>
          <td class="user-role">
            <div class="roles-badges">
              <span
                v-for="rol in user.roles"
                :key="rol.id_rol"
                :class="['badge', roleColor(rol.nombre_rol)]"
              >
                {{ rol.nombre_rol }}
              </span>
              <span v-if="!user.roles || user.roles.length === 0" class="badge badge-none">Sin rol</span>
            </div>
          </td>
          <td class="user-action">
            <div class="roles-checkboxes">
              <label
                v-for="rol in rolesFiltrados"
                :key="rol.value"
                class="role-checkbox-label"
                :class="{ 'role-checkbox-checked': userRolesIds(user).includes(rol.value) }"
                :title="rol.label"
              >
                <input
                  type="checkbox"
                  :value="rol.value"
                  :checked="userRolesIds(user).includes(rol.value)"
                  @change="handleRoleChange(user, rol.value, $event.target.checked)"
                  :disabled="loading"
                  class="role-checkbox"
                />
                <span class="role-checkbox-text">{{ rol.label }}</span>
              </label>
            </div>
          </td>
        </tr>
      </tbody>
      </table>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import usuariosService from '@/services/usuariosService';

const props = defineProps({
  searchTerm: { type: String, default: '' },
  roleFilter: { type: String, default: 'todos' }
});

const emit = defineEmits(['usuarios-cargados', 'usuario-actualizado']);

const users = ref([]);
const roles = ref([]);
const loading = ref(false);
const error = ref(null);

// Cargar datos al montar el componente
onMounted(async () => {
  await cargarDatos();
});

// Cargar usuarios y roles
async function cargarDatos() {
  loading.value = true;
  error.value = null;

  try {
    // Cargar usuarios y roles en paralelo
    const [usuariosResponse, rolesResponse] = await Promise.all([
      usuariosService.listarUsuarios(),
      usuariosService.listarRoles()
    ]);

    if (usuariosResponse.success) {
      users.value = usuariosResponse.data;
      // Resetear selecciones cuando se cargan nuevos usuarios
      userRolesSelections.value = {};
      emit('usuarios-cargados', users.value);
    } else {
      throw new Error(usuariosResponse.error || 'Error al cargar usuarios');
    }

    if (rolesResponse.success) {
      // Solo mostrar Entrenador y Administrador (excluir SuperAdmin, Usuario, Deportista, Acudiente)
      const rolesPermitidos = ['entrenador', 'administrador'];
      roles.value = rolesResponse.data
        .filter(rol => {
          const nombreLower = rol.nombre_rol.toLowerCase();
          return rolesPermitidos.includes(nombreLower);
        })
        .map(rol => ({
          value: rol.id_rol,
          label: rol.nombre_rol
        }));
    } else {
      throw new Error(rolesResponse.error || 'Error al cargar roles');
    }
  } catch (err) {
    error.value = err.message;
    console.error('Error al cargar datos:', err);
  } finally {
    loading.value = false;
  }
}

// Obtener IDs de roles del usuario (todos)
function userRolesIds(user) {
  return (user.roles || []).map(r => r.id_rol);
}

// Obtener IDs de roles gestionables del usuario (solo Entrenador y Administrador)
function userGestionableRolesIds(user) {
  const rolesPermitidos = ['entrenador', 'administrador'];
  return (user.roles || [])
    .filter(r => rolesPermitidos.includes(r.nombre_rol?.toLowerCase()))
    .map(r => r.id_rol);
}

// Filtrar usuarios localmente
const filteredUsers = ref([]);

watch(
  () => [props.searchTerm, props.roleFilter, users.value],
  () => {
    const text = props.searchTerm.trim().toLowerCase();
    const roleFilter = props.roleFilter;

    filteredUsers.value = users.value.filter(user => {
      const matchesText = !text ||
        user.usuario.toLowerCase().includes(text);

      const matchesRole = roleFilter === 'todos' ||
        user.roles.some(rol => rol.nombre_rol.toLowerCase() === roleFilter.toLowerCase());

      return matchesText && matchesRole;
    });
  },
  { immediate: true }
);

// Roles filtrados (sin SuperAdmin)
const rolesFiltrados = computed(() => roles.value);

// Manejar cambio de checkbox de rol
const userRolesSelections = ref({}); // Guardar selecciones temporales por usuario

function handleRoleChange(user, roleId, checked) {
  const userId = user.id_usuario;

  // Si no existe selección previa, inicializar con roles gestionables actuales del usuario
  if (!userRolesSelections.value[userId]) {
    userRolesSelections.value[userId] = [...userGestionableRolesIds(user)];
  }

  // Actualizar selección en el estado
  if (checked) {
    if (!userRolesSelections.value[userId].includes(roleId)) {
      userRolesSelections.value[userId].push(roleId);
    }
  } else {
    userRolesSelections.value[userId] = userRolesSelections.value[userId].filter(id => id !== roleId);
  }

  const newSelection = [...userRolesSelections.value[userId]];

  // Cancelar timeout anterior si existe
  if (userRolesSelections.value[`${userId}_timeout`]) {
    clearTimeout(userRolesSelections.value[`${userId}_timeout`]);
  }

  // Guardar una copia inmutable de los roles para enviar después del delay
  const rolesToSend = [...newSelection];

  // Aplicar cambios después de un pequeño delay para evitar múltiples llamadas
  userRolesSelections.value[`${userId}_timeout`] = setTimeout(() => {
    updateRoles(user, rolesToSend);
  }, 500);
}

// Actualizar múltiples roles de usuario
async function updateRoles(user, selectedRoleIds) {
  try {
    loading.value = true;
    error.value = null;

    const response = await usuariosService.cambiarRolUsuario(user.id_usuario, selectedRoleIds);

    if (response.success) {
      // Actualizar el usuario localmente
      const userIndex = users.value.findIndex(u => u.id_usuario === user.id_usuario);
      if (userIndex !== -1) {
        const updatedUsers = [...users.value];
        updatedUsers[userIndex] = {
          ...updatedUsers[userIndex],
          roles: response.data.roles
        };
        users.value = updatedUsers;

        // Resetear selecciones solo con roles gestionables del estado actual
        userRolesSelections.value[user.id_usuario] = [...userGestionableRolesIds(updatedUsers[userIndex])];

        emit('usuario-actualizado', updatedUsers[userIndex]);
      }

      const rolesNames = response.data.roles.map(r => r.nombre_rol).join(', ');
      console.log(`Roles actualizados: ${user.usuario} ahora tiene: ${rolesNames}`);
    } else {
      throw new Error(response.error || 'Error al actualizar roles');
    }
  } catch (err) {
    error.value = err.message;
    console.error('Error al actualizar roles:', err);
    alert(`❌ Error al actualizar roles: ${err.message}`);
  } finally {
    loading.value = false;
  }
}

function roleColor(role) {
  switch (role) {
    case "SuperAdmin":
      return "badge-admin";
    case "Administrador":
      return "badge-admin";
    case "Entrenador":
      return "badge-moderator";
    case "Deportista":
      return "badge-user";
    case "Acudiente":
      return "badge-user";
    default:
      return "badge-user";
  }
}
</script>

<style scoped>
.tabla-usuarios {
  width: 100%;
  font-size: 18px;
  border-collapse: collapse;
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  table-layout: fixed;
}

.tabla-usuarios thead tr {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  color: #374151;
  font-weight: 600;
  text-align: left;
}

.tabla-usuarios th {
  padding: 16px 20px;
  font-size: 22px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #d1d5db;
  text-align: center;
}

.tabla-usuarios th:nth-child(1) {
  width: 30%;
}

.tabla-usuarios th:nth-child(2) {
  width: 30%;
}

.tabla-usuarios th:nth-child(3) {
  width: 40%;
}

.tabla-usuarios tbody tr {
  transition: all 0.3s ease;
  border-bottom: 1px solid #f3f4f6;
}

.tabla-usuarios tbody tr:nth-child(even) {
  background-color: #f9fafb;
}

.tabla-usuarios tbody tr:hover {
  background-color: #f0f9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tabla-usuarios td {
  padding: 16px 20px;
  font-size: 14px;
  color: #374151;
  vertical-align: middle;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tabla-usuarios td:first-child {
  font-weight: 600;
  color: #1f2937;
}

/* Estilos para las filas de usuario */
.user-row {
  transition: all 0.3s ease;
  cursor: pointer;
}

.user-row--even {
  background-color: #f9fafb;
}

.user-row--odd {
  background-color: white;
}

.user-row:hover {
  background-color: #f0f9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-name {
  font-weight: 600;
  color: #1f2937;
}

.user-role {
  text-align: center;
  vertical-align: middle;
}

.user-action {
  text-align: center;
  vertical-align: middle;
  display: flex;
  justify-content: center;
  align-items: center;
}

.role-select {
  padding: 8px 12px;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  background-color: white;
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 140px;
}

.role-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.role-select:hover {
  border-color: #9ca3af;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
  letter-spacing: 0.3px;
}

.badge-admin {
  background-color: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.badge-moderator {
  background-color: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.badge-user {
  background-color: #f9fafb;
  color: #6b7280;
  border: 1px solid #e5e7eb;
}

.badge-none {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.roles-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
}

.roles-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 200px;
  max-width: 250px;
  padding: 12px;
  background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin: 0 auto;
}

.role-checkbox-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 10px 14px;
  border-radius: 8px;
  background-color: #ffffff;
  border: 2px solid #e5e7eb;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.role-checkbox-label::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background-color: #3b82f6;
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.role-checkbox-label:hover {
  background-color: #f0f9ff;
  border-color: #93c5fd;
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
}

.role-checkbox-label:hover::before {
  transform: scaleY(1);
}

.role-checkbox-label.role-checkbox-checked,
.role-checkbox-label:has(.role-checkbox:checked) {
  background-color: #eff6ff;
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
}

.role-checkbox-label.role-checkbox-checked::before,
.role-checkbox-label:has(.role-checkbox:checked)::before {
  transform: scaleY(1);
}

.role-checkbox-label.role-checkbox-checked .role-checkbox-text,
.role-checkbox-label:has(.role-checkbox:checked) .role-checkbox-text {
  color: #1e40af;
  font-weight: 600;
}

.role-checkbox {
  width: 20px;
  height: 20px;
  min-width: 20px;
  cursor: pointer;
  accent-color: #3b82f6;
  border-radius: 4px;
  border: 2px solid #d1d5db;
  transition: all 0.3s ease;
  position: relative;
}

.role-checkbox:hover {
  border-color: #3b82f6;
  transform: scale(1.1);
}

.role-checkbox:checked {
  background-color: #3b82f6;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.role-checkbox:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

.role-checkbox:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.role-checkbox-text {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  user-select: none;
  transition: color 0.3s ease;
  flex: 1;
}

.role-checkbox-label:hover .role-checkbox-text {
  color: #1e40af;
}

select {
  padding: 8px 12px;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  background-color: white;
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 140px;
}

select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

select:hover {
  border-color: #9ca3af;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Responsive */
@media (max-width: 768px) {
  .tabla-usuarios {
    font-size: 12px;
  }

  .tabla-usuarios th,
  .tabla-usuarios td {
    padding: 12px 16px;
  }

  .roles-checkboxes {
    min-width: 160px;
    max-width: 200px;
    padding: 8px;
    gap: 8px;
  }

  .role-checkbox-label {
    padding: 8px 10px;
    gap: 10px;
  }

  .role-checkbox {
    width: 18px;
    height: 18px;
    min-width: 18px;
  }

  .role-checkbox-text {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .roles-checkboxes {
    min-width: 140px;
    max-width: 180px;
    padding: 6px;
    gap: 6px;
  }

  .role-checkbox-label {
    padding: 6px 8px;
    gap: 8px;
  }

  .role-checkbox {
    width: 16px;
    height: 16px;
    min-width: 16px;
  }

  .role-checkbox-text {
    font-size: 11px;
  }

  select {
    min-width: 120px;
    font-size: 12px;
    padding: 6px 10px;
  }
}

@media (max-width: 768px) {
  select {
    min-width: 120px;
    font-size: 12px;
    padding: 6px 10px;
  }
}
</style>

