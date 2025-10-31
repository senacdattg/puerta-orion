/**
 * Composable para gestionar la lógica relacionada con roles de usuario
 * @module composables/useUserRole
 */

import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

/**
 * Configuración de elementos de navegación con sus roles permitidos
 */
export const navigationConfig = [
  {
    id: 'registro-deportista',
    title: 'Registrar Deportista',
    route: '/registrar-deportista-form',
    icon: 'fas fa-user-plus',
    colorClass: 'nav-card--green',
    roles: ['Administrador', 'Entrenador']
  },
  {
    id: 'registro-acudiente',
    title: 'Registrar Acudiente',
    route: '/registrar-acudiente',
    icon: 'fas fa-user-friends',
    colorClass: 'nav-card--teal',
    roles: ['Administrador', 'Entrenador']
  },
  {
    id: 'completar-perfil',
    title: 'Completar Perfil',
    route: '/completar-perfil',
    icon: 'fas fa-user-edit',
    colorClass: 'nav-card--orange',
    roles: ['Deportista', 'Acudiente']
  },
  {
    id: 'calendario',
    title: 'Ver Calendario',
    route: '/calendario',
    icon: 'fas fa-calendar-alt',
    colorClass: 'nav-card--blue',
    roles: ['Administrador', 'Entrenador', 'Deportista', 'Acudiente']
  },
  {
    id: 'galeria',
    title: 'Galería',
    route: '/galeria',
    icon: 'fas fa-images',
    colorClass: 'nav-card--gray',
    roles: ['Administrador', 'Entrenador', 'Deportista', 'Acudiente']
  },
  {
    id: 'admin',
    title: 'Panel Admin',
    route: '/admin-manager',
    icon: 'fas fa-cog',
    colorClass: 'nav-card--red',
    roles: ['Administrador', 'SuperAdmin']
  },
  {
    id: 'deportistas',
    title: 'Deportistas',
    route: '/deportistas',
    icon: 'fas fa-users',
    colorClass: 'nav-card--green',
    roles: ['Administrador', 'Entrenador']
  },
  {
    id: 'mensualidades',
    title: 'Mensualidades',
    route: '/mensualidades',
    icon: 'fas fa-money-bill-wave',
    colorClass: 'nav-card--purple',
    roles: ['Administrador', 'Entrenador']
  }
]

/**
 * Composable principal para manejar roles de usuario
 * @returns {Object} Objeto con propiedades y métodos relacionados con roles
 */
