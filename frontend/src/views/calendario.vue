<script setup>
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import Encabezado from '../components/layout/encabezado.vue';
import Titulo from '../components/ui/titulo-club.vue';
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
  const roleNames = roles.map(role =>
    typeof role === 'string' ? role : role.nombre_rol
  )

  // Priorizar roles en orden de importancia
  if (roleNames.includes('SuperAdmin')) {
    return 'SuperAdmin'
  } else if (roleNames.includes('Administrador')) {
    return 'Administrador'
  } else if (roleNames.includes('Entrenador')) {
    return 'Entrenador'
  } else if (roleNames.includes('Deportista')) {
    return 'Deportista'
  } else if (roleNames.includes('Acudiente')) {
    return 'Acudiente'
  } else if (roleNames.includes('usuario')) {
    return 'Usuario'
  }

  return 'Usuario'
});
</script>

<template>
  <main>
    <Encabezado />
    <Titulo />
    <CalendarioComponent :rol="rolUsuario" />
    <Pie />
  </main>
</template>
