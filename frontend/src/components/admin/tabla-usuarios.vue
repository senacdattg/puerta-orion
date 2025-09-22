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
        <tr
          v-for="(user, index) in users"
          :key="user.id"
          :class="[
            'user-row',
            index % 2 === 0 ? 'user-row--even' : 'user-row--odd'
          ]"
        >
          <td class="user-name">{{ user.name }}</td>
          <td class="user-role">
            <span :class="['badge', roleColor(user.role)]">
              {{ user.role }}
            </span>
          </td>
          <td class="user-action">
            <select
              v-model="user.role"
              @change="updateRole(user, user.role)"
              class="role-select"
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
import { ref, watch } from 'vue';
const props = defineProps({
  searchTerm: { type: String, default: '' },
  roleFilter: { type: String, default: 'todos' }
});

const roles = [
  { value: 'user', label: 'Usuario' },
  { value: 'moderator', label: 'Moderador' },
  { value: 'admin', label: 'Administrador' }
];

const allUsers = [
  { id: 1, name: "Kevin", role: "user" },
  { id: 2, name: "Mario", role: "moderator" },
  { id: 3, name: "Olarte", role: "admin" }
];

const users = ref(allUsers);

watch(
  () => [props.searchTerm, props.roleFilter],
  () => {
    const text = props.searchTerm.trim().toLowerCase();
    const role = props.roleFilter;
    users.value = allUsers.filter(u => {
      const matchesText = !text || u.name.toLowerCase().includes(text);
      const matchesRole = role === 'todos' || u.role === role;
      return matchesText && matchesRole;
    });
  },
  { immediate: true }
);

function updateRole(user, newRole) {
  user.role = newRole;
  console.log(`Rol actualizado: ${user.name} ahora es ${newRole}`);
}

function roleColor(role) {
  switch (role) {
    case "admin":
      return "badge-admin";
    case "moderator":
      return "badge-moderator";
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
}

.user-action {
  text-align: center;
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

