<template>
  <section class="quick-nav-section">
    <div class="container">
      <h2 class="section-title">Acciones Rápidas</h2>
      <div class="nav-grid">
        <router-link
          v-for="item in navigationItems"
          :key="item.id"
          :to="item.route"
          class="nav-card"
          :class="item.colorClass"
        >
          <div class="nav-icon">
            <i :class="item.icon"></i>
          </div>
          <h3 class="nav-title">{{ item.title }}</h3>
        </router-link>
      </div>
    </div>
  </section>
</template>

<script setup>
// Datos de navegación específicos para la imagen
const navigationItems = [
  {
    id: 'calendario',
    title: 'Ver Calendario',
    route: '/calendario',
    icon: 'fas fa-calendar-alt',
    colorClass: 'nav-card--blue'
  },
  {
    id: 'galeria',
    title: 'Galería',
    route: '/galeria',
    icon: 'fas fa-images',
    colorClass: 'nav-card--gray'
  },
  {
    id: 'admin',
    title: 'Panel Admin',
    route: '/admin-manager',
    icon: 'fas fa-cog',
    colorClass: 'nav-card--red'
  },
  {
    id: 'deportistas',
    title: 'Deportistas',
    route: '/deportistas',
    icon: 'fas fa-users',
    colorClass: 'nav-card--green'
  }
]
</script>

<style scoped>
.quick-nav-section {
  padding: 60px 20px;
  background-color: white;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 40px;
}

.nav-grid {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.nav-card {
  background: white;
  border-radius: 12px;
  padding: 25px 30px;
  text-decoration: none;
  color: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: none;
  position: relative;
  overflow: hidden;
  min-width: 200px;
  text-align: center;
}

.nav-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.nav-card--blue {
  background-color: #0047ab;
}

.nav-card--gray {
  background-color: #6c757d;
}

.nav-card--red {
  background-color: #dc3545;
}

.nav-card--green {
  background-color: #28a745;
}

.nav-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
  text-align: center;
}

.nav-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

@media (max-width: 768px) {
  .nav-grid {
    flex-direction: column;
    align-items: center;
  }

  .nav-card {
    width: 100%;
    max-width: 300px;
  }

  .section-title {
    font-size: 1.5rem;
  }
}
</style>
