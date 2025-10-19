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

// Determinar el rol del usuario (Admin si es admin, Usuario en caso contrario)
const rolUsuario = computed(() => {
  return authStore.isAdmin ? 'Admin' : 'Usuario';
});
</script>

<template>
  <main>
    <Encabezado :rol="rolUsuario"/>
    <Titulo />
    <CalendarioComponent :rol="rolUsuario" />
    <Pie />
  </main>
</template>
