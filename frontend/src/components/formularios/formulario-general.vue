<template>
  <form class="formulario-datos" name="formulario-registro" @submit.prevent="manejarSubmit">
  <section class="seccion-formulario">
    <h3>{{  obtenerTitulo() }}</h3>

    <!-- Mensajes de feedback -->
    <div v-if="mensajeError" class="mensaje-error">
      <i class="fas fa-exclamation-circle"></i>
      {{ mensajeError }}
    </div>

    <div v-if="mensajeExito" class="mensaje-exito">
      <i class="fas fa-check-circle"></i>
      {{ mensajeExito }}
    </div>

    <!-- Cargando catálogos -->
    <div v-if="cargandoCatalogos" class="mensaje-info">
      <i class="fas fa-spinner fa-spin"></i>
      Cargando información...
    </div>

    <div v-else>
      <!-- Nombres -->
      <div class="fila-texto">
        <input
        v-model="form.nombre1"
        type="text"
        name="primer_nombre"
        autocomplete="given-name"
        placeholder="Primer nombre *"
        required
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="(event) => manejarEntradaNombre('nombre1', event)"
        />
        <input
        v-model="form.nombre2"
        type="text"
        name="segundo_nombre"
        autocomplete="additional-name"
        placeholder="Segundo nombre"
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="(event) => manejarEntradaNombre('nombre2', event, false)"
        />
      </div>

      <div class="fila-texto">
        <input
        v-model="form.apellido1"
        type="text"
        name="primer_apellido"
        autocomplete="family-name"
        placeholder="Primer apellido *"
        required
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="(event) => manejarEntradaNombre('apellido1', event)"
        />
        <input
        v-model="form.apellido2"
        type="text"
        name="segundo_apellido"
        autocomplete="additional-name"
        placeholder="Segundo apellido"
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="(event) => manejarEntradaNombre('apellido2', event, false)"
        />
      </div>

      <hr class="form-divider" />

      <!-- Género y Documento -->
      <div class="fila-texto">
        <select
        v-model="form.idSexo"
        required
        :disabled="modo === 'ver' || cargando"
        @change="limpiarMensajes"
        >
          <option value="" disabled hidden>Género *</option>
          <option v-for="sexo in sexos" :key="sexo.id" :value="sexo.id">
            {{ sexo.nombre }}
          </option>
        </select>

        <select
        v-model="form.idTipoDocumento"
        required
        :disabled="modo === 'ver' || cargando"
        @change="limpiarMensajes"
        >
          <option value="" disabled hidden>Tipo de documento *</option>
          <option v-for="tipo in tiposDocumento" :key="tipo.id" :value="tipo.id">
            {{ tipo.nombre }}
          </option>
        </select>
      </div>

      <div class="fila-texto">
        <input
        type="text"
        v-model="form.numeroDocumento"
        name="numero_documento"
        autocomplete="off"
        placeholder="Número de documento *"
        required
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="manejarDocumento"
        />
      </div>

      <hr class="form-divider" />

      <!-- Correo, teléfono y dirección -->
      <div class="fila-texto">
        <input
        type="email"
        v-model="form.correo"
        name="correo_electronico"
        autocomplete="email"
        placeholder="Correo electrónico *"
        required
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="limpiarMensajes"
        />
        <input
        type="text"
        v-model="form.telefono"
        name="telefono"
        autocomplete="tel"
        placeholder="Número telefónico"
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="manejarTelefono"
        />
      </div>

      <div class="fila-texto">
        <input
        type="text"
        v-model="form.direccion"
        name="direccion"
        autocomplete="address-line1"
        placeholder="Dirección"
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="(event) => manejarEntradaDireccion(event)"
        />
      </div>

      <hr class="form-divider" />

      <!-- Usuario y contraseña -->
      <div class="fila-texto">
        <input
        type="text"
        v-model="form.usuario"
        name="usuario"
        autocomplete="username"
        placeholder="Nombre de usuario *"
        required
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="limpiarMensajes"
        />
      </div>

      <div class="fila-texto">
        <input
        type="password"
        v-model="form.contrasena"
        name="contrasena"
        autocomplete="new-password"
        placeholder="Contraseña *"
        required
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="limpiarMensajes"
        />
        <input
        type="password"
        v-model="form.confirmarContrasena"
        name="confirmar_contrasena"
        autocomplete="new-password"
        placeholder="Confirmar contraseña *"
        required
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="limpiarMensajes"
        />
      </div>

      <hr class="form-divider" />

      <!-- Botones -->
      <div v-if="modo !== 'ver'" class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button
          type="submit"
          class="boton-formulario"
          style="width: 150px;"
          :disabled="cargando"
        >
          <span v-if="!cargando">{{ obtenerTextoBoton() }}</span>
          <span v-else>
            <i class="fas fa-spinner fa-spin"></i> Procesando...
          </span>
        </button>
        <button
          v-if="modo === 'actualizar'"
          type="button"
          class="boton-formulario"
          style="width: 150px;"
          @click="cancelar"
          :disabled="cargando"
        >
          Cancelar
        </button>
        <button
          v-if="modo === 'registrar' && mostrarBotonLogin"
          type="button"
          class="boton-secundario"
          style="width: 150px;"
          @click="volverLogin"
          :disabled="cargando"
        >
          Volver al login
        </button>
      </div>
    </div>
  </section>
  </form>
