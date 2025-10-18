<template>
  <header class="encabezado" >
    <i v-if="!sinMenu"
    class="fa-solid fa-bars menu-toggle"
    @click="toggleMenu"
    ></i>

    <img src="@/assets/imgs/logo.png" alt="Logo">
    
    <!-- Info del usuario autenticado -->
    <div v-if="!sinMenu && authStore.estaAutenticado" class="usuario-info">
      <span class="usuario-nombre">
        <i class="fas fa-user-circle"></i>
        {{ authStore.nombreUsuario || 'Usuario' }}
      </span>
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
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Props
const props = defineProps({
  rol: {
    type: String,
    default: ''
  },
  sinMenu: {
    type: Boolean,
    default: false
  }
})

// Estado
const menuVisible = ref(false)
const opciones = ref([])

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
    ],
    Entrenador: [
      { texto: "Inicio", link: "/home", icono: "fas fa-home" },
      { texto: "Perfil", link: "/ver-general", icono: "fas fa-user" },
      { texto: "Deportistas", link: "/deportistas", icono: "fas fa-users" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
    ],
    Acudiente: [
      { texto: "Inicio", link: "/home", icono: "fas fa-home" },
      { texto: "Perfil", link: "/ver-general", icono: "fas fa-user" },
      { texto: "Mensualidades", link: "/mensualidades", icono: "fas fa-wallet" },
    ],
    Deportista: [
      { texto: "Inicio", link: "/home", icono: "fas fa-home" },
      { texto: "Perfil", link: "/ver-deportista", icono: "fas fa-user" },
      { texto: "Mensualidades", link: "/mensualidades", icono: "fas fa-wallet" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
    ],
    Admin: [
      { texto: "Inicio", link: "/home", icono: "fas fa-home" },
      { texto: "Perfil", link: "/ver-general", icono: "fas fa-user" },
      { texto: "Deportistas", link: "/deportistas", icono: "fas fa-users" },
      { texto: "Mensualidades", link: "/mensualidades", icono: "fas fa-wallet" },
      { texto: "Calendario", link: "/calendario", icono: "fas fa-calendar" },
      { texto: "Galería", link: "/galeria", icono: "fas fa-images" },
      { texto: "Panel Admin", link: "/admin-manager", icono: "fas fa-cog" },
    ]
  }
  
  opciones.value = opcionesPorRol[props.rol] || [
    { texto: "Inicio", link: "/home", icono: "fas fa-home" }
  ]
}

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

