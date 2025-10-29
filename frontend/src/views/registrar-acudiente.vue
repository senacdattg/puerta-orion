<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

// Redirigir al formulario correcto para usuarios autenticados que completan su perfil
onMounted(() => {
  // Si el usuario está autenticado, redirigir al formulario de completar perfil
  if (authStore.token) {
    router.replace('/formulario-acudiente-completo');
  }
});
</script>

<template>
  <main>
    <div style="text-align: center; padding: 2rem;">
      <p>Redirigiendo...</p>
    </div>
  </main>
</template>

<style scoped>
.contenido-principal-tarjetas {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
