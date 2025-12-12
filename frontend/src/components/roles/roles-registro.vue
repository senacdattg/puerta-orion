<template>
  <main class="contenedor-roles">
    <div class="contenedor">
      <div class="titulo">{{ esSeleccionRol ? 'SELECCIONAR ROL' : 'REGISTRO ROLES' }}</div>

      <div v-if="loading" class="loading-message">Cargando roles...</div>
      <div v-if="error" class="error-message">{{ error }}</div>

      <div class="tarjetas">
        <div
          v-for="rol in rolesFiltrados"
          :key="rol.id_rol || rol.id || rol.nombre_rol"
          :class="['sub-contenedor', {
            'rol-disponible': tieneRol(rol),
            'rol-no-disponible': !tieneRol(rol),
            'rol-seleccionado': rolSeleccionado === obtenerNombreRol(rol)
          }]"
          @click="seleccionarRol(rol)"
        >
          <div class="icono-rol">
            <i :class="obtenerIcono(rol)"></i>
          </div>
          <h1 class="sub-titulo">{{ obtenerNombreRolParaMostrar(rol) }}</h1>
          <div v-if="!tieneRol(rol)" class="badge-no-disponible">No disponible</div>
        </div>
      </div>

      <button class="boton" @click="accionBoton">{{ esSeleccionRol ? 'Cerrar sesión' : 'Volver' }}</button>
    </div>
  </main>
</template>

<script setup>
import { useRouter, useRoute } from "vue-router"
import { ref, computed, onMounted } from "vue"
import { useAuthStore } from "@/stores/auth"
import usuariosService from "@/services/usuariosService"
import Swal from "sweetalert2"

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const props = defineProps({
  usuarioRoles: {
    type: Array,
    default: () => []
  }
})

// Determinar si es selección de rol (después de login) o registro
const esSeleccionRol = computed(() => route.name === 'seleccionar-rol')

const todosRoles = ref([])
const loading = ref(false)
const error = ref('')
const rolSeleccionado = ref(null)

// Mapeo de roles a iconos
const iconosRoles = {
  'SuperAdmin': 'fas fa-crown',
  'Administrador': 'fas fa-user-shield',
  'Entrenador': 'fas fa-clipboard-list',
  'Deportista': 'fas fa-running',
  'Acudiente': 'fa-solid fa-user-group',
  'Usuario': 'fas fa-user',
  'Aspirante': 'fas fa-user-plus'
}

// Obtener icono para un rol
function obtenerIcono(rol) {
  const nombre = obtenerNombreRol(rol)
  return iconosRoles[nombre] || 'fas fa-user'
}

// Obtener nombre del rol (manejar diferentes formatos)
function obtenerNombreRol(rol) {
  if (typeof rol === 'string') return rol
  return rol.nombre_rol || rol.nombre || rol.rol || 'Sin nombre'
}

// Obtener nombre del rol para mostrar (SuperAdmin se muestra como Administrador)
function obtenerNombreRolParaMostrar(rol) {
  const nombre = obtenerNombreRol(rol)
  return nombre === 'SuperAdmin' ? 'Administrador' : nombre
}

// Obtener roles del usuario
const rolesUsuario = computed(() => {
  if (esSeleccionRol.value && authStore.user?.roles) {
    // Mapear todos los roles del usuario, incluyendo 'Usuario'
    const rolesMapeados = authStore.user.roles.map(r => obtenerNombreRol(r))
    return rolesMapeados
  }
  return props.usuarioRoles.map(r => obtenerNombreRol(r))
})

// Filtrar roles para mostrar solo los seleccionables
const rolesFiltrados = computed(() => {
  const nombresRoles = new Set(rolesUsuario.value.map(r => obtenerNombreRol(r)))

  // Si tiene Deportista y Acudiente, excluir Usuario
  const tieneDeportista = nombresRoles.has('Deportista')
  const tieneAcudiente = nombresRoles.has('Acudiente')
  const debeExcluirUsuario = tieneDeportista && tieneAcudiente

  return todosRoles.value.filter(rol => {
    const nombreRol = obtenerNombreRol(rol)

    // Excluir SuperAdmin siempre
    if (nombreRol === 'SuperAdmin') {
      return false
    }

    // Si debe excluir Usuario y el rol es Usuario, no mostrarlo
    if (debeExcluirUsuario && (nombreRol === 'Usuario' || nombreRol === 'usuario')) {
      return false
    }

    return true
  })
})

// Verificar si el usuario tiene un rol específico
function tieneRol(rol) {
  const nombreRol = obtenerNombreRol(rol)
  return rolesUsuario.value.includes(nombreRol)
}

