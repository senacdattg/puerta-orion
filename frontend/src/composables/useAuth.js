import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

/**
 * Composable para manejar la autenticación del usuario
 * Proporciona métodos y propiedades reactivas para el estado de autenticación
 */
export function useAuth() {
  const authStore = useAuthStore()

  // Estado reactivo
  const isAuthenticated = computed(() => authStore.estaAutenticado)
  const user = computed(() => authStore.user)
  const token = computed(() => authStore.token)
  const isLoading = computed(() => authStore.isLoading)

  // Métodos de autenticación
  const login = async (credentials) => {
    try {
      await authStore.login(credentials)
      return { success: true }
    } catch (error) {
      console.error('Error en login:', error)
      return { success: false, error: error.message }
    }
  }

  const logout = async () => {
    try {
      await authStore.logout()
      return { success: true }
    } catch (error) {
      console.error('Error en logout:', error)
      return { success: false, error: error.message }
    }
  }

  const register = async (userData) => {
    try {
      await authStore.register(userData)
      return { success: true }
    } catch (error) {
      console.error('Error en registro:', error)
      return { success: false, error: error.message }
    }
  }

  const verifyToken = async () => {
    try {
      return await authStore.verifyToken()
    } catch (error) {
      console.error('Error verificando token:', error)
      return false
    }
  }

  const refreshUser = async () => {
    try {
      await authStore.inicializar()
      return { success: true }
    } catch (error) {
      console.error('Error refrescando usuario:', error)
      return { success: false, error: error.message }
    }
  }

  // Propiedades computadas útiles
  const userName = computed(() => {
    if (!user.value) return 'Usuario'
    return user.value.persona?.nombre_completo?.split(' ')[0] || 'Usuario'
  })

  const userEmail = computed(() => {
    return user.value?.persona?.correo_electronico || ''
  })

  const hasRole = (role) => {
    if (!user.value?.roles) return false
    return user.value.roles.some(r =>
      typeof r === 'string' ? r === role : r.nombre_rol === role
    )
  }

  const hasAnyRole = (roles) => {
    if (!user.value?.roles) return false
    return roles.some(role => hasRole(role))
  }

  return {
    // Estado
    isAuthenticated,
    user,
    token,
    isLoading,
    userName,
    userEmail,

    // Métodos
    login,
    logout,
    register,
    verifyToken,
    refreshUser,

    // Utilidades
    hasRole,
    hasAnyRole
  }
}

