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
  const permissions = ref([]) // Permisos específicos del usuario según rol activo
  const rolesSelector = ref({}) // Roles disponibles según backend
  const panels = ref([]) // Paneles autorizados según rol activo
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
        rolesSelector.value = response.user?.roles_selector || {}
        panels.value = response.user?.paneles || []
        activeRole.value = response.user?.rol_activo || null

        // Guardar en localStorage
        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))
        if (activeRole.value) {
          localStorage.setItem('activeRole', activeRole.value)
        } else {
          localStorage.removeItem('activeRole')
        }

        // Verificar cuántos roles tiene el usuario
        const userRoles = response.user?.roles || []
        const roleNames = userRoles.map(role => typeof role === 'string' ? role : role.nombre_rol)

        if (activeRole.value) {
          await loadPermissionsForRole(activeRole.value)
        } else if (roleNames.length === 1) {
          await loadPermissionsForRole(roleNames[0])
        } else {
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
      rolesSelector.value = {}
      panels.value = []
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

      // Guardar el rol activo actual antes de verificar el token
      const rolActivoAntes = activeRole.value || localStorage.getItem('activeRole')

      const response = await authService.verifyToken(token.value)

      if (response.success) {
        // Token válido, cargar datos del usuario si no están cargados
        if (!user.value) {
          await loadUserProfile()
        }
        
        // Restaurar el rol activo si se cambió durante loadUserProfile
        if (rolActivoAntes && activeRole.value !== rolActivoAntes) {
          const rolesUsuario = user.value?.roles || []
          const nombresRoles = rolesUsuario.map(r => {
            if (typeof r === 'string') return r
            if (r.nombre_rol) return r.nombre_rol
            return String(r)
          })
          if (nombresRoles.some(r => r === rolActivoAntes || r.toLowerCase() === rolActivoAntes.toLowerCase())) {
            console.log(`🔄 [verifyToken] Restaurando rol activo después de verificar token: ${rolActivoAntes}`)
            activeRole.value = rolActivoAntes
            localStorage.setItem('activeRole', rolActivoAntes)
            await loadPermissionsForRole(rolActivoAntes)
          }
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
      if (activeRole.value) {
        await loadPermissionsForRole(activeRole.value)
        return
      }

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

  const refreshRoleOptions = async () => {
    try {
      const response = await authService.getRoleOptions()
      if (!response.success) {
        return { success: false, error: response.error }
      }

      const {
        roles_selector: selector = {},
        rol_activo: rolBackend = null,
        paneles: panelBackend = []
      } = response.data || {}

      rolesSelector.value = selector || {}
      panels.value = Array.isArray(panelBackend) ? panelBackend : []

      // Obtener roles disponibles y del usuario para validación
      const rolesDisponibles = Object.keys(selector || {}).filter(key => selector[key])
      const rolesUsuario = user.value?.roles || []
      const nombresRoles = rolesUsuario.map(r => {
        if (typeof r === 'string') return r
        if (r.nombre_rol) return r.nombre_rol
        return String(r)
      })

      // Obtener el rol activo actual (prioridad: store > localStorage)
      const rolActivoActual = activeRole.value || localStorage.getItem('activeRole')
      
      // Validar si el rol activo actual es válido
      const rolActivoEsValido = rolActivoActual && (
        rolesDisponibles.includes(rolActivoActual) || 
        nombresRoles.includes(rolActivoActual)
      )

      // Estrategia: SIEMPRE mantener el rol activo guardado si es válido, incluso si el backend sugiere otro
      // El backend puede estar cambiando el rol automáticamente, pero el frontend debe respetar la selección del usuario
      if (rolActivoActual && rolActivoEsValido) {
        // El rol guardado es válido, SIEMPRE mantenerlo (ignorar completamente el del backend si es diferente)
        if (rolBackend && rolBackend !== rolActivoActual) {
          console.log(`✅ [refreshRoleOptions] Manteniendo rol activo guardado: ${rolActivoActual} (backend sugiere: ${rolBackend}, IGNORANDO cambio del backend)`)
        }
        activeRole.value = rolActivoActual
        localStorage.setItem('activeRole', rolActivoActual)
        await loadPermissionsForRole(rolActivoActual)
        console.log(`✅ [refreshRoleOptions] Rol activo mantenido: ${rolActivoActual}`)
      } else if (rolBackend) {
        // No hay rol válido guardado, usar el del backend
        if (rolActivoActual && !rolActivoEsValido) {
          console.log(`🔄 [refreshRoleOptions] Rol guardado (${rolActivoActual}) no es válido, actualizando a ${rolBackend}`)
        } else {
          console.log(`📥 [refreshRoleOptions] No hay rol guardado, usando rol del backend: ${rolBackend}`)
        }
        activeRole.value = rolBackend
        localStorage.setItem('activeRole', rolBackend)
        await loadPermissionsForRole(rolBackend)
      } else if (rolActivoActual) {
        // Backend no devuelve rol pero tenemos uno guardado (aunque no válido), intentar mantenerlo
        console.log(`⚠️ [refreshRoleOptions] Rol guardado (${rolActivoActual}) no está en roles disponibles, pero manteniéndolo temporalmente`)
        activeRole.value = rolActivoActual
        localStorage.setItem('activeRole', rolActivoActual)
        await loadPermissionsForRole(rolActivoActual)
      } else {
        // No hay rol válido, limpiar
        console.log(`🧹 [refreshRoleOptions] No hay rol activo válido, limpiando`)
        activeRole.value = null
        localStorage.removeItem('activeRole')
        permissions.value = []
      }

      if (user.value) {
        user.value = {
          ...user.value,
          rol_activo: activeRole.value || rolBackend,
          roles_selector: selector,
          paneles: panelBackend
        }
        localStorage.setItem('user', JSON.stringify(user.value))
      }

      return { success: true }
    } catch (error) {
      console.error('Error al refrescar opciones de rol:', error)
      return { success: false, error: error.message || 'Error inesperado' }
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

        rolesSelector.value = response.data?.roles_selector || {}
        panels.value = response.data?.paneles || []
        
        // Solo actualizar el rol activo si no hay uno guardado o si el del backend es diferente
        // pero está en los roles del usuario (para evitar sobrescribir selecciones explícitas)
        const rolBackend = response.data?.rol_activo || null
        const rolActivoActual = activeRole.value || localStorage.getItem('activeRole')
        const rolesUsuario = response.data?.roles || []
        const nombresRoles = rolesUsuario.map(r => {
          if (typeof r === 'string') return r
          if (r.nombre_rol) return r.nombre_rol
          return String(r)
        })
        
        // Si hay un rol activo guardado y está en los roles del usuario, mantenerlo
        if (rolActivoActual && nombresRoles.some(r => r === rolActivoActual || r.toLowerCase() === rolActivoActual.toLowerCase())) {
          console.log(`✅ Manteniendo rol activo guardado en loadUserProfile: ${rolActivoActual} (backend sugiere: ${rolBackend})`)
          activeRole.value = rolActivoActual
          localStorage.setItem('activeRole', rolActivoActual)
        } else if (rolBackend) {
          // No hay rol guardado válido, usar el del backend
          activeRole.value = rolBackend
          localStorage.setItem('activeRole', rolBackend)
        } else {
          activeRole.value = null
          localStorage.removeItem('activeRole')
        }

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

  const validarTokenParaCarga = () => {
    if (!token.value) {
      console.warn('No hay token para cargar detalle del perfil')
      return false
    }
    return true
  }

  const loadUserProfileDetail = async () => {
    try {
      if (!validarTokenParaCarga()) {
        return false
      }

      isLoading.value = true
      console.log('🔄 Iniciando carga de detalle del perfil...')

      const response = await authService.getProfileDetail()
      console.log('📥 Respuesta del servicio:', response)

      if (response && response.success) {
        userDetail.value = extraerUserDetail(response)
        console.log('✅ userDetail actualizado:', userDetail.value)

        if (response.warning) {
          console.warn('⚠️ Advertencia al cargar detalle:', response.warning)
        }
        return true
      }

      manejarErrorRespuestaPerfil(response)
      return false
    } catch (err) {
      return manejarErrorCargaPerfil(err)
    } finally {
      isLoading.value = false
      console.log('🏁 Carga de detalle finalizada')
    }
  }

  const extraerUserDetail = (response) => {
    if (response.data) {
      return response.data
    }
    // Extraer todos los campos excepto success sin usar destructuring con variable
    const rest = { ...response }
    delete rest.success
    return rest
  }

  const manejarErrorRespuestaPerfil = (response) => {
    if (response?.expired) {
      console.warn('⚠️ Token expirado. Por favor, cierra sesión y vuelve a iniciar sesión.')
    } else {
      console.warn('❌ Error al cargar detalle del perfil:', response?.error || 'Respuesta sin éxito')
    }
    userDetail.value = null
  }

  const manejarErrorCargaPerfil = (err) => {
    if (!err.message?.includes('expirado') && !err.message?.includes('401')) {
      console.error('❌ Excepción al cargar detalle del perfil:', err)
      console.error('📋 Detalles del error:', {
        message: err.message,
        stack: err.stack
      })
    }

    userDetail.value = null

    if (err.message && err.message.includes('persona asociada')) {
      console.warn('⚠️ Continuando con datos parciales')
    }
    return false
  }

  const validarUsuarioGuardado = (savedUser) => {
    return savedUser && savedUser !== 'null' && savedUser !== 'undefined'
  }

  const parsearUsuarioGuardado = (savedUser) => {
    try {
      return JSON.parse(savedUser)
    } catch (parseError) {
      console.warn('Error al parsear usuario guardado:', parseError)
      localStorage.removeItem('user')
      return null
    }
  }

  const aplicarDatosUsuario = (usuarioParseado) => {
    if (!usuarioParseado) {
      return
    }

    user.value = usuarioParseado

    if (usuarioParseado.roles_selector) {
      rolesSelector.value = usuarioParseado.roles_selector
    }

    if (usuarioParseado.paneles) {
      panels.value = usuarioParseado.paneles
    }

    if (!activeRole.value && usuarioParseado.rol_activo) {
      activeRole.value = usuarioParseado.rol_activo
      localStorage.setItem('activeRole', usuarioParseado.rol_activo)
    }
  }

  const cargarUsuarioDesdeLocalStorage = () => {
    const savedUser = localStorage.getItem('user')
    if (!validarUsuarioGuardado(savedUser)) {
      return
    }

    const usuarioParseado = parsearUsuarioGuardado(savedUser)
    aplicarDatosUsuario(usuarioParseado)
  }

  const cargarRolActivoDesdeLocalStorage = async () => {
    const savedActiveRole = localStorage.getItem('activeRole')
    if (!savedActiveRole || savedActiveRole === 'null' || savedActiveRole === 'undefined') {
      return
    }

    activeRole.value = savedActiveRole
    await loadPermissionsForRole(savedActiveRole)
  }

  const verificarTokenSiExiste = async () => {
    if (!token.value || token.value === 'null' || token.value === 'undefined') {
      return
    }

    const isValid = await verifyToken()
    if (!isValid) {
      console.log('Token inválido, limpiando sesión')
    }
  }

  const limpiarDatosCorruptos = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('activeRole')
    token.value = null
    user.value = null
    activeRole.value = null
    permissions.value = []
  }

  const inicializar = async () => {
    try {
      cargarUsuarioDesdeLocalStorage()
      await cargarRolActivoDesdeLocalStorage()
      await verificarTokenSiExiste()
    } catch (err) {
      console.warn('Error al inicializar auth store:', err)
      limpiarDatosCorruptos()
    }
  }

  const clearError = () => {
    error.value = null
  }

  const updateUser = (userData) => {
    user.value = { ...user.value, ...userData }
    if (userData?.roles_selector) {
      rolesSelector.value = userData.roles_selector
    }
    if (userData?.paneles) {
      panels.value = userData.paneles
    }
    if (userData?.rol_activo) {
      activeRole.value = userData.rol_activo
      localStorage.setItem('activeRole', userData.rol_activo)
    }
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  // Función para establecer el rol activo seleccionado y cargar sus permisos
  const setActiveRole = async (roleName, forzarCambio = false) => {
    try {
      if (!roleName) {
        throw new Error('Debe proporcionar un rol válido')
      }

      // Verificar si hay un rol activo guardado que fue seleccionado explícitamente
      const rolActivoGuardado = localStorage.getItem('activeRole')
      const rolActual = activeRole.value || rolActivoGuardado
      
      // Si hay un rol guardado y es diferente del solicitado, y no se está forzando el cambio,
      // verificar si el cambio es necesario o si es un cambio automático no deseado
      if (rolActivoGuardado && rolActivoGuardado !== roleName && !forzarCambio) {
        // Verificar que el rol solicitado esté en los roles del usuario
        const rolesUsuario = user.value?.roles || []
        const nombresRoles = rolesUsuario.map(r => {
          if (typeof r === 'string') return r
          if (r.nombre_rol) return r.nombre_rol
          return String(r)
        })
        const rolSolicitadoEsValido = nombresRoles.some(r => 
          r === roleName || r.toLowerCase() === roleName.toLowerCase()
        )
        const rolGuardadoEsValido = nombresRoles.some(r => 
          r === rolActivoGuardado || r.toLowerCase() === rolActivoGuardado.toLowerCase()
        )
        
        // Si ambos roles son válidos, mantener el guardado (fue seleccionado explícitamente)
        if (rolGuardadoEsValido && rolSolicitadoEsValido && rolActivoGuardado !== roleName) {
          console.log(`⚠️ [setActiveRole] Intento de cambiar rol de "${rolActivoGuardado}" a "${roleName}", pero "${rolActivoGuardado}" fue seleccionado explícitamente. Manteniendo "${rolActivoGuardado}"`)
          // No cambiar el rol, solo actualizar permisos si es necesario
          if (activeRole.value !== rolActivoGuardado) {
            activeRole.value = rolActivoGuardado
            await loadPermissionsForRole(rolActivoGuardado)
          }
          return { success: true, message: 'Rol mantenido (fue seleccionado explícitamente)' }
        }
      }

      console.log(`🔄 [setActiveRole] Cambiando rol activo a: ${roleName}`)

      const response = await authService.activateRole(roleName)
      if (!response.success) {
        throw new Error(response.error || 'No se pudo cambiar el rol activo')
      }

      const {
        rol_activo: rolBackend = roleName,
        roles_selector: selector = rolesSelector.value,
        paneles: panelBackend = panels.value
      } = response.data || {}

      // Asegurar que el rol del backend coincida con el solicitado (puede haber diferencias de mayúsculas)
      const rolFinal = rolBackend || roleName
      activeRole.value = rolFinal
      localStorage.setItem('activeRole', rolFinal)
      console.log(`✅ [setActiveRole] Rol activo establecido: ${rolFinal}`)

      rolesSelector.value = selector || {}
      panels.value = Array.isArray(panelBackend) ? panelBackend : []

      await loadPermissionsForRole(rolFinal)

      if (user.value) {
        user.value = {
          ...user.value,
          rol_activo: rolFinal,
          roles_selector: selector,
          paneles: panels.value
        }
        localStorage.setItem('user', JSON.stringify(user.value))
      }

      return { success: true }
    } catch (error) {
      console.error('❌ [setActiveRole] Error al establecer rol activo:', error)
      return { success: false, error: error.message || 'Error al cambiar rol activo' }
    }
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
    rolesSelector,
    panels,
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
    refreshRoleOptions,
    inicializar,
    clearError,
    updateUser,
    setActiveRole, // Nueva acción para establecer rol activo
    clearActiveRole // Nueva acción para limpiar rol activo
  }
})
