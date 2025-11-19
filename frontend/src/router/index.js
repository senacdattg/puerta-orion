import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Inicio from '@/views/Inicio.vue'
import ActualizarDeportista from '@/views/actualizar-deportista.vue'
import RegistrarDeportista from '@/views/registrar-deportista.vue'
import RegistrarGeneral from '@/views/registrar-general.vue'
import ActualizarGeneral from '@/views/actualizar-general.vue'

import TablaMensualidades from '@/views/mensualidades.vue'
import TablaDeportistas from '@/views/vista-deportistas.vue'
import Galeria from '@/views/galeria-vista.vue'
import RolesRegistroVista from '@/views/roles-registro-vista.vue'
import Calendario from '@/views/calendario.vue'
import Login from '@/views/login.vue'
import ForgotPassword from '@/views/forgot-password.vue'
import ResetPassword from '@/views/reset-password.vue'
import panelAdmin from '@/views/admin-manager.vue'
import CompletarPerfil from '@/views/completar-perfil.vue'
import RegistrarAcudiente from '@/views/registrar-acudiente.vue'
import FormularioAcudienteCompleto from '@/views/formulario-acudiente-completo.vue'
import RegistrarDeportistaForm from '@/views/registrar-deportista-form.vue'
import DeportistaDashboard from '@/views/DeportistaDashboard.vue'
import AcudienteDashboard from '@/views/AcudienteDashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { requiresGuest: true }
    },
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: ForgotPassword,
      meta: { requiresGuest: true }
    },
    {
      path: '/auth/reset-password',
      name: 'reset-password',
      component: ResetPassword,
      meta: { requiresGuest: true }
    },
    {
      path: '/home',
      name: 'home',
      component: Inicio,
      meta: { requiresAuth: true }
    },
    {
      path: '/inicio',
      redirect: '/home'
    },
    {
      path: '/actualizar-deportista',
      name: 'actualizar-deportista',
      component: ActualizarDeportista,
      meta: { requiresAuth: true }
    },
    {
      path: '/registrar-deportista',
      name: 'registrar-deportista',
      component: RegistrarDeportista,
      meta: { requiresAuth: true }
    },
    {
      path: '/registrar-general',
      name: 'registrar-general',
      component: RegistrarGeneral,
      meta: { requiresGuest: true }
    },
    {
      path: '/actualizar-general',
      name: 'actualizar-general',
      component: ActualizarGeneral,
      meta: { requiresAuth: true }
    },
    {
      path: '/mensualidades',
      name: 'mensualidades',
      component: TablaMensualidades,
      meta: { requiresAuth: true, requiresPermission: 'ver_mensualidad' }
    },
    {
      path: '/deportistas',
      name: 'deportistas',
      component: TablaDeportistas,
      meta: { requiresAuth: true }
    },
    {
      path: '/galeria',
      name: 'galeria',
      component: Galeria,
      meta: { requiresAuth: true }
    },
    {
      path: '/roles-registro',
      name: 'roles-registro',
      component: RolesRegistroVista,
      meta: { requiresGuest: true }
    },
    {
      path: '/seleccionar-rol',
      name: 'seleccionar-rol',
      component: RolesRegistroVista,
      meta: { requiresAuth: true }
    },
    {
      path: '/calendario',
      name: 'calendario',
      component: Calendario,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin-manager',
      name: 'admin-manager',
      component: panelAdmin,
      meta: { requiresAuth: true, requiresRole: ['SuperAdmin', 'Administrador'] }
    },
    {
      path: '/completar-perfil',
      name: 'completar-perfil',
      component: CompletarPerfil,
      meta: { requiresAuth: true, requiresRole: ['Deportista', 'Acudiente'] }
    },
    {
      path: '/registrar-acudiente',
      name: 'registrar-acudiente',
      component: RegistrarAcudiente,
      meta: { requiresAuth: true }
    },
    {
      path: '/formulario-acudiente-completo',
      name: 'formulario-acudiente-completo',
      component: FormularioAcudienteCompleto,
      meta: { requiresAuth: true }
    },
    {
      path: '/registrar-deportista-form',
      name: 'registrar-deportista-form',
      component: RegistrarDeportistaForm,
      meta: { requiresAuth: true }
    },
    {
      path: '/acudiente/ver-acudidos',
      name: 'ver-acudidos',
      component: () => import('@/views/ver-acudidos.vue'),
      meta: { requiresAuth: true, requiresRole: ['Acudiente'] }
    },
    {
      path: '/asignar-acudido',
      name: 'asignar-acudido',
      component: () => import('@/views/asignar-acudido.vue'),
      meta: { requiresAuth: true, requiresRole: ['Acudiente'] }
    },
    {
      path: '/asignar-acudiente',
      name: 'asignar-acudiente',
      component: () => import('@/views/asignar-acudiente.vue'),
      meta: { requiresAuth: true, requiresRole: ['Deportista'] }
    },
    {
      path: '/actualizar-info',
      name: 'actualizar-info',
      component: () => import('@/views/actualizar-info.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/perfil',
      name: 'perfil',
      component: () => import('@/views/perfil.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/eventos',
      name: 'eventos',
      component: () => import('@/views/eventos.vue'),
      meta: { requiresAuth: true, requiresRole: ['Deportista', 'Acudiente'] }
    },
    // Rutas del panel de deportista
    {
      path: '/deportista/dashboard',
      name: 'deportista-dashboard',
      component: DeportistaDashboard,
      meta: { requiresAuth: true, requiresRole: ['Deportista'] }
    },
    {
      path: '/deportista/mensualidades',
      name: 'deportista-mensualidades',
      component: TablaMensualidades,
      meta: { requiresAuth: true, requiresRole: ['Deportista'] }
    },
    {
      path: '/deportista/eventos',
      name: 'deportista-eventos',
      component: () => import('@/views/eventos.vue'),
      meta: { requiresAuth: true, requiresRole: ['Deportista'] }
    },
    {
      path: '/deportista/calendario',
      name: 'deportista-calendario',
      component: Calendario,
      meta: { requiresAuth: true, requiresRole: ['Deportista'] }
    },
    {
      path: '/deportista/galeria',
      name: 'deportista-galeria',
      component: Galeria,
      meta: { requiresAuth: true, requiresRole: ['Deportista'] }
    },
    // Rutas del panel de acudiente
    {
      path: '/acudiente/dashboard',
      name: 'acudiente-dashboard',
      component: AcudienteDashboard,
      meta: { requiresAuth: true, requiresRole: ['Acudiente'] }
    }
  ],
})

