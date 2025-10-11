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
          <h4 class="footer-subtitle">Enlaces Rápidos</h4>
          <ul class="footer-links">
            <li><router-link to="/calendario">Calendario</router-link></li>
            <li><router-link to="/galeria">Galería</router-link></li>
            <li><router-link to="/deportistas">Deportistas</router-link></li>
            <li><router-link to="/admin-manager">Panel Admin</router-link></li>
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
import { APP_CONFIG, SOCIAL_LINKS } from '@/config/constants'

// Usar constantes del archivo de configuración
const appConfig = APP_CONFIG
const socialLinks = SOCIAL_LINKS
</script>

