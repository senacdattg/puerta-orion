<template>
  <main class="actualizar-info-page">
    <Encabezado />
    <TituloClub />
    <div class="actualizar-container">
      <div class="actualizar-header">
        <h1 class="actualizar-title">
          <i class="fas fa-edit"></i>
          Actualizar Información
        </h1>
        <p class="actualizar-subtitle">Modifica tus datos personales y de usuario</p>
      </div>

      <div class="actualizar-content">
        <div v-if="error" class="alert alert-error">
          <i class="fas fa-exclamation-circle"></i>
          {{ error }}
        </div>

        <div v-if="mensajeExito" class="alert alert-success">
          <i class="fas fa-check-circle"></i>
          {{ mensajeExito }}
        </div>

        <form @submit.prevent="actualizarInformacion" class="form-actualizar" v-if="!isLoading">
          <!-- Información Personal -->
          <div class="form-section">
            <h3>
              <i class="fas fa-user"></i>
              Información Personal
            </h3>

            <div class="form-row">
              <div class="form-group">
                <label for="primer_nombre">Primer Nombre *</label>
                <input
                  type="text"
                  id="primer_nombre"
                  v-model="formData.primer_nombre"
                  required
                  maxlength="50"
                  class="form-input"
                >
              </div>

              <div class="form-group">
                <label for="segundo_nombre">Segundo Nombre</label>
                <input
                  type="text"
                  id="segundo_nombre"
                  v-model="formData.segundo_nombre"
                  maxlength="50"
                  class="form-input"
                >
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="primer_apellido">Primer Apellido *</label>
                <input
                  type="text"
                  id="primer_apellido"
                  v-model="formData.primer_apellido"
                  required
                  maxlength="50"
                  class="form-input"
                >
              </div>

              <div class="form-group">
                <label for="segundo_apellido">Segundo Apellido</label>
                <input
                  type="text"
                  id="segundo_apellido"
                  v-model="formData.segundo_apellido"
                  maxlength="50"
                  class="form-input"
                >
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="id_tipo_documento">Tipo de Documento *</label>
                <select
                  id="id_tipo_documento"
                  v-model.number="formData.id_tipo_documento"
                  required
                  class="form-input"
                >
                  <option value="">Seleccione un tipo</option>
                  <option
                    v-for="tipo in catalogos.tiposDocumento"
                    :key="tipo.id_documento || tipo.id"
                    :value="tipo.id_documento || tipo.id"
                  >
                    {{ tipo.nombre_documento || tipo.nombre }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="documento">Número de Documento *</label>
                <input
                  type="text"
                  id="documento"
                  v-model="formData.documento"
                  required
                  maxlength="20"
                  class="form-input"
                >
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="correo_electronico">Correo Electrónico *</label>
                <input
                  type="email"
                  id="correo_electronico"
                  v-model="formData.correo_electronico"
                  required
                  maxlength="100"
                  class="form-input"
                >
              </div>

              <div class="form-group">
                <label for="telefono">Teléfono</label>
                <input
                  type="tel"
                  id="telefono"
                  v-model="formData.telefono"
                  maxlength="20"
                  class="form-input"
                >
              </div>
            </div>

            <div class="form-group">
              <label for="direccion">Dirección</label>
              <textarea
                id="direccion"
                v-model="formData.direccion"
                class="form-textarea"
                rows="3"
                maxlength="200"
              ></textarea>
            </div>

            <div class="form-group">
              <label for="id_sexo">Sexo *</label>
              <select
                id="id_sexo"
                v-model.number="formData.id_sexo"
                required
                class="form-input"
              >
                <option value="">Seleccione una opción</option>
                <option
                  v-for="sexo in catalogos.sexos"
                  :key="sexo.id_sexo || sexo.id"
                  :value="sexo.id_sexo || sexo.id"
                >
                  {{ sexo.nombre_sexo || sexo.nombre }}
                </option>
              </select>
            </div>
          </div>

          <!-- Información de Usuario -->
          <div class="form-section">
            <h3>
              <i class="fas fa-user-circle"></i>
              Información de Usuario
            </h3>

            <div class="form-group">
              <label for="usuario">Nombre de Usuario *</label>
              <input
                type="text"
                id="usuario"
                v-model="formData.usuario"
                required
                maxlength="50"
                class="form-input"
              >
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="cancelar" class="btn-cancel">
              <i class="fas fa-times"></i>
              Cancelar
            </button>
            <button type="submit" class="btn-save" :disabled="guardando">
              <i class="fas fa-save"></i>
              {{ guardando ? 'Guardando...' : 'Guardar Cambios' }}
            </button>
          </div>
        </form>

        <div v-if="isLoading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Cargando datos...</p>
        </div>
      </div>
    </div>
    <FooterEnhanced />
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import authService from '@/services/authService'
import { API_CONFIG } from '@/config/environment'
import Encabezado from '@/components/layout/encabezado.vue'
import TituloClub from '@/components/ui/titulo-club.vue'
import FooterEnhanced from '@/components/layout/pie.vue'

const router = useRouter()
const authStore = useAuthStore()
const guardando = ref(false)
const isLoading = ref(true)
const error = ref(null)
const mensajeExito = ref(null)

const catalogos = ref({
  tiposDocumento: [],
  sexos: []
})

const formData = ref({
  primer_nombre: '',
  segundo_nombre: '',
  primer_apellido: '',
  segundo_apellido: '',
  correo_electronico: '',
  telefono: '',
  direccion: '',
  documento: '',
  id_tipo_documento: null,
  id_sexo: null,
  usuario: ''
})

const baseURL = API_CONFIG.baseURL

async function cargarCatalogos() {
  try {
    const [tiposDocRes, sexosRes] = await Promise.all([
      fetch(`${baseURL}/api/catalogos/tipos-documento`),
      fetch(`${baseURL}/api/catalogos/sexos`)
    ])

    if (tiposDocRes.ok) {
      const tiposDocData = await tiposDocRes.json()
      catalogos.value.tiposDocumento = tiposDocData?.data || []
    }

    if (sexosRes.ok) {
      const sexosData = await sexosRes.json()
      catalogos.value.sexos = sexosData?.data || []
    }
  } catch (err) {
    console.error('Error al cargar catálogos:', err)
  }
}

async function cargarDatosUsuario() {
  try {
    isLoading.value = true
    error.value = null

    // Cargar detalle del perfil si no está cargado
    if (!authStore.userDetail) {
      await authStore.loadUserProfileDetail()
    }

    const detalle = authStore.userDetail
    const usuario = authStore.user

    if (detalle?.persona) {
      formData.value.primer_nombre = detalle.persona.primer_nombre || ''
      formData.value.segundo_nombre = detalle.persona.segundo_nombre || ''
      formData.value.primer_apellido = detalle.persona.primer_apellido || ''
      formData.value.segundo_apellido = detalle.persona.segundo_apellido || ''
      formData.value.correo_electronico = detalle.persona.correo_electronico || ''
      formData.value.telefono = detalle.persona.telefono || ''
      formData.value.direccion = detalle.persona.direccion || ''
      formData.value.documento = detalle.persona.documento || ''
      formData.value.id_tipo_documento = detalle.persona.id_tipo_documento || null
      formData.value.id_sexo = detalle.persona.id_sexo || null
    } else if (usuario?.persona) {
      // Fallback a datos del usuario si no hay detalle
      const persona = usuario.persona
      formData.value.primer_nombre = persona.primer_nombre || ''
      formData.value.segundo_nombre = persona.segundo_nombre || ''
      formData.value.primer_apellido = persona.primer_apellido || ''
      formData.value.segundo_apellido = persona.segundo_apellido || ''
      formData.value.correo_electronico = persona.correo_electronico || ''
      formData.value.telefono = persona.telefono || ''
      formData.value.direccion = persona.direccion || ''
      formData.value.documento = persona.documento || ''
      formData.value.id_tipo_documento = persona.id_tipo_documento || null
      formData.value.id_sexo = persona.id_sexo || null
    }

    // Cargar datos de usuario
    if (detalle?.usuario) {
      formData.value.usuario = detalle.usuario.usuario || ''
    } else if (usuario) {
      formData.value.usuario = usuario.usuario || usuario.username || ''
    }
  } catch (err) {
    console.error('Error al cargar datos del usuario:', err)
    error.value = 'Error al cargar los datos del usuario. Por favor, recarga la página.'
  } finally {
    isLoading.value = false
  }
}

const actualizarInformacion = async () => {
  guardando.value = true
  error.value = null
  mensajeExito.value = null

  try {
    const idUsuario = authStore.user?.id_usuario
    if (!idUsuario) {
      throw new Error('No se pudo obtener el ID del usuario')
    }

    // Preparar datos_persona
    const datosPersona = {
      primer_nombre: formData.value.primer_nombre.trim(),
      primer_apellido: formData.value.primer_apellido.trim(),
      correo_electronico: formData.value.correo_electronico.trim(),
      documento: formData.value.documento.trim(),
      id_tipo_documento: formData.value.id_tipo_documento,
      id_sexo: formData.value.id_sexo
    }

    // Agregar campos opcionales solo si tienen valor
    if (formData.value.segundo_nombre?.trim()) {
      datosPersona.segundo_nombre = formData.value.segundo_nombre.trim()
    }
    if (formData.value.segundo_apellido?.trim()) {
      datosPersona.segundo_apellido = formData.value.segundo_apellido.trim()
    }
    if (formData.value.telefono?.trim()) {
      datosPersona.telefono = formData.value.telefono.trim()
    }
    if (formData.value.direccion?.trim()) {
      datosPersona.direccion = formData.value.direccion.trim()
    }

    // Preparar datos_usuario
    const datosUsuario = {
      usuario: formData.value.usuario.trim()
    }

    // Llamar al servicio
    const resultado = await authService.updateUser(idUsuario, datosPersona, datosUsuario)

    if (resultado.success) {
      mensajeExito.value = resultado.message || 'Información actualizada correctamente'
      
      // Recargar datos del usuario
      await authStore.loadUserProfileDetail()
      await authStore.loadUserProfile()

      // Redirigir al perfil después de un breve delay
      setTimeout(() => {
        router.push('/perfil')
      }, 1500)
    } else {
      throw new Error(resultado.error || 'Error al actualizar la información')
    }
  } catch (err) {
    console.error('Error actualizando información:', err)
    error.value = err.message || 'Error al actualizar la información. Por favor, intenta nuevamente.'
  } finally {
    guardando.value = false
  }
}

const cancelar = () => {
  router.push('/perfil')
}

onMounted(async () => {
  await Promise.all([
    cargarCatalogos(),
    cargarDatosUsuario()
  ])
})
</script>

<style scoped>
.actualizar-info-page {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 2rem 1rem;
}

.actualizar-container {
  max-width: 900px;
  margin: 0 auto;
}

.actualizar-header {
  text-align: center;
  margin-bottom: 2rem;
}

.actualizar-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.actualizar-subtitle {
  font-size: 1.1rem;
  color: #6c757d;
  margin: 0;
}

.actualizar-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.alert {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.alert-error {
  background: #fee;
  border: 1px solid #fcc;
  color: #c33;
}

.alert-success {
  background: #efe;
  border: 1px solid #cfc;
  color: #3c3;
}

.loading-state {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}

.loading-state i {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.form-section {
  margin-bottom: 2.5rem;
}

.form-section:last-of-type {
  margin-bottom: 2rem;
}

.form-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e9ecef;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #007bff;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1.5rem;
  border-top: 2px solid #e9ecef;
  margin-top: 2rem;
}

.btn-cancel,
.btn-save {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.btn-cancel {
  background: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background: #5a6268;
}

.btn-save {
  background: #28a745;
  color: white;
}

.btn-save:hover:not(:disabled) {
  background: #218838;
}

.btn-save:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

@media (max-width: 768px) {
  .actualizar-info-page {
    padding: 1rem 0.5rem;
  }

  .actualizar-title {
    font-size: 2rem;
  }

  .actualizar-content {
    padding: 1.5rem;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn-cancel,
  .btn-save {
    width: 100%;
    justify-content: center;
  }
}
</style>