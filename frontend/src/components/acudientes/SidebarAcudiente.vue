<template>
  <aside class="sidebar-acudiente" :class="{ open: isOpen }">
    <div class="sidebar-header">
      <button
        class="sidebar-toggle"
        @click="toggleSidebar"
        v-if="isMobile"
      >
        <i class="fas fa-times"></i>
      </button>
    </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
          @click="handleNavClick"
        >
          <i :class="item.icon"></i>
          <span class="nav-text">{{ item.label }}</span>
        </router-link>
        
        <!-- Opción de cerrar sesión -->
        <a
          v-if="authStore.estaAutenticado"
          @click="handleLogout"
          class="nav-item logout-nav"
        >
          <i class="fas fa-sign-out-alt"></i>
          <span class="nav-text">Cerrar Sesión</span>
        </a>
      </nav>
  </aside>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

defineOptions({
  name: 'SidebarAcudiente'
})

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isMobile = ref(false)

const menuItems = [
  {
    path: '/acudiente/dashboard',
    label: 'Inicio',
    icon: 'fas fa-home'
  },
  {
    path: '/ver-acudidos',
    label: 'Mis Acudidos',
    icon: 'fas fa-users'
  },
  {
    path: '/mensualidades',
    label: 'Mensualidades',
    icon: 'fas fa-money-bill-wave'
  },
  {
    path: '/eventos',
    label: 'Eventos',
    icon: 'fas fa-calendar-check'
  },
  {
    path: '/calendario',
    label: 'Calendario',
    icon: 'fas fa-calendar-alt'
  },
  {
    path: '/galeria',
    label: 'Galería',
    icon: 'fas fa-images'
  },
  {
    path: '/perfil',
    label: 'Configuración',
    icon: 'fas fa-cog'
  }
]

async function handleLogout() {
  const confirmar = confirm('¿Estás seguro de que deseas cerrar sesión?')
  if (confirmar) {
    await authStore.logout()
    router.replace('/login')
  }
}

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const handleNavClick = () => {
  if (isMobile.value && props.isOpen) {
    emit('close')
  }
}

const toggleSidebar = () => {
  emit('close')
}

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.sidebar-acudiente {
  background: linear-gradient(180deg, #004AAD 0%, #003d8f 100%);
  width: 250px;
  height: calc(100vh - 70px);
  position: fixed;
  left: 0;
  top: 70px;
  z-index: var(--z-fixed);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.2);
  transition: transform var(--transicion);
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.sidebar-header {
  padding: var(--espaciado-md);
  display: flex;
  justify-content: flex-end;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.sidebar-toggle {
  background: none;
  border: none;
  color: var(--color-blanco);
  font-size: var(--tamano-fuente-lg);
  cursor: pointer;
  padding: var(--espaciado-xs);
  transition: var(--transicion);
}

.sidebar-toggle:hover {
  color: #FFD600;
  transform: rotate(90deg);
}

.sidebar-nav {
  flex: 1;
  padding: var(--espaciado-sm) 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: var(--espaciado-md) var(--espaciado-lg);
  color: rgba(255, 255, 255, 0.95);
  text-decoration: none;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  border-left: 4px solid transparent;
  font-family: 'Poppins', sans-serif;
  font-size: var(--tamano-fuente-base);
  gap: var(--espaciado-md);
  cursor: pointer;
  margin: 2px var(--espaciado-xs);
  border-radius: 0 var(--radio-borde-pequeno) var(--radio-borde-pequeno) 0;
  white-space: nowrap;
  position: relative;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.15);
  color: var(--color-blanco);
  border-left-color: rgba(255, 214, 0, 0.6);
  transform: translateX(4px);
}

.nav-item.active {
  background: linear-gradient(90deg, rgba(255, 214, 0, 0.25) 0%, rgba(255, 214, 0, 0.1) 100%);
  color: #FFD600;
  border-left-color: #FFD600;
  font-weight: var(--peso-fuente-semibold);
  box-shadow: 0 2px 8px rgba(255, 214, 0, 0.2);
}

.nav-item i {
  width: 20px;
  text-align: center;
  font-size: var(--tamano-fuente-lg);
}

.nav-text {
  flex: 1;
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar-acudiente {
    transform: translateX(-100%);
    box-shadow: none;
  }

  .sidebar-acudiente.open {
    transform: translateX(0);
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.3);
  }
}

/* Scrollbar personalizado */
.sidebar-nav::-webkit-scrollbar {
  width: 6px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>

