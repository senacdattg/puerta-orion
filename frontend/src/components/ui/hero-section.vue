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
          <h2 class="welcome-title">¡Bienvenido, Usuario!</h2>
          <p class="welcome-description">
            Gestiona el club deportivo desde tu panel de administración
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
// Componente enfocado únicamente en mostrar la sección hero
// No tiene lógica de negocio, solo presentación
</script>

<style scoped>
.hero-section {
  background-color: #f8f9fa;
  padding: 40px 20px;
  min-height: 600px;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

.hero-branding {
  text-align: center;
}

.logo-container {
  margin-bottom: 20px;
}

.hero-logo {
  width: 120px;
  height: 120px;
  object-fit: contain;
}

.brand-text {
  margin-bottom: 30px;
}

.brand-title {
  font-size: 2rem;
  font-weight: 700;
  color: #333;
  margin: 0;
  letter-spacing: 1px;
}

.brand-buttons {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 25px;
}

.brand-button {
  padding: 15px 30px;
  border-radius: 25px;
  font-weight: 700;
  font-size: 1.1rem;
  letter-spacing: 0.5px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.brand-button--yellow {
  background-color: #f7d600;
  color: #0047ab;
}

.brand-button--blue {
  background-color: #0047ab;
  color: white;
}

.brand-tagline {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 20px;
  font-weight: 500;
}

.decorative-element {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.line {
  height: 2px;
  width: 40px;
}

.line--yellow {
  background-color: #f7d600;
}

.line--blue {
  background-color: #0047ab;
}

.dot {
  width: 8px;
  height: 8px;
  background-color: #f7d600;
  border-radius: 50%;
}

.welcome-section {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.welcome-content {
  margin-bottom: 20px;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #0047ab;
  margin: 0 0 15px 0;
}

.welcome-description {
  font-size: 1.1rem;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.stats-cards {
  display: flex;
  gap: 20px;
}

.stat-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  flex: 1;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

@media (max-width: 768px) {
  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 40px;
  }

  .stats-cards {
    justify-content: center;
  }

  .welcome-title {
    font-size: 2rem;
  }

  .brand-title {
    font-size: 1.5rem;
  }
}
</style>
