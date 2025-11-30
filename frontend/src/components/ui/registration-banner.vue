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
          v-if="mostrarOpcionAcudiente"
          class="btn btn-primary btn-icon"
          @click="navigateToRegister('acudiente')"
        >
          <i class="fas fa-user-friends icon"></i>
          Registrarse como Acudiente
        </button>
        <button
          v-if="!yaEsDeportista"
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
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserRegistration } from '@/composables/useUserRegistration'

// Definir nombre del componente para el linter
defineOptions({
  name: 'RegistrationBanner'
})

const router = useRouter()
const authStore = useAuthStore()

// Use shared registration logic
const {
  yaEsDeportista,
  mostrarOpcionAcudiente
} = useUserRegistration()

// Cargar perfil del usuario si no está cargado
onMounted(async () => {
  if (!authStore.user) {
    await authStore.loadUserProfile()
  }
  // Cargar detalle del usuario para obtener información del deportista (fecha_nacimiento)
  if (!authStore.userDetail) {
    await authStore.loadUserProfileDetail()
  }
})

// Función para navegar a registro
const navigateToRegister = (type) => {
  if (type === 'acudiente') {
    // Si el usuario ya está autenticado, debe completar su perfil
    // Usar el formulario de completar perfil que requiere asociación con deportista
    router.push('/formulario-acudiente-completo')
  } else if (type === 'deportista') {
    router.push('/registrar-deportista-form')
  }
}
</script>


