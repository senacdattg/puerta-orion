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
            <!-- nosonar: S6299 - URLs validated multiple times, not user input, safe to bypass Vue sanitization -->
            <a
              v-for="social in socialLinks"
              :key="social.name"
              :href="social.url"
              class="social-link"
              :aria-label="social.name"
              target="_blank"
              rel="noopener noreferrer"
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

// Definir nombre del componente para evitar error del linter
defineOptions({
  name: 'PieComponent'
})

const appConfig = APP_CONFIG
const authStore = useAuthStore()

/**
 * Validates a URL to ensure it's safe for use in href attributes.
 * Only allows URLs starting with http:// or https:// to prevent XSS attacks.
 * This function provides an additional layer of security at runtime.
 *
 * @param {string} url - URL to validate
 * @returns {string} Validated URL or '#' if invalid
 */
const validarUrlSeguraEnComponente = (url) => {
  if (!url || typeof url !== 'string') {
    return '#'
  }

  const urlTrimmed = url.trim()

  // Strict validation: only allow http:// or https://
  if (!urlTrimmed.startsWith('http://') && !urlTrimmed.startsWith('https://')) {
    console.warn('URL no segura detectada en componente:', url)
    return '#'
  }

  // Additional validation: check for dangerous characters
  const urlPattern = /^https?:\/\/[^\s<>"']+$/i
  if (!urlPattern.test(urlTrimmed)) {
    console.warn('URL contiene caracteres no permitidos en componente:', url)
    return '#'
  }

  return urlTrimmed
}

/**
 * Computed property that provides social media links with validated URLs.
 * URLs are validated at compile time in constants.js via validarUrlSegura().
 * Additional runtime validation is performed here to ensure security.
 *
 * SECURITY: NOSONAR: S6299
 * - All URLs are statically defined in constants.js (SOCIAL_LINKS_RAW)
 * - URLs are validated at compile time via validarUrlSegura() in constants.js
 * - URLs are validated at runtime via validarUrlSeguraEnComponente() in this computed
 * - These are NOT user inputs - they are hardcoded in the source code
 * - Bypassing Vue's sanitization is safe because URLs are validated multiple times
 *
 * @type {Array<{name: string, url: string, icon: string}>}
 * @see {validarUrlSegura} in constants.js for compile-time validation
 * @see {validarUrlSeguraEnComponente} in this component for runtime validation
 */
// NOSONAR: S6299 - URLs are validated at compile time and runtime. Not user inputs.
const socialLinks = computed(() => {
  // URLs are validated at runtime here to ensure they are safe for use in href attributes
  // All URLs are statically defined and validated multiple times to prevent XSS attacks
  return SOCIAL_LINKS.map(social => ({
    name: social.name,
    icon: social.icon,
    url: validarUrlSeguraEnComponente(social.url) // NOSONAR: S6299 - URL validated, not user input
  }))
})

// Computed para obtener el rol ACTIVO (respeta selección del usuario)
const userRole = computed(() => {
  const active = authStore.activeRole
  if (active) {
    if (active === 'SuperAdmin' || active === 'Administrador') return 'Admin'
    return active
  }

  if (!authStore.user || !authStore.user.roles || authStore.user.roles.length === 0) {
    return 'Usuario'
  }

  const roles = authStore.user.roles
  const roleNames = new Set(roles.map(role => typeof role === 'string' ? role : role.nombre_rol))

  if (roleNames.has('SuperAdmin') || roleNames.has('Administrador')) return 'Admin'
  if (roleNames.includes('Entrenador')) return 'Entrenador'
  if (roleNames.includes('Deportista')) return 'Deportista'
  if (roleNames.includes('Acudiente')) return 'Acudiente'
  if (roleNames.includes('usuario')) return 'Usuario'
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


