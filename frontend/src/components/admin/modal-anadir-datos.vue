<template>
  <div v-if="mostrar" class="modal-overlay modal-anadir-overlay" @click="cerrar">
    <div class="modal-content modal-anadir" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">
          <i class="fas fa-database"></i>
          Añadir Datos
        </h2>
        <button class="btn-cerrar" @click="cerrar">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- Paso 1: elegir entidad -->
      <div v-if="paso === 1" class="modal-body">
        <div class="seleccion-rol">
          <h3 class="paso-titulo">Selecciona el tipo de dato a gestionar</h3>
          <p class="paso-descripcion">Elige una categoría para crear o administrar datos base del sistema</p>

          <div class="roles-grid">
            <div
              v-for="item in items"
              :key="item.id"
              class="rol-option"
              :class="{ seleccionado: seleccionado?.id === item.id }"
              @click="seleccionar(item)"
            >
              <div class="rol-icono">
                <i :class="item.icono"></i>
              </div>
              <div class="rol-info">
                <h4 class="rol-nombre">{{ item.nombre }}</h4>
                <p class="rol-descripcion">{{ item.descripcion }}</p>
              </div>
              <div class="rol-check">
                <i v-if="seleccionado?.id === item.id" class="fas fa-check"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Paso 2: formulario simple para la entidad seleccionada -->
      <div v-else-if="paso === 2" class="modal-body">
        <button class="btn-volver" @click="volverPaso1">
          <i class="fas fa-arrow-left"></i>
          Volver
        </button>
        <form class="formulario-datos" @submit.prevent="enviar">
          <section class="seccion-formulario">
            <h3>Crear {{ seleccionado?.nombre }}</h3>

            <component
              :is="componenteFormulario"
              v-model="form"
            />

            <div class="botones-formulario" style="justify-content: center; gap: 10px;">
              <button type="submit" class="boton-formulario" style="width: 150px;">Guardar</button>
            </div>
          </section>
        </form>
      </div>

      <div class="modal-footer">
        <div v-if="paso === 1" class="footer-acciones">
          <button class="btn btn--outline" @click="cerrar">Cancelar</button>
          <button class="btn btn--primary" :disabled="!seleccionado" @click="paso = 2">Continuar <i class="fas fa-arrow-right"></i></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import TipoDocumento from '../datos-dinamicos/tipo-documento.vue'
import Sexo from '../datos-dinamicos/sexo.vue'
import Ciudad from '../datos-dinamicos/ciudad.vue'
import Eps from '../datos-dinamicos/eps.vue'
import MetodoPago from '../datos-dinamicos/metodo-pago.vue'
import TipoEvento from '../datos-dinamicos/tipo-evento.vue'
import Swal from 'sweetalert2'

const props = defineProps({
  mostrar: { type: Boolean, default: false },
  temaInicial: { type: String, default: '' }
})

const emit = defineEmits(['cerrar','guardar-dato'])

const items = ref([
  { id: 'tipo_documento', nombre: 'Tipos de Documento', icono: 'fas fa-id-card', descripcion: 'Gestiona los tipos de documento' },
  { id: 'sexo', nombre: 'Sexo', icono: 'fas fa-venus-mars', descripcion: 'Gestiona valores de sexo' },
  { id: 'ciudad', nombre: 'Ciudades', icono: 'fas fa-city', descripcion: 'Gestiona ciudades de residencia' },
  { id: 'eps', nombre: 'EPS', icono: 'fas fa-hospital', descripcion: 'Gestiona entidades de salud' },
  { id: 'metodo_pago', nombre: 'Métodos de Pago', icono: 'fas fa-money-check-alt', descripcion: 'Gestiona métodos de pago' },
  { id: 'tipo-evento', nombre: 'Tipo Evento', icono: 'fas fa-calendar-alt', descripcion: 'Gestiona tipos de eventos' }
])

const paso = ref(1)
const seleccionado = ref(null)
const form = ref({
  nombre: '',
  codigo: '',
  descripcion: '',
  estado: true
})

