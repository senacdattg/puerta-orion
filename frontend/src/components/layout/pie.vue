<template>
  <footer class="footer-enhanced">
    <div class="container">
      <div class="footer-content">
        <div class="footer-section">
          <h3 class="footer-title">{{ appConfig.fullName }}</h3>
          <p class="footer-description">
            {{ appConfig.description }} desde {{ appConfig.founded }}
          </p>
          <div class="social-links">
            <a
              v-for="social in socialLinks"
              :key="social.name"
              :href="social.url"
              class="social-link"
              :aria-label="social.name"
            >
              <i :class="social.icon"></i>
            </a>
          </div>
        </div>

        <div class="footer-section">
          <h4 class="footer-subtitle">Acciones Rápidas</h4>
          <ul class="footer-links">
            <li v-for="accion in accionesRapidas" :key="accion.texto">
              <router-link :to="accion.link">
                <i :class="accion.icono"></i>
                {{ accion.texto }}
              </router-link>
            </li>
          </ul>
        </div>

        <div class="footer-section">
          <h4 class="footer-subtitle">Contacto</h4>
          <div class="contact-info">
            <p><i class="fas fa-map-marker-alt"></i> {{ appConfig.contact.address }}</p>
            <p><i class="fas fa-phone"></i> {{ appConfig.contact.phone }}</p>
            <p><i class="fas fa-envelope"></i> {{ appConfig.contact.email }}</p>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <p>&copy; 2024 {{ appConfig.fullName }}. Todos los derechos reservados.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { APP_CONFIG, SOCIAL_LINKS } from '@/config/constants'

// Usar constantes del archivo de configuración
const appConfig = APP_CONFIG
const socialLinks = SOCIAL_LINKS
const authStore = useAuthStore()

// Computed para obtener el rol del usuario desde la sesión
const userRole = computed(() => {
  if (!authStore.user || !authStore.user.roles || authStore.user.roles.length === 0) {
    return 'Usuario'
  }

  // Obtener el primer rol del usuario (o el más relevante)
  const roles = authStore.user.roles
  const roleNames = roles.map(role =>
    typeof role === 'string' ? role : role.nombre_rol
  )

  // Priorizar roles en orden de importancia
  if (roleNames.includes('SuperAdmin') || roleNames.includes('Administrador')) {
    return 'Admin'
  } else if (roleNames.includes('Entrenador')) {
    return 'Entrenador'
  } else if (roleNames.includes('Deportista')) {
    return 'Deportista'
  } else if (roleNames.includes('Acudiente')) {
    return 'Acudiente'
  } else if (roleNames.includes('usuario')) {
    return 'Usuario'
  }

  return 'UsuarioSinAuth'
})

// Computed para obtener las acciones rápidas según el rol
const accionesRapidas = computed(() => {
  const accionesPorRol = {
    Usuario: [
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
      { texto: "Mi Perfil", link: "/ver-general", icono: "fas fa-user" },
    ],
    Entrenador: [
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Deportistas", link: "/deportistas", icono: "fas fa-users" },
      { texto: "Mi Perfil", link: "/ver-general", icono: "fas fa-user" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
    ],
    Acudiente: [
      { texto: "Mis Deportistas", link: "/ver-acudidos", icono: "fas fa-child" },
      { texto: "Mensualidades", link: "/mensualidades", icono: "fas fa-wallet" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Mi Perfil", link: "/ver-general", icono: "fas fa-user" },
    ],
    Deportista: [
      { texto: "Mi Perfil", link: "/perfil", icono: "fas fa-user" },
      { texto: "Mensualidades", link: "/mensualidades", icono: "fas fa-wallet" },
      { texto: "Eventos", link: "/eventos", icono: "fas fa-calendar-check" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
    ],
    Admin: [
      { texto: "Panel Admin", link: "/admin-manager", icono: "fas fa-cog" },
      { texto: "Deportistas", link: "/deportistas", icono: "fas fa-users" },
      { texto: "Mensualidades", link: "/mensualidades", icono: "fas fa-wallet" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
    ],
    UsuarioSinAuth: [
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
    ]
  }

  const rolActual = userRole.value
  return accionesPorRol[rolActual] || accionesPorRol['UsuarioSinAuth']
})
</script>

<style scoped>
.footer-links a {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.footer-links a i {
  width: 1rem;
  text-align: center;
}
</style>

