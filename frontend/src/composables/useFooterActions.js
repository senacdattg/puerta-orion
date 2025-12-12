/**
 * Composable for footer actions based on user role
 * Provides reusable logic for userRole and accionesRapidas following DRY principles
 */

import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

/**
 * Gets the current user role for display purposes
 * @param {Object} authStore - Auth store instance
 * @returns {string} User role
 */
function getUserRole(authStore) {
  const active = authStore.activeRole
  if (active) {
    if (active === 'SuperAdmin' || active === 'Administrador') {
      return 'Admin'
    }
    return active
  }

  if (!authStore.user?.roles?.length) { // NOSONAR: S6582
    return 'Usuario'
  }

  const roles = authStore.user.roles
  const roleNames = new Set(roles.map(role => typeof role === 'string' ? role : role.nombre_rol))

  if (roleNames.has('SuperAdmin') || roleNames.has('Administrador')) {
    return 'Admin'
  }
  if (roleNames.has('Entrenador')) {
    return 'Entrenador'
  }
  if (roleNames.has('Deportista')) {
    return 'Deportista'
  }
  if (roleNames.has('Acudiente')) {
    return 'Acudiente'
  }
  if (roleNames.has('usuario')) {
    return 'Usuario'
  }
  return 'UsuarioSinAuth'
}

/**
 * Gets quick actions based on user role
 * @param {string} role - User role
 * @returns {Array} Array of action objects
 */
function getAccionesPorRol(role) {
  const accionesPorRol = {
    Usuario: [
      { texto: 'Calendario', link: '/calendario', icono: 'fas fa-calendar' },
      { texto: 'Galería', link: '/galeria', icono: 'fas fa-images' },
      { texto: 'Mi Perfil', link: '/perfil', icono: 'fas fa-user' }
    ],
    Entrenador: [
      { texto: 'Calendario', link: '/calendario', icono: 'fas fa-calendar' },
      { texto: 'Deportistas', link: '/deportistas', icono: 'fas fa-users' },
      { texto: 'Mi Perfil', link: '/perfil', icono: 'fas fa-user' },
      { texto: 'Galería', link: '/galeria', icono: 'fas fa-images' }
    ],
    Acudiente: [
      { texto: 'Mis Deportistas', link: '/acudiente/ver-acudidos', icono: 'fas fa-child' },
      { texto: 'Mensualidades', link: '/mensualidades', icono: 'fas fa-wallet' },
      { texto: 'Calendario', link: '/calendario', icono: 'fas fa-calendar' },
      { texto: 'Mi Perfil', link: '/perfil', icono: 'fas fa-user' }
    ],
    Deportista: [
      { texto: 'Mi Perfil', link: '/perfil', icono: 'fas fa-user' },
      { texto: 'Mensualidades', link: '/mensualidades', icono: 'fas fa-wallet' },
      { texto: 'Eventos', link: '/eventos', icono: 'fas fa-calendar-check' },
      { texto: 'Calendario', link: '/calendario', icono: 'fas fa-calendar' }
    ],
    Admin: [
      { texto: 'Panel Admin', link: '/admin-manager', icono: 'fas fa-cog' },
      { texto: 'Deportistas', link: '/deportistas', icono: 'fas fa-users' },
      { texto: 'Mensualidades', link: '/mensualidades', icono: 'fas fa-wallet' },
      { texto: 'Calendario', link: '/calendario', icono: 'fas fa-calendar' }
    ],
    UsuarioSinAuth: [
      { texto: 'Calendario', link: '/calendario', icono: 'fas fa-calendar' },
      { texto: 'Galería', link: '/galeria', icono: 'fas fa-images' }
    ]
  }

  return accionesPorRol[role] || accionesPorRol['UsuarioSinAuth']
}

/**
 * Composable for footer actions
 * @returns {Object} Computed properties for userRole and accionesRapidas
 */
export function useFooterActions() {
  const authStore = useAuthStore()

  const userRole = computed(() => getUserRole(authStore))

  const accionesRapidas = computed(() => {
    const rolActual = userRole.value
    return getAccionesPorRol(rolActual)
  })

  return {
    userRole,
    accionesRapidas
  }
}

