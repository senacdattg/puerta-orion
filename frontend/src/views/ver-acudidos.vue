<template>
  <main class="ver-acudidos-page">
    <Encabezado />
    <div class="ver-acudidos-container">
      <div class="ver-acudidos-header">
        <h1 class=" ver-acudidos-title">
          <i class="fas fa-users"></i>
          Gestión de Acudidos
        </h1>
        <p class="ver-acudidos-subtitle">Gestiona y asigna deportistas a tu cuenta</p>
      </div>

      <!-- Botón de acudir a un deportista -->
      <div class="action-header">
        <button class="btn-create-new" @click="abrirModalAcudir">
          <i class="fas fa-user-plus"></i>
          Acudir a un Deportista
        </button>
      </div>

      <!-- Lista de acudidos o estado vacío -->
      <div v-if="acudidos.length > 0" class="acudidos-grid">
        <div
          v-for="acudido in acudidos"
          :key="acudido.id"
          class="acudido-card"
        >
          <div class="card-header">
            <div class="acudido-avatar">
              <i class="fas fa-user"></i>
            </div>
            <div class="acudido-info">
              <h3>{{ acudido.nombre_completo }}</h3>
              <p>{{ acudido.categoria }}</p>
            </div>
          </div>

          <div class="card-content">
            <div class="info-item">
              <i class="fas fa-calendar"></i>
              <span>Edad: {{ acudido.edad }} años</span>
            </div>
            <div class="info-item">
              <i class="fas fa-envelope"></i>
              <span>{{ acudido.correo_electronico }}</span>
            </div>
            <div class="info-item">
              <i class="fas fa-phone"></i>
              <span>{{ acudido.telefono }}</span>
            </div>
          </div>

          <div class="card-actions">
            <button class="btn-action btn-view" @click="verDetalle(acudido)">
              <i class="fas fa-eye"></i>
              Ver Detalle
            </button>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-user-friends"></i>
        </div>
        <h3>No tienes acudidos registrados</h3>
        <p>Asigna deportistas a tu cuenta para gestionar su información</p>
        <button class="btn-primary" @click="abrirModalAcudir">
          <i class="fas fa-user-plus"></i>
          Acudir a un Deportista
        </button>
      </div>
    </div>

    <!-- Modal para buscar y asociar deportista -->
    <div v-if="mostrarModalAcudir" class="modal-overlay" @click.self="cerrarModalAcudir">
      <div class="modal-content modal-sm" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">Acudir a un Deportista</h2>
          <button class="btn-cerrar" @click="cerrarModalAcudir">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <!-- Búsqueda de deportista -->
          <div class="busqueda-deportista">
            <div class="busqueda-row">
              <label class="form-label">🔍 Buscar deportista:</label>
              <div class="input-busqueda">
                <input
                  type="text"
                  inputmode="numeric"
                  pattern="[0-9]*"
                  v-model="busquedaDeportista"
                  @input="manejarBusqueda"
                  placeholder="Buscar por documento..."
                  class="input-text"
                />
              </div>
            </div>
            <div v-if="buscando" class="cargando-busqueda">
              <i class="fas fa-spinner fa-spin"></i>
              <span>Buscando...</span>
            </div>
          </div>

          <!-- Lista de deportistas encontrados -->
          <div v-if="deportistasEncontrados.length > 0" class="deportistas-lista">
            <h4 class="lista-titulo">📋 Deportistas encontrados</h4>
            <div class="deportistas-grid">
              <div
                v-for="deportista in deportistasEncontrados"
                :key="deportista.id_deportista"
                class="deportista-item"
                :class="{ 'seleccionado': deportistaSeleccionado?.id_deportista === deportista.id_deportista }"
                @click="seleccionarDeportista(deportista)"
              >
                <div class="deportista-info">
                  <strong class="deportista-nombre">{{ deportista.nombre_completo || deportista.nombre || 'Sin nombre' }}</strong>
                  <div class="deportista-detalles">
                    <span v-if="deportista.documento" class="detalle-item">
                      <i class="fas fa-id-card"></i>
                      {{ deportista.documento }}
                    </span>
                    <span v-if="deportista.categoria" class="detalle-item">
                      <i class="fas fa-tag"></i>
                      {{ deportista.categoria }}
                    </span>
                  </div>
                </div>
                <i v-if="deportistaSeleccionado?.id_deportista === deportista.id_deportista" class="fas fa-check-circle icono-seleccionado"></i>
              </div>
            </div>
          </div>

          <div v-else-if="busquedaDeportista && !buscando && deportistasEncontrados.length === 0" class="sin-resultados-busqueda">
            <i class="fas fa-search"></i>
            <p>No se encontraron deportistas con ese criterio de búsqueda.</p>
          </div>

          <!-- Formulario de asociación -->
          <div v-if="deportistaSeleccionado" class="formulario-asociacion">
            <div class="separador"></div>
            <h4 class="formulario-titulo">📝 Datos de la asociación</h4>
            <div class="form-group">
              <label class="form-label">Parentesco <span class="required">*</span></label>
              <select v-model="idParentesco" class="select-input" required>
                <option value="">Seleccione un parentesco</option>
                <option
                  v-for="parentesco in parentescos"
                  :key="parentesco.id_parentesco"
                  :value="parentesco.id_parentesco"
                >
                  {{ parentesco.nombre }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="esResponsable" />
                <span>Es responsable legal</span>
              </label>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancelar" @click="cerrarModalAcudir">
            Cancelar
          </button>
          <button
            class="btn-confirmar"
            @click="asociarDeportista"
            :disabled="!deportistaSeleccionado || !idParentesco || asociando"
          >
            <span v-if="asociando">Asociando...</span>
            <span v-else>Asociar Deportista</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para ver perfil completo del deportista -->
    <div v-if="mostrarModalPerfil" class="modal-overlay modal-deportistas-overlay" @click.self="cerrarModalPerfil">
      <div class="modal-content modal-deportistas" @click.stop>
        <div v-if="cargandoPerfil" class="cargando-perfil">
          <p>Cargando información...</p>
        </div>
        <PerfilDeportistaVista
          v-else-if="deportistaSeleccionadoPerfil"
          :datos="deportistaSeleccionadoPerfil"
          :modoEdicion="modoEdicionPerfil"
          @cerrar="cerrarModalPerfil"
          @editar="habilitarEdicionPerfil"
          @cancelar="cancelarEdicionPerfil"
          @guardar="manejarGuardadoPerfil"
        />
        <div v-else class="error-perfil">
          <p>No se pudo cargar la información del deportista</p>
        </div>
      </div>
    </div>

    <Pie />
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Encabezado from '@/components/layout/encabezado.vue'
import Pie from '@/components/layout/pie.vue'
import { useAuthStore } from '@/stores/auth'
import deportistasService from '@/services/deportistasService'
import authService from '@/services/authService'
import catalogosService from '@/services/catalogosService'
import PerfilDeportistaVista from '@/components/deportistas/perfil-deportista-vista.vue'
import Swal from 'sweetalert2'
import { getApiBaseUrl } from '@/config/environment'

// Constantes para validación de documento
const MIN_DOCUMENTO = 6
const MAX_DOCUMENTO = 20

// Función para normalizar documento (solo números)
function normalizarDocumento(valor = '') {
  return (valor || '')
    .toString()
    .replace(/\D/g, '') // Solo números
    .slice(0, MAX_DOCUMENTO)
}

const authStore = useAuthStore()

const acudidos = ref([])

// Estado del modal de acudir
const mostrarModalAcudir = ref(false)
const busquedaDeportista = ref('')
const deportistasEncontrados = ref([])
const buscando = ref(false)
const deportistaSeleccionado = ref(null)
const parentescos = ref([])
const idParentesco = ref('')
const esResponsable = ref(false)
const asociando = ref(false)

// Función para manejar el input de búsqueda (normalizar y buscar)
function manejarBusqueda(event) {
  const valorNormalizado = normalizarDocumento(event?.target?.value ?? busquedaDeportista.value ?? '')
  busquedaDeportista.value = valorNormalizado
  buscarDeportistas()
}


onMounted(async () => {
  // Recargar el perfil del usuario para obtener información actualizada
  console.log('🔄 Recargando perfil del usuario...')
  await authStore.loadUserProfile()

  // Esperar un momento para que se actualice el perfil
  setTimeout(() => {
    cargarAcudidos()
  }, 500)
})

const cargarAcudidos = async () => {
  try {
    console.log('🔍 Usuario autenticado:', authStore.user)
    console.log('🔍 Token:', authStore.token ? 'Token existe' : 'No hay token')

    // Obtener el ID del acudiente desde el usuario autenticado
    const acudienteId = authStore.user?.acudiente?.id_acudiente
    console.log('🔍 ID del acudiente:', acudienteId)

    if (!acudienteId) {
      console.error('❌ No se encontró ID del acudiente en el usuario autenticado')
      console.log('💡 Info del usuario:', JSON.stringify(authStore.user, null, 2))
      acudidos.value = []
      return
    }

    const baseURL = getApiBaseUrl()
    const endpoint = `/deportistas/acudientes/${acudienteId}/deportistas`
    const url = `${baseURL}${endpoint}`
    console.log(`🌐 Llamando al endpoint: ${url}`)

    // Llamar al backend para obtener los deportistas asociados
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    console.log('📡 Estado de la respuesta:', response.status)

    // Verificar si la respuesta es JSON válido
    let result
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      result = await response.json()
    } else {
      const text = await response.text()
      console.error('❌ Respuesta no es JSON:', text.substring(0, 200))
      throw new Error(`Error del servidor: ${response.status} ${response.statusText}`)
    }
    console.log('📦 Datos recibidos:', result)

    if (response.ok && result.success) {
      acudidos.value = result.data || []
      console.log(`✅ ${acudidos.value.length} deportista(s) cargado(s)`)
      console.log('📋 Deportistas:', acudidos.value)
    } else {
      console.error('❌ Error al cargar deportistas:', result.message)
      acudidos.value = []
    }
  } catch (error) {
    console.error('❌ Error cargando acudidos:', error)
    acudidos.value = []
  }
}

