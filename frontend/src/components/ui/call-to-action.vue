<template>
  <section class="cta-section">
    <div class="container">
      <div class="cta-content">
        <h2 class="cta-title">¿Listo para comenzar tu viaje deportivo?</h2>
        <p class="cta-description">
          Únete a nuestra comunidad y descubre todo tu potencial atlético
        </p>
        <div class="cta-buttons">
          <router-link to="/roles-registro" class="cta-button cta-button--primary">
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
// Componente enfocado únicamente en mostrar el call-to-action
// No tiene lógica de negocio, solo presentación
</script>

<style scoped>
.cta-section {
  padding: 80px 20px;
  background: linear-gradient(135deg, #0047ab 0%, #0d47a1 100%);
  color: white;
  text-align: center;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

.cta-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 20px 0;
  line-height: 1.2;
}

.cta-description {
  font-size: 1.2rem;
  line-height: 1.6;
  margin: 0 0 40px 0;
  opacity: 0.9;
}

.cta-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  border-radius: 50px;
  text-decoration: none;
  font-size: 1.1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 3px solid transparent;
}

.cta-button--primary {
  background-color: #f7d600;
  color: #0047ab;
  border-color: #f7d600;
}

.cta-button--primary:hover {
  background-color: #ffc107;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(247, 214, 0, 0.4);
}

.cta-button--secondary {
  background-color: transparent;
  color: white;
  border-color: white;
}

.cta-button--secondary:hover {
  background-color: white;
  color: #0047ab;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 255, 255, 0.3);
}

@media (max-width: 768px) {
  .cta-title {
    font-size: 2rem;
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .cta-button {
    width: 100%;
    max-width: 300px;
    justify-content: center;
  }
}
</style>

