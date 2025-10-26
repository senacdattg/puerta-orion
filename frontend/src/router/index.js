import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Inicio from '@/views/Inicio.vue'
import ActualizarDeportista from '@/views/actualizar-deportista.vue'
import RegistrarDeportista from '@/views/registrar-deportista.vue'
import VerDeportista from '@/views/ver-deportista.vue'
import RegistrarGeneral from '@/views/registrar-general.vue'
import VerGeneral from '@/views/ver-general.vue'
import ActualizarGeneral from '@/views/actualizar-general.vue'
import VerRoles from '@/views/vista-roles.vue'
import TablaMensualidades from '@/views/mensualidades.vue'
import TablaDeportistas from '@/views/vista-deportistas.vue'
import Galeria from '@/views/galeria-vista.vue'
import RolesRegistroVista from '@/views/roles-registro-vista.vue'
import Calendario from '@/views/calendario.vue'
import Login from '@/views/login.vue'
import panelAdmin from '@/views/admin-manager.vue'
import CompletarPerfil from '@/views/completar-perfil.vue'
import RegistrarAcudiente from '@/views/registrar-acudiente.vue'
import RegistrarDeportistaForm from '@/views/registrar-deportista-form.vue'

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
      path: '/ver-deportista/:id',
      name: 'ver-deportista',
      component: VerDeportista,
      meta: { requiresAuth: true }
    },
    {
      path: '/registrar-general',
      name: 'registrar-general',
      component: RegistrarGeneral,
      meta: { requiresGuest: true }
    },
    {
      path: '/ver-general',
      name: 'ver-general',
      component: VerGeneral,
      meta: { requiresAuth: true }
    },
    {
      path: '/actualizar-general',
      name: 'actualizar-general',
      component: ActualizarGeneral,
      meta: { requiresAuth: true }
    },
    {
      path: '/ver-roles',
      name: 'ver-roles',
      component: VerRoles,
      meta: { requiresAuth: true }
    },
    {
      path: '/mensualidades',
      name: 'mensualidades',
      component: TablaMensualidades,
      meta: { requiresAuth: true }
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
      path: '/calendario',
      name: 'calendario',
      component: Calendario,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin-manager',
      name: 'admin-manager',
      component: panelAdmin,
      meta: { requiresAuth: true, requiresRole: ['Administrador', 'Entrenador'] }
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
      path: '/registrar-deportista-form',
      name: 'registrar-deportista-form',
      component: RegistrarDeportistaForm,
      meta: { requiresAuth: true }
    },
    {
      path: '/ver-acudidos',
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
    }
  ],
})

// Función auxiliar para obtener la ruta de redirección según el rol
function getDefaultRouteForRole(userRoles) {
  if (!userRoles || userRoles.length === 0) {
    return '/home'
  }

  // Extraer nombres de roles
  const roleNames = userRoles.map(role =>
    typeof role === 'string' ? role : role.nombre_rol
  )

  // Priorizar roles en orden jerárquico
  if (roleNames.includes('SuperAdmin') || roleNames.includes('Administrador')) {
    return '/admin-manager'
  } else if (roleNames.includes('Entrenador')) {
    return '/home'
  } else if (roleNames.includes('Deportista')) {
    return '/home'
  } else if (roleNames.includes('Acudiente')) {
    return '/home'
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

// Guard de navegación global
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Inicializar el store si no está inicializado
  if (!authStore.user && authStore.token) {
    await authStore.inicializar()
  }

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)
  const requiresRole = to.matched.some(record => record.meta.requiresRole)

  // Verificar si el token es válido (no solo si existe)
  let isAuthenticated = false
  if (authStore.token) {
    isAuthenticated = await authStore.verifyToken()
  }

  if (requiresAuth && !isAuthenticated) {
    // Ruta requiere autenticación pero el usuario no está autenticado o token expirado
    console.log('🔒 Redirigiendo a login: usuario no autenticado')
    next('/login')
  } else if (requiresGuest && isAuthenticated) {
    // Ruta es para invitados pero el usuario ya está autenticado
    // Redirigir a la ruta por defecto según el rol
    const defaultRoute = getDefaultRouteForRole(authStore.user?.roles)
    console.log('🔄 Redirigiendo usuario autenticado:', defaultRoute)
    next(defaultRoute)
  } else if (requiresAuth && isAuthenticated && requiresRole) {
    // Verificar si el usuario tiene el rol requerido
    const requiredRoles = to.meta.requiresRole
    const userRoles = authStore.user?.roles || []

    if (!hasRequiredRole(userRoles, requiredRoles)) {
      console.log('🚫 Acceso denegado: rol insuficiente. Requerido:', requiredRoles, 'Usuario:', userRoles)
      // Redirigir al home si no tiene el rol requerido
      next('/home')
    } else {
      console.log('✅ Acceso autorizado para:', to.path)
      next()
    }
  } else {
    // Permitir navegación
    next()
  }
})

export default router
