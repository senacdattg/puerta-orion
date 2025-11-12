<template>
  <div class="tabla-datos-container">
    <div class="tabla-header">
      <div class="header-controls">
        <select v-model="temaSeleccionado" @change="cargarDatos" class="select-tema">
          <option value="">Selecciona un tipo de dato</option>
          <option v-for="item in itemsDisponibles" :key="item.id" :value="item.id">
            {{ item.nombre }}
          </option>
        </select>
        <button class="btn btn-refresh" @click="cargarDatos" :disabled="cargando">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': cargando }"></i>
          Actualizar
        </button>
      </div>
    </div>

    <div v-if="!temaSeleccionado" class="empty-state">
      <div class="empty-icon">
        <i class="fas fa-database"></i>
      </div>
      <p>Selecciona un tipo de dato para comenzar</p>
    </div>

    <div v-else-if="cargando" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando datos...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="cargarDatos">Reintentar</button>
    </div>

    <div v-else-if="datos.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="fas fa-inbox"></i>
      </div>
      <p>No hay registros para este tipo de dato</p>
      <button class="btn btn-primary" @click="$emit('crear-nuevo', temaSeleccionado)">
        <i class="fas fa-plus"></i>
        Crear nuevo
      </button>
    </div>

    <table v-else class="tabla-datos">
      <caption class="sr-only">Tabla de datos dinámicos mostrando información de {{ temaSeleccionado }}</caption>
      <thead>
        <tr>
          <th>ID</th>
          <th>Nombre</th>
          <th v-if="temaSeleccionado === 'eps'">Código</th>
          <th v-if="tieneEstado">Estado</th>
          <th v-if="temaSeleccionado === 'tipo-evento'">Descripción</th>
          <th class="acciones-col">Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="dato in datos" :key="obtenerId(dato)" :class="{ 'inactivo': esInactivo(dato) }">
          <td>{{ obtenerId(dato) }}</td>
          <td>{{ obtenerNombre(dato) }}</td>
          <td v-if="temaSeleccionado === 'eps'">{{ dato.codigo_eps || '-' }}</td>
          <td v-if="tieneEstado">
            <span :class="['badge-estado', dato.estado ? 'activo' : 'inactivo']">
              {{ dato.estado ? 'Activo' : 'Inactivo' }}
            </span>
          </td>
          <td v-if="temaSeleccionado === 'tipo-evento'" class="descripcion-col">
            {{ dato.descripcion || '-' }}
          </td>
          <td class="acciones-col">
            <div class="acciones-buttons">
              <button
                class="btn-icon btn-edit"
                @click="editarDato(dato)"
                title="Editar"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button
                class="btn-icon btn-delete"
                @click="confirmarEliminar(dato)"
                title="Eliminar"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { API_CONFIG } from '@/config/environment'
import Swal from 'sweetalert2'

const props = defineProps({
  recargar: { type: Boolean, default: false }
})

const emit = defineEmits(['editar-dato', 'crear-nuevo', 'dato-eliminado'])

// Watch para recargar cuando cambie la prop recargar
watch(() => props.recargar, (nuevoValor) => {
  if (nuevoValor && temaSeleccionado.value) {
    cargarDatos()
  }
})

const itemsDisponibles = [
  { id: 'tipo-documento', nombre: 'Tipos de Documento' },
  { id: 'sexo', nombre: 'Sexo' },
  { id: 'ciudad-residencia', nombre: 'Ciudades' },
  { id: 'eps', nombre: 'EPS' },
  { id: 'metodo-pago', nombre: 'Métodos de Pago' },
  { id: 'tipo-evento', nombre: 'Tipos de Evento' }
]

const temaSeleccionado = ref('')
const datos = ref([])
const cargando = ref(false)
const error = ref(null)

// Mapeo de campos según el tipo de dato
const camposNombre = {
  'tipo-documento': 'nombre_documento',
  'sexo': 'nombre',
  'ciudad-residencia': 'nombre_ciudad',
  'eps': 'nombre_eps',
  'metodo-pago': 'nombre_metodo',
  'tipo-evento': 'nombre'
}

const tieneEstado = computed(() => {
  return ['eps', 'metodo-pago'].includes(temaSeleccionado.value)
})

function obtenerId(dato) {
  // Obtener el ID según el tipo de dato (según los nombres que devuelven los modelos en to_dict)
  if (temaSeleccionado.value === 'tipo-documento') return dato.id_documento || dato.id
  if (temaSeleccionado.value === 'sexo') return dato.id_sexo || dato.id
  if (temaSeleccionado.value === 'ciudad-residencia') return dato.id_ciudad || dato.id
  if (temaSeleccionado.value === 'eps') return dato.id_eps || dato.id
  if (temaSeleccionado.value === 'metodo-pago') return dato.id_metodo_pago || dato.id
  if (temaSeleccionado.value === 'tipo-evento') return dato.id_tipo_evento || dato.id
  return dato.id
}

