import { createRouter, createWebHistory } from 'vue-router'
import Inicio from '../views/Inicio.vue'
import ActualizarDeportista from '../views/actualizar-deportista.vue'
import RegistrarDeportista from '../views/registrar-deportista.vue'
import VerDeportista from '../views/ver-deportista.vue'
import RegistrarGeneral from '../views/registrar-general.vue'
import VerGeneral from '../views/ver-general.vue'
import ActualizarGeneral from '../views/actualizar-general.vue'

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
    }
  ],
})

export default router
