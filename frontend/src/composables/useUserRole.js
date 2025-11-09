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

  const availableRoles = computed(() => {
    const selector = authStore.rolesSelector || {}
    const entries = Object.entries(selector).filter(([, visible]) => visible)
    if (entries.length > 0) {
      return entries.map(([role]) => role)
    }

    const rawRoles = authStore.userRoles || []
    return rawRoles.length > 0 ? rawRoles : ['Usuario']
  })

  const userRole = computed(() => {
    if (authStore.activeRole) {
      return authStore.activeRole
    }
    const roles = availableRoles.value
    return roles.length > 0 ? roles[0] : 'Usuario'
  })

  const isAdminOrCoach = computed(() => {
    return ['Administrador', 'SuperAdmin', 'Entrenador'].includes(userRole.value)
  })

  const isDeportista = computed(() => {
    return userRole.value === 'Deportista'
  })

  const isAcudiente = computed(() => {
    return userRole.value === 'Acudiente'
  })

  const allowedPanels = computed(() => {
    const result = {}
    const panelList = authStore.panels || []
    panelList.forEach(panel => {
      if (panel && panel.module) {
        result[panel.module] = panel.allowed !== false
      }
    })
    return result
  })

  const panelModuleMap = {
    calendario: 'calendario',
    galeria: 'galeria',
    mensualidades: 'mensualidades',
    deportistas: 'deportistas',
    admin: 'panel_admin'
  }

  const availableRoleSet = computed(() => new Set(
    availableRoles.value.map(role => {
      if (typeof role === 'string') return role
      if (role?.nombre_rol) return role.nombre_rol
      return role?.rol || role
    })
  ))

  const filteredNavigation = computed(() => {
    const rolesSet = availableRoleSet.value
    const hasRoles = rolesSet.size > 0

    return navigationConfig.filter(item => {
      const moduleKey = panelModuleMap[item.id]
      if (moduleKey && allowedPanels.value[moduleKey] === false) {
        return false
      }

      if (!hasRoles) {
        return moduleKey ? allowedPanels.value[moduleKey] !== false : true
      }

      return item.roles.some(role => rolesSet.has(role))
    })
  })

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

  const hasRole = (roleName) => {
    return availableRoleSet.value.has(roleName)
  }

  const canAccessRoute = (routeName) => {
    const rolesSet = availableRoleSet.value
    const navItem = navigationConfig.find(item => item.route === routeName)

    if (!navItem) return true // Si no está en la config, permitir acceso
    if (rolesSet.size === 0) {
      const moduleKey = panelModuleMap[navItem.id]
      if (moduleKey) {
        return allowedPanels.value[moduleKey] !== false
      }
      return false
    }

    return navItem.roles.some(role => rolesSet.has(role))
  }

  return {
    // Propiedades computadas
    userRole,
    isAdminOrCoach,
    isDeportista,
    isAcudiente,
    availableRoles,
    filteredNavigation,
    welcomeMessage,

    // Métodos
    hasRole,
    canAccessRoute
  }
}