// Función auxiliar para obtener la ruta de redirección según el rol
function getDefaultRouteForRole(userRoles, activeRole = null) {
  // Si hay un rol activo seleccionado, usarlo para la redirección
  if (activeRole) {
    // Normalizar el nombre del rol para comparación (primera letra mayúscula)
    const rolNormalizado = activeRole?.charAt(0).toUpperCase() + activeRole?.slice(1).toLowerCase()
    
    switch(rolNormalizado) {
      case 'SuperAdmin':
      case 'Administrador':
        return '/admin-manager'
      case 'Deportista':
        return '/deportista/dashboard'
      case 'Acudiente':
        return '/acudiente/dashboard'
      case 'Usuario':
      case 'Entrenador':
      default:
        return '/home'
    }
  }

  // Si no hay rol activo, verificar cuántos roles tiene
  if (!userRoles || userRoles.length === 0) {
    return '/home'
  }

  // Extraer nombres de roles
  const roleNames = userRoles.map(role =>
    typeof role === 'string' ? role : role.nombre_rol
  )

  // Si tiene múltiples roles pero no ha seleccionado uno, redirigir a selección
  if (roleNames.length > 1) {
    return '/seleccionar-rol'
  }

  // Si tiene un solo rol, usar ese para redirección automática
  if (roleNames.length === 1) {
    const singleRole = roleNames[0]
    // Normalizar el nombre del rol para comparación
    const rolNormalizado = singleRole?.charAt(0).toUpperCase() + singleRole?.slice(1).toLowerCase()
    
    switch(rolNormalizado) {
      case 'SuperAdmin':
      case 'Administrador':
        return '/admin-manager'
      case 'Deportista':
        return '/deportista/dashboard'
      case 'Acudiente':
        return '/acudiente/dashboard'
      case 'Usuario':
      case 'Entrenador':
      default:
        return '/home'
    }
  }

  return '/home'
}

