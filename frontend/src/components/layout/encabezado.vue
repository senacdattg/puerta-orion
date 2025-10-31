<template>
  <header class="header-deportista">
    <div class="header-left">
      <img
        src="@/assets/imgs/logo.png"
        alt="Logo"
        class="header-logo"
      />
    </div>

    <div class="header-center">
      <h2 class="welcome-message">
        Bienvenido, {{ nombreUsuario }} 👋
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

    <!-- Menú lateral (estático como en DeportistaDashboard) -->
    <aside
      class="sidebar-deportista open"
      v-show="!sinMenu"
    >
      <div class="sidebar-header">
        <button
          class="sidebar-toggle"
          @click="closeMenu"
          v-if="isMobile"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="op in opciones"
          :key="op.link"
          :to="op.link"
          class="nav-item"
          :class="{ active: isActiveRoute(op.link) }"
          @click="closeMenu"
        >
          <i :class="op.icono"></i>
          <span class="nav-text">{{ op.texto }}</span>
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
  </header>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Definir nombre del componente para evitar error del linter
defineOptions({
  name: 'EncabezadoComponent'
})

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Props
const props = defineProps({
  sinMenu: {
    type: Boolean,
    default: false
  }
})

// Estado
const showProfileMenu = ref(false)
const profileMenuRef = ref(null)
const menuVisible = ref(false)
const opciones = ref([])
const isMobile = ref(false)
const hoverTimeout = ref(null)
const menuOpenedByClick = ref(false) // Track si se abrió por click

// Computed para obtener el rol ACTIVO (respeta selección del usuario)
const userRole = computed(() => {
  const active = authStore.activeRole
  if (active) {
    if (active === 'SuperAdmin' || active === 'Administrador') return 'Admin'
    return active
  }

  if (!authStore.user || !authStore.user.roles || authStore.user.roles.length === 0) {
    return 'Usuario'
  }

  const roles = authStore.user.roles
  const roleNames = roles.map(role => typeof role === 'string' ? role : role.nombre_rol)

  if (roleNames.includes('SuperAdmin') || roleNames.includes('Administrador')) return 'Admin'
  if (roleNames.includes('Entrenador')) return 'Entrenador'
  if (roleNames.includes('Deportista')) return 'Deportista'
  if (roleNames.includes('Acudiente')) return 'Acudiente'
  if (roleNames.includes('usuario')) return 'Usuario'
  return 'Usuario'
})

// Computed para obtener la foto de perfil
const fotoPerfil = computed(() => {
  return authStore.user?.persona?.foto || null
})

// Computed para obtener el nombre del usuario
const nombreUsuario = computed(() => {
  if (authStore.user && authStore.user.persona) {
    return authStore.user.persona.nombre_completo ||
           authStore.user.persona.primer_nombre ||
           authStore.user.username ||
           'Usuario'
  }
  return authStore.user?.username || 'Usuario'
})

// Métodos
function toggleProfileMenu() {
  showProfileMenu.value = !showProfileMenu.value
}

function toggleMenu() {
  menuOpenedByClick.value = !menuVisible.value // Si se abre por click, marcar como tal
  menuVisible.value = !menuVisible.value
}

function closeMenu() {
  menuOpenedByClick.value = false
  menuVisible.value = false
}

function showMenuOnHover() {
  // Mostrar inmediatamente al pasar el mouse sobre el logo o el sidebar en desktop
  if (!isMobile.value) {
    menuVisible.value = true
  }
}

function hideMenuOnHover() {
  // No cerrar por hover; se cierra con clic fuera o botón cerrar en móvil
}

function isActiveRoute(path) {
  const currentPath = route.path
  return currentPath === path || currentPath.startsWith(path + '/')
}

async function handleLogout() {
  const confirmar = confirm('¿Estás seguro de que deseas cerrar sesión?')
  if (confirmar) {
    closeMenu()
    await authStore.logout()
    router.replace('/login')
  }
}

function handleOutsideClick(e) {
  const header = document.querySelector('.header-deportista')
  const sidebar = document.querySelector('.sidebar-deportista')

  // Cerrar menú si se hace clic fuera del header y sidebar
  if (header && sidebar) {
    if (!header.contains(e.target) && !sidebar.contains(e.target)) {
      menuVisible.value = false
    }
  }

  // Cerrar el menú de perfil si se hace clic fuera
  if (profileMenuRef.value && !profileMenuRef.value.contains(e.target)) {
    showProfileMenu.value = false
  }
}