// Mapeo de IDs a componentes
const componentes = {
  'tipo_documento': TipoDocumento,
  'sexo': Sexo,
  'ciudad': Ciudad,
  'eps': Eps,
  'metodo_pago': MetodoPago,
  'tipo-evento': TipoEvento
}

// Componente del formulario según la selección
const componenteFormulario = computed(() => {
  if (!seleccionado.value) return null
  return componentes[seleccionado.value.id] || null
})

const REGEX_CODIGO_EPS = /^[A-Z0-9-]{2,20}$/
const NAME_MIN_LENGTH = 2

function validarFormulario() {
  const errores = []
  const nombre = form.value.nombre?.trim()

  if (!nombre || nombre.length < NAME_MIN_LENGTH) {
    errores.push('El nombre es obligatorio y debe tener al menos 2 caracteres')
  }

  if (seleccionado.value?.id === 'eps') {
    if (!form.value.codigo || !REGEX_CODIGO_EPS.test(form.value.codigo)) {
      errores.push('Debes ingresar un código de EPS válido (2 a 20 caracteres alfanuméricos, puede incluir guiones)')
    }

    if (form.value.estado !== true && form.value.estado !== false) {
      errores.push('Debes seleccionar un estado para la EPS')
    }
  }

  if (seleccionado.value?.id === 'metodo_pago') {
    if (form.value.estado !== true && form.value.estado !== false) {
      errores.push('Debes seleccionar un estado para el método de pago')
    }
  }

  if (seleccionado.value?.id === 'tipo-evento') {
    if (!form.value.descripcion || form.value.descripcion.trim().length === 0) {
      errores.push('La descripción es obligatoria para el tipo de evento')
    } else if (form.value.descripcion.length > 500) {
      errores.push('La descripción no puede exceder los 500 caracteres')
    }
  }

  return errores
}

function cerrar() {
  // Limpiar selección y resetear al cerrar
  seleccionado.value = null
  paso.value = 1
  form.value = {
    nombre: '',
    codigo: '',
    descripcion: '',
    estado: true
  }
  emit('cerrar')
}

// Limpiar selección cuando se abre el modal
watch(() => props.mostrar, (nuevoValor) => {
  if (nuevoValor) {
    // Si hay un tema inicial, seleccionarlo automáticamente
    if (props.temaInicial) {
      // Mapear temas del backend a IDs del frontend
      const temaMap = {
        'tipo-documento': 'tipo_documento',
        'ciudad-residencia': 'ciudad',
        'metodo-pago': 'metodo_pago',
        'tipo-evento': 'tipo-evento',
        'eps': 'eps',
        'sexo': 'sexo'
      }
      const idFrontend = temaMap[props.temaInicial] || props.temaInicial
      const item = items.value.find(i => i.id === idFrontend)
      if (item) {
        seleccionar(item)
        paso.value = 2
      } else {
        seleccionado.value = null
        paso.value = 1
      }
    } else {
      seleccionado.value = null
      paso.value = 1
    }
    form.value = {
      nombre: '',
      codigo: '',
      descripcion: '',
      estado: true
    }
  }
})

function seleccionar(item){
  seleccionado.value = item
  // Inicializar form según el tipo seleccionado
  form.value = {
    nombre: '',
    codigo: '',
    descripcion: '',
    estado: true
  }
}

function volverPaso1(){
  paso.value = 1
  form.value = {
    nombre: '',
    codigo: '',
    descripcion: '',
    estado: true
  }
}

async function enviar(){
  const errores = validarFormulario()
  if (errores.length > 0) {
    await Swal.fire({
      icon: 'error',
      title: 'Corrige los errores',
      html: errores.join('<br>')
    })
    return
  }

  emit('guardar-dato', { entidad: seleccionado.value.id, ...form.value })
  await Swal.fire({
    icon: 'success',
    title: 'Dato creado',
    timer: 1500,
    showConfirmButton: false
  })
  volverPaso1()
  cerrar()
}
</script>




