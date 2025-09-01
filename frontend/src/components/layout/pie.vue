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

<style scoped>
.footer-enhanced {
  background-color: var(--primary-color);
  color: white;
  padding: 60px 20px 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  margin-bottom: 40px;
}

.footer-section {
  display: flex;
  flex-direction: column;
}

.footer-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 15px 0;
  color: var(--secondary-color);
}

.footer-description {
  font-size: 1rem;
  line-height: 1.6;
  margin: 0 0 20px 0;
  opacity: 0.9;
}

.social-links {
  display: flex;
  gap: 15px;
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background-color: var(--secondary-color);
  color: var(--primary-color);
  border-radius: 50%;
  text-decoration: none;
  transition: var(--transition);
  font-size: 1.2rem;
}

.social-link:hover {
  background-color: white;
  transform: translateY(-2px);
}

.footer-subtitle {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 20px 0;
  color: var(--secondary-color);
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 10px;
}

.footer-links a {
  color: white;
  text-decoration: none;
  opacity: 0.9;
  transition: var(--transition);
}

.footer-links a:hover {
  opacity: 1;
  color: var(--secondary-color);
}

.contact-info p {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 10px 0;
  opacity: 0.9;
}

.contact-info i {
  color: var(--secondary-color);
  width: 20px;
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding-top: 20px;
  text-align: center;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .social-links {
    justify-content: center;
  }

  .contact-info p {
    justify-content: center;
  }
}
</style>
