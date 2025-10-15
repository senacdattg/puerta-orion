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
  },
  {
    id: 'mensualidades',
    title: 'Mensualidades',
    route: '/mensualidades',
    icon: 'fas fa-money-bill-wave',
    colorClass: 'nav-card--purple'
  }
]
</script>

