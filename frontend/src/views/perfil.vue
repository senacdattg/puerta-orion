<template>
  <main class="perfil-page">
    <Encabezado :rol="userRole" />
    <TituloClub />

    <div class="perfil-container">
      <div class="perfil-header">
        <h1 class="perfil-title">
          <i class="fas fa-user"></i>
          Mi Perfil
        </h1>
        <p class="perfil-subtitle">Consulta y gestiona tu información personal</p>
      </div>

      <div class="perfil-content">
        <div class="perfil-card">
          <div class="card-header">
            <h3>Información Personal</h3>
            <button class="btn btn-primary btn-icon" @click="editarPerfil">
              <i class="fas fa-edit icon"></i>
              Editar
            </button>
          </div>

          <div class="card-content" v-if="usuario">
            <div class="info-row">
              <label>Nombre completo:</label>
              <span>{{ usuario.persona?.nombre_completo || 'No disponible' }}</span>
            </div>

            <div class="info-row">
              <label>Correo electrónico:</label>
              <span>{{ usuario.persona?.correo_electronico || 'No disponible' }}</span>
            </div>

            <div class="info-row">
              <label>Documento:</label>
              <span>{{ usuario.persona?.documento || 'No disponible' }}</span>
            </div>

            <div class="info-row">
              <label>Teléfono:</label>
              <span>{{ usuario.persona?.telefono || 'No disponible' }}</span>
            </div>

            <div class="info-row">
              <label>Dirección:</label>
              <span>{{ usuario.persona?.direccion || 'No disponible' }}</span>
            </div>
          </div>
        </div>

        <div class="perfil-card" v-if="usuario?.roles">
          <div class="card-header">
            <h3>Roles Asignados</h3>
          </div>

          <div class="card-content">
            <div class="roles-list">
              <div
                v-for="rol in usuario.roles"
                :key="rol.id_rol"
                class="role-badge"
                :class="getRoleClass(rol.nombre_rol)"
              >
                <i :class="getRoleIcon(rol.nombre_rol)"></i>
                {{ rol.nombre_rol }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <FooterEnhanced />
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserRole } from '@/composables/useUserRole'
import Encabezado from '@/components/layout/encabezado.vue'
import TituloClub from '@/components/ui/titulo-club.vue'
import FooterEnhanced from '@/components/layout/pie.vue'

// Definir nombre del componente para el linter
defineOptions({
  name: 'PerfilPage'
})

const router = useRouter()
const authStore = useAuthStore()
const { userRole } = useUserRole()
const usuario = ref(null)

onMounted(() => {
  usuario.value = authStore.user
})

const editarPerfil = () => {
  router.push('/actualizar-info')
}

const getRoleClass = (rol) => {
  const classes = {
    'Administrador': 'role-admin',
    'Entrenador': 'role-coach',
    'Deportista': 'role-athlete',
    'Acudiente': 'role-guardian',
    'usuario': 'role-user'
  }
  return classes[rol] || 'role-default'
}

const getRoleIcon = (rol) => {
  const icons = {
    'Administrador': 'fas fa-crown',
    'Entrenador': 'fas fa-whistle',
    'Deportista': 'fas fa-running',
    'Acudiente': 'fas fa-user-friends',
    'usuario': 'fas fa-user'
  }
  return icons[rol] || 'fas fa-user'
}
</script>

<style scoped>
/* Los estilos están en /assets/css/perfiles.css */
</style>
