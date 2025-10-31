<template>
  <header class="header-deportista">
    <div class="header-left">
      <img src="@/assets/imgs/logo.png" alt="Logo" class="header-logo" />
    </div>

    <div class="header-center">
      <h2 class="welcome-message">
        Bienvenido, {{ nombreDeportista }} 👋
      </h2>
    </div>

    <div class="header-right">
      <div class="profile-menu-container" ref="profileMenuRef">
        <button
          class="profile-button"
          @click="toggleProfileMenu"
          :class="{ active: showProfileMenu }"
        >
          <img
            v-if="fotoPerfil"
            :src="fotoPerfil"
            alt="Foto de perfil"
            class="profile-image"
          />
          <div v-else class="profile-placeholder">
            <i class="fas fa-user"></i>
          </div>
        </button>

        <transition name="fade">
          <div v-if="showProfileMenu" class="profile-dropdown">
            <button @click="verPerfil" class="dropdown-item">
              <i class="fas fa-user"></i>
              Ver perfil
            </button>
            <button @click="editarPerfil" class="dropdown-item">
              <i class="fas fa-edit"></i>
              Editar información
            </button>
            <hr class="dropdown-divider" />
            <button @click="cerrarSesion" class="dropdown-item logout">
              <i class="fas fa-sign-out-alt"></i>
              Cerrar sesión
            </button>
          </div>
        </transition>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

defineOptions({
  name: 'HeaderDeportista'
})

const router = useRouter()
const authStore = useAuthStore()
const showProfileMenu = ref(false)
const profileMenuRef = ref(null)

const nombreDeportista = computed(() => {
  if (authStore.user?.persona) {
    return authStore.user.persona.nombre_completo ||
           authStore.user.persona.primer_nombre ||
           authStore.user.username ||
           'Deportista'
  }
  return authStore.user?.username || 'Deportista'
})

const fotoPerfil = computed(() => {
  return authStore.user?.persona?.foto || null
})

const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value
}

const verPerfil = () => {
  showProfileMenu.value = false
  router.push('/perfil')
}

const editarPerfil = () => {
  showProfileMenu.value = false
  router.push('/actualizar-info')
}

const cerrarSesion = async () => {
  showProfileMenu.value = false
  const confirmar = confirm('¿Estás seguro de que deseas cerrar sesión?')

  if (confirmar) {
    await authStore.logout()
    router.push('/login')
  }
}

const handleClickOutside = (event) => {
  if (profileMenuRef.value && !profileMenuRef.value.contains(event.target)) {
    showProfileMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.header-deportista {
  background: linear-gradient(135deg, #004AAD 0%, #003d8f 100%);
  padding: var(--espaciado-md) var(--espaciado-xl);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: calc(var(--z-fixed) + 10);
  height: 70px;
  min-height: 70px;
}

.header-left {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--espaciado-md);
  flex: 0 0 auto;
  padding-top: var(--espaciado-xs);
}

.header-logo {
  height: 45px;
  width: auto;
  object-fit: contain;
}

.header-title {
  color: var(--color-blanco);
  font-size: var(--tamano-fuente-xl);
  font-weight: var(--peso-fuente-bold);
  font-family: 'Poppins', sans-serif;
}

.header-center {
  flex: 1;
  text-align: center;
  margin: 0 var(--espaciado-lg);
}

.welcome-message {
  color: var(--color-blanco);
  font-size: var(--tamano-fuente-lg);
  font-weight: var(--peso-fuente-semibold);
  font-family: 'Poppins', sans-serif;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--espaciado-md);
  flex: 0 0 auto;
}

.profile-menu-container {
  position: relative;
}

.profile-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  border-radius: var(--radio-borde-circular);
  transition: var(--transicion);
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #FFD600;
  background: transparent;
  position: relative;
}

.profile-button:hover,
.profile-button.active {
  border-color: #FFD600;
  transform: scale(1.05);
  background: transparent;
}

.profile-image {
  width: 100%;
  height: 100%;
  border-radius: var(--radio-borde-circular);
  object-fit: cover;
}

.profile-placeholder {
  width: 100%;
  height: 100%;
  border-radius: var(--radio-borde-circular);
  background: #87CEEB; /* Sky blue - azul claro sólido */
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff; /* Icono blanco */
  font-size: 22px;
}

.profile-dropdown {
  position: absolute;
  top: calc(100% + var(--espaciado-sm));
  right: 0;
  background: var(--color-blanco);
  border-radius: var(--radio-borde);
  box-shadow: var(--sombra-media);
  min-width: 200px;
  overflow: hidden;
  z-index: var(--z-dropdown);
}

.dropdown-item {
  width: 100%;
  padding: var(--espaciado-md);
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--espaciado-sm);
  color: var(--color-gris-oscuro);
  font-size: var(--tamano-fuente-base);
  transition: var(--transicion);
  font-family: 'Poppins', sans-serif;
}

.dropdown-item:hover {
  background: var(--color-gris-claro);
  color: #004AAD;
}

.dropdown-item i {
  width: 20px;
  text-align: center;
  color: #004AAD;
}

.dropdown-item.logout {
  color: var(--color-peligro);
}

.dropdown-item.logout:hover {
  background: #fee;
  color: var(--color-peligro-hover);
}

.dropdown-item.logout i {
  color: var(--color-peligro);
}

.dropdown-divider {
  margin: var(--espaciado-xs) 0;
  border: none;
  border-top: 1px solid var(--color-gris-medio);
}

/* Transiciones */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transicion), transform var(--transicion);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive */
@media (max-width: 768px) {
  .header-deportista {
    padding: var(--espaciado-sm) var(--espaciado-md);
    flex-wrap: wrap;
  }


  .header-title {
    display: none;
  }

  .header-center {
    order: 3;
    flex: 1 1 100%;
    margin: var(--espaciado-sm) 0 0 0;
  }

  .welcome-message {
    font-size: var(--tamano-fuente-base);
  }

  .header-left {
    flex: 1;
  }

  .header-right {
    flex: 0 0 auto;
  }
}
</style>