// Estado para el modal de perfil completo
const mostrarModalPerfil = ref(false)
const deportistaSeleccionadoPerfil = ref(null)
const cargandoPerfil = ref(false)
const modoEdicionPerfil = ref(false)

const verDetalle = async (acudido) => {
  cargandoPerfil.value = true
  mostrarModalPerfil.value = true
  deportistaSeleccionadoPerfil.value = null
  modoEdicionPerfil.value = false

  try {
    // Obtener información completa del deportista
    const response = await deportistasService.obtenerDeportistaPorId(acudido.id)

    if (response.success && response.data) {
      deportistaSeleccionadoPerfil.value = response.data
    } else {
      await Swal.fire({
        icon: 'error',
        title: 'No se pudo cargar el deportista',
        text: 'Intenta nuevamente más tarde.'
      })
      mostrarModalPerfil.value = false
    }
  } catch (error) {
    console.error('Error al obtener perfil del deportista:', error)
    await Swal.fire({
      icon: 'error',
      title: 'Error de conexión',
      text: 'Error al cargar la información del deportista.'
    })
    mostrarModalPerfil.value = false
  } finally {
    cargandoPerfil.value = false
  }
}

const cerrarModalPerfil = () => {
  mostrarModalPerfil.value = false
  deportistaSeleccionadoPerfil.value = null
  modoEdicionPerfil.value = false
}

