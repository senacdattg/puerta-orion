import { createRouter, createWebHistory } from 'vue-router'
import Inicio from '../views/Inicio.vue'
import ActualizarDeportista from '../views/actualizar-deportista.vue'
import RegistrarDeportista from '../views/registrar-deportista.vue'
import VerDeportista from '../views/ver-deportista.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Inicio,
    },
    {
      path: '/actualizar',
      name: 'actualizar',
      component: ActualizarDeportista,
    },
    {
      path: '/registrar',
      name: 'registrar',
      component: RegistrarDeportista,
    },
    {
      path: '/ver',
      name: 'ver',
      component: VerDeportista,
    },
  ],
})

export default router
