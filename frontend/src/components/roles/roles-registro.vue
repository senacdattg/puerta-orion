<template>
  <main class="contenedor-roles">
    <div class="contenedor">
      <div class="titulo">{{ esSeleccionRol ? 'SELECCIONAR ROL' : 'REGISTRO ROLES' }}</div>

      <div v-if="loading" class="loading-message">Cargando roles...</div>
      <div v-if="error" class="error-message">{{ error }}</div>

      <div class="tarjetas">
        <div
          v-for="rol in todosRoles"
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
          <h1 class="sub-titulo">{{ obtenerNombreRol(rol) }}</h1>
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

// Obtener roles del usuario
const rolesUsuario = computed(() => {
  if (esSeleccionRol.value && authStore.user?.roles) {
    // Mapear todos los roles del usuario, incluyendo 'Usuario'
    const rolesMapeados = authStore.user.roles.map(r => obtenerNombreRol(r))
    console.log('📋 Roles del usuario disponibles:', rolesMapeados)
    return rolesMapeados
  }
  return props.usuarioRoles.map(r => obtenerNombreRol(r))
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
    const result = await authStore.setActiveRole(nombreRol)
    
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

    // Usar el rol activo actualizado del store después del cambio
    const rolActivoFinal = authStore.activeRole || nombreRol
    console.log(`✅ Rol activo establecido: ${rolActivoFinal} (seleccionado: ${nombreRol})`)

    await Swal.fire({
      icon: 'success',
      title: 'Rol seleccionado',
      text: `Ingresarás con el rol ${rolActivoFinal}.`,
      timer: 1200,
      timerProgressBar: true,
      showConfirmButton: false
    })

    // Redirigir según el rol activo final (no el seleccionado, por si el backend lo cambió)
    redirigirSegunRol(rolActivoFinal)
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

  console.log(`🔄 Redirigiendo a ${rutaDestino} para rol: ${rolNormalizado}`)
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
      console.log('✅ Todos los roles cargados:', todosRoles.value)
      console.log('📋 Roles del usuario:', rolesUsuario.value)
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

<style scoped>
/* Roles disponibles - color brillante */
.rol-disponible {
  opacity: 1 !important;
  cursor: pointer;
  background-color: #f4d800 !important;
  position: relative;
}

.rol-disponible:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 8px 20px rgba(244, 216, 0, 0.5);
}

/* Roles no disponibles - color opaco */
.rol-no-disponible {
  opacity: 0.4 !important;
  cursor: not-allowed !important;
  background-color: #d3d3d3 !important;
  filter: grayscale(100%);
  position: relative;
}

.rol-no-disponible:hover {
  transform: none;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.rol-no-disponible .icono-rol,
.rol-no-disponible .sub-titulo {
  color: #666 !important;
}

/* Rol seleccionado */
.rol-seleccionado {
  border: 3px solid #10b981 !important;
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.5) !important;
  transform: scale(1.05);
}

/* Badge para roles no disponibles */
.badge-no-disponible {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(239, 68, 68, 0.95);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Mensajes de carga y error */
.loading-message, .error-message {
  text-align: center;
  padding: 20px;
  margin: 20px 0;
  width: 100%;
}

.error-message {
  color: #ef4444;
  background: #fee2e2;
  border-radius: 8px;
  border: 1px solid #fecaca;
}

.loading-message {
  color: #0047ab;
  background: #e0f2fe;
  border-radius: 8px;
  border: 1px solid #bae6fd;
}

.sub-contenedor {
  position: relative;
}
</style>
