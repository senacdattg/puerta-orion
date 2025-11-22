<template>
  <header class="header-deportista">
    <div class="header-inner container">
    <div class="header-left">
      <button
        v-if="!sinMenu"
        class="menu-trigger"
        @click="toggleMenu"
        :class="{ open: menuVisible }"
        :aria-expanded="menuVisible.toString()"
        aria-label="Alternar menú"
      >
        <i class="fas" :class="menuVisible ? 'fa-bars-staggered' : 'fa-bars'"></i>
      </button>
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
            <hr class="dropdown-divider" />
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
      class="sidebar-deportista"
      :class="{ open: menuVisible }"
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
          @click="handleMenuLinkClick"
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
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, onUpdated, computed, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Swal from 'sweetalert2'

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

// Computed para obtener el rol del usuario desde la sesión
const userRole = computed(() => {
  if (!authStore.user || !authStore.user.roles || authStore.user.roles.length === 0) {
    return 'Usuario'
  }

  // Obtener el primer rol del usuario (o el más relevante)
  const roles = authStore.user.roles
  const roleNames = roles.map(role =>
    typeof role === 'string' ? role : role.nombre_rol
  )

  // Priorizar roles en orden de importancia
  if (roleNames.includes('SuperAdmin') || roleNames.includes('Administrador')) {
    return 'Admin'
  } else if (roleNames.includes('Entrenador')) {
    return 'Entrenador'
  } else if (roleNames.includes('Deportista')) {
    return 'Deportista'
  } else if (roleNames.includes('Acudiente')) {
    return 'Acudiente'
  } else if (roleNames.includes('usuario')) {
    return 'Usuario'
  }

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
  if (props.sinMenu) return // No hacer nada si el menú está deshabilitado
  menuVisible.value = !menuVisible.value
  applyLayoutOffsets()
}

function closeMenu() {
  menuOpenedByClick.value = false
  menuVisible.value = false
  applyLayoutOffsets()
}

function isActiveRoute(path) {
  const currentPath = route.path
  return currentPath === path || currentPath.startsWith(path + '/')
}

function handleMenuLinkClick() {
  // Cerrar menú en móvil cuando se hace clic en un link
  if (isMobile.value) {
    closeMenu()
  }
}

async function handleLogout() {
  const result = await Swal.fire({
    icon: 'question',
    title: '¿Cerrar sesión?',
    text: 'Se finalizará tu sesión actual.',
    showCancelButton: true,
    confirmButtonText: 'Sí, salir',
    cancelButtonText: 'Cancelar'
  })

  if (result.isConfirmed) {
    closeMenu()
    await authStore.logout()
    await Swal.fire({
      icon: 'success',
      title: 'Sesión cerrada',
      timer: 1200,
      showConfirmButton: false
    })
    router.replace('/login')
  }
}

function handleOutsideClick(e) {
  const header = document.querySelector('.header-deportista')
  const sidebar = document.querySelector('.sidebar-deportista')

  // Cerrar menú si se hace clic fuera del header y sidebar
  if (header && sidebar) {
    // Solo cerrar automáticamente en móvil; en desktop se mantiene abierto
    if (isMobile.value && !header.contains(e.target) && !sidebar.contains(e.target)) {
      menuVisible.value = false
      applyLayoutOffsets()
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
      { texto: "Perfil", link: "/perfil", icono: "fas fa-user" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
    ],
    Entrenador: [
      { texto: "Inicio", link: "/home", icono: "fas fa-home" },
      { texto: "Perfil", link: "/perfil", icono: "fas fa-user" },
      { texto: "Deportistas", link: "/deportistas", icono: "fas fa-users" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
    ],
    Acudiente: [
      { texto: "Inicio", link: "/acudiente/dashboard", icono: "fas fa-home" },
      { texto: "Mis Acudidos", link: "/acudiente/ver-acudidos", icono: "fas fa-users" },
      { texto: "Mensualidades", link: "/mensualidades", icono: "fas fa-money-bill-wave" },
      { texto: "Eventos", link: "/eventos", icono: "fas fa-calendar-check" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar-alt" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
      { texto: "Configuración", link: "/perfil", icono: "fas fa-cog" },
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
      { texto: "Perfil", link: "/perfil", icono: "fas fa-user" },
      { texto: "Deportistas", link: "/deportistas", icono: "fas fa-users" },
      { texto: "Mensualidades", link: "/mensualidades", icono: "fas fa-wallet" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
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

async function checkMobile() {
  const wasMobile = isMobile.value
  isMobile.value = window.innerWidth < 768
  // En móvil: menú cerrado por defecto. En desktop: abierto por defecto
  if (!props.sinMenu) {
    const shouldBeOpen = !isMobile.value
    // Solo cambiar si el estado debe cambiar
    if (menuVisible.value !== shouldBeOpen) {
      menuVisible.value = shouldBeOpen
      // Sincronizar offsets después del cambio de estado
      await nextTick()
      applyLayoutOffsets()
    } else if (wasMobile !== isMobile.value) {
      // Si cambió de móvil a desktop o viceversa pero el estado ya era correcto, aún así sincronizar
      await nextTick()
      applyLayoutOffsets()
    }
  }
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

// Watcher para sincronizar offsets cuando cambia la ruta (navegación entre páginas)
watch(() => route.path, async () => {
  await nextTick()
  applyLayoutOffsets()
})

function verPerfil() {
  showProfileMenu.value = false
  // Usar siempre el nuevo perfil con selector de roles
  router.push('/perfil')
}

function editarPerfil() {
  showProfileMenu.value = false
  router.push('/actualizar-info')
}

async function cerrarSesion() {
  showProfileMenu.value = false
  const result = await Swal.fire({
    icon: 'question',
    title: '¿Cerrar sesión?',
    text: 'Se finalizará tu sesión actual.',
    showCancelButton: true,
    confirmButtonText: 'Sí, salir',
    cancelButtonText: 'Cancelar'
  })

  if (result.isConfirmed) {
    await authStore.logout()
    await Swal.fire({
      icon: 'success',
      title: 'Sesión cerrada',
      timer: 1200,
      showConfirmButton: false
    })
    router.replace('/login')
  }
}

// Ciclo de vida
onMounted(async () => {
  if (!props.sinMenu) {
    checkMobile()
    cargarOpciones()
    // Asegurar que los offsets se aplican después de que el estado inicial se establezca
    await nextTick()
    applyLayoutOffsets()

    document.addEventListener("click", handleOutsideClick)
    window.addEventListener("resize", async () => {
      checkMobile()
      // Aplicar offsets después de resize también
      await nextTick()
      applyLayoutOffsets()
    })
  } else {
    document.addEventListener("click", handleOutsideClick)
    // Incluso sin menú, aplicar el offset del header
    await nextTick()
    applyLayoutOffsets()
  }
})

// Aplicar offsets después de cada actualización del componente
onUpdated(() => {
  applyLayoutOffsets()
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

// Ajustes globales de layout: evita interferencias del header/menú con el contenido
function applyLayoutOffsets() {
  // Header fijo siempre presente
  document.body.classList.add('has-fixed-header')

  // Sidebar empuja contenido solo cuando está visible
  if (!props.sinMenu && menuVisible.value) {
    document.body.classList.add('has-static-sidebar')
  } else {
    document.body.classList.remove('has-static-sidebar')
  }
}
</script>


