<template>
  <section class="club-info-section">
    <div class="container">
      <div class="info-content">
        <div class="info-text">
          <h2 class="info-title">Sobre Nuestro Club</h2>
          <p class="info-description">
            El Club Deportivo Puerta de Orión es una institución comprometida con el desarrollo 
            deportivo y personal de nuestros atletas. Con más de 25 años de experiencia, 
            hemos formado campeones no solo en el deporte, sino en la vida.
          </p>
          <div class="info-features">
            <div class="feature-item">
              <i class="fas fa-trophy feature-icon"></i>
              <span class="feature-text">Excelencia deportiva</span>
            </div>
            <div class="feature-item">
              <i class="fas fa-heart feature-icon"></i>
              <span class="feature-text">Valores humanos</span>
            </div>
            <div class="feature-item">
              <i class="fas fa-users feature-icon"></i>
              <span class="feature-text">Comunidad unida</span>
            </div>
          </div>
        </div>
        <div class="info-image">
          <div class="image-placeholder">
            <i class="fas fa-medal placeholder-icon"></i>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
// Componente enfocado únicamente en mostrar información del club
// No tiene lógica de negocio, solo presentación
</script>

<style scoped>
.club-info-section {
  padding: 80px 20px;
  background-color: white;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.info-content {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 60px;
  align-items: center;
}

.info-text {
  max-width: 600px;
}

.info-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #0047ab;
  margin: 0 0 25px 0;
}

.info-description {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #555;
  margin: 0 0 30px 0;
}

.info-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.feature-icon {
  font-size: 1.5rem;
  color: #f7d600;
  width: 30px;
  text-align: center;
}

.feature-text {
  font-size: 1.1rem;
  font-weight: 500;
  color: #333;
}

.info-image {
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-placeholder {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #f7d600 0%, #ffc107 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 30px rgba(247, 214, 0, 0.3);
}

.placeholder-icon {
  font-size: 6rem;
  color: #0047ab;
}

@media (max-width: 768px) {
  .info-content {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 40px;
  }
  
  .info-title {
    font-size: 2rem;
  }
  
  .image-placeholder {
    width: 250px;
    height: 250px;
  }
  
  .placeholder-icon {
    font-size: 4rem;
  }
}
</style>

