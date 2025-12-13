import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Solo Login se carga inmediatamente (página inicial)
import Login from '@/views/login.vue'

// Todas las demás rutas con lazy loading para code splitting
const Inicio = () => import('@/views/Inicio.vue')
const RegistrarDeportista = () => import('@/views/registrar-deportista.vue')
const RegistrarGeneral = () => import('@/views/registrar-general.vue')
const TablaMensualidades = () => import('@/views/mensualidades.vue')
const TablaDeportistas = () => import('@/views/vista-deportistas.vue')
const Galeria = () => import('@/views/galeria-vista.vue')
const RolesRegistroVista = () => import('@/views/roles-registro-vista.vue')
const Calendario = () => import('@/views/calendario.vue')
const ForgotPassword = () => import('@/views/forgot-password.vue')
const ResetPassword = () => import('@/views/reset-password.vue')
const panelAdmin = () => import('@/views/admin-manager.vue')
const CompletarPerfil = () => import('@/views/completar-perfil.vue')
const RegistrarAcudiente = () => import('@/views/registrar-acudiente.vue')
const FormularioAcudienteCompleto = () => import('@/views/formulario-acudiente-completo.vue')
const RegistrarDeportistaForm = () => import('@/views/registrar-deportista-form.vue')
const DeportistaDashboard = () => import('@/views/DeportistaDashboard.vue')
const AcudienteDashboard = () => import('@/views/AcudienteDashboard.vue')

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

  const roleNames = new Set(userRoles.map(role =>
    typeof role === 'string' ? role : role.nombre_rol
  ))

  return requiredRoles.some(requiredRole => roleNames.has(requiredRole))
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
    next('/seleccionar-rol')
    return true
  }

  const defaultRoute = getDefaultRouteForRole(rawRoles, authStore.activeRole)
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
      next()
      return
    }
    next('/seleccionar-rol')
    return
  }

  const userRoles = selectorRoles.length ? selectorRoles : (authStore.user?.roles || [])

  if (!hasRequiredRole(userRoles, requiredRoles)) {
    const roleNames = obtenerNombresRoles(selectorRoles.length ? selectorRoles : (authStore.user?.roles || []))
    if (roleNames.length > 1) {
      next('/seleccionar-rol')
    } else {
      next('/home')
    }
    return
  }

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
              (authStore.hasPermission?.(requiredPermission))

  if (!has) {
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
// Solo refrescar si no hay rolesSelector Y no hay rol activo guardado
// Esto evita sobrescribir el rol activo que el usuario seleccionó explícitamente
async function refrescarOpcionesRol(authStore, isAuthenticated) {
  if (isAuthenticated && !Object.keys(authStore.rolesSelector || {}).length) {
    const tieneRolActivo = authStore.activeRole || localStorage.getItem('activeRole')
    if (tieneRolActivo) {
    }
    await authStore.refreshRoleOptions?.()
    // Verificar si el refresh cambió el rol y restaurarlo si es necesario
    if (tieneRolActivo && authStore.activeRole !== tieneRolActivo) {
      const rolesUsuario = authStore.user?.roles || []
      const nombresRoles = rolesUsuario.map(r => {
        if (typeof r === 'string') return r
        if (r.nombre_rol) return r.nombre_rol
        return String(r)
      })
      if (nombresRoles.some(r => r === tieneRolActivo || r.toLowerCase() === tieneRolActivo.toLowerCase())) {
        await authStore.setActiveRole?.(tieneRolActivo)
      }
    }
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
  const requiresRoleRecord = to.matched.find(r => r.meta?.requiresRole)
  return {
    requiresAuth: to.matched.some(record => record.meta.requiresAuth),
    requiresGuest: to.matched.some(record => record.meta.requiresGuest),
    requiresRole: requiresRoleRecord?.meta?.requiresRole || null,
    requiredPermission: to.matched.find(r => r.meta?.requiresPermission)?.meta?.requiresPermission
  }
}

// Navigation guard function - exported for testing
export async function navigationGuard(to, from, next) {
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
    manejarRutaRequiereRol(authStore, selectorRoles, meta.requiresRole, to, next)
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
}

// Guard de navegación global
router.beforeEach(navigationGuard)

export default router