// Función para verificar si el usuario tiene el rol requerido
function hasRequiredRole(userRoles, requiredRoles) {
  if (!requiredRoles || requiredRoles.length === 0) return true
  if (!userRoles || userRoles.length === 0) return false

  const roleNames = userRoles.map(role =>
    typeof role === 'string' ? role : role.nombre_rol
  )

  return requiredRoles.some(requiredRole => roleNames.includes(requiredRole))
}

// Función auxiliar para obtener nombres de roles
function obtenerNombresRoles(roles) {
  return roles.map(r => typeof r === 'string' ? r : r?.nombre_rol).filter(Boolean)
}

// Función auxiliar para inicializar el auth store
async function inicializarAuthStore(authStore) {
  if (!authStore.user && authStore.token) {
    await authStore.inicializar()
  }
}

// Función auxiliar para obtener roles del selector
function obtenerSelectorRoles(authStore) {
  return Object.entries(authStore.rolesSelector || {})
    .filter(([, visible]) => visible)
    .map(([role]) => role)
}

// Función auxiliar para manejar rutas que requieren autenticación
function manejarRutaRequiereAuth(isAuthenticated, next) {
  if (!isAuthenticated) {
    console.log('🔒 Redirigiendo a login: usuario no autenticado')
    next('/login')
    return true
  }
  return false
}

// Función auxiliar para manejar rutas de invitados
function manejarRutaRequiereGuest(isAuthenticated, authStore, selectorRoles, next) {
  if (!isAuthenticated) return false

  const rawRoles = selectorRoles.length ? selectorRoles : (authStore.user?.roles || [])
  const roleNames = obtenerNombresRoles(rawRoles)

  if (roleNames.length > 1 && !authStore.activeRole) {
    console.log('🔄 Usuario con múltiples roles, redirigiendo a selección de rol')
    next('/seleccionar-rol')
    return true
  }

  const defaultRoute = getDefaultRouteForRole(rawRoles, authStore.activeRole)
  console.log('🔄 Redirigiendo usuario autenticado:', defaultRoute)
  next(defaultRoute)
  return true
}

// Función auxiliar para verificar rol activo
function verificarRolActivo(activeRole, requiredRoles) {
  const roleNames = requiredRoles.map(r => typeof r === 'string' ? r : (r.nombre_rol || String(r)))
  return roleNames.includes(activeRole)
}

// Función auxiliar para manejar rutas que requieren roles
function manejarRutaRequiereRol(authStore, selectorRoles, requiredRoles, to, next) {
  if (authStore.activeRole) {
    if (verificarRolActivo(authStore.activeRole, requiredRoles)) {
      console.log('✅ Acceso autorizado con rol activo:', authStore.activeRole)
      next()
      return
    }
    console.log('🚫 Acceso denegado: rol activo no coincide. Requerido:', requiredRoles, 'Rol activo:', authStore.activeRole)
    next('/seleccionar-rol')
    return
  }

  const userRoles = selectorRoles.length ? selectorRoles : (authStore.user?.roles || [])
  console.log('🔍 Verificando rol para:', to.path)
  console.log('🔍 Roles requeridos:', requiredRoles)
  console.log('🔍 Roles del usuario:', userRoles)

  if (!hasRequiredRole(userRoles, requiredRoles)) {
    console.log('🚫 Acceso denegado: rol insuficiente. Requerido:', requiredRoles, 'Usuario:', userRoles)
    const roleNames = obtenerNombresRoles(selectorRoles.length ? selectorRoles : (authStore.user?.roles || []))
    if (roleNames.length > 1) {
      next('/seleccionar-rol')
    } else {
      next('/home')
    }
    return
  }

  console.log('✅ Acceso autorizado para:', to.path)
  next()
}

// Función auxiliar para verificar si es SuperAdmin o Administrador
function esSuperAdminOAdministrador(activeRole) {
  return ['SuperAdmin', 'Administrador'].includes(activeRole)
}