const habilitarEdicionPerfil = () => {
  modoEdicionPerfil.value = true
}

const cancelarEdicionPerfil = () => {
  modoEdicionPerfil.value = false
}

const manejarGuardadoPerfil = async () => {
  modoEdicionPerfil.value = false

  try {
    if (deportistaSeleccionadoPerfil.value) {
      const idDeportista = deportistaSeleccionadoPerfil.value.id || deportistaSeleccionadoPerfil.value.id_deportista
      if (idDeportista) {
        const response = await deportistasService.obtenerDeportistaPorId(idDeportista)
        if ((response.status === 'success' || response.success) && response.data) {
          deportistaSeleccionadoPerfil.value = response.data
        }
      }
    }
  } catch (error) {
    console.error('Error al refrescar información del deportista:', error)
  }

  await cargarAcudidos()
}

// Funciones para el modal de acudir
const abrirModalAcudir = async () => {
  mostrarModalAcudir.value = true
  busquedaDeportista.value = ''
  deportistasEncontrados.value = []
  deportistaSeleccionado.value = null
  idParentesco.value = ''
  esResponsable.value = false

  // Cargar parentescos
  try {
    parentescos.value = await catalogosService.getParentescos()
    console.log('✅ Parentescos cargados:', parentescos.value)
  } catch (error) {
    console.error('❌ Error al cargar parentescos:', error)
    await Swal.fire({
      icon: 'error',
      title: 'No se pudieron cargar los parentescos',
      text: 'Por favor, intenta de nuevo.'
    })
  }
}

