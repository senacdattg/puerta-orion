/**
 * Store de autenticación usando Pinia
 * Gestiona el estado global de autenticación del usuario
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authService from '@/services/authService'

export const useAuthStore = defineStore('auth', () => {
  // Estado reactivo
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const permissions = ref([]) // Nuevo: permisos específicos del usuario
  const activeRole = ref(localStorage.getItem('activeRole') || null) // Rol activo seleccionado
  const userDetail = ref(null) // Detalle completo del usuario (con información por rol)
  const isLoading = ref(false)
  const error = ref(null)

  // Getters computados
  const isAuthenticated = computed(() => !!token.value)
  const estaAutenticado = computed(() => !!token.value) // Alias para compatibilidad

  // Extraer nombres de roles (manejar objetos o strings)
  const userRoles = computed(() => {
    const roles = user.value?.roles || []
    return roles.map(role => {
      if (typeof role === 'string') return role
      if (role.nombre_rol) return role.nombre_rol
      if (role.rol) return role.rol
      return role.toString()
    })
  })

  const hasRole = computed(() => (roleName) => userRoles.value.includes(roleName))
  const isAdmin = computed(() => hasRole.value('Administrador'))
  const isDeportista = computed(() => hasRole.value('Deportista'))
  const isAcudiente = computed(() => hasRole.value('Acudiente'))
  const isEntrenador = computed(() => hasRole.value('Entrenador'))

  // Nuevos getters basados en permisos específicos de la BD
  const puedeCrearEventos = computed(() => permissions.value.includes('crear_evento'))
  const puedeEditarEventos = computed(() => permissions.value.includes('editar_evento'))
  const puedeEliminarEventos = computed(() => permissions.value.includes('eliminar_evento'))
  const puedeVerEventos = computed(() => permissions.value.includes('ver_evento') || permissions.value.includes('ver_calendario'))
  const puedeGestionarUsuarios = computed(() => permissions.value.includes('gestionar_usuarios'))
  const puedeAccederPanelAdmin = computed(() => permissions.value.includes('acceso_panel_admin'))

  // Método para verificar permisos específicos
  const hasPermission = (permissionName) => {
    return permissions.value.includes(permissionName)
  }

  // Acciones
  const login = async (credentials) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await authService.login(credentials)

      if (response.success) {
        token.value = response.token
        user.value = response.user

        // Guardar en localStorage
        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))

        // Verificar cuántos roles tiene el usuario
        const userRoles = response.user?.roles || []
        const roleNames = userRoles.map(role => typeof role === 'string' ? role : role.nombre_rol)

        // Solo cargar permisos si tiene un solo rol
        // Si tiene múltiples roles, limpiar permisos y esperar a que seleccione uno
        if (roleNames.length === 1) {
          // Un solo rol: cargar permisos de ese rol
          await loadPermissionsForRole(roleNames[0])
        } else if (roleNames.length > 1) {
          // Múltiples roles: limpiar permisos y establecer activeRole como null
          permissions.value = []
          activeRole.value = null
          localStorage.removeItem('activeRole')
          console.log('⚠️ Usuario con múltiples roles, esperando selección de rol')
        } else {
          // Sin roles: limpiar permisos
          permissions.value = []
        }

        return { success: true, user: response.user, token: response.token }
      } else {
        error.value = response.error || 'Error de autenticación'
        return { success: false, error: error.value }
      }
    } catch (err) {
      error.value = err.message || 'Error de conexión'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await authService.register(userData)

      if (response.success) {
        return { success: true, data: response.data }
      } else {
        error.value = response.error || 'Error de registro'
        return { success: false, error: error.value }
      }
    } catch (err) {
      error.value = err.message || 'Error de conexión'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      if (token.value) {
        await authService.logout(token.value)
      }
    } catch (err) {
      console.warn('Error al cerrar sesión en el servidor:', err)
    } finally {
      // Limpiar estado local independientemente del resultado del servidor
      token.value = null
      user.value = null
      permissions.value = [] // Limpiar permisos
      error.value = null

      // Limpiar localStorage
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      clearActiveRole() // Limpiar rol activo al hacer logout
      
      // Limpiar permisos
      permissions.value = []
    }
  }

  const verifyToken = async () => {
    try {
      if (!token.value || token.value === 'null' || token.value === 'undefined') {
        return false
      }

      const response = await authService.verifyToken(token.value)

      if (response.success) {
        // Token válido, cargar datos del usuario si no están cargados
        if (!user.value) {
          await loadUserProfile()
        }
        return true
      } else {
        // Token inválido, limpiar estado
        console.log('Token inválido según respuesta del servidor')
        await logout()
        return false
      }
    } catch (err) {
      console.warn('Error al verificar token:', err)
      // Solo hacer logout si hay un token válido
      if (token.value && token.value !== 'null' && token.value !== 'undefined') {
        await logout()
      }
      return false
    }
  }

  const loadUserPermissions = async () => {
    try {
      const response = await authService.getUserPermissions()
      if (response.success) {
        permissions.value = response.permisos || []
        console.log('🔍 Permisos cargados desde BD:', permissions.value)
      } else {
        console.warn('⚠️ No se pudieron cargar permisos específicos, usando permisos por rol')
        // Fallback a permisos basados en roles si no se pueden cargar permisos específicos
        setPermissionsByRole()
      }
    } catch (error) {
      console.warn('⚠️ Error cargando permisos específicos:', error.message)
      // Fallback a permisos basados en roles
      setPermissionsByRole()
    }
  }

  // Nueva función para cargar permisos de un rol específico
  const loadPermissionsForRole = async (roleName) => {
    try {
      if (!roleName) {
        console.warn('⚠️ No se proporcionó nombre de rol para cargar permisos')
        permissions.value = []
        return
      }

      const response = await authService.getRolePermissions(roleName)
      if (response.success) {
        permissions.value = response.permisos || []
        console.log(`🔍 Permisos cargados para rol "${roleName}":`, permissions.value)
      } else {
        console.warn(`⚠️ No se pudieron cargar permisos para el rol "${roleName}"`)
        permissions.value = []
      }
    } catch (error) {
      console.warn(`⚠️ Error cargando permisos del rol "${roleName}":`, error.message)
      permissions.value = []
    }
  }

  const setPermissionsByRole = () => {
    // Fallback: establecer permisos basados en roles si no hay permisos específicos
    if (!user.value || !user.value.roles) {
      permissions.value = []
      return
    }

    const roles = user.value.roles.map(role =>
      typeof role === 'string' ? role : role.nombre_rol
    )

    const permisos = []

    // SuperAdmin y Administrador tienen todos los permisos
    if (roles.includes('SuperAdmin') || roles.includes('Administrador')) {
      permisos.push(
        'crear_evento', 'editar_evento', 'eliminar_evento', 'ver_evento', 'ver_calendario',
        'gestionar_usuarios', 'acceso_panel_admin'
      )
    }
    // Entrenador puede crear y editar eventos
    else if (roles.includes('Entrenador')) {
      permisos.push('crear_evento', 'editar_evento', 'ver_evento', 'ver_calendario')
    }
    // Otros roles solo pueden ver eventos
    else {
      permisos.push('ver_evento', 'ver_calendario')
    }

    permissions.value = permisos
    console.log('🔍 Permisos establecidos por rol:', permissions.value)
  }

  const loadUserProfile = async () => {
    try {
      if (!token.value) return false

      const response = await authService.getProfile()

      if (response.success) {
        user.value = response.data
        localStorage.setItem('user', JSON.stringify(user.value))

        // Cargar permisos después de cargar el perfil
        await loadUserPermissions()

        return true
      } else {
        await logout()
        return false
      }
    } catch (err) {
      console.warn('Error al cargar perfil:', err)
      await logout()
      return false
    }
  }

  const loadUserProfileDetail = async () => {
    try {
      if (!token.value) {
        console.warn('No hay token para cargar detalle del perfil')
        return false
      }

      isLoading.value = true
      console.log('🔄 Iniciando carga de detalle del perfil...')

      const response = await authService.getProfileDetail()
      console.log('📥 Respuesta del servicio:', response)

      if (response && response.success) {
        userDetail.value = response.data
        console.log('✅ userDetail actualizado:', userDetail.value)

        // Si hay un warning, solo lo logueamos pero no fallamos
        if (response.warning) {
          console.warn('⚠️ Advertencia al cargar detalle:', response.warning)
        }
        return true
      } else {
        console.warn('❌ Error al cargar detalle del perfil:', response?.error || 'Respuesta sin éxito')
        userDetail.value = null
        return false
      }
    } catch (err) {
      console.error('❌ Excepción al cargar detalle del perfil:', err)
      console.error('📋 Detalles del error:', {
        message: err.message,
        stack: err.stack
      })

      userDetail.value = null

      // Si el error es sobre persona no asociada, permitir continuar con datos parciales
      if (err.message && err.message.includes('persona asociada')) {
        console.warn('⚠️ Continuando con datos parciales')
        return false
      }
      return false
    } finally {
      isLoading.value = false
      console.log('🏁 Carga de detalle finalizada')
    }
  }

  const inicializar = async () => {
    try {
      // Cargar datos del localStorage con validación
      const savedUser = localStorage.getItem('user')
      if (savedUser && savedUser !== 'null' && savedUser !== 'undefined') {
        try {
          user.value = JSON.parse(savedUser)
        } catch (parseError) {
          console.warn('Error al parsear usuario guardado:', parseError)
          localStorage.removeItem('user')
        }
      }

      // Cargar rol activo del localStorage y sus permisos
      const savedActiveRole = localStorage.getItem('activeRole')
      if (savedActiveRole && savedActiveRole !== 'null' && savedActiveRole !== 'undefined') {
        activeRole.value = savedActiveRole
        // Cargar permisos del rol activo si existe
        await loadPermissionsForRole(savedActiveRole)
      }

      // Verificar token si existe
      if (token.value && token.value !== 'null' && token.value !== 'undefined') {
        const isValid = await verifyToken()
        if (!isValid) {
          console.log('Token inválido, limpiando sesión')
        }
      }
    } catch (err) {
      console.warn('Error al inicializar auth store:', err)
      // Limpiar datos corruptos
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('activeRole')
      token.value = null
      user.value = null
      activeRole.value = null
      permissions.value = [] // Limpiar permisos
    }
  }

  const clearError = () => {
    error.value = null
  }

  const updateUser = (userData) => {
    user.value = { ...user.value, ...userData }
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  // Función para establecer el rol activo seleccionado y cargar sus permisos
  const setActiveRole = async (roleName) => {
    activeRole.value = roleName
    localStorage.setItem('activeRole', roleName)
    
    // Cargar permisos del rol seleccionado
    await loadPermissionsForRole(roleName)
  }

  // Función para limpiar el rol activo (útil al hacer logout)
  const clearActiveRole = () => {
    activeRole.value = null
    localStorage.removeItem('activeRole')
  }

  return {
    // Estado
    user,
    token,
    permissions, // Nuevo: permisos específicos
    activeRole, // Rol activo seleccionado
    userDetail, // Detalle completo del usuario
    isLoading,
    error,

    // Getters
    isAuthenticated,
    estaAutenticado,
    userRoles,
    hasRole,
    isAdmin,
    isDeportista,
    isAcudiente,
    isEntrenador,

    // Nuevos getters de permisos
    puedeCrearEventos,
    puedeEditarEventos,
    puedeEliminarEventos,
    puedeVerEventos,
    puedeGestionarUsuarios,
    puedeAccederPanelAdmin,

    // Métodos
    hasPermission,

    // Acciones
    login,
    register,
    logout,
    verifyToken,
    loadUserProfile,
    loadUserProfileDetail, // Nueva acción para cargar detalle completo
    loadUserPermissions, // Nueva acción
    loadPermissionsForRole, // Nueva acción para cargar permisos de un rol específico
    setPermissionsByRole, // Nueva acción
    inicializar,
    clearError,
    updateUser,
    setActiveRole, // Nueva acción para establecer rol activo
    clearActiveRole // Nueva acción para limpiar rol activo
  }
})
