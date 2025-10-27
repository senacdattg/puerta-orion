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
            <span :class="['badge', roleColor(user.roles[0]?.nombre_rol)]">
              {{ user.roles[0]?.nombre_rol || 'Sin rol' }}
            </span>
          </td>
          <td class="user-action">
            <select
              :value="user.roles[0]?.id_rol"
              @change="updateRole(user, $event.target.value)"
              class="role-select"
              :disabled="loading"
            >
              <option
                v-for="rol in roles"
                :key="rol.value"
                :value="rol.value"
              >
                {{ rol.label }}
              </option>
            </select>
          </td>
        </tr>
      </tbody>
      </table>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
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
      // Emitir al padre la lista cargada
      emit('usuarios-cargados', users.value);
    } else {
      throw new Error(usuariosResponse.error || 'Error al cargar usuarios');
    }

    if (rolesResponse.success) {
      roles.value = rolesResponse.data.map(rol => ({
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

// Filtrar usuarios localmente
const filteredUsers = ref([]);

watch(
  () => [props.searchTerm, props.roleFilter, users.value],
  () => {
    const text = props.searchTerm.trim().toLowerCase();
    const roleFilter = props.roleFilter;

    filteredUsers.value = users.value.filter(user => {
      const matchesText = !text ||
        user.usuario.toLowerCase().includes(text) ||
        user.persona.nombre_completo.toLowerCase().includes(text);

      const matchesRole = roleFilter === 'todos' ||
        user.roles.some(rol => rol.nombre_rol.toLowerCase() === roleFilter.toLowerCase());

      return matchesText && matchesRole;
    });
  },
  { immediate: true }
);

// Actualizar rol de usuario
async function updateRole(user, newRoleId) {
  try {
    loading.value = true;
    error.value = null; // Limpiar errores previos

    const response = await usuariosService.cambiarRolUsuario(user.id_usuario, newRoleId);

    if (response.success) {
      // Actualizar el usuario localmente
      const userIndex = users.value.findIndex(u => u.id_usuario === user.id_usuario);
      if (userIndex !== -1) {
        // Forzar la reactividad creando un nuevo array
        const updatedUsers = [...users.value];
        updatedUsers[userIndex] = {
          ...updatedUsers[userIndex], // Mantener datos existentes
          roles: response.data.roles  // Solo actualizar los roles
        };
        users.value = updatedUsers; // Asignar el nuevo array

        // Debug: verificar que se actualizó
        console.log('Usuario actualizado:', updatedUsers[userIndex]);
        // Notificar al padre el usuario actualizado
        emit('usuario-actualizado', updatedUsers[userIndex]);
      }

      console.log(`Rol actualizado: ${user.usuario} ahora es ${response.data.roles[0]?.nombre_rol}`);

      // Mostrar notificación de éxito
      alert(`✅ Rol actualizado exitosamente!\nUsuario: ${user.usuario} ahora es ${response.data.roles[0]?.nombre_rol}`);
    } else {
      throw new Error(response.error || 'Error al actualizar rol');
    }
  } catch (err) {
    error.value = err.message;
    console.error('Error al actualizar rol:', err);
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
  border-collapse: collapse;
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.tabla-usuarios thead tr {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  color: #374151;
  font-weight: 600;
  text-align: left;
}

.tabla-usuarios th {
  padding: 16px 20px;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #d1d5db;
  text-align: left;
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

  select {
    min-width: 120px;
    font-size: 12px;
    padding: 6px 10px;
  }
}
</style>

