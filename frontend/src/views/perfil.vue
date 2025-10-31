<template>
  <main class="perfil-page">
    <Encabezado />
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

        <div class="perfil-card" v-if="usuario?.roles && usuario.roles.length > 1">
          <div class="card-header">
            <h3>Gestión de Roles</h3>
            <p class="card-subtitle">Cambia entre tus diferentes paneles de acceso</p>
          </div>

          <div class="card-content">
            <SelectorRoles />

            <div class="roles-info">
              <h4>Roles asignados:</h4>
              <div class="roles-list">
                <div
                  v-for="rol in usuario.roles"
                  :key="getRolId(rol)"
                  class="role-badge"
                  :class="getRoleClass(getNombreRol(rol))"
                >
                  <i :class="getRoleIcon(getNombreRol(rol))"></i>
                  {{ getNombreRolCompleto(rol) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="perfil-card" v-else-if="usuario?.roles && usuario.roles.length === 1">
          <div class="card-header">
            <h3>Rol Asignado</h3>
          </div>

          <div class="card-content">
            <div class="role-badge single" :class="getRoleClass(getNombreRol(usuario.roles[0]))">
              <i :class="getRoleIcon(getNombreRol(usuario.roles[0]))"></i>
              {{ getNombreRolCompleto(usuario.roles[0]) }}
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
import Encabezado from '@/components/layout/encabezado.vue'
import TituloClub from '@/components/ui/titulo-club.vue'
import FooterEnhanced from '@/components/layout/pie.vue'
import SelectorRoles from '@/components/layout/selector-roles.vue'

// Definir nombre del componente para el linter
defineOptions({
  name: 'PerfilPage'
})

const router = useRouter()
const authStore = useAuthStore()
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
    'usuario': 'fas fa-user',
    'Usuario': 'fas fa-user'
  }
  return icons[rol] || 'fas fa-user'
}

const getNombreRol = (rol) => {
  if (typeof rol === 'string') return rol
  if (typeof rol === 'object' && rol !== null && rol.nombre_rol) {
    return rol.nombre_rol
  }
  return 'usuario'
}

const getNombreRolCompleto = (rol) => {
  const nombres = {
    'Deportista': '🏃 Deportista',
    'Acudiente': '👨‍👩‍👧 Acudiente',
    'Entrenador': '⚽ Entrenador',
    'Administrador': '👤 Administrador',
    'SuperAdmin': '👑 Super Admin',
    'Usuario': '👤 Usuario',
    'usuario': '👤 Usuario'
  }
  return nombres[getNombreRol(rol)] || getNombreRol(rol)
}

const getRolId = (rol) => {
  if (typeof rol === 'object' && rol !== null && rol.id_rol) {
    return rol.id_rol
  }
  return getNombreRol(rol)
}
</script>

<style scoped>
/* Los estilos están en /assets/css/perfiles.css */
</style>
