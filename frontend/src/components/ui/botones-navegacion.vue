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
import { useUserRole } from '@/composables/useUserRole'

// Usar el composable para obtener la navegación filtrada
const { filteredNavigation: navigationItems } = useUserRole()
</script>

