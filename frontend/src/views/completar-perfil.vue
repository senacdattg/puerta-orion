<template>
  <main class="completar-perfil-container">
    <Encabezado :sin-menu="false"/>

    <div class="completar-perfil-content">
      <!-- Paso 1: Selección de tipo de perfil -->
      <div v-if="paso === 1" class="seleccion-perfil">
        <div class="card-completar">
          <img src="@/assets/imgs/icono.png" alt="Icono" class="icono-completar" />
          <h2 class="titulo-completar">¡Completa tu Perfil!</h2>
          <p class="descripcion-completar">
            Para continuar, necesitamos saber si eres deportista o acudiente.
            Selecciona la opción que mejor te describa:
          </p>

          <!-- Mensajes de error y éxito -->
          <div v-if="mensajeError" class="mensaje-error">
            {{ mensajeError }}
          </div>
          <div v-if="mensajeExito" class="mensaje-exito">
            {{ mensajeExito }}
          </div>

          <div class="opciones-perfil">
            <button
              v-if="!yaEsDeportista"
              class="opcion-btn opcion-deportista"
              @click="seleccionarTipoPerfil('deportista')"
              :disabled="cargando"
            >
              <div class="opcion-icono">🏃</div>
              <h3>Soy Deportista</h3>
              <p>Participo en entrenamientos y competencias</p>
            </button>

            <button
              v-if="mostrarOpcionAcudiente"
              class="opcion-btn opcion-acudiente"
              @click="seleccionarTipoPerfil('acudiente')"
              :disabled="cargando"
            >
              <div class="opcion-icono">👨‍👩‍👧</div>
              <h3>Soy Acudiente</h3>
              <p>Acompaño y apoyo a un deportista</p>
            </button>

            <!-- Mensaje si es deportista menor de edad -->
            <div v-if="yaEsDeportista && !esMayorDeEdad && edadDeportista !== null" class="mensaje-info">
              <p>Debes ser mayor de edad (18 años) para registrarte como acudiente. Tu edad actual es {{ edadDeportista }} años.</p>
            </div>

            <div v-if="yaEsDeportista && yaEsAcudiente" class="mensaje-info">
              <p>Ya tienes los roles de Deportista y Acudiente registrados.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Paso 2: Formulario para deportista -->
      <div v-if="paso === 2 && tipoPerfilSeleccionado === 'deportista'" class="formulario-perfil">
        <div class="card-completar">
          <h2 class="titulo-completar">Datos de Deportista</h2>
          <p class="descripcion-completar">
            Completa tu información como deportista
          </p>

          <!-- Mensajes de error y éxito -->
          <div v-if="mensajeError" class="mensaje-error">
            {{ mensajeError }}
          </div>
          <div v-if="mensajeExito" class="mensaje-exito">
            {{ mensajeExito }}
          </div>

          <form @submit.prevent="completarPerfilDeportista" class="form-deportista">
            <div class="form-group">
              <label for="categoria">Categoría *</label>
              <select
                id="categoria"
                v-model="formDeportista.id_categoria"
                required
                :disabled="cargando"
              >
                <option value="">Seleccione una categoría</option>
                <option v-for="cat in categorias" :key="cat.id_categoria" :value="cat.id_categoria">
                  {{ cat.nombre_categoria }}
                </option>
              </select>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="peso">Peso (kg)</label>
                <input
                  type="number"
                  id="peso"
                  v-model="formDeportista.peso"
                  step="0.1"
                  :disabled="cargando"
                  placeholder="Ej: 70.5"
                />
              </div>

              <div class="form-group">
                <label for="altura">Altura (m)</label>
                <input
                  type="number"
                  id="altura"
                  v-model="formDeportista.altura"
                  step="0.01"
                  :disabled="cargando"
                  placeholder="Ej: 1.75"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="fecha_nacimiento">Año de Nacimiento</label>
              <input
                type="number"
                id="fecha_nacimiento"
                v-model="formDeportista.fecha_nacimiento"
                min="1900"
                :max="new Date().getFullYear()"
                :disabled="cargando"
                placeholder="Ej: 2000"
              />
            </div>

            <div class="form-group">
              <label for="tipo_sanguineo">Tipo de Sangre</label>
              <select
                id="tipo_sanguineo"
                v-model="formDeportista.id_tipo_sanguineo"
                :disabled="cargando"
              >
                <option value="">Seleccione tipo de sangre</option>
                <option v-for="tipo in tiposSanguineos" :key="tipo.id_tipo_sangre" :value="tipo.id_tipo_sangre">
                  {{ tipo.tipo_sangre }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="eps">EPS</label>
              <select
                id="eps"
                v-model="formDeportista.id_eps"
                :disabled="cargando"
              >
                <option value="">Seleccione EPS</option>
                <option v-for="eps in listaEps" :key="eps.id_eps" :value="eps.id_eps">
                  {{ eps.nombre_eps }}
                </option>
              </select>
            </div>

            <div class="form-actions">
              <button
                type="button"
                class="btn-secondary"
                @click="volverAtras"
                :disabled="cargando"
              >
                Volver
              </button>
              <button
                type="submit"
                class="btn-primary"
                :disabled="cargando"
              >
                <span v-if="cargando">Guardando...</span>
                <span v-else>Completar Registro</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Paso 2: Confirmación para acudiente -->
      <div v-if="paso === 2 && tipoPerfilSeleccionado === 'acudiente'" class="confirmacion-perfil">
        <div class="card-completar">
          <div class="opcion-icono-grande">👨‍👩‍👧</div>
          <h2 class="titulo-completar">Confirmar Registro como Acudiente</h2>
          <p class="descripcion-completar">
            ¿Estás seguro de que deseas registrarte como acudiente?
            Podrás acompañar y apoyar a un deportista.
          </p>

          <!-- Mensajes de error y éxito -->
          <div v-if="mensajeError" class="mensaje-error">
            {{ mensajeError }}
          </div>
          <div v-if="mensajeExito" class="mensaje-exito">
            {{ mensajeExito }}
          </div>

          <div class="form-actions">
            <button
              type="button"
              class="btn-secondary"
              @click="volverAtras"
              :disabled="cargando"
            >
              Volver
            </button>
            <button
              type="button"
              class="btn-primary"
              @click="completarPerfilAcudiente"
              :disabled="cargando"
            >
              <span v-if="cargando">Guardando...</span>
              <span v-else>Confirmar Registro</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <Pie />
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import authService from '@/services/authService'
import Encabezado from '@/components/layout/encabezado.vue'
import Pie from '@/components/layout/pie.vue'
import { getApiUrl } from '@/config/environment'
import { useUserRegistration } from '@/composables/useUserRegistration'

const router = useRouter()
const authStore = useAuthStore()

// Estado reactivo
const paso = ref(1)
const tipoPerfilSeleccionado = ref(null)
const cargando = ref(false)
const mensajeError = ref('')
const mensajeExito = ref('')

// Use shared registration logic
const {
  yaEsDeportista,
  yaEsAcudiente,
  edadDeportista,
  esMayorDeEdad,
  mostrarOpcionAcudiente
} = useUserRegistration()

// Datos para formulario de deportista
const formDeportista = ref({
  id_categoria: '',
  peso: null,
  altura: null,
  fecha_nacimiento: null,
  id_tipo_sanguineo: '',
  id_eps: ''
})

// Catálogos
const categorias = ref([])
const tiposSanguineos = ref([])
const listaEps = ref([])

// Funciones
function limpiarMensajes() {
  mensajeError.value = ''
  mensajeExito.value = ''
}

function seleccionarTipoPerfil(tipo) {
  limpiarMensajes()

  // Redirigir según el tipo seleccionado
  if (tipo === 'deportista') {
    router.push('/formulario-deportista-completo')
  } else if (tipo === 'acudiente') {
    router.push('/formulario-acudiente-completo')
  }
}

function volverAtras() {
  limpiarMensajes()
  paso.value = 1
  tipoPerfilSeleccionado.value = null
}

const validarCategoria = () => {
  if (!formDeportista.value.id_categoria) {
    mensajeError.value = 'Por favor selecciona una categoría'
    return false
  }
  return true
}

const validarYProcesarPeso = (datosDeportista) => {
  const pesoStr = formDeportista.value.peso
  if (!pesoStr || pesoStr.toString().trim() === '') {
    return true
  }

  const peso = Number.parseFloat(pesoStr)
  if (Number.isNaN(peso) || peso <= 0 || peso > 300) {
    mensajeError.value = 'El peso debe ser un número entre 1 y 300 kg'
    return false
  }

  datosDeportista.peso = peso
  return true
}

const validarYProcesarAltura = (datosDeportista) => {
  const alturaStr = formDeportista.value.altura
  if (!alturaStr || alturaStr.toString().trim() === '') {
    return true
  }

  const altura = Number.parseFloat(alturaStr)
  if (Number.isNaN(altura) || altura <= 0 || altura > 3) {
    mensajeError.value = 'La altura debe ser un número entre 0.1 y 3 metros'
    return false
  }

  datosDeportista.altura = altura
  return true
}

const validarYProcesarFechaNacimiento = (datosDeportista) => {
  const fechaStr = formDeportista.value.fecha_nacimiento
  if (!fechaStr || fechaStr.toString().trim() === '') {
    return true
  }

  const año = Number.parseInt(fechaStr, 10)
  const añoActual = new Date().getFullYear()

  if (Number.isNaN(año) || año < 1900 || año > añoActual) {
    mensajeError.value = `El año de nacimiento debe estar entre 1900 y ${añoActual}`
    return false
  }

  datosDeportista.fecha_nacimiento = año
  return true
}

const agregarCamposOpcionales = (datosDeportista) => {
  if (formDeportista.value.id_tipo_sanguineo && formDeportista.value.id_tipo_sanguineo !== '') {
    datosDeportista.id_tipo_sanguineo = Number.parseInt(formDeportista.value.id_tipo_sanguineo, 10)
  }

  if (formDeportista.value.id_eps && formDeportista.value.id_eps !== '') {
    datosDeportista.id_eps = Number.parseInt(formDeportista.value.id_eps, 10)
  }
}

const construirDatosDeportista = () => {
  const datosDeportista = {
    id_categoria: Number.parseInt(formDeportista.value.id_categoria, 10)
  }

  if (!validarYProcesarPeso(datosDeportista)) {
    return null
  }

  if (!validarYProcesarAltura(datosDeportista)) {
    return null
  }

  if (!validarYProcesarFechaNacimiento(datosDeportista)) {
    return null
  }

  agregarCamposOpcionales(datosDeportista)
  return datosDeportista
}

const manejarExitoCompletarPerfil = async () => {
  mensajeExito.value = '¡Perfil completado exitosamente! Redirigiendo...'
  await authStore.loadUserProfile()

  setTimeout(() => {
    router.push('/deportista/dashboard')
  }, 2000)
}

async function completarPerfilDeportista() {
  if (!validarCategoria()) {
    return
  }

  cargando.value = true
  limpiarMensajes()

  try {
    const datosDeportista = construirDatosDeportista()
    if (!datosDeportista) {
      return
    }

    const resultado = await authService.completarPerfilDeportista(datosDeportista)

    if (resultado.success) {
      await manejarExitoCompletarPerfil()
    } else {
      mensajeError.value = resultado.error || 'Error al completar perfil'
    }
  } catch (error) {
    mensajeError.value = error.message || 'Error de conexión'
  } finally {
    cargando.value = false
  }
}

async function completarPerfilAcudiente() {
  cargando.value = true
  limpiarMensajes()

  try {
    const resultado = await authService.completarPerfilAcudiente()

    if (resultado.success) {
      mensajeExito.value = '¡Perfil completado exitosamente! Redirigiendo...'

      // Recargar datos del usuario
      await authStore.loadUserProfile()

      // Redirigir a home después de 2 segundos
      setTimeout(() => {
        router.push('/home')
      }, 2000)
    } else {
      mensajeError.value = resultado.error || 'Error al completar perfil'
    }
  } catch (error) {
    mensajeError.value = error.message || 'Error de conexión'
  } finally {
    cargando.value = false
  }
}

async function cargarCatalogos() {
  try {
    // Cargar categorías
    const resCategorias = await fetch(getApiUrl('/api/catalogos/categorias'))
    if (resCategorias.ok) {
      const dataCategorias = await resCategorias.json()
      categorias.value = dataCategorias.data || []
    }

    // Cargar tipos sanguíneos
    const resTiposSanguineos = await fetch(getApiUrl('/api/catalogos/tipos-sanguineos'))
    if (resTiposSanguineos.ok) {
      const dataTiposSanguineos = await resTiposSanguineos.json()
      tiposSanguineos.value = dataTiposSanguineos.data || []
    }

    // Cargar EPS
    const resEps = await fetch(getApiUrl('/api/catalogos/eps'))
    if (resEps.ok) {
      const dataEps = await resEps.json()
      listaEps.value = dataEps.data || []
    }
  } catch (error) {
    console.error('Error al cargar catálogos:', error)
  }
}

onMounted(async () => {
  // Cargar perfil del usuario si no está cargado
  if (!authStore.user) {
    await authStore.loadUserProfile()
  }
  // Cargar detalle del usuario para obtener información del deportista (fecha_nacimiento)
  if (!authStore.userDetail) {
    await authStore.loadUserProfileDetail()
  }
  cargarCatalogos()
})
</script>

