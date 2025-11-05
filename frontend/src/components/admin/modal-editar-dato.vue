<template>
  <div v-if="mostrar" class="modal-overlay" @click="cerrar">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">
          <i class="fas fa-edit"></i>
          Editar {{ nombreTipo }}
        </h2>
        <button class="btn-cerrar" @click="cerrar">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <form class="formulario-edicion" @submit.prevent="guardar">
          <component 
            :is="componenteFormulario" 
            v-model="formData"
          />

          <div class="botones-formulario">
            <button type="button" class="btn btn-secundario" @click="cerrar">
              Cancelar
            </button>
            <button type="submit" class="btn btn-primary" :disabled="guardando">
              <i v-if="guardando" class="fas fa-spinner fa-spin"></i>
              {{ guardando ? 'Guardando...' : 'Guardar Cambios' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { API_CONFIG } from '@/config/environment'
import TipoDocumento from '../datos-dinamicos/tipo-documento.vue'
import Sexo from '../datos-dinamicos/sexo.vue'
import Ciudad from '../datos-dinamicos/ciudad.vue'
import Eps from '../datos-dinamicos/eps.vue'
import MetodoPago from '../datos-dinamicos/metodo-pago.vue'
import TipoEvento from '../datos-dinamicos/tipo-evento.vue'

const props = defineProps({
  mostrar: { type: Boolean, default: false },
  tema: { type: String, default: '' },
  dato: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['cerrar', 'guardado'])

const guardando = ref(false)
const formData = ref({})

// Mapeo de temas a componentes
const componentes = {
  'tipo-documento': TipoDocumento,
  'sexo': Sexo,
  'ciudad-residencia': Ciudad,
  'eps': Eps,
  'metodo-pago': MetodoPago,
  'tipo-evento': TipoEvento
}

// Mapeo de temas a nombres
const nombresTipo = {
  'tipo-documento': 'Tipo de Documento',
  'sexo': 'Sexo',
  'ciudad-residencia': 'Ciudad',
  'eps': 'EPS',
  'metodo-pago': 'Método de Pago',
  'tipo-evento': 'Tipo de Evento'
}

// Mapeo de campos según el tipo
const camposNombre = {
  'tipo-documento': 'nombre_documento',
  'sexo': 'nombre',
  'ciudad-residencia': 'nombre_ciudad',
  'eps': 'nombre_eps',
  'metodo-pago': 'nombre_metodo',
  'tipo-evento': 'nombre'
}

const componenteFormulario = computed(() => {
  if (!props.tema) return null
  return componentes[props.tema] || null
})

const nombreTipo = computed(() => {
  return nombresTipo[props.tema] || 'Dato'
})

// Inicializar formData cuando cambia el dato
watch(() => props.dato, (nuevoDato) => {
  if (!nuevoDato || Object.keys(nuevoDato).length === 0) {
    formData.value = {}
    return
  }

  const campoNombre = camposNombre[props.tema]
  
  // Construir el objeto formData según el tipo
  formData.value = {
    nombre: nuevoDato[campoNombre] || nuevoDato.nombre || ''
  }

  // Agregar campos adicionales según el tipo
  if (props.tema === 'eps') {
    formData.value.codigo = nuevoDato.codigo_eps || ''
    formData.value.estado = nuevoDato.estado !== undefined ? nuevoDato.estado : true
  } else if (props.tema === 'metodo-pago') {
    formData.value.estado = nuevoDato.estado !== undefined ? nuevoDato.estado : true
  } else if (props.tema === 'tipo-evento') {
    formData.value.descripcion = nuevoDato.descripcion || ''
  }
}, { immediate: true, deep: true })

function cerrar() {
  formData.value = {}
  emit('cerrar')
}

async function guardar() {
  guardando.value = true

  try {
    const id = obtenerId(props.dato)
    
    if (!id) {
      alert('❌ Error: No se pudo obtener el ID del registro')
      guardando.value = false
      return
    }
    
    const campoNombre = camposNombre[props.tema]
    
    // Preparar datos según el tipo
    const datos = {}
    datos[campoNombre] = formData.value.nombre?.trim()

    if (!datos[campoNombre]) {
      alert('❌ El nombre es requerido')
      guardando.value = false
      return
    }

    // Campos adicionales según el tipo
    if (props.tema === 'eps') {
      if (formData.value.codigo) {
        datos.codigo_eps = formData.value.codigo.trim()
      }
      if (formData.value.estado !== undefined) {
        datos.estado = formData.value.estado
      }
    } else if (props.tema === 'metodo-pago') {
      if (formData.value.estado !== undefined) {
        datos.estado = formData.value.estado
      }
    } else if (props.tema === 'tipo-evento') {
      if (formData.value.descripcion) {
        datos.descripcion = formData.value.descripcion.trim()
      }
    }

    const base = API_CONFIG.baseURL || ''
    const response = await fetch(`${base}/api/dynamic-data/${props.tema}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(datos)
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
      alert('✅ Registro actualizado exitosamente')
      emit('guardado', result.data)
      cerrar()
    } else {
      alert(`❌ Error: ${result.error || 'No se pudo actualizar el registro'}`)
    }
  } catch (error) {
    console.error('Error al guardar:', error)
    alert(`❌ Error: ${error.message || 'Error de conexión'}`)
  } finally {
    guardando.value = false
  }
}

function obtenerId(dato) {
  if (!dato) return null
  
  // Obtener el ID según el tipo de dato (según los nombres que devuelven los modelos en to_dict)
  if (props.tema === 'tipo-documento') return dato.id_documento || dato.id
  if (props.tema === 'sexo') return dato.id_sexo || dato.id
  if (props.tema === 'ciudad-residencia') return dato.id_ciudad || dato.id
  if (props.tema === 'eps') return dato.id_eps || dato.id
  if (props.tema === 'metodo-pago') return dato.id_metodo_pago || dato.id
  if (props.tema === 'tipo-evento') return dato.id_tipo_evento || dato.id
  
  return dato.id
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  background: linear-gradient(135deg, #0047ab 0%, #0d47a1 100%);
  color: white;
  padding: 25px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-cerrar {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-cerrar:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-body {
  padding: 30px;
  max-height: calc(90vh - 100px);
  overflow-y: auto;
}

.formulario-edicion {
  width: 100%;
}

.botones-formulario {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background-color: #0047ab;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #003d8f;
}

.btn-primary:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn-secundario {
  background-color: transparent;
  color: #6c757d;
  border: 2px solid #6c757d;
}

.btn-secundario:hover {
  background-color: #6c757d;
  color: white;
}

.fa-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>

