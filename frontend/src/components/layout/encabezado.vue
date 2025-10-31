<template>
  <header class="encabezado" >
    <i v-if="!sinMenu"
    class="fa-solid fa-bars menu-toggle"
    @click="toggleMenu"
    ></i>

    <img src="@/assets/imgs/logo.png" alt="Logo">

    <!-- Info del usuario autenticado con dropdown -->
    <div v-if="!sinMenu && authStore.estaAutenticado" class="usuario-info">
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

    <div class="menu-categorias" id="menu" v-show="menuVisible">
      <ul id="menu-opciones">
        <li v-for="(op, index) in opciones" :key="index">
          <router-link
            :to="op.link"
            @click="closeMenu"
            class="menu-link"
          >
            <i :class="op.icono + ' icono-menu'"></i> {{ op.texto }}
          </router-link>
        </li>

        <!-- Opción de cerrar sesión -->
        <li v-if="authStore.estaAutenticado">
          <a @click="handleLogout" class="menu-link">
            <i class="fas fa-sign-out-alt icono-menu"></i> Cerrar Sesión
          </a>
        </li>
      </ul>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Definir nombre del componente para evitar error del linter
defineOptions({
  name: 'EncabezadoComponent'
})

const router = useRouter()
const authStore = useAuthStore()

// Props
const props = defineProps({
  sinMenu: {
    type: Boolean,
    default: false
  }
})

// Estado
const menuVisible = ref(false)
const opciones = ref([])
const showProfileMenu = ref(false)
const profileMenuRef = ref(null)

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

// Métodos
function toggleMenu() {
  menuVisible.value = !menuVisible.value
}

function closeMenu() {
  menuVisible.value = false
}

function toggleProfileMenu() {
  showProfileMenu.value = !showProfileMenu.value
}

function handleOutsideClick(e) {
  const header = document.querySelector('.encabezado')
  if (header && !header.contains(e.target)) {
    menuVisible.value = false
  }

  // Cerrar el menú de perfil si se hace clic fuera
  if (profileMenuRef.value && !profileMenuRef.value.contains(e.target)) {
    showProfileMenu.value = false
  }
}

function verPerfil() {
  showProfileMenu.value = false
  router.push('/perfil')
}

function editarPerfil() {
  showProfileMenu.value = false
  router.push('/actualizar-info')
}

async function cerrarSesion() {
  showProfileMenu.value = false
  const confirmar = confirm('¿Estás seguro de que deseas cerrar sesión?')

  if (confirmar) {
    closeMenu()
    await authStore.logout()
    router.push('/login')
  }
}

async function handleLogout() {
  const confirmar = confirm('¿Estás seguro de que deseas cerrar sesión?')

  if (confirmar) {
    closeMenu()
    await authStore.logout()
    router.replace('/login')
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

// Ciclo de vida
onMounted(() => {
  if (!props.sinMenu) {
    cargarOpciones()
    document.addEventListener("click", handleOutsideClick)
  }
})

onBeforeUnmount(() => {
  document.removeEventListener("click", handleOutsideClick)
})
</script>

<style scoped>
.usuario-info {
  margin-left: auto;
  margin-right: 20px;
  display: flex;
  align-items: center;
}

.profile-menu-container {
  position: relative;
}

.profile-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  border-radius: 50%;
  transition: all 0.3s ease;
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
  border-radius: 50%;
  object-fit: cover;
}

.profile-placeholder {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #87CEEB; /* Sky blue - azul claro sólido */
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff; /* Icono blanco */
  font-size: 22px;
  border: none;
}

.profile-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  overflow: hidden;
  z-index: 1000;
}

.dropdown-item {
  width: 100%;
  padding: 12px 16px;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #333333;
  font-size: 14px;
  transition: all 0.2s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.dropdown-item:hover {
  background: #f5f5f5;
  color: #004AAD;
}

.dropdown-item i {
  width: 20px;
  text-align: center;
  color: #004AAD;
  font-size: 16px;
}

.dropdown-item.logout {
  color: #dc3545;
}

.dropdown-item.logout:hover {
  background: #fee;
  color: #c82333;
}

.dropdown-item.logout i {
  color: #dc3545;
}

.dropdown-divider {
  margin: 4px 0;
  border: none;
  border-top: 1px solid #e5e5e5;
}

/* Transiciones */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.menu-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  align-items: center;
  padding: 10px 15px;
  transition: background-color 0.3s ease;
}

.menu-link:hover {
  background-color: rgba(0, 123, 255, 0.1);
}

@media (max-width: 768px) {
  .usuario-info {
    display: none;
  }
}
</style>