const cerrarModalAcudir = () => {
  mostrarModalAcudir.value = false
  busquedaDeportista.value = ''
  deportistasEncontrados.value = []
  deportistaSeleccionado.value = null
  idParentesco.value = ''
  esResponsable.value = false
}

const buscarDeportistas = async () => {
  const busqueda = busquedaDeportista.value.trim()

  if (!busqueda) {
    deportistasEncontrados.value = []
    return
  }

  // Validar que tenga al menos 6 dígitos
  if (busqueda.length < MIN_DOCUMENTO) {
    deportistasEncontrados.value = []
    return
  }

  // Buscar deportista por documento usando el nuevo servicio específico para acudientes
  buscando.value = true
  try {
    const respuesta = await deportistasService.buscarDeportistaPorDocumentoParaAcudiente(busqueda)

    if (respuesta?.success && respuesta.encontrado) {
      const deportista = respuesta.data
      deportistasEncontrados.value = [deportista]
      console.log('✅ Deportista encontrado por documento:', deportista)
    } else {
      deportistasEncontrados.value = []

      // Verificar si el deportista ya es acudido
      if (respuesta?.ya_acudido) {
        const nombreDeportista = respuesta.data?.nombre_completo || respuesta.data?.nombre || 'este deportista'
        await Swal.fire({
          icon: 'info',
          title: 'Deportista ya asociado',
          text: `${nombreDeportista} ya es acudido por ti.`,
          confirmButtonText: 'Entendido'
        })
      } else {
        const mensaje = respuesta?.message || 'No se encontró un deportista con ese documento.'
        console.log('ℹ️', mensaje)
      }
    }
  } catch (error) {
    console.error('❌ Error al buscar por documento:', error)
    deportistasEncontrados.value = []
    await Swal.fire({
      icon: 'error',
      title: 'Error al buscar deportista',
      text: error.message || 'Por favor, intenta de nuevo.'
    })
  } finally {
    buscando.value = false
  }
}

const seleccionarDeportista = (deportista) => {
  deportistaSeleccionado.value = deportista
  console.log('✅ Deportista seleccionado:', deportista)
}

const asociarDeportista = async () => {
  if (!deportistaSeleccionado.value || !idParentesco.value) {
    await Swal.fire({
      icon: 'warning',
      title: 'Datos incompletos',
      text: 'Selecciona un deportista y un parentesco antes de continuar.'
    })
    return
  }

  // Validar que el usuario no se esté acudiendo a sí mismo
  const usuarioActual = authStore.user
  const idPersonaUsuario = usuarioActual?.persona?.id_persona || usuarioActual?.id_persona

  // Verificar si el deportista seleccionado tiene el mismo id_persona que el usuario actual
  if (deportistaSeleccionado.value.id_persona === idPersonaUsuario ||
      deportistaSeleccionado.value.persona?.id_persona === idPersonaUsuario) {
    await Swal.fire({
      icon: 'info',
      title: 'Acción no permitida',
      text: 'No puedes acudirte a ti mismo.'
    })
    return
  }

  asociando.value = true
  try {
    const datos = {
      id_deportista: deportistaSeleccionado.value.id_deportista,
      id_parentesco: parseInt(idParentesco.value),
      es_responsable: esResponsable.value
    }

    console.log('🔄 Asociando deportista con datos:', datos)

    // Primero intentar asociar como acudiente existente
    let response = await authService.asociarAcudienteDeportista(datos)

    // Si falla porque no es acudiente, intentar completar perfil
    if (!response.success && response.error && response.error.includes('no está registrado como acudiente')) {
      console.log('🔄 Usuario no es acudiente, completando perfil...')
      response = await authService.completarPerfilAcudiente(datos)
    }

    if (response.success) {
      await Swal.fire({
        icon: 'success',
        title: 'Deportista asociado',
        text: 'La asociación se realizó correctamente.',
        timer: 1500,
        showConfirmButton: false
      })
      cerrarModalAcudir()
      // Recargar la lista de acudidos
      await cargarAcudidos()
      // Recargar el perfil del usuario
      await authStore.loadUserProfile()
    } else {
      await Swal.fire({
        icon: 'error',
        title: 'No se pudo asociar',
        text: response.error || 'Error desconocido.'
      })
    }
  } catch (error) {
    console.error('❌ Error al asociar deportista:', error)
    await Swal.fire({
      icon: 'error',
      title: 'Error de conexión',
      text: error.message || 'No pudimos completar la asociación.'
    })
  } finally {
    asociando.value = false
  }
}
</script>