export function useUserRole() {
  const authStore = useAuthStore()

  /**
   * Obtiene el rol activo del usuario (respecta el rol seleccionado en localStorage)
   * Si no hay rol activo, usa el rol principal basado en jerarquía de prioridades
   * @returns {string} Nombre del rol activo
   */
  const userRole = computed(() => {
    // PRIORIDAD 1: Usar el rol activo del store (si fue seleccionado explícitamente)
    const activeRole = authStore.activeRole
    if (activeRole) {
      if (activeRole === 'SuperAdmin' || activeRole === 'Administrador') {
        return 'Admin'
      }
      return activeRole
    }

    const userRoles = authStore.userRoles

    if (!userRoles || userRoles.length === 0) {
      return 'Usuario'
    }

    // Extraer nombres de roles (pueden ser objetos o strings)
    const roleNames = userRoles.map(role => {
      if (typeof role === 'string') return role
      if (role.nombre_rol) return role.nombre_rol
      if (role.rol) return role.rol
      return role.toString()
    })

    // PRIORIDAD 2: Si tiene UN SOLO rol, usar ese (automático)
    if (roleNames.length === 1) {
      const singleRole = roleNames[0]
      if (singleRole === 'SuperAdmin' || singleRole === 'Administrador') {
        return 'Admin'
      }
      return singleRole
    }

    // PRIORIDAD 3: Si tiene MÚLTIPLES roles pero NO ha seleccionado uno, devolver null/UsuarioSinAuth
    // NO usar fallback automático para evitar asignar Admin por defecto
    return 'UsuarioSinAuth'
  })

  /**
   * Función helper para extraer nombres de roles
   */
  // Nota: getRoleNames no se utiliza actualmente; eliminar para evitar warning del linter

  /**
   * Verifica si el usuario es administrador o entrenador (basado en el rol activo)
   * @returns {boolean}
   */
  const isAdminOrCoach = computed(() => {
    return userRole.value === 'Administrador' ||
           userRole.value === 'SuperAdmin' ||
           userRole.value === 'Entrenador'
  })

  /**
   * Verifica si el usuario es deportista (basado en el rol activo)
   * @returns {boolean}
   */
  const isDeportista = computed(() => {
    return userRole.value === 'Deportista'
  })

  /**
   * Verifica si el usuario es acudiente (basado en el rol activo)
   * @returns {boolean}
   */
  const isAcudiente = computed(() => {
    return userRole.value === 'Acudiente'
  })

  /**
   * Filtra elementos de navegación según los roles del usuario
   * @returns {Array} Array de elementos de navegación permitidos
   */
  const filteredNavigation = computed(() => {
    const userRoles = authStore.userRoles
    console.log('🔍 Debug filteredNavigation:')
    console.log('- userRoles:', userRoles)
    console.log('- authStore.user:', authStore.user)

    // Si no hay roles, mostrar solo calendario y galería
    if (!userRoles || userRoles.length === 0) {
      console.log('- No hay roles, mostrando calendario y galería')
      return navigationConfig.filter(item =>
        item.id === 'calendario' || item.id === 'galeria'
      )
    }

    // Extraer nombres de roles (en caso de que sean objetos)
    const roleNames = userRoles.map(role => {
      if (typeof role === 'string') return role
      if (role.nombre_rol) return role.nombre_rol
      if (role.rol) return role.rol
      return role.toString()
    })

    console.log('- roleNames extraídos:', roleNames)

    // Filtrar elementos según los roles del usuario
    const filtered = navigationConfig.filter(item => {
      return item.roles.some(role => roleNames.includes(role))
    })

    console.log('- elementos filtrados:', filtered)
    return filtered
  })

  /**
   * Obtiene el mensaje de bienvenida personalizado según el rol
   * @returns {Object} Objeto con título y descripción
   */
  const welcomeMessage = computed(() => {
    const userName = authStore.user?.nombre || 'Usuario'

    if (isAdminOrCoach.value) {
      return {
        title: `¡Bienvenido, ${userName}!`,
        description: 'Gestiona el club deportivo desde tu panel de administración'
      }
    }

    return {
      title: `¡Bienvenido, ${userName}!`,
      description: 'Accede al calendario de actividades y galería de fotos del club'
    }
  })

  /**
   * Verifica si el usuario tiene un rol específico
   * @param {string} roleName - Nombre del rol a verificar
   * @returns {boolean}
   */
  const hasRole = (roleName) => {
    const userRoles = authStore.userRoles
    if (!userRoles || userRoles.length === 0) return false

    // Los roles ya están procesados como strings en el store
    return userRoles.includes(roleName)
  }

  /**
   * Verifica si el usuario tiene acceso a una ruta específica
   * @param {string} routeName - Nombre de la ruta
   * @returns {boolean}
   */
  const canAccessRoute = (routeName) => {
    const userRoles = authStore.userRoles
    const navItem = navigationConfig.find(item => item.route === routeName)

    if (!navItem) return true // Si no está en la config, permitir acceso
    if (!userRoles || userRoles.length === 0) return false

    // Los roles ya están procesados como strings en el store
    return navItem.roles.some(role => userRoles.includes(role))
  }

  return {
    // Propiedades computadas
    userRole,
    isAdminOrCoach,
    isDeportista,
    isAcudiente,
    filteredNavigation,
    welcomeMessage,

    // Métodos
    hasRole,
    canAccessRoute
  }
}

