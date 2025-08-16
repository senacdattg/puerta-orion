import { createRouter, createWebHistory } from 'vue-router'
import Inicio from '../views/Inicio.vue'
import ActualizarDeportista from '../views/actualizar-deportista.vue'

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
  ],
})

export default router
