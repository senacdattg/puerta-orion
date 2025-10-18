<template>
  <form class="formulario-datos" @submit.prevent="manejarSubmit">
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
        placeholder="Primer nombre *"
        required
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="limpiarMensajes"
        />
        <input
        v-model="form.nombre2"
        type="text"
        placeholder="Segundo nombre"
        :readonly="modo === 'ver'"
        :disabled="cargando"
        />
      </div>

      <div class="fila-texto">
        <input
        v-model="form.apellido1"
        type="text"
        placeholder="Primer apellido *"
        required
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="limpiarMensajes"
        />
        <input
        v-model="form.apellido2"
        type="text"
        placeholder="Segundo apellido"
        :readonly="modo === 'ver'"
        :disabled="cargando"
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
        placeholder="Número de documento *"
        required
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="limpiarMensajes"
        />
      </div>

      <hr class="form-divider" />

      <!-- Correo, teléfono y dirección -->
      <div class="fila-texto">
        <input
        type="email"
        v-model="form.correo"
        placeholder="Correo electrónico *"
        required
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="limpiarMensajes"
        />
        <input
        type="tel"
        v-model="form.telefono"
        placeholder="Número telefónico *"
        required
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="limpiarMensajes"
        />
      </div>

      <div class="fila-texto">
        <input
        type="text"
        v-model="form.direccion"
        placeholder="Dirección *"
        required
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="limpiarMensajes"
        />
      </div>

      <hr class="form-divider" />

      <!-- Usuario y contraseña -->
      <div class="fila-texto">
        <input
        type="text"
        v-model="form.usuario"
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
        placeholder="Contraseña *"
        required
        :readonly="modo === 'ver'"
        :disabled="cargando"
        @input="limpiarMensajes"
        />
        <input
        type="password"
        v-model="form.confirmarContrasena"
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
          v-if="modo === 'registrar'"
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
import { useAuthStore } from "@/stores/auth"
import catalogosService from "@/services/catalogosService"

const router = useRouter()
const authStore = useAuthStore()

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

// Catálogos
const tiposDocumento = ref([])
const sexos = ref([])

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
      return 'Registrarse'
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

  // Validar teléfono (solo números)
  if (!/^\d+$/.test(form.value.telefono)) {
    mensajeError.value = 'El teléfono debe contener solo números'
    return false
  }

  // Validar documento (solo números)
  if (!/^\d+$/.test(form.value.numeroDocumento)) {
    mensajeError.value = 'El número de documento debe contener solo números'
    return false
  }

  return true
}

// Manejar envío del formulario
async function manejarSubmit() {
  limpiarMensajes()

  if (!validarFormulario()) {
    return
  }

  if (props.modo === 'registrar') {
    await registrarUsuario()
  } else {
    emit('submit', form.value)
  }
}

// Registrar usuario
async function registrarUsuario() {
  cargando.value = true

  try {
    // Preparar datos para el backend
    const datosPersona = {
      primer_nombre: form.value.nombre1,
      segundo_nombre: form.value.nombre2 || null,
      primer_apellido: form.value.apellido1,
      segundo_apellido: form.value.apellido2 || null,
      documento: form.value.numeroDocumento,
      correo_electronico: form.value.correo,
      direccion: form.value.direccion,
      telefono: form.value.telefono,
      id_tipo_documento: parseInt(form.value.idTipoDocumento),
      id_sexo: parseInt(form.value.idSexo)
    }

    const datosUsuario = {
      usuario: form.value.usuario,
      password: form.value.contrasena
    }

    // Registrar usando el store
    const datosRegistro = {
      persona: datosPersona,
      usuario: datosUsuario
    }
    const resultado = await authStore.register(datosRegistro)

    if (resultado.success) {
      mensajeExito.value = '¡Registro exitoso! Redirigiendo al login...'

      // Limpiar formulario
      limpiarFormulario()

      // Redirigir al login después de 2 segundos
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      mensajeError.value = resultado.error || 'Error al registrar usuario'
    }
  } catch (error) {
    console.error('Error en registro:', error)
    mensajeError.value = 'Error al procesar el registro'
  } finally {
    cargando.value = false
  }
}

// Limpiar mensajes
function limpiarMensajes() {
  mensajeError.value = ''
  mensajeExito.value = ''
}

// Limpiar formulario
function limpiarFormulario() {
  form.value = {
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
  }
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
    Object.keys(props.datos).forEach(key => {
      if (form.value.hasOwnProperty(key)) {
        form.value[key] = props.datos[key]
      }
    })
  }
})

// Observar cambios en los datos
watch(() => props.datos, (nuevosDatos) => {
  if (nuevosDatos && Object.keys(nuevosDatos).length > 0) {
    Object.keys(nuevosDatos).forEach(key => {
      if (form.value.hasOwnProperty(key)) {
        form.value[key] = nuevosDatos[key]
      }
    })
  }
}, { deep: true })
</script>

<style scoped>
.mensaje-error {
  background-color: #fee;
  border: 1px solid #fcc;
  color: #c33;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  animation: slideDown 0.3s ease-out;
}

.mensaje-exito {
  background-color: #efe;
  border: 1px solid #cfc;
  color: #3c3;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  animation: slideDown 0.3s ease-out;
}

.mensaje-info {
  background-color: #eef;
  border: 1px solid #ccf;
  color: #33c;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.boton-formulario:disabled,
.boton-secundario:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

input:disabled,
select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.boton-secundario {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.boton-secundario:hover:not(:disabled) {
  background-color: #5a6268;
}
</style>
