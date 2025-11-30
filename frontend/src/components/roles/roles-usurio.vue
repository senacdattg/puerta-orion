<template>
  <main class="contenedor-roles">
    <div class="contenedor">
      <div class="titulo"> GESTIÓN DE ROLES </div>

      <!-- Selector de vista actual -->
      <div class="selector-rol">
        <label for="selector-vista-actual" class="label">Vista actual:</label>
        <select id="selector-vista-actual" v-model="rolActual" @change="cambiarRol" class="select-rol">
          <option v-for="r in rolesDisponibles" :key="r" :value="r">{{ r }}</option>
        </select>
      </div>

      <!-- Roles asignados (visual) -->
      <div class="tarjetas">
        <div v-for="(rol, index) in roles" :key="index" class="sub-contenedor"
          :class="{ inactivo: !usuarioRoles.includes(rol.nombre) }">
          <div class="icono-rol">
            <i :class="rol.icono"></i>
          </div>
          <h1 class="sub-titulo">{{ rol.nombre }}</h1>
        </div>
      </div>

      <button class="boton" @click="accionBoton">Volver</button>
    </div>
  </main>
  </template>

<script setup>
import { useRouter } from "vue-router"
import { ref, computed, onMounted } from "vue"
import { useAuthStore } from "@/stores/auth"

const router = useRouter()
const authStore = useAuthStore()

const props = defineProps({
  usuarioRoles: { type: Array, default: () => [] }
})

const roles = ref([
  { nombre: "Aspirante", icono: "fas fa-user-plus" },
  { nombre: "Deportista", icono: "fas fa-running" },
  { nombre: "Acudiente", icono: "fa-solid fa-user-group" },
  { nombre: "Entrenador", icono: "fa-solid fa-chalkboard-user" },
  { nombre: "Administrador", icono: "fa-solid fa-user-gear" }
])

// Roles del usuario (desde props o store)
const usuarioRoles = computed(() => {
  const list = props.usuarioRoles && props.usuarioRoles.length
    ? props.usuarioRoles
    : (authStore.user?.roles || []).map(r => typeof r === 'string' ? r : r?.nombre_rol)
  return list
})

// Lista para el selector (solo roles que posee)
const rolesDisponibles = computed(() => {
  const selectorEntries = Object.entries(authStore.rolesSelector || {}).filter(([, visible]) => visible)
  if (selectorEntries.length > 0) {
    return selectorEntries.map(([rol]) => rol)
  }
  return usuarioRoles.value
})

// Rol actual tomado del store (solo si está en rolesDisponibles)
const getRolInicial = () => {
  if (authStore.activeRole && rolesDisponibles.value.includes(authStore.activeRole)) {
    return authStore.activeRole
  }
  return rolesDisponibles.value[0] || 'Usuario'
}
const rolActual = ref(getRolInicial())

async function cambiarRol() {
  const nombreRol = rolActual.value
  const previo = authStore.activeRole
  const resultado = await authStore.setActiveRole(nombreRol)

  if (resultado?.success === false) {
    console.warn('No se pudo cambiar el rol activo:', resultado.error)
    rolActual.value = previo || rolesDisponibles.value[0] || 'Usuario'
    return
  }

  switch (nombreRol) {
    case 'SuperAdmin':
    case 'Administrador':
      router.replace('/admin-manager'); break
    case 'Entrenador':
      router.replace('/home'); break
    case 'Deportista':
      router.replace('/deportista/dashboard'); break
    case 'Acudiente':
      router.replace('/acudiente/dashboard'); break
    default:
      router.replace('/home')
  }
}

function accionBoton() {
  router.push('/ver-general')
}

onMounted(() => {
  // Sincronizar el valor inicial con el store si existe
  if (authStore.activeRole && rolesDisponibles.value.includes(authStore.activeRole)) {
    rolActual.value = authStore.activeRole
  }
})
</script>
