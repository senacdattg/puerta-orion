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
        <form class="formulario-edicion formulario-datos" @submit.prevent="guardar">
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
import { ref, watch, computed, nextTick } from 'vue'
import { API_CONFIG } from '@/config/environment'
import TipoDocumento from '../datos-dinamicos/tipo-documento.vue'
import Sexo from '../datos-dinamicos/sexo.vue'
import Ciudad from '../datos-dinamicos/ciudad.vue'
import Eps from '../datos-dinamicos/eps.vue'
import MetodoPago from '../datos-dinamicos/metodo-pago.vue'
import TipoEvento from '../datos-dinamicos/tipo-evento.vue'
import Swal from 'sweetalert2'
import { useModalScrollLock } from '@/composables/useModalScrollLock'
import { extraerMensajeError } from '@/utils/error-handling'

const props = defineProps({
  mostrar: { type: Boolean, default: false },
  tema: { type: String, default: '' },
  dato: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['cerrar', 'guardado'])

// Bloquear scroll del body cuando el modal está abierto
useModalScrollLock(computed(() => props.mostrar))

const guardando = ref(false)
const formData = ref({})
const formDataInicial = ref({}) // Guardar datos iniciales para comparar cambios

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
  if (!props.tema) {
    console.log('modal-editar-dato: No hay tema')
    return null
  }
  const componente = componentes[props.tema] || null
  console.log('modal-editar-dato: tema =', props.tema, 'componente =', componente ? componente.name : 'null')
  return componente
})

const nombreTipo = computed(() => {
  return nombresTipo[props.tema] || 'Dato'
})

// Función para normalizar valores igual que al guardar
function normalizarValorParaComparacion(valor) {
  if (valor === null || valor === undefined) {
    return ''
  }
  if (typeof valor === 'string') {
    return valor.trim()
  }
  return valor
}

// Inicializar formData cuando cambia el dato
watch(() => props.dato, async (nuevoDato) => {
  if (!nuevoDato || Object.keys(nuevoDato).length === 0) {
    formData.value = {}
    formDataInicial.value = {}
    return
  }

  const campoNombre = camposNombre[props.tema]

  // Construir el objeto formData según el tipo
  // Los valores se normalizarán automáticamente por el componente hijo (eps.vue, etc.)
  const datosIniciales = {
    nombre: nuevoDato[campoNombre] || nuevoDato.nombre || ''
  }

  // Agregar campos adicionales según el tipo
  if (props.tema === 'eps') {
    datosIniciales.codigo = nuevoDato.codigo_eps || ''
    datosIniciales.estado = nuevoDato.estado === undefined ? true : Boolean(nuevoDato.estado)
  } else if (props.tema === 'metodo-pago') {
    datosIniciales.estado = nuevoDato.estado === undefined ? true : Boolean(nuevoDato.estado)
  } else if (props.tema === 'tipo-evento') {
    datosIniciales.descripcion = nuevoDato.descripcion || ''
  }

  formData.value = { ...datosIniciales }

  // Esperar a que el componente hijo normalice los valores antes de guardar los iniciales
  // Usar nextTick para asegurar que el componente hijo haya procesado los valores
  await nextTick()
  // Esperar un momento adicional para que la normalización del componente hijo se complete
  setTimeout(() => {
    // Guardar los valores normalizados que vienen del componente hijo
    formDataInicial.value = structuredClone(formData.value)
  }, 150)
}, { immediate: true, deep: true })

function verificarCambios() {
  if (!formDataInicial.value || Object.keys(formDataInicial.value).length === 0) {
    return false
  }

  // Normalizar y comparar nombre
  const nombreInicial = normalizarValorParaComparacion(formDataInicial.value.nombre)
  const nombreActual = normalizarValorParaComparacion(formData.value.nombre)
  if (nombreInicial !== nombreActual) {
    return true
  }

  // Comparar campos adicionales según el tipo (normalizados igual que al guardar)
  if (props.tema === 'eps') {
    const codigoInicial = normalizarValorParaComparacion(formDataInicial.value.codigo)
    const codigoActual = normalizarValorParaComparacion(formData.value.codigo)

    // Comparar código normalizado
    if (codigoInicial !== codigoActual) {
      return true
    }

    // Comparar estado (convertir a boolean para comparación estricta)
    const estadoInicial = Boolean(formDataInicial.value.estado)
    const estadoActual = Boolean(formData.value.estado)
    if (estadoInicial !== estadoActual) {
      return true
    }
  } else if (props.tema === 'metodo-pago') {
    const estadoInicial = Boolean(formDataInicial.value.estado)
    const estadoActual = Boolean(formData.value.estado)
    if (estadoInicial !== estadoActual) {
      return true
    }
  } else if (props.tema === 'tipo-evento') {
    const descripcionInicial = normalizarValorParaComparacion(formDataInicial.value.descripcion)
    const descripcionActual = normalizarValorParaComparacion(formData.value.descripcion)
    if (descripcionInicial !== descripcionActual) {
      return true
    }
  }

  return false
}

async function cerrar() {
  // Verificar si hay cambios sin guardar
  const tieneCambios = verificarCambios()

  if (tieneCambios) {
    const result = await Swal.fire({
      icon: 'question',
      title: '¿Cerrar edición?',
      text: '¿Estás seguro de que deseas cerrar? Los cambios no guardados se perderán.',
      showCancelButton: true,
      confirmButtonText: 'Sí, cerrar',
      cancelButtonText: 'Continuar',
      confirmButtonColor: '#dc3545',
      cancelButtonColor: '#6c757d'
    })

    if (!result.isConfirmed) {
      return
    }
  }

  formData.value = {}
  formDataInicial.value = {}
  emit('cerrar')
}

