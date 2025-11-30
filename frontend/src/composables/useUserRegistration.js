/**
 * Composable for user registration logic
 * Provides reusable logic for checking user roles and age requirements
 */

import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

/**
 * Composable for user registration status and age calculations
 * @returns {Object} Computed properties for user registration logic
 */
export function useUserRegistration() {
  const authStore = useAuthStore()

  // Check if user already has Deportista role
  const yaEsDeportista = computed(() => {
    const roles = authStore.userRoles || []
    return roles.includes('Deportista')
  })

  // Check if user already has Acudiente role
  const yaEsAcudiente = computed(() => {
    const roles = authStore.userRoles || []
    return roles.includes('Acudiente')
  })

  // Calculate athlete age based on fecha_nacimiento
  const edadDeportista = computed(() => {
    try {
      // Search for fecha_nacimiento in different places in the store
      const userDetail = authStore.userDetail
      const deportista = userDetail?.deportista || authStore.user?.deportista

      if (!deportista) {
        return null
      }

      const fechaNacimiento = deportista.fecha_nacimiento

      if (!fechaNacimiento) {
        return null
      }

      // If fecha_nacimiento is just the year (number)
      const añoActual = new Date().getFullYear()
      const añoNacimiento = typeof fechaNacimiento === 'number'
        ? fechaNacimiento
        : new Date(fechaNacimiento).getFullYear()
      const edad = añoActual - añoNacimiento

      return edad
    } catch (error) {
      console.error('Error al calcular edad:', error)
      return null
    }
  })

  // Check if athlete is of legal age (>= 18 years)
  const esMayorDeEdad = computed(() => {
    const edad = edadDeportista.value
    if (edad === null) {
      return false // If age cannot be calculated, default to not showing
    }
    return edad >= 18
  })

  // Show acudiente option only if:
  // 1. Not already acudiente
  // 2. And is of legal age (if is athlete)
  const mostrarOpcionAcudiente = computed(() => {
    if (yaEsAcudiente.value) {
      return false
    }

    // If is athlete, only show if is of legal age
    if (yaEsDeportista.value) {
      return esMayorDeEdad.value
    }

    // If not athlete, show option (backend will validate age)
    return true
  })

  return {
    yaEsDeportista,
    yaEsAcudiente,
    edadDeportista,
    esMayorDeEdad,
    mostrarOpcionAcudiente
  }
}

