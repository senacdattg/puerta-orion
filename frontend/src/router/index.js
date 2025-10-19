import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Inicio from '../views/Inicio.vue'
import ActualizarDeportista from '../views/actualizar-deportista.vue'
import RegistrarDeportista from '../views/registrar-deportista.vue'
import VerDeportista from '../views/ver-deportista.vue'
import RegistrarGeneral from '../views/registrar-general.vue'
import VerGeneral from '../views/ver-general.vue'
import ActualizarGeneral from '../views/actualizar-general.vue'
import VerRoles from '../views/vista-roles.vue'
import TablaMensualidades from '../views/mensualidades.vue'
import TablaDeportistas from '../views/vista-deportistas.vue'
import Galeria from '../views/galeria-vista.vue'
import RolesRegistroVista from '@/views/roles-registro-vista.vue'
import Calendario from '../views/calendario.vue'
import Login from '../views/login.vue'
import panelAdmin from '../views/admin-manager.vue'

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
      meta: { requiresAuth: true }
    }
  ],
})

// Guard de navegación global
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Inicializar el store si no está inicializado
  if (!authStore.usuario && authStore.token) {
    await authStore.inicializar()
  }

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)

  // Verificar si el token es válido (no solo si existe)
  let isAuthenticated = false
  if (authStore.token) {
    isAuthenticated = await authStore.verifyToken()
  }

  if (requiresAuth && !isAuthenticated) {
    // Ruta requiere autenticación pero el usuario no está autenticado o token expirado
    next('/login')
  } else if (requiresGuest && isAuthenticated) {
    // Ruta es para invitados pero el usuario ya está autenticado
    next('/home')
  } else {
    // Permitir navegación
    next()
  }
})

export default router