// Función para sanitizar datos igual que en crear
function prepararDatosPorEntidad() {
  const nombre = formData.value.nombre?.trim() || ''

  const mapeoCampos = {
    'tipo-documento': { nombre_documento: nombre },
    'sexo': { nombre: nombre },
    'ciudad-residencia': { nombre_ciudad: nombre }
  }

  if (mapeoCampos[props.tema]) {
    return mapeoCampos[props.tema]
  }

  if (props.tema === 'metodo-pago') {
    return {
      nombre_metodo: nombre,
      estado: formData.value.estado === undefined ? true : formData.value.estado
    }
  }

  if (props.tema === 'eps') {
    const datos = { nombre_eps: nombre }
    if (formData.value.codigo) {
      datos.codigo_eps = formData.value.codigo.trim()
    }
    datos.estado = formData.value.estado ?? true
    return datos
  }

  if (props.tema === 'tipo-evento') {
    const datos = { nombre: nombre }
    if (formData.value.descripcion) {
      datos.descripcion = formData.value.descripcion.trim()
    }
    return datos
  }

  return { nombre: nombre }
}

async function guardar() {
  // Verificar si hay cambios antes de continuar
  const tieneCambios = verificarCambios()

  if (!tieneCambios) {
    await Swal.fire({
      icon: 'info',
      title: 'Sin cambios',
      text: 'No se han realizado modificaciones. No hay nada que guardar.',
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#004AAD'
    })
    return
  }

  const errores = validarDatos()
  if (errores.length > 0) {
    await Swal.fire({
      icon: 'error',
      title: 'Corrige los errores',
      html: `<p><strong>Por favor corrige los siguientes errores:</strong></p><p>${errores.join('<br>')}</p>`,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    })
    return
  }

  const id = obtenerId(props.dato)
  if (!id) {
    await Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No se pudo obtener el ID del registro',
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    })
    return
  }

  // Confirmar antes de guardar
  const nombreEntidad = nombreTipo.value
  const nombreDato = formData.value.nombre?.trim() || 'dato'
  const confirmacion = await Swal.fire({
    icon: 'question',
    title: '¿Guardar cambios?',
    text: `¿Estás seguro de que deseas guardar los cambios en el ${nombreEntidad.toLowerCase()} "${nombreDato}"?`,
    showCancelButton: true,
    confirmButtonText: 'Sí, guardar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#004AAD',
    cancelButtonColor: '#6c757d'
  })

  if (!confirmacion.isConfirmed) {
    return
  }

  // Mostrar loading mientras se procesa
  Swal.fire({
    title: 'Guardando cambios...',
    text: 'Por favor espera mientras procesamos tu solicitud.',
    allowOutsideClick: false,
    allowEscapeKey: false,
    didOpen: () => {
      Swal.showLoading()
    }
  })

  try {
    guardando.value = true

    const datos = prepararDatosPorEntidad()

    const base = API_CONFIG.baseURL || ''
    const response = await fetch(`${base}/api/dynamic-data/${props.tema}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(datos)
    })

    // Cerrar el loading
    Swal.close()

    if (!response.ok) {
      // Intentar obtener el mensaje de error del JSON
      let errorMessage = `Error ${response.status}: ${response.statusText}`
      try {
        const errorData = await response.json()
        errorMessage = errorData.error || errorMessage
      } catch {
        // Si no es JSON, usar el mensaje por defecto
      }

      const mensajeError = extraerMensajeErrorDato(errorMessage)
      await Swal.fire({
        icon: 'error',
        title: 'Error al actualizar',
        html: `<p><strong>No se pudieron guardar los cambios.</strong></p><p>${mensajeError}</p>`,
        confirmButtonText: 'Entendido',
        confirmButtonColor: '#dc3545'
      })
      return
    }

    const result = await response.json()

    if (result.success) {
      // Actualizar datos iniciales con los nuevos datos guardados
      formDataInicial.value = structuredClone(formData.value)

      // Éxito: mostrar notificación de confirmación
      await Swal.fire({
        icon: 'success',
        title: '¡Dato actualizado exitosamente!',
        text: `El ${nombreEntidad.toLowerCase()} "${nombreDato}" ha sido actualizado correctamente en el sistema.`,
        confirmButtonText: 'Aceptar',
        confirmButtonColor: '#004AAD'
      })
      emit('guardado', result.data)
      cerrar()
    } else {
      const mensajeError = extraerMensajeErrorDato(result.error)
      await Swal.fire({
        icon: 'error',
        title: 'Error al actualizar',
        html: `<p><strong>No se pudo actualizar el registro.</strong></p><p>${mensajeError}</p>`,
        confirmButtonText: 'Entendido',
        confirmButtonColor: '#dc3545'
      })
    }
  } catch (error) {
    // Cerrar el loading si aún está abierto
    Swal.close()

    console.error('Error al guardar:', error)
    const mensajeError = extraerMensajeErrorDato(error)

    await Swal.fire({
      icon: 'error',
      title: 'Error al guardar',
      html: `<p><strong>Ocurrió un error inesperado.</strong></p><p>${mensajeError}</p>`,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    })
  } finally {
    guardando.value = false
  }
}

// Alias for consistency with component naming
const extraerMensajeErrorDato = extraerMensajeError

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


