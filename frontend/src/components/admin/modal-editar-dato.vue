<template>
  <div v-if="mostrar" class="modal-overlay modal-editar-overlay" @click="cerrar">
    <div class="modal-content modal-editar" @click.stop>
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
import Swal from 'sweetalert2'

const props = defineProps({
  mostrar: { type: Boolean, default: false },
  tema: { type: String, default: '' },
  dato: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['cerrar', 'guardado'])

const guardando = ref(false)
const formData = ref({})

const REGEX_CODIGO_EPS = /^[A-Z0-9-]{2,20}$/
const NAME_MIN_LENGTH = 2

function validarDatos() {
  const errores = []
  const nombre = formData.value.nombre?.trim()

  if (!nombre || nombre.length < NAME_MIN_LENGTH) {
    errores.push('El nombre es obligatorio y debe tener al menos 2 caracteres')
  }

  if (props.tema === 'eps') {
    if (!formData.value.codigo || !REGEX_CODIGO_EPS.test(formData.value.codigo)) {
      errores.push('El código de la EPS debe contener entre 2 y 20 caracteres alfanuméricos (puede incluir guiones)')
    }
    if (formData.value.estado !== true && formData.value.estado !== false) {
      errores.push('Debes seleccionar un estado para la EPS')
    }
  }

  if (props.tema === 'metodo-pago') {
    if (formData.value.estado !== true && formData.value.estado !== false) {
      errores.push('Debes seleccionar un estado para el método de pago')
    }
  }

  if (props.tema === 'tipo-evento') {
    if (!formData.value.descripcion || formData.value.descripcion.trim().length === 0) {
      errores.push('La descripción es obligatoria para el tipo de evento')
    } else if (formData.value.descripcion.length > 500) {
      errores.push('La descripción no puede exceder los 500 caracteres')
    }
  }

  return errores
}

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
      await Swal.fire({
        icon: 'error',
        title: 'No se pudo obtener el ID del registro'
      })
      guardando.value = false
      return
    }

    const errores = validarDatos()
    if (errores.length > 0) {
      await Swal.fire({
        icon: 'error',
        title: 'Corrige los errores',
        html: errores.join('<br>')
      })
      guardando.value = false
      return
    }

    const campoNombre = camposNombre[props.tema]

    // Preparar datos según el tipo
    const datos = {}
    datos[campoNombre] = formData.value.nombre?.trim()

    // Campos adicionales según el tipo
    if (props.tema === 'eps') {
      datos.codigo_eps = formData.value.codigo.trim()
      datos.estado = formData.value.estado
    } else if (props.tema === 'metodo-pago') {
      datos.estado = formData.value.estado
    } else if (props.tema === 'tipo-evento') {
      datos.descripcion = formData.value.descripcion.trim()
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
      await Swal.fire({
        icon: 'success',
        title: 'Registro actualizado',
        timer: 1500,
        showConfirmButton: false
      })
      emit('guardado', result.data)
      cerrar()
    } else {
      await Swal.fire({
        icon: 'error',
        title: 'Error al actualizar',
        text: result.error || 'No se pudo actualizar el registro'
      })
    }
  } catch (error) {
    console.error('Error al guardar:', error)
    await Swal.fire({
      icon: 'error',
      title: 'Error al guardar',
      text: error.message || 'Error de conexión'
    })
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