function obtenerNombre(dato) {
  const campo = camposNombre[temaSeleccionado.value]
  return dato[campo] || dato.nombre || '-'
}

function esInactivo(dato) {
  return tieneEstado.value && dato.estado === false
}

async function cargarDatos() {
  if (!temaSeleccionado.value) {
    datos.value = []
    return
  }

  cargando.value = true
  error.value = null

  try {
    const base = API_CONFIG.baseURL || ''
    const response = await fetch(`${base}/api/dynamic-data/${temaSeleccionado.value}`, {
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`)
    }

    const result = await response.json()

    if (result.success) {
      datos.value = result.data || []
    } else {
      throw new Error(result.error || 'Error al cargar los datos')
    }
  } catch (err) {
    error.value = err.message
    datos.value = []
    console.error('Error cargando datos:', err)
  } finally {
    cargando.value = false
  }
}

function editarDato(dato) {
  emit('editar-dato', {
    tema: temaSeleccionado.value,
    dato: dato
  })
}

async function confirmarEliminar(dato) {
  const nombre = obtenerNombre(dato)
  const confirmacion = await Swal.fire({
    icon: 'question',
    title: `¿Eliminar "${nombre}"?`,
    text: `Esta acción ${tieneEstado.value ? 'desactivará' : 'eliminará'} el registro.`,
    showCancelButton: true,
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar'
  })

  if (!confirmacion.isConfirmed) return

  await eliminarDato(dato)
}

async function eliminarDato(dato) {
  const id = obtenerId(dato)

  if (!id) {
    await Swal.fire({
      icon: 'error',
      title: 'No se pudo obtener el ID del registro'
    })
    return
  }

  try {
    const base = API_CONFIG.baseURL || ''
    const response = await fetch(`${base}/api/dynamic-data/${temaSeleccionado.value}/${id}`, {
      method: 'DELETE',
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    if (!response.ok) {
      // Intentar obtener el mensaje de error del JSON
      let errorMessage = `Error ${response.status}: ${response.statusText}`
      try {
        const errorData = await response.json()
        errorMessage = errorData.error || errorMessage
      } catch {
        // Si no es JSON, usar el mensaje por defecto
      }
      throw new Error(errorMessage)
    }

    const result = await response.json()

    if (result.success) {
      await Swal.fire({
        icon: 'success',
        title: 'Registro eliminado',
        text: 'El registro se eliminó correctamente.',
        timer: 1500,
        showConfirmButton: false
      })
      emit('dato-eliminado')
      await cargarDatos()
    } else {
      throw new Error(result.error || 'Error al eliminar')
    }
  } catch (err) {
    await Swal.fire({
      icon: 'error',
      title: 'No se pudo eliminar',
      text: err.message || 'Ocurrió un error al eliminar el registro.'
    })
    console.error('Error eliminando dato:', err)
  }
}

// Cargar datos cuando cambia el tema seleccionado
onMounted(() => {
  // No cargar datos automáticamente, esperar a que el usuario seleccione un tema
})
</script>

<style scoped>
.tabla-datos-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tabla-header {
  margin-bottom: 20px;
}

.header-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.select-tema {
  flex: 1;
  max-width: 300px;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

.btn-refresh {
  padding: 10px 15px;
  background: #0047ab;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.3s;
}

.btn-refresh:hover:not(:disabled) {
  background: #003d8f;
}

.btn-refresh:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.fa-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-state, .loading-state, .error-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-icon {
  font-size: 48px;
  color: #ccc;
  margin-bottom: 15px;
}

.loading-state .spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #0047ab;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

.error-state {
  color: #dc3545;
}

.error-state i {
  font-size: 48px;
  margin-bottom: 15px;
}

.tabla-datos {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.tabla-datos thead {
  background: #f8f9fa;
}

.tabla-datos th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #dee2e6;
}

.tabla-datos td {
  padding: 12px;
  border-bottom: 1px solid #e9ecef;
}

.tabla-datos tbody tr:hover {
  background: #f8f9fa;
}

.tabla-datos tbody tr.inactivo {
  opacity: 0.6;
  background: #f8f9fa;
}

.acciones-col {
  width: 120px;
  text-align: center;
}

.acciones-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-edit {
  background: #ffc107;
  color: white;
}

.btn-edit:hover {
  background: #e0a800;
}

.btn-delete {
  background: #dc3545;
  color: white;
}

.btn-delete:hover {
  background: #c82333;
}

.badge-estado {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge-estado.activo {
  background: #d4edda;
  color: #155724;
}

.badge-estado.inactivo {
  background: #f8d7da;
  color: #721c24;
}

.descripcion-col {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-primary {
  padding: 10px 20px;
  background: #0047ab;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: background 0.3s;
}

.btn-primary:hover {
  background: #003d8f;
}
</style>

