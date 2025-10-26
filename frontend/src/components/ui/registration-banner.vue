<template>
  <div class="registration-banner">
    <div class="banner-content">
      <div class="banner-icon">
        <i class="fas fa-user-plus"></i>
      </div>
      <div class="banner-text">
        <h3>¡Completa tu registro!</h3>
        <p>Para acceder a todas las funcionalidades, completa tu registro como Acudiente o Deportista</p>
      </div>
      <div class="banner-actions">
        <button
          class="btn btn-primary btn-icon"
          @click="navigateToRegister('acudiente')"
        >
          <i class="fas fa-user-friends icon"></i>
          Registrarse como Acudiente
        </button>
        <button
          class="btn btn-warning btn-icon"
          @click="navigateToRegister('deportista')"
        >
          <i class="fas fa-running icon"></i>
          Registrarse como Deportista
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

// Definir nombre del componente para el linter
defineOptions({
  name: 'RegistrationBanner'
})

const router = useRouter()

// Función para navegar a registro
const navigateToRegister = (type) => {
  if (type === 'acudiente') {
    router.push('/registrar-acudiente')
  } else if (type === 'deportista') {
    router.push('/registrar-deportista-form')
  }
}
</script>

<style scoped>
/* Los estilos están en /assets/css/dashboards.css */
</style>
