<template>
  <header class="encabezado" >
    <i v-if="!sinMenu"
    class="fa-solid fa-bars menu-toggle"
    @click="toggleMenu"
    ></i>

    <img src="@/assets/imgs/logo.png" alt="Logo">

    <!-- Info del usuario autenticado -->
    <div v-if="!sinMenu && authStore.estaAutenticado" class="usuario-info">
      <router-link to="/perfil" class="usuario-nombre usuario-link">
        <i class="fas fa-user-circle"></i>
        {{ nombreUsuario }}
      </router-link>
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
        <li v-if="authStore.estaAutenticado" class="logout-item">
          <a @click="handleLogout" class="menu-link logout-link">
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
import SelectorRoles from './selector-roles.vue'

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
    return 'Aspirante'
  }

  return 'Usuario'
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
function toggleMenu() {
  menuVisible.value = !menuVisible.value
}

function closeMenu() {
  menuVisible.value = false
}

function handleOutsideClick(e) {
  const header = document.querySelector('.encabezado')
  if (header && !header.contains(e.target)) {
    menuVisible.value = false
  }
}

async function handleLogout() {
  const confirmar = confirm('¿Estás seguro de que deseas cerrar sesión?')

  if (confirmar) {
    closeMenu()
    await authStore.logout()
    router.push('/login')
  }
}

function cargarOpciones() {
  const opcionesPorRol = {
    Aspirante: [
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
      { texto: "Inicio", link: "/home", icono: "fas fa-home" },
      { texto: "Perfil", link: "/ver-general", icono: "fas fa-user" },
      { texto: "Deportistas", link: "/deportistas", icono: "fas fa-users" },
      { texto: "Mensualidades", link: "/mensualidades", icono: "fas fa-wallet" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
      { texto: "Panel Admin", link: "/admin-manager", icono: "fas fa-cog" },
    ],
    Usuario: [
      { texto: "Inicio", link: "/home", icono: "fas fa-home" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
    ]
  }

  const rolActual = userRole.value
  opciones.value = opcionesPorRol[rolActual] || opcionesPorRol['Usuario']
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

.usuario-nombre {
  color: #333;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.usuario-nombre i {
  font-size: 20px;
  color: #007bff;
}

.usuario-link {
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
}

.usuario-link:hover {
  color: #007bff;
  transform: scale(1.05);
}

.usuario-link:hover i {
  color: #0056b3;
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

.logout-item {
  border-top: 1px solid #e0e0e0;
  margin-top: 8px;
  padding-top: 8px;
}

.logout-link {
  color: #dc3545 !important;
  cursor: pointer;
}

.logout-link:hover {
  background-color: rgba(220, 53, 69, 0.1) !important;
}

@media (max-width: 768px) {
  .usuario-info {
    display: none;
  }
}
</style>

