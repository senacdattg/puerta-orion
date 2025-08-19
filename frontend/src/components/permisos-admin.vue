<script setup>
import { ref } from "vue"

// Simulación de usuarios
const users = ref([
  { id: 1, name: "Kevin", role: "user" },
  { id: 2, name: "Santiago", role: "moderator" },
  { id: 3, name: "Prada", role: "admin" }
])

// Función para cambiar rol
function updateRole(user, newRole) {
  user.role = newRole
  // Aquí podrías hacer una petición a la API para guardar el cambio
  console.log(`Rol actualizado: ${user.name} ahora es ${newRole}`)
}
</script>

<template>
  <div class="p-4 bg-white rounded-lg shadow-md">
    <h2 class="text-xl font-bold mb-4">Gestión de Roles</h2>

    <table class="w-full border">
      <thead>
        <tr class="bg-gray-200">
          <th class="p-2">Usuario</th>
          <th class="p-2">Rol</th>
          <th class="p-2">Acción</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id" class="border-t">
          <td class="p-2">{{ user.name }}</td>
          <td class="p-2">{{ user.role }}</td>
          <td class="p-2">
            <select
              v-model="user.role"
              @change="updateRole(user, user.role)"
              class="border p-1 rounded"
            >
              <option value="user">Usuario</option>
              <option value="moderator">Moderador</option>
              <option value="admin">Administrador</option>
            </select>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