// Función para seleccionar un rol
async function seleccionarRol(rol) {
  if (!tieneRol(rol)) {
    await Swal.fire({
      icon: 'info',
      title: 'Rol no disponible',
      text: 'No tienes acceso a este rol con tu cuenta.'
    })
    return
  }

  if (esSeleccionRol.value) {
    const nombreRol = obtenerNombreRol(rol)
    rolSeleccionado.value = nombreRol

    // Guardar rol activo en el store (esto también cargará los permisos del rol)
    // Pasar true como segundo parámetro para forzar el cambio cuando el usuario selecciona explícitamente
    const result = await authStore.setActiveRole(nombreRol, true)

    // Verificar si el cambio de rol fue exitoso
    if (!result.success) {
      console.error('Error al cambiar rol activo:', result.error)
      await Swal.fire({
        icon: 'error',
        title: 'Error al cambiar rol',
        text: result.error || 'No se pudo cambiar el rol activo. Por favor, intenta de nuevo.'
      })
      return
    }

    // Usar el rol que el usuario seleccionó explícitamente, no el que puede haber devuelto el backend
    // El backend puede devolver un rol diferente si tiene lógica automática, pero debemos respetar la selección del usuario
    const rolActivoFinal = authStore.activeRole || nombreRol

    // Verificar que el rol final coincida con el seleccionado
    // Si no coincide, usar el seleccionado (el usuario eligió explícitamente)
    const rolParaUsar = (rolActivoFinal === nombreRol || rolActivoFinal?.toLowerCase() === nombreRol?.toLowerCase())
      ? rolActivoFinal
      : nombreRol


    // Mostrar nombre normalizado en el mensaje (SuperAdmin se muestra como Administrador)
    const rolParaMostrar = rolParaUsar === 'SuperAdmin' ? 'Administrador' : rolParaUsar
    await Swal.fire({
      icon: 'success',
      title: 'Rol seleccionado',
      text: `Ingresarás con el rol ${rolParaMostrar}.`,
      timer: 1200,
      timerProgressBar: true,
      showConfirmButton: false
    })

    // Redirigir según el rol que el usuario seleccionó explícitamente
    redirigirSegunRol(rolParaUsar)
  } else {
    // Modo registro - redirigir al formulario correspondiente
    irFormulario(rol.ruta)
  }
}

// Función para redirigir según el rol seleccionado
function redirigirSegunRol(rolNombre) {
  let rutaDestino

  // Normalizar el nombre del rol para comparación (primera letra mayúscula)
  const rolNormalizado = rolNombre?.charAt(0).toUpperCase() + rolNombre?.slice(1).toLowerCase()

  switch(rolNormalizado) {
    case 'SuperAdmin':
    case 'Administrador':
      rutaDestino = '/admin-manager'
      break
    case 'Deportista':
      rutaDestino = '/deportista/dashboard'
      break
    case 'Acudiente':
      rutaDestino = '/acudiente/dashboard'
      break
    case 'Usuario':
    case 'Entrenador':
    default:
      rutaDestino = '/home'
      break
  }

  router.push(rutaDestino)
}

// Función para cargar roles desde el backend
async function cargarRoles() {
  if (!esSeleccionRol.value) {
    // Modo registro - usar roles hardcodeados
    todosRoles.value = [
      { nombre: "Aspirante", icono: "fas fa-user-plus", ruta: '/registrar-general'},
      { nombre: "Deportista", icono: "fas fa-running", ruta: '/registrar-deportista'},
      { nombre: "Acudiente", icono: "fa-solid fa-user-group", ruta: '/registrar-general'}
    ]
    return
  }

  // Modo selección - cargar todos los roles desde el backend
  // Esto permite mostrar todos los roles: los que el usuario tiene (amarillos) y los que no (grises)
  loading.value = true
  error.value = ''

  try {
    const response = await usuariosService.listarRoles()

    if (response.success && response.data) {
      todosRoles.value = response.data
    } else {
      error.value = 'No se pudieron cargar los roles'
      await Swal.fire({
        icon: 'error',
        title: 'Error al cargar roles',
        text: response.error || 'Intenta recargar la página.'
      })
    }
  } catch (err) {
    console.error('Error cargando roles:', err)
    error.value = 'Error al cargar roles'
    await Swal.fire({
      icon: 'error',
      title: 'Error de conexión',
      text: 'No pudimos obtener tus roles. Revisa tu conexión e intenta de nuevo.'
    })
  } finally {
    loading.value = false
  }
}

function irFormulario(ruta) {
  router.push(ruta)
}

async function accionBoton() {
  if (esSeleccionRol.value) {
    const confirm = await Swal.fire({
      icon: 'question',
      title: '¿Cerrar sesión?',
      text: 'Perderás el progreso actual y volverás a la pantalla de login.',
      showCancelButton: true,
      confirmButtonText: 'Sí, cerrar sesión',
      cancelButtonText: 'Cancelar'
    })
    if (confirm.isConfirmed) {
      await authStore.logout()
      router.replace("/login")
    }
  } else {
    router.replace("/login")
  }
}

onMounted(() => {
  cargarRoles()
})
</script>

