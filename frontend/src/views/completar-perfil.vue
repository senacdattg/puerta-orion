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
              class="opcion-btn opcion-deportista"
              @click="seleccionarTipoPerfil('deportista')"
              :disabled="cargando"
            >
              <div class="opcion-icono">🏃</div>
              <h3>Soy Deportista</h3>
              <p>Participo en entrenamientos y competencias</p>
            </button>

            <button
              class="opcion-btn opcion-acudiente"
              @click="seleccionarTipoPerfil('acudiente')"
              :disabled="cargando"
            >
              <div class="opcion-icono">👨‍👩‍👧</div>
              <h3>Soy Acudiente</h3>
              <p>Acompaño y apoyo a un deportista</p>
            </button>
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

const router = useRouter()
const authStore = useAuthStore()

// Estado reactivo
const paso = ref(1)
const tipoPerfilSeleccionado = ref(null)
const cargando = ref(false)
const mensajeError = ref('')
const mensajeExito = ref('')

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

async function completarPerfilDeportista() {
  if (!formDeportista.value.id_categoria) {
    mensajeError.value = 'Por favor selecciona una categoría'
    return
  }

  cargando.value = true
  limpiarMensajes()

  try {
    // Preparar datos para enviar con validación mejorada
    const datosDeportista = {
      id_categoria: parseInt(formDeportista.value.id_categoria)
    }

    // Validar y agregar campos opcionales solo si tienen valor válido
    if (formDeportista.value.peso && formDeportista.value.peso.trim() !== '') {
      const peso = parseFloat(formDeportista.value.peso)
      if (!isNaN(peso) && peso > 0 && peso <= 300) {
        datosDeportista.peso = peso
      } else {
        mensajeError.value = 'El peso debe ser un número entre 1 y 300 kg'
        return
      }
    }

    if (formDeportista.value.altura && formDeportista.value.altura.trim() !== '') {
      const altura = parseFloat(formDeportista.value.altura)
      if (!isNaN(altura) && altura > 0 && altura <= 3) {
        datosDeportista.altura = altura
      } else {
        mensajeError.value = 'La altura debe ser un número entre 0.1 y 3 metros'
        return
      }
    }

    if (formDeportista.value.fecha_nacimiento && formDeportista.value.fecha_nacimiento.trim() !== '') {
      const año = parseInt(formDeportista.value.fecha_nacimiento)
      const añoActual = new Date().getFullYear()
      if (!isNaN(año) && año >= 1900 && año <= añoActual) {
        datosDeportista.fecha_nacimiento = año
      } else {
        mensajeError.value = `El año de nacimiento debe estar entre 1900 y ${añoActual}`
        return
      }
    }

    if (formDeportista.value.id_tipo_sanguineo && formDeportista.value.id_tipo_sanguineo !== '') {
      datosDeportista.id_tipo_sanguineo = parseInt(formDeportista.value.id_tipo_sanguineo)
    }

    if (formDeportista.value.id_eps && formDeportista.value.id_eps !== '') {
      datosDeportista.id_eps = parseInt(formDeportista.value.id_eps)
    }

    const resultado = await authService.completarPerfilDeportista(datosDeportista)

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
    const resCategorias = await fetch(`${import.meta.env.VITE_API_URL}/api/catalogos/categorias`)
    if (resCategorias.ok) {
      const dataCategorias = await resCategorias.json()
      categorias.value = dataCategorias.data || []
    }

    // Cargar tipos sanguíneos
    const resTiposSanguineos = await fetch(`${import.meta.env.VITE_API_URL}/api/catalogos/tipos-sanguineos`)
    if (resTiposSanguineos.ok) {
      const dataTiposSanguineos = await resTiposSanguineos.json()
      tiposSanguineos.value = dataTiposSanguineos.data || []
    }

    // Cargar EPS
    const resEps = await fetch(`${import.meta.env.VITE_API_URL}/api/catalogos/eps`)
    if (resEps.ok) {
      const dataEps = await resEps.json()
      listaEps.value = dataEps.data || []
    }
  } catch (error) {
    console.error('Error al cargar catálogos:', error)
  }
}

onMounted(() => {
  cargarCatalogos()
})
</script>

<style scoped>
.completar-perfil-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.completar-perfil-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.seleccion-perfil,
.formulario-perfil,
.confirmacion-perfil {
  width: 100%;
  max-width: 800px;
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-completar {
  background: white;
  border-radius: 20px;
  padding: 3rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.icono-completar {
  width: 80px;
  height: 80px;
  display: block;
  margin: 0 auto 1.5rem;
}

.titulo-completar {
  text-align: center;
  color: #333;
  font-size: 2rem;
  margin-bottom: 1rem;
  font-weight: 700;
}

.descripcion-completar {
  text-align: center;
  color: #666;
  font-size: 1.1rem;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.opciones-perfil {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.opcion-btn {
  background: white;
  border: 3px solid #e0e0e0;
  border-radius: 15px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.opcion-btn:hover:not(:disabled) {
  border-color: #667eea;
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.opcion-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.opcion-deportista:hover:not(:disabled) {
  border-color: #667eea;
}

.opcion-acudiente:hover:not(:disabled) {
  border-color: #764ba2;
}

.opcion-icono {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.opcion-icono-grande {
  font-size: 6rem;
  text-align: center;
  margin-bottom: 1.5rem;
}

.opcion-btn h3 {
  color: #333;
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.opcion-btn p {
  color: #666;
  font-size: 1rem;
  margin: 0;
}

.form-deportista {
  margin-top: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 600;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.8rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  justify-content: center;
}

.btn-primary,
.btn-secondary {
  padding: 1rem 2rem;
  border: none;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 150px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #e0e0e0;
  color: #333;
}

.btn-secondary:hover:not(:disabled) {
  background: #d0d0d0;
}

.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.mensaje-error {
  background-color: #fee;
  color: #c33;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  text-align: center;
  border: 1px solid #fcc;
}

.mensaje-exito {
  background-color: #efe;
  color: #3c3;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  text-align: center;
  border: 1px solid #cfc;
}

@media (max-width: 768px) {
  .card-completar {
    padding: 2rem;
  }

  .titulo-completar {
    font-size: 1.5rem;
  }

  .descripcion-completar {
    font-size: 1rem;
  }

  .opciones-perfil {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>