</template>
<script setup>
import { ref, onMounted, watch } from "vue"
import { useRouter } from "vue-router"
import catalogosService from "@/services/catalogosService"
import { sanitizarNombre, sanitizarDireccion } from "@/utils/sanitization"

const router = useRouter()

// Props del componente
const props = defineProps({
  modo: {
    type: String,
    required: true,
    validator: (value) => ['actualizar', 'registrar', 'ver'].includes(value)
  },
  datos: {
    type: Object,
    default: () => ({})
  },
  mostrarBotonLogin: {
    type: Boolean,
    default: true
  },
  textoBotonRegistrar: {
    type: String,
    default: 'Registrarse'
  }
})

// Emitir eventos al componente padre
const emit = defineEmits(['submit', 'cancel'])

// Estado del formulario
const form = ref({
  nombre1: "",
  nombre2: "",
  apellido1: "",
  apellido2: "",
  idTipoDocumento: "",
  numeroDocumento: "",
  idSexo: "",
  correo: "",
  telefono: "",
  direccion: "",
  usuario: "",
  contrasena: "",
  confirmarContrasena: ""
})

// Estado de la UI
const cargando = ref(false)
const cargandoCatalogos = ref(false)
const mensajeError = ref('')
const mensajeExito = ref('')

const REGEX_NOMBRE = /^[A-ZÁÉÍÓÚÜÑ ]+$/
const REGEX_CORREO = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i
const MAX_DOCUMENTO = 10
const MIN_DOCUMENTO = 6
const MAX_TELEFONO = 10

// Catálogos
const tiposDocumento = ref([])
const sexos = ref([])

// Use shared sanitization utilities

function manejarEntradaNombre(campo, event, obligatorio = true) {
  limpiarMensajes()
  const valor = event?.target?.value ?? form.value[campo]
  form.value[campo] = sanitizarNombre(valor, obligatorio)
}

function manejarDocumento(event) {
  limpiarMensajes()
  const digitos = (event?.target?.value ?? form.value.numeroDocumento ?? '')
    .replace(/\D/g, '').slice(0, MAX_DOCUMENTO) // NOSONAR: S7781 - replaceAll() no acepta regex
  form.value.numeroDocumento = digitos
}

function manejarTelefono(event) {
  limpiarMensajes()
  const digitos = (event?.target?.value ?? form.value.telefono ?? '')
    .replace(/\D/g, '').slice(0, MAX_TELEFONO) // NOSONAR: S7781 - replaceAll() no acepta regex
  form.value.telefono = digitos
}

function manejarEntradaDireccion(event) {
  limpiarMensajes()
  form.value.direccion = sanitizarDireccion(event?.target?.value ?? form.value.direccion ?? '')
}

function normalizarCamposTexto() {
  manejarEntradaNombre('nombre1', null)
  manejarEntradaNombre('nombre2', null, false)
  manejarEntradaNombre('apellido1', null)
  manejarEntradaNombre('apellido2', null, false)
  manejarDocumento(null)
  manejarTelefono(null)
  manejarEntradaDireccion(null)
  if (form.value.usuario) {
    form.value.usuario = form.value.usuario.trim()
  }
  if (form.value.correo) {
    form.value.correo = form.value.correo.trim().toLowerCase()
  }
}

