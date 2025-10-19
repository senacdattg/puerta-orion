<template>
  <section class="hero-section">
    <div class="hero-content">
      <div class="hero-branding">
        <div class="logo-container">
          <img src="@/assets/imgs/logo.png" alt="Logo ORION" class="hero-logo">
        </div>
        <div class="brand-text">
          <h1 class="brand-title">ESCUELA DE VOLEIBOL</h1>
        </div>
        <div class="brand-buttons">
          <div class="brand-button brand-button--yellow">
            CLUB DEPORTIVO
          </div>
          <div class="brand-button brand-button--blue">
            PUERTA DE ORIÓN
          </div>
        </div>
        <div class="brand-tagline">
          Excelencia • Pasión • Deporte
        </div>
        <div class="decorative-element">
          <div class="line line--yellow"></div>
          <div class="dot"></div>
          <div class="line line--blue"></div>
        </div>
      </div>

      <div class="welcome-section">
        <div class="welcome-content">
          <h2 class="welcome-title">{{ welcomeMessage.title }}</h2>
          <p class="welcome-description">
            {{ welcomeMessage.description }}
          </p>
        </div>

        <div class="stats-cards">
          <div class="stat-card">
            <span class="stat-number">12</span>
            <span class="stat-label">Actividades</span>
          </div>
          <div class="stat-card">
            <span class="stat-number">3</span>
            <span class="stat-label">Próximos Eventos</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useUserRole } from '@/composables/useUserRole'

// Usar el composable para obtener el mensaje de bienvenida personalizado
const { welcomeMessage } = useUserRole()
</script>
