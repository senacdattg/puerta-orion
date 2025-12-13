<script setup>
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import Encabezado from '../components/layout/encabezado.vue';
import CalendarioComponent from '../components/admin/calendario-component.vue';
import Pie from '../components/layout/pie.vue';

// Definir nombre del componente para evitar error del linter
defineOptions({
  name: 'CalendarioView'
});

// Obtener el store de autenticación
const authStore = useAuthStore();

// Computed para obtener el rol del usuario desde la sesión (igual que en el menú)
const rolUsuario = computed(() => {
  if (!authStore.user || !authStore.user.roles || authStore.user.roles.length === 0) {
    return 'Usuario'
  }

  // Obtener el primer rol del usuario (o el más relevante)
  const roles = authStore.user.roles
  // Prefer Set over array for efficient role checking
  const roleNames = new Set(roles.map(role =>
    typeof role === 'string' ? role : role.nombre_rol
  ))

  // Priorizar roles en orden de importancia
  if (roleNames.has('SuperAdmin')) {
    return 'SuperAdmin'
  } else if (roleNames.has('Administrador')) {
    return 'Administrador'
  } else if (roleNames.has('Entrenador')) {
    return 'Entrenador'
  } else if (roleNames.has('Deportista')) {
    return 'Deportista'
  } else if (roleNames.has('Acudiente')) {
    return 'Acudiente'
  } else if (roleNames.has('usuario')) {
    return 'Usuario'
  }

  return 'Usuario'
});
</script>

<template>
  <main>
    <Encabezado />
    <CalendarioComponent :rol="rolUsuario" />
    <Pie />
  </main>
</template>