// Función para obtener el título según el modo
function obtenerTitulo() {
  switch (props.modo) {
    case 'registrar':
      return 'Registro de Usuario'
    case 'actualizar':
      return 'Actualizar Perfil'
    case 'ver':
      return 'Información del Usuario'
    default:
      return 'Formulario'
  }
}

// Función para obtener el texto del botón según el modo
function obtenerTextoBoton() {
  switch (props.modo) {
    case 'registrar':
      return props.textoBotonRegistrar
    case 'actualizar':
      return 'Actualizar'
    default:
      return 'Enviar'
  }
}

// Cargar catálogos desde el backend
async function cargarCatalogos() {
  cargandoCatalogos.value = true

  try {
    const resultado = await catalogosService.cargarCatalogosFormulario()

    tiposDocumento.value = resultado.tiposDocumento || []
    sexos.value = resultado.sexos || []
  } catch (error) {
    console.error('Error al cargar catálogos:', error)
    mensajeError.value = 'Error al cargar información del sistema'
  } finally {
    cargandoCatalogos.value = false
  }
}

// Validar formulario
function validarFormulario() {
  // Validar contraseñas
  if (form.value.contrasena !== form.value.confirmarContrasena) {
    mensajeError.value = 'Las contraseñas no coinciden'
    return false
  }

  // Validar longitud de contraseña
  if (form.value.contrasena.length < 6) {
    mensajeError.value = 'La contraseña debe tener al menos 6 caracteres'
    return false
  }

  // Validar nombres obligatorios
  if (!REGEX_NOMBRE.test(form.value.nombre1)) {
    mensajeError.value = 'El primer nombre solo debe contener letras y espacios'
    return false
  }

  if (!REGEX_NOMBRE.test(form.value.apellido1)) {
    mensajeError.value = 'El primer apellido solo debe contener letras y espacios'
    return false
  }

  if (form.value.nombre2 && !REGEX_NOMBRE.test(form.value.nombre2)) {
    mensajeError.value = 'El segundo nombre solo debe contener letras y espacios'
    return false
  }

  if (form.value.apellido2 && !REGEX_NOMBRE.test(form.value.apellido2)) {
    mensajeError.value = 'El segundo apellido solo debe contener letras y espacios'
    return false
  }

  // Validar teléfono (solo números)
  if (form.value.telefono && !/^\d{10}$/.test(form.value.telefono)) {
    mensajeError.value = 'El teléfono debe contener exactamente 10 dígitos cuando se proporciona'
    return false
  }

  // Validar documento (solo números y longitud)
  if (!/^\d+$/.test(form.value.numeroDocumento)) {
    mensajeError.value = 'El número de documento debe contener solo dígitos'
    return false
  }

  if (form.value.numeroDocumento.length < MIN_DOCUMENTO || form.value.numeroDocumento.length > MAX_DOCUMENTO) {
    mensajeError.value = 'El número de documento debe tener entre 6 y 10 dígitos'
    return false
  }

  if (!REGEX_CORREO.test(form.value.correo)) {
    mensajeError.value = 'Ingrese un correo electrónico válido'
    return false
  }

  return true
}

// Manejar envío del formulario
async function manejarSubmit() {
  limpiarMensajes()

  normalizarCamposTexto()

  if (!validarFormulario()) {
    return
  }

  // Emitir evento submit para que el padre pueda mostrar confirmación
  emit('submit', form.value)
}

// Limpiar mensajes
function limpiarMensajes() {
  mensajeError.value = ''
  mensajeExito.value = ''
}

// Volver al login
function volverLogin() {
  router.push('/login')
}

// Cancelar
function cancelar() {
  emit('cancel')
}

// Cargar datos cuando se proporcionen
onMounted(async () => {
  // Cargar catálogos
  await cargarCatalogos()

  // Cargar datos si se proporcionan
  if (props.datos && Object.keys(props.datos).length > 0) {
    for (const key of Object.keys(props.datos)) {
      if (Object.hasOwn(form.value, key)) {
        form.value[key] = props.datos[key]
      }
    }
    normalizarCamposTexto()
  }
})

// Observar cambios en los datos
watch(() => props.datos, (nuevosDatos) => {
  if (nuevosDatos && Object.keys(nuevosDatos).length > 0) {
    for (const key of Object.keys(nuevosDatos)) {
      if (Object.hasOwn(form.value, key)) {
        form.value[key] = nuevosDatos[key]
      }
    }
    normalizarCamposTexto()
  }
}, { deep: true })
</script>

