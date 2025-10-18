<template>
  <section class="cta-section">
    <div class="container">
      <div class="cta-content">
        <h2 class="cta-title">¿Listo para comenzar tu viaje deportivo?</h2>
        <p class="cta-description">
          Únete a nuestra comunidad y descubre todo tu potencial atlético
        </p>
        <div class="cta-buttons">
          <router-link to="/registrar-general" class="cta-button cta-button--primary">
            <i class="fas fa-user-plus"></i>
            Registrarse
          </router-link>
          <router-link to="/login" class="cta-button cta-button--secondary">
            <i class="fas fa-sign-in-alt"></i>
            Iniciar Sesión
          </router-link>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import '@/assets/css/components/call-to-action.css'
</script>

