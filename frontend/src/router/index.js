import { createRouter, createWebHistory } from 'vue-router'
import Inicio from '../views/Inicio.vue'
import ActualizarDeportista from '../views/actualizar-deportista.vue'
import RegistrarDeportista from '../views/registrar-deportista.vue'
import VerDeportista from '../views/ver-deportista.vue'
import RegistrarGeneral from '../views/registrar-general.vue'
import VerGeneral from '../views/ver-general.vue'
import ActualizarGeneral from '../views/actualizar-general.vue'
import VerRoles from '../views/vista-roles.vue'
import TablaMensualidades from '../views/mensualidades.vue'
import TablaDeportistas from '../views/deportistas.vue'
import Galeria from '../views/galeria-vista.vue'
import RolesRegistroVista from '@/views/roles-registro-vista.vue'
import Login from '../views/login.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Inicio,
    },
    {
      path: '/actualizar-deportista',
      name: 'actualizar-deportista',
      component: ActualizarDeportista,
    },
    {
      path: '/registrar-deportista',
      name: 'registrar-deportista',
      component: RegistrarDeportista,
    },
    {
      path: '/ver-deportista',
      name: 'ver-deportista',
      component: VerDeportista,
    },
    {
      path: '/registrar-general',
      name: 'registrar-general',
      component: RegistrarGeneral,
    },
    {
      path: '/ver-general',
      name: 'ver-general',
      component: VerGeneral,
    },
    {
      path: '/actualizar-general',
      name: 'actualizar-general',
      component: ActualizarGeneral,
    },
    {
      path: '/ver-roles',
      name: 'ver-roles',
      component: VerRoles,
    },
    {
      path: '/mensualidades',
      name: 'mensualidades',
      component: TablaMensualidades
    },
    {
      path: '/deportistas',
      name: 'deportistas',
      component: TablaDeportistas
    },
    {
      path: '/galeria',
      name: 'galeria',
      component: Galeria
    },
    {
      path: '/roles-registro',
      name: 'roles-registro',
      component: RolesRegistroVista
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    }
  ],
})

export default router
