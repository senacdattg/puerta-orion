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
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Definir nombre del componente para el linter
defineOptions({
  name: 'RegistrationBanner'
})

const router = useRouter()
const authStore = useAuthStore()

// Verificar si el usuario ya tiene los roles
const yaEsDeportista = computed(() => {
  const roles = authStore.userRoles || []
  return roles.includes('Deportista')
})

const yaEsAcudiente = computed(() => {
  const roles = authStore.userRoles || []
  return roles.includes('Acudiente')
})

// Calcular edad del deportista basándose en fecha_nacimiento
const edadDeportista = computed(() => {
  try {
    // Buscar fecha_nacimiento en diferentes lugares del store
    const userDetail = authStore.userDetail
    const deportista = userDetail?.deportista || authStore.user?.deportista

    if (!deportista) return null

    const fechaNacimiento = deportista.fecha_nacimiento

    if (!fechaNacimiento) return null

    // Si fecha_nacimiento es solo el año (número)
    const añoActual = new Date().getFullYear()
    const añoNacimiento = typeof fechaNacimiento === 'number' ? fechaNacimiento : new Date(fechaNacimiento).getFullYear()
    const edad = añoActual - añoNacimiento

    return edad
  } catch (error) {
    console.error('Error al calcular edad:', error)
    return null
  }
})

// Verificar si el deportista es mayor de edad (>= 18 años)
const esMayorDeEdad = computed(() => {
  const edad = edadDeportista.value
  if (edad === null) return false // Si no se puede calcular la edad, por defecto no mostrar
  return edad >= 18
})

// Mostrar opción de acudiente solo si:
// 1. No es ya acudiente
// 2. Y es mayor de edad (si es deportista)
const mostrarOpcionAcudiente = computed(() => {
  if (yaEsAcudiente.value) return false

  // Si es deportista, solo mostrar si es mayor de edad
  if (yaEsDeportista.value) {
    return esMayorDeEdad.value
  }

  // Si no es deportista, mostrar la opción (el backend validará la edad)
  return true
})

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