// Función auxiliar para manejar rutas que requieren permisos
async function manejarRutaRequierePermiso(authStore, requiredPermission, next) {
  if (esSuperAdminOAdministrador(authStore.activeRole)) {
    next()
    return true
  }

  if (!authStore.permissions || authStore.permissions.length === 0) {
    try {
      await authStore.loadUserPermissions?.()
    } catch (err) {
      console.warn('Error cargando permisos:', err)
    }
  }

  const permisos = authStore.permissions || []
  const has = (Array.isArray(permisos) && permisos.includes(requiredPermission)) ||
              (authStore.hasPermission && authStore.hasPermission(requiredPermission))

  if (!has) {
    console.log('🚫 Acceso denegado: permiso insuficiente. Requerido:', requiredPermission)
    next('/home')
    return true
  }

  return false
}

// Función auxiliar para validar acceso a mensualidades
function validarAccesoMensualidades(to, authStore, next) {
  if (to.name !== 'mensualidades') return false

  const active = authStore.activeRole
  if (!esSuperAdminOAdministrador(active) && ['Entrenador', 'Usuario'].includes(active)) {
    console.log('🚫 Acceso denegado a mensualidades por rol (Entrenador/Usuario)')
    next('/home')
    return true
  }

  return false
}

// Función auxiliar para validar selección de rol
function validarSeleccionRol(requiresAuth, isAuthenticated, to, authStore, next) {
  if (!requiresAuth || !isAuthenticated || to.path.includes('/seleccionar-rol') || to.path === '/home') {
    return false
  }

  const userRoles = authStore.user?.roles || []
  const roleNames = obtenerNombresRoles(userRoles)

  if (roleNames.length > 1 && !authStore.activeRole) {
    console.log('🔄 Usuario con múltiples roles sin seleccionar, redirigiendo a selección')
    next('/seleccionar-rol')
    return true
  }

  return false
}

// Función auxiliar para verificar token
async function verificarToken(authStore) {
  if (!authStore.token) {
    return false
  }
  return await authStore.verifyToken()
}

// Función auxiliar para refrescar opciones de rol si es necesario
async function refrescarOpcionesRol(authStore, isAuthenticated) {
  if (isAuthenticated && !Object.keys(authStore.rolesSelector || {}).length) {
    await authStore.refreshRoleOptions?.()
  }
}

// Función auxiliar para verificar autenticación
async function verificarAutenticacion(authStore) {
  const isAuthenticated = await verificarToken(authStore)
  await refrescarOpcionesRol(authStore, isAuthenticated)
  return isAuthenticated
}

// Función auxiliar para extraer metadatos de la ruta
function extraerMetadatosRuta(to) {
  return {
    requiresAuth: to.matched.some(record => record.meta.requiresAuth),
    requiresGuest: to.matched.some(record => record.meta.requiresGuest),
    requiresRole: to.matched.some(record => record.meta.requiresRole),
    requiredPermission: to.matched.find(r => r.meta && r.meta.requiresPermission)?.meta?.requiresPermission
  }
}

// Guard de navegación global
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  await inicializarAuthStore(authStore)
  const isAuthenticated = await verificarAutenticacion(authStore)
  const selectorRoles = obtenerSelectorRoles(authStore)
  const meta = extraerMetadatosRuta(to)

  if (meta.requiresAuth && manejarRutaRequiereAuth(isAuthenticated, next)) {
    return
  }

  if (meta.requiresGuest && manejarRutaRequiereGuest(isAuthenticated, authStore, selectorRoles, next)) {
    return
  }

  if (meta.requiresAuth && isAuthenticated && meta.requiresRole) {
    const requiredRoles = to.meta.requiresRole
    manejarRutaRequiereRol(authStore, selectorRoles, requiredRoles, to, next)
    return
  }

  if (meta.requiresAuth && isAuthenticated && meta.requiredPermission) {
    if (await manejarRutaRequierePermiso(authStore, meta.requiredPermission, next)) {
      return
    }
  }

  if (validarAccesoMensualidades(to, authStore, next)) {
    return
  }

  if (validarSeleccionRol(meta.requiresAuth, isAuthenticated, to, authStore, next)) {
    return
  }

  next()
})

export default router