function cargarOpciones() {
  const opcionesPorRol = {
    Usuario: [
      { texto: "Inicio", link: "/home", icono: "fas fa-home" },
      { texto: "Perfil", link: "/ver-general", icono: "fas fa-user" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
    ],
    Entrenador: [
      { texto: "Inicio", link: "/home", icono: "fas fa-home" },
      { texto: "Perfil", link: "/ver-general", icono: "fas fa-user" },
      { texto: "Deportistas", link: "/deportistas", icono: "fas fa-users" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
    ],
    Acudiente: [
      { texto: "Inicio", link: "/home", icono: "fas fa-home" },
      { texto: "Perfil", link: "/ver-general", icono: "fas fa-user" },
      { texto: "Mis Deportistas", link: "/ver-acudidos", icono: "fas fa-child" },
      { texto: "Mensualidades", link: "/mensualidades", icono: "fas fa-wallet" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
    ],
    Deportista: [
      { texto: "Inicio", link: "/home", icono: "fas fa-home" },
      { texto: "Perfil", link: "/perfil", icono: "fas fa-user" },
      { texto: "Mensualidades", link: "/mensualidades", icono: "fas fa-wallet" },
      { texto: "Eventos", link: "/eventos", icono: "fas fa-calendar-check" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
    ],
    Admin: [
      { texto: "Inicio", link: "/admin-manager", icono: "fas fa-home" },
      { texto: "Perfil", link: "/ver-general", icono: "fas fa-user" },
      { texto: "Deportistas", link: "/deportistas", icono: "fas fa-users" },
      { texto: "Mensualidades", link: "/mensualidades", icono: "fas fa-wallet" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
      { texto: "Panel Admin", link: "/admin-manager", icono: "fas fa-cog" },
    ],
    UsuarioSinAuth: [
      { texto: "Inicio", link: "/home", icono: "fas fa-home" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
    ]
  }

  const rolActual = userRole.value
  opciones.value = opcionesPorRol[rolActual] || opcionesPorRol['UsuarioSinAuth']
}

function checkMobile() {
  isMobile.value = window.innerWidth < 768
}

// Watcher para recargar opciones cuando cambie el rol del usuario
watch(userRole, (newRole, oldRole) => {
  if (newRole !== oldRole) {
    cargarOpciones()
  }
})

// Watcher para recargar opciones cuando cambie el estado de autenticación
watch(() => authStore.user, (newUser, oldUser) => {
  if (newUser !== oldUser) {
    cargarOpciones()
  }
}, { deep: true })

function verPerfil() {
  showProfileMenu.value = false
  // Deportista usa /perfil, otros roles usan /ver-general
  const rol = userRole.value
  if (rol === 'Deportista') {
    router.push('/perfil')
  } else {
    router.push('/ver-general')
  }
}

function editarPerfil() {
  showProfileMenu.value = false
  router.push('/actualizar-info')
}

async function cerrarSesion() {
  showProfileMenu.value = false
  const confirmar = confirm('¿Estás seguro de que deseas cerrar sesión?')

  if (confirmar) {
    await authStore.logout()
    router.replace('/login')
  }
}

// Ciclo de vida
onMounted(() => {
  if (!props.sinMenu) {
    checkMobile()
    cargarOpciones()
    document.addEventListener("click", handleOutsideClick)
    window.addEventListener("resize", checkMobile)
  } else {
    document.addEventListener("click", handleOutsideClick)
  }
})

onBeforeUnmount(() => {
  document.removeEventListener("click", handleOutsideClick)
  if (hoverTimeout.value) {
    clearTimeout(hoverTimeout.value)
  }
  if (!props.sinMenu) {
    window.removeEventListener("resize", checkMobile)
  }
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
  cursor: pointer;
  transition: transform var(--transicion);
}

.header-logo:hover {
  transform: scale(1.05);
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


/* Estilos del menú lateral (estilo SidebarDeportista) */
.sidebar-deportista {
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
  transform: translateX(-100%);
}

.sidebar-deportista.open {
  transform: translateX(0);
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

.nav-item.logout-nav {
  color: rgba(255, 255, 255, 0.9);
  margin-top: auto;
}

.nav-item.logout-nav:hover {
  background: rgba(220, 53, 69, 0.2);
  color: #ff6b7a;
  border-left-color: rgba(220, 53, 69, 0.6);
}

.nav-item i {
  width: 20px;
  text-align: center;
  font-size: var(--tamano-fuente-lg);
}

.nav-text {
  flex: 1;
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

  .sidebar-deportista {
    transform: translateX(-100%);
    box-shadow: none;
  }

  .sidebar-deportista.open {
    transform: translateX(0);
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.3);
  }
}
</style>
