<template>
  <main class="actualizar-info-page">
    <Encabezado />
    <div class="actualizar-container">
      <div class="actualizar-header">
        <h1 class="actualizar-title">
          <i class="fas fa-edit"></i>
          Actualizar Información
        </h1>
        <p class="actualizar-subtitle">Modifica tus datos personales y de usuario</p>
      </div>

      <div class="actualizar-content">
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
                  :readonly="!puedeEditarCampo.primerNombre"
                  :disabled="!puedeEditarCampo.primerNombre"
                  class="form-input"
                  :style="!puedeEditarCampo.primerNombre ? 'background-color: #f5f5f5; cursor: not-allowed;' : ''"
                >
                <small v-if="!puedeEditarCampo.primerNombre" style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
              </div>

              <div class="form-group">
                <label for="segundo_nombre">Segundo Nombre</label>
                <input
                  type="text"
                  id="segundo_nombre"
                  v-model="formData.segundo_nombre"
                  maxlength="50"
                  :readonly="!puedeEditarCampo.segundoNombre"
                  :disabled="!puedeEditarCampo.segundoNombre"
                  class="form-input"
                  :style="!puedeEditarCampo.segundoNombre ? 'background-color: #f5f5f5; cursor: not-allowed;' : ''"
                >
                <small v-if="!puedeEditarCampo.segundoNombre" style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
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
                  :readonly="!puedeEditarCampo.primerApellido"
                  :disabled="!puedeEditarCampo.primerApellido"
                  class="form-input"
                  :style="!puedeEditarCampo.primerApellido ? 'background-color: #f5f5f5; cursor: not-allowed;' : ''"
                >
                <small v-if="!puedeEditarCampo.primerApellido" style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
              </div>

              <div class="form-group">
                <label for="segundo_apellido">Segundo Apellido</label>
                <input
                  type="text"
                  id="segundo_apellido"
                  v-model="formData.segundo_apellido"
                  maxlength="50"
                  :readonly="!puedeEditarCampo.segundoApellido"
                  :disabled="!puedeEditarCampo.segundoApellido"
                  class="form-input"
                  :style="!puedeEditarCampo.segundoApellido ? 'background-color: #f5f5f5; cursor: not-allowed;' : ''"
                >
                <small v-if="!puedeEditarCampo.segundoApellido" style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="id_tipo_documento">Tipo de Documento *</label>
                <input
                  type="text"
                  id="id_tipo_documento"
                  :value="catalogos.tiposDocumento.find(t => (t.id_documento || t.id) === formData.id_tipo_documento)?.nombre_documento || catalogos.tiposDocumento.find(t => (t.id_documento || t.id) === formData.id_tipo_documento)?.nombre || ''"
                  readonly
                  disabled
                  class="form-input"
                  style="background-color: #f5f5f5; cursor: not-allowed;"
                >
                <small style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
              </div>

              <div class="form-group">
                <label for="documento">Número de Documento *</label>
                <input
                  type="text"
                  id="documento"
                  v-model="formData.documento"
                  required
                  maxlength="20"
                  :readonly="!puedeEditarCampo.numeroDocumento"
                  :disabled="!puedeEditarCampo.numeroDocumento"
                  class="form-input"
                  :style="!puedeEditarCampo.numeroDocumento ? 'background-color: #f5f5f5; cursor: not-allowed;' : ''"
                >
                <small v-if="!puedeEditarCampo.numeroDocumento" style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
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
              <input
                type="text"
                id="id_sexo"
                :value="catalogos.sexos.find(s => (s.id_sexo || s.id) === formData.id_sexo)?.nombre_sexo || catalogos.sexos.find(s => (s.id_sexo || s.id) === formData.id_sexo)?.nombre || ''"
                readonly
                disabled
                class="form-input"
                style="background-color: #f5f5f5; cursor: not-allowed;"
              >
              <small style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
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

          <!-- Información del Deportista (solo si es deportista Y no es acudiente) -->
          <div v-if="esDeportista && rolUsuario !== 'Acudiente'" class="form-section">
            <h3>
              <i class="fas fa-running"></i>
              Información del Deportista
            </h3>

            <div class="form-row">
              <div class="form-group">
                <label for="fecha_nacimiento">Fecha de Nacimiento</label>
                <input
                  type="date"
                  id="fecha_nacimiento"
                  :value="formDataDeportista.fecha_nacimiento"
                  readonly
                  disabled
                  class="form-input"
                  style="background-color: #f5f5f5; cursor: not-allowed;"
                >
                <small style="color: #6c757d; font-size: 0.875rem;">La fecha de nacimiento no se puede modificar</small>
              </div>

              <div class="form-group">
                <label for="fecha_ingreso">Fecha de Ingreso</label>
                <input
                  type="date"
                  id="fecha_ingreso"
                  :value="formDataDeportista.fecha_ingreso"
                  readonly
                  disabled
                  class="form-input"
                  style="background-color: #f5f5f5; cursor: not-allowed;"
                >
                <small style="color: #6c757d; font-size: 0.875rem;">La fecha de ingreso no se puede modificar</small>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="id_tipo_sanguineo">Tipo Sanguíneo *</label>
                <input
                  type="text"
                  id="id_tipo_sanguineo"
                  :value="catalogosDeportista.tiposSanguineos.find(t => t.id_tipo_sangre === formDataDeportista.id_tipo_sanguineo)?.tipo_sangre || ''"
                  readonly
                  disabled
                  class="form-input"
                  style="background-color: #f5f5f5; cursor: not-allowed;"
                >
                <small style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
              </div>

              <div class="form-group">
                <label for="id_ciudad_residencia">Ciudad de Residencia *</label>
                <input
                  type="text"
                  id="id_ciudad_residencia"
                  :value="catalogosDeportista.ciudades.find(c => c.id_ciudad === formDataDeportista.id_ciudad_residencia)?.nombre_ciudad || ''"
                  readonly
                  disabled
                  class="form-input"
                  style="background-color: #f5f5f5; cursor: not-allowed;"
                >
                <small style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="id_eps">EPS *</label>
                <select
                  id="id_eps"
                  v-model.number="formDataDeportista.id_eps"
                  required
                  :disabled="!puedeEditarCampo.eps"
                  class="form-input"
                  :style="!puedeEditarCampo.eps ? 'background-color: #f5f5f5; cursor: not-allowed;' : ''"
                >
                  <option value="">Seleccione una EPS</option>
                  <option
                    v-for="eps in catalogosDeportista.eps"
                    :key="eps.id_eps"
                    :value="eps.id_eps"
                  >
                    {{ eps.nombre_eps }}
                  </option>
                </select>
                <small v-if="!puedeEditarCampo.eps" style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
              </div>

              <div class="form-group">
                <label for="id_categoria">Categoría</label>
                <input
                  type="text"
                  id="id_categoria"
                  :value="categoriaNombre"
                  readonly
                  disabled
                  class="form-input"
                  style="background-color: #f5f5f5; cursor: not-allowed;"
                >
                <small style="color: #6c757d; font-size: 0.875rem;">La categoría se asigna automáticamente según la fecha de nacimiento</small>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="peso">Peso (kg)</label>
                <input
                  type="number"
                  id="peso"
                  v-model.number="formDataDeportista.peso"
                  step="0.1"
                  min="0"
                  :readonly="!puedeEditarPesoAltura"
                  :disabled="!puedeEditarPesoAltura"
                  class="form-input"
                >
              </div>

              <div class="form-group">
                <label for="altura">Altura (m)</label>
                <input
                  type="number"
                  id="altura"
                  v-model.number="formDataDeportista.altura"
                  step="0.01"
                  min="0"
                  :readonly="!puedeEditarPesoAltura"
                  :disabled="!puedeEditarPesoAltura"
                  class="form-input"
                >
              </div>
            </div>

            <div v-if="!puedeEditarPesoAltura" class="alert alert-info" style="background: #fff3cd; border: 1px solid #ffc107; color: #856404;">
              <i class="fas fa-info-circle"></i>
              <small>Nota: Solo Entrenador y Administrador pueden editar peso y altura</small>
            </div>

            <hr style="margin: 1.5rem 0; border: 0; border-top: 1px solid #e9ecef;" />

            <!-- Información Deportiva -->
            <h4 style="font-size: 1.1rem; font-weight: 600; color: #2c3e50; margin-bottom: 1rem;">
              <i class="fas fa-futbol"></i>
              Información Deportiva
            </h4>

            <div class="form-row">
              <div class="form-group">
                <label for="id_deporte">Deporte Principal *</label>
                <select
                  id="id_deporte"
                  v-model.number="formDataDeportista.id_deporte"
                  required
                  :disabled="!puedeEditarCampo.deporte"
                  class="form-input"
                  :style="!puedeEditarCampo.deporte ? 'background-color: #f5f5f5; cursor: not-allowed;' : ''"
                >
                  <option value="">Seleccione un deporte</option>
                  <option
                    v-for="deporte in catalogosDeportista.deportes"
                    :key="deporte.id_deporte"
                    :value="deporte.id_deporte"
                  >
                    {{ deporte.nombre }}
                  </option>
                </select>
                <small v-if="!puedeEditarCampo.deporte" style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
              </div>

              <div class="form-group">
                <label for="id_institucion_registro">Institución de Registro *</label>
                <select
                  id="id_institucion_registro"
                  v-model.number="formDataDeportista.id_institucion_registro"
                  required
                  :disabled="!puedeEditarCampo.institucionRegistro"
                  class="form-input"
                  :style="!puedeEditarCampo.institucionRegistro ? 'background-color: #f5f5f5; cursor: not-allowed;' : ''"
                >
                  <option value="">Seleccione una institución</option>
                  <option
                    v-for="inst in catalogosDeportista.institucionesRegistro"
                    :key="inst.id_institucion"
                    :value="inst.id_institucion"
                  >
                    {{ inst.nombre_institucion }}
                  </option>
                </select>
                <small v-if="!puedeEditarCampo.institucionRegistro" style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
              </div>
            </div>

            <div class="form-group">
              <label>¿Practica otro deporte además del principal?</label>
              <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                  <input
                    type="radio"
                    v-model="formDataDeportista.practica_otro_deporte"
                    :value="true"
                  >
                  Sí
                </label>
                <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                  <input
                    type="radio"
                    v-model="formDataDeportista.practica_otro_deporte"
                    :value="false"
                  >
                  No
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>¿Participa en escuela de formación?</label>
              <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                  <input
                    type="radio"
                    v-model="formDataDeportista.participa_escuela"
                    :value="true"
                    :disabled="!puedeEditarCampo.participaEscuela"
                  >
                  Sí
                </label>
                <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                  <input
                    type="radio"
                    v-model="formDataDeportista.participa_escuela"
                    :value="false"
                    :disabled="!puedeEditarCampo.participaEscuela"
                  >
                  No
                </label>
              </div>
              <small v-if="!puedeEditarCampo.participaEscuela" style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
            </div>

            <div v-if="formDataDeportista.participa_escuela" class="form-group">
              <label for="id_escuela">Escuela de Formación</label>
              <select
                id="id_escuela"
                v-model.number="formDataDeportista.id_escuela"
                :disabled="!puedeEditarCampo.escuela"
                class="form-input"
                :style="!puedeEditarCampo.escuela ? 'background-color: #f5f5f5; cursor: not-allowed;' : ''"
              >
                <option value="">Seleccione una escuela</option>
                <option
                  v-for="escuela in catalogosDeportista.escuelas"
                  :key="escuela.id_escuela"
                  :value="escuela.id_escuela"
                >
                  {{ escuela.nombre }}
                </option>
              </select>
              <small v-if="!puedeEditarCampo.escuela" style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
            </div>

            <hr style="margin: 1.5rem 0; border: 0; border-top: 1px solid #e9ecef;" />

            <!-- Información Médica -->
            <h4 style="font-size: 1.1rem; font-weight: 600; color: #2c3e50; margin-bottom: 1rem;">
              <i class="fas fa-heartbeat"></i>
              Antecedentes Médicos
            </h4>

            <div class="form-group">
              <label>¿Tiene alguna enfermedad o condición médica?</label>
              <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                  <input
                    type="radio"
                    v-model="formDataDeportista.tiene_enfermedades"
                    :value="true"
                    :disabled="!puedeEditarCampo.antecedentesMedicos"
                  >
                  Sí
                </label>
                <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                  <input
                    type="radio"
                    v-model="formDataDeportista.tiene_enfermedades"
                    :value="false"
                    :disabled="!puedeEditarCampo.antecedentesMedicos"
                  >
                  No
                </label>
              </div>
              <small v-if="!puedeEditarCampo.antecedentesMedicos" style="color: #6c757d; font-size: 0.875rem;">No se puede modificar</small>
            </div>

            <div v-if="formDataDeportista.tiene_enfermedades === true">
              <div class="form-group">
                <label for="tipo_enfermedad">Tipo de Enfermedad</label>
                <select
                  id="tipo_enfermedad"
                  v-model.number="formDataDeportista.tipo_enfermedad"
                  :disabled="!puedeEditarCampo.antecedentesMedicos"
                  class="form-input"
                  :style="!puedeEditarCampo.antecedentesMedicos ? 'background-color: #f5f5f5; cursor: not-allowed;' : ''"
                >
                  <option :value="null">Seleccione tipo de enfermedad (opcional)</option>
                  <option
                    v-for="tipo in catalogosDeportista.tiposEnfermedad"
                    :key="tipo.id_tipo_enfermedad"
                    :value="tipo.id_tipo_enfermedad"
                  >
                    {{ tipo.nombre }}
                  </option>
                </select>
              </div>

              <div v-if="formDataDeportista.tipo_enfermedad" class="form-group">
                <label>Diagnósticos:</label>
                <div style="max-height: 200px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px; padding: 10px; margin-top: 10px;"
                     :style="!puedeEditarCampo.antecedentesMedicos ? 'background-color: #f5f5f5; cursor: not-allowed;' : ''">
                  <div
                    v-for="diagnostico in diagnosticosDisponibles"
                    :key="diagnostico.id_diagnostico"
                    style="display: flex; align-items: center; padding: 5px 0;"
                  >
                    <input
                      type="checkbox"
                      :id="`diag-${diagnostico.id_diagnostico}`"
                      :value="diagnostico.id_diagnostico"
                      v-model="formDataDeportista.diagnostico"
                      :disabled="!puedeEditarCampo.antecedentesMedicos"
                      style="margin-right: 8px;"
                    />
                    <label :for="`diag-${diagnostico.id_diagnostico}`"
                           :style="puedeEditarCampo.antecedentesMedicos ? 'cursor: pointer; margin: 0;' : 'cursor: not-allowed; margin: 0;'">
                      {{ diagnostico.nombre }}
                    </label>
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label>¿Existe alguna recomendación médica?</label>
                <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                  <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                    <input
                      type="radio"
                      v-model="formDataDeportista.recomendacion_medica"
                      :value="true"
                      :disabled="!puedeEditarCampo.antecedentesMedicos"
                    >
                    Sí
                  </label>
                  <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                    <input
                      type="radio"
                      v-model="formDataDeportista.recomendacion_medica"
                      :value="false"
                      :disabled="!puedeEditarCampo.antecedentesMedicos"
                    >
                    No
                  </label>
                </div>
              </div>

              <div v-if="formDataDeportista.recomendacion_medica === true" class="form-group">
                <label for="descripcion_recomendacion">Describa la recomendación:</label>
                <textarea
                  id="descripcion_recomendacion"
                  v-model="formDataDeportista.descripcion_recomendacion"
                  :readonly="!puedeEditarCampo.antecedentesMedicos"
                  :disabled="!puedeEditarCampo.antecedentesMedicos"
                  class="form-textarea"
                  rows="3"
                  placeholder="Escriba aquí..."
                  :style="!puedeEditarCampo.antecedentesMedicos ? 'background-color: #f5f5f5; cursor: not-allowed;' : ''"
                ></textarea>
              </div>
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import authService from '@/services/authService'
import deportistasService from '@/services/deportistasService'
import catalogosService from '@/services/catalogosService'
import { API_CONFIG } from '@/config/environment'
import Encabezado from '@/components/layout/encabezado.vue'
import FooterEnhanced from '@/components/layout/pie.vue'
import Swal from 'sweetalert2'

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

const catalogosDeportista = ref({
  tiposSanguineos: [],
  ciudades: [],
  eps: [],
  categorias: [],
  deportes: [],
  escuelas: [],
  institucionesRegistro: [],
  tiposEnfermedad: [],
  diagnosticos: []
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

const formDataDeportista = ref({
  fecha_nacimiento: '',
  fecha_ingreso: '',
  id_tipo_sanguineo: null,
  id_ciudad_residencia: null,
  id_eps: null,
  id_categoria: null,
  peso: null,
  altura: null,
  id_deporte: null,
  id_escuela: null,
  id_institucion_registro: null,
  practica_otro_deporte: false,
  participa_escuela: false,
  tiene_enfermedades: null,
  tipo_enfermedad: null,
  diagnostico: [],
  recomendacion_medica: false,
  descripcion_recomendacion: ''
})

// Computed para filtrar diagnósticos según el tipo de enfermedad seleccionado
const diagnosticosDisponibles = computed(() => {
  if (!formDataDeportista.value.tipo_enfermedad) return []
  return catalogosDeportista.value.diagnosticos.filter(
    d => d.id_tipo_enfermedad === formDataDeportista.value.tipo_enfermedad
  )
})

// Computed para mostrar el nombre de la categoría
const categoriaNombre = computed(() => {
  if (!formDataDeportista.value.id_categoria) return '—'
  const categoria = catalogosDeportista.value.categorias.find(
    c => c.id_categoria === formDataDeportista.value.id_categoria
  )
  return categoria?.nombre_categoria || '—'
})

// Computed para verificar si el usuario es deportista
const esDeportista = computed(() => {
  return authStore.userDetail?.deportista?.id_deportista ||
         authStore.user?.deportista?.id_deportista ||
         false
})

// Computed para obtener el rol del usuario
const rolUsuario = computed(() => {
  const activeRole = authStore.activeRole
  const userRoles = authStore.userRoles

  // Si hay un rol activo, usarlo
  if (activeRole) {
    return activeRole
  }

  // Extraer nombres de roles
  const nombresRoles = userRoles.map(rol => {
    if (typeof rol === 'string') return rol
    if (rol.nombre_rol) return rol.nombre_rol
    return rol.toString()
  })

  // Prioridad: Entrenador > Deportista > Acudiente
  if (nombresRoles.includes('Entrenador') || nombresRoles.includes('Administrador') || nombresRoles.includes('SuperAdmin')) {
    return 'Entrenador'
  }
  if (nombresRoles.includes('Deportista')) {
    return 'Deportista'
  }
  if (nombresRoles.includes('Acudiente')) {
    return 'Acudiente'
  }

  return null
})

// Computed para validar si puede editar peso y altura
const puedeEditarPesoAltura = computed(() => {
  const rol = rolUsuario.value
  const rolesPermitidos = ['Entrenador', 'Administrador', 'SuperAdmin']
  return rolesPermitidos.includes(rol)
})

// Computed para verificar qué campos puede editar según el rol
const puedeEditarCampo = computed(() => {
  const rol = rolUsuario.value

  if (rol === 'Deportista') {
    return {
      // Datos personales
      tipoDocumento: false,
      numeroDocumento: false,
      primerNombre: false,
      segundoNombre: false,
      primerApellido: false,
      segundoApellido: false,
      sexo: false,
      correo: true,
      telefono: true,
      direccion: true,
      // Datos deportista
      fechaNacimiento: false,
      fechaIngreso: false,
      categoria: false,
      tipoSanguineo: false,
      ciudadResidencia: false,
      eps: true,
      peso: puedeEditarPesoAltura.value,
      altura: puedeEditarPesoAltura.value,
      deporte: true,
      institucionRegistro: true,
      participaEscuela: true,
      practicaOtroDeporte: true,
      escuela: true,
      antecedentesMedicos: true
    }
  } else if (rol === 'Acudiente') {
    return {
      // Solo puede editar sus propios datos personales
      tipoDocumento: false,
      numeroDocumento: false,
      primerNombre: false,
      segundoNombre: false,
      primerApellido: false,
      segundoApellido: false,
      sexo: false,
      correo: true,
      telefono: true,
      direccion: true,
      // No puede editar datos del deportista
      fechaNacimiento: false,
      fechaIngreso: false,
      categoria: false,
      tipoSanguineo: false,
      ciudadResidencia: false,
      eps: false,
      peso: false,
      altura: false,
      deporte: false,
      institucionRegistro: false,
      participaEscuela: false,
      practicaOtroDeporte: false,
      escuela: false,
      antecedentesMedicos: false
    }
  } else if (rol === 'Entrenador') {
    return {
      // Puede editar  excepto tipo y número de documento
      tipoDocumento: false,
      numeroDocumento: false,
      primerNombre: true,
      segundoNombre: true,
      primerApellido: true,
      segundoApellido: true,
      sexo: true,
      correo: true,
      telefono: true,
      direccion: true,
      // Datos deportista
      fechaNacimiento: false,
      fechaIngreso: false,
      categoria: false,
      tipoSanguineo: true,
      ciudadResidencia: true,
      eps: true,
      peso: true,
      altura: true,
      deporte: true,
      institucionRegistro: true,
      participaEscuela: true,
      practicaOtroDeporte: true,
      escuela: true,
      antecedentesMedicos: true
    }
  }

  // Por defecto, permitir edición si no hay rol específico (Administrador, etc.)
  return {
    tipoDocumento: false,
    numeroDocumento: false,
    primerNombre: true,
    segundoNombre: true,
    primerApellido: true,
    segundoApellido: true,
    sexo: true,
    correo: true,
    telefono: true,
    direccion: true,
    fechaNacimiento: false,
    fechaIngreso: false,
    categoria: false,
    tipoSanguineo: true,
    ciudadResidencia: true,
    eps: true,
    peso: true,
    altura: true,
    deporte: true,
    institucionRegistro: true,
    participaEscuela: true,
    escuela: true,
    antecedentesMedicos: true
  }
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

async function cargarCatalogosDeportista() {
  if (!esDeportista.value) return

  try {
    const endpoints = [
      '/api/deportistas/catalogos/grupos-sanguineos',
      '/api/deportistas/catalogos/ciudades-residencia',
      '/api/deportistas/catalogos/eps',
      '/api/deportistas/catalogos/deportes',
      '/api/deportistas/catalogos/escuelas',
      '/api/deportistas/catalogos/instituciones-registro',
      '/api/catalogos/tipos-enfermedad',
      '/api/deportistas/catalogos/diagnosticos'
    ]

    const responses = await Promise.all(
      endpoints.map(endpoint => fetch(`${baseURL}${endpoint}`))
    )

    const processResponse = async (res) => {
      try {
        const data = await res.json()
        return res.ok ? (data.data || data) : []
      } catch {
        return []
      }
    }

    const resultados = await Promise.all(
      responses.map(res => processResponse(res))
    )

    catalogosDeportista.value.tiposSanguineos = resultados[0] || []
    catalogosDeportista.value.ciudades = resultados[1] || []
    catalogosDeportista.value.eps = resultados[2] || []
    catalogosDeportista.value.deportes = resultados[3] || []
    catalogosDeportista.value.escuelas = resultados[4] || []
    catalogosDeportista.value.institucionesRegistro = resultados[5] || []
    catalogosDeportista.value.tiposEnfermedad = resultados[6] || []
    catalogosDeportista.value.diagnosticos = resultados[7] || []

    // Cargar categorías
    try {
      const categorias = await catalogosService.getCategorias()
      catalogosDeportista.value.categorias = Array.isArray(categorias) ? categorias : []
    } catch (err) {
      console.error('Error al cargar categorías:', err)
      catalogosDeportista.value.categorias = []
    }
  } catch (err) {
    console.error('Error al cargar catálogos de deportista:', err)
  }
}

const cargarDatosPersona = (persona) => {
  if (!persona) return

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

const cargarDatosUsuarioForm = (detalle, usuario) => {
  if (detalle?.usuario) {
    formData.value.usuario = detalle.usuario.usuario || ''
  } else if (usuario) {
    formData.value.usuario = usuario.usuario || usuario.username || ''
  }
}

const cargarDatosDeportista = (deportista) => {
  if (!deportista) return

  if (deportista.fecha_nacimiento) {
    formDataDeportista.value.fecha_nacimiento = deportista.fecha_nacimiento
  }
  if (deportista.fecha_ingreso) {
    formDataDeportista.value.fecha_ingreso = deportista.fecha_ingreso
  }
  if (deportista.peso !== undefined && deportista.peso !== null) {
    formDataDeportista.value.peso = deportista.peso
  }
  if (deportista.altura !== undefined && deportista.altura !== null) {
    formDataDeportista.value.altura = deportista.altura
  }
  if (deportista.id_tipo_sanguineo) {
    formDataDeportista.value.id_tipo_sanguineo = deportista.id_tipo_sanguineo
  }
  if (deportista.id_ciudad_recidencia) {
    formDataDeportista.value.id_ciudad_residencia = deportista.id_ciudad_recidencia
  }
  if (deportista.id_eps) {
    formDataDeportista.value.id_eps = deportista.id_eps
  }
  if (deportista.id_categoria) {
    formDataDeportista.value.id_categoria = deportista.id_categoria
  }
}

const cargarInformacionDeportiva = (info) => {
  if (!info) return

  if (info.id_deporte) {
    formDataDeportista.value.id_deporte = info.id_deporte
  }
  if (info.id_escuela) {
    formDataDeportista.value.id_escuela = info.id_escuela
  }
  if (info.id_institucion_registro) {
    formDataDeportista.value.id_institucion_registro = info.id_institucion_registro
  }
  if (info.practica_otro_deporte !== undefined) {
    formDataDeportista.value.practica_otro_deporte = info.practica_otro_deporte
  }
  if (info.participa_escuela !== undefined) {
    formDataDeportista.value.participa_escuela = info.participa_escuela
  }
  if (info.id_categoria) {
    formDataDeportista.value.id_categoria = info.id_categoria
  }
  if (info.recomendacion_medica !== undefined) {
    formDataDeportista.value.recomendacion_medica = info.recomendacion_medica
  }
  if (info.descripcion_recomendacion) {
    formDataDeportista.value.descripcion_recomendacion = info.descripcion_recomendacion
  }
}

const cargarDatosSalud = (salud) => {
  if (!salud) return

  if (salud.tipos_enfermedad_ids && salud.tipos_enfermedad_ids.length > 0) {
    formDataDeportista.value.tipo_enfermedad = salud.tipos_enfermedad_ids[0]
    formDataDeportista.value.tiene_enfermedades = true
  }
  if (salud.diagnosticos && Array.isArray(salud.diagnosticos)) {
    formDataDeportista.value.diagnostico = salud.diagnosticos.map(d =>
      typeof d === 'object' ? d.id_diagnostico : d
    )
  }
}

async function cargarDatosUsuario() {
  try {
    isLoading.value = true
    error.value = null

    if (!authStore.userDetail) {
      await authStore.loadUserProfileDetail()
    }

    const detalle = authStore.userDetail
    const usuario = authStore.user

    if (detalle?.persona) {
      cargarDatosPersona(detalle.persona)
    } else if (usuario?.persona) {
      cargarDatosPersona(usuario.persona)
    }

    cargarDatosUsuarioForm(detalle, usuario)

    if (detalle?.deportista) {
      cargarDatosDeportista(detalle.deportista)
    }

    if (detalle?.informacion_deportiva) {
      cargarInformacionDeportiva(detalle.informacion_deportiva)
    }

    if (detalle?.salud) {
      cargarDatosSalud(detalle.salud)
    }
  } catch (err) {
    console.error('Error al cargar datos del usuario:', err)
    error.value = 'Error al cargar los datos del usuario. Por favor, recarga la página.'
    await Swal.fire({
      icon: 'error',
      title: 'No pudimos cargar tus datos',
      text: 'Recarga la página o intenta más tarde.'
    })
  } finally {
    isLoading.value = false
  }
}

const confirmarActualizacion = async () => {
  const confirmacion = await Swal.fire({
    icon: 'question',
    title: '¿Guardar cambios?',
    text: 'Se actualizará tu perfil con la información ingresada.',
    showCancelButton: true,
    confirmButtonText: 'Sí, actualizar',
    cancelButtonText: 'Cancelar'
  })
  return confirmacion.isConfirmed
}

const prepararDatosPersona = () => {
  const datosPersona = {
    correo_electronico: formData.value.correo_electronico.trim()
  }

  if (puedeEditarCampo.value.telefono && formData.value.telefono?.trim()) {
    datosPersona.telefono = formData.value.telefono.trim()
  }
  if (puedeEditarCampo.value.direccion && formData.value.direccion?.trim()) {
    datosPersona.direccion = formData.value.direccion.trim()
  }

  if (rolUsuario.value === 'Entrenador') {
    datosPersona.primer_nombre = formData.value.primer_nombre.trim()
    datosPersona.primer_apellido = formData.value.primer_apellido.trim()
    datosPersona.id_sexo = formData.value.id_sexo

    if (formData.value.segundo_nombre?.trim()) {
      datosPersona.segundo_nombre = formData.value.segundo_nombre.trim()
    }
    if (formData.value.segundo_apellido?.trim()) {
      datosPersona.segundo_apellido = formData.value.segundo_apellido.trim()
    }
  }

  return datosPersona
}

const prepararDatosUsuario = () => {
  return {
    usuario: formData.value.usuario.trim()
  }
}

const prepararDatosDeportistaBasicos = () => {
  const datosDeportista = {}

  if (puedeEditarCampo.value.tipoSanguineo) {
    datosDeportista.id_tipo_sanguineo = formDataDeportista.value.id_tipo_sanguineo || null
  }
  if (puedeEditarCampo.value.ciudadResidencia) {
    datosDeportista.id_ciudad_recidencia = formDataDeportista.value.id_ciudad_residencia || null
  }
  if (puedeEditarCampo.value.eps) {
    datosDeportista.id_eps = formDataDeportista.value.id_eps || null
  }

  return datosDeportista
}

const agregarDatosDeporte = (datosInfo) => {
  if (puedeEditarCampo.value.deporte) {
    datosInfo.id_deporte = formDataDeportista.value.id_deporte || null
  }
}

const agregarDatosEscuela = (datosInfo) => {
  if (puedeEditarCampo.value.escuela && formDataDeportista.value.participa_escuela && formDataDeportista.value.id_escuela) {
    datosInfo.id_escuela = formDataDeportista.value.id_escuela
  }
}

const agregarDatosInstitucion = (datosInfo) => {
  if (puedeEditarCampo.value.institucionRegistro) {
    datosInfo.id_institucion_registro = formDataDeportista.value.id_institucion_registro || null
  }
}

const agregarDatosPracticaDeporte = (datosInfo) => {
  if (puedeEditarCampo.value.practicaOtroDeporte !== undefined) {
    datosInfo.practica_otro_deporte = puedeEditarCampo.value.practicaOtroDeporte
      ? (formDataDeportista.value.practica_otro_deporte || false)
      : undefined
  }
}

const agregarDatosParticipaEscuela = (datosInfo) => {
  if (puedeEditarCampo.value.participaEscuela !== undefined) {
    datosInfo.participa_escuela = puedeEditarCampo.value.participaEscuela
      ? (formDataDeportista.value.participa_escuela || false)
      : undefined
  }
}

const calcularRecomendacionMedica = () => {
  if (formDataDeportista.value.tiene_enfermedades === true) {
    return formDataDeportista.value.recomendacion_medica
  }
  return false
}

const calcularDescripcionRecomendacion = () => {
  const tieneEnfermedades = formDataDeportista.value.tiene_enfermedades === true
  const tieneRecomendacion = formDataDeportista.value.recomendacion_medica

  if (tieneEnfermedades && tieneRecomendacion) {
    return formDataDeportista.value.descripcion_recomendacion
  }
  return null
}

const agregarDatosAntecedentesMedicos = (datosInfo) => {
  if (!puedeEditarCampo.value.antecedentesMedicos) {
    return
  }

  datosInfo.recomendacion_medica = calcularRecomendacionMedica()
  datosInfo.descripcion_recomendacion = calcularDescripcionRecomendacion()
}

const prepararDatosInformacionDeportiva = () => {
  const datosInfo = {}

  agregarDatosDeporte(datosInfo)
  agregarDatosEscuela(datosInfo)
  agregarDatosInstitucion(datosInfo)
  agregarDatosPracticaDeporte(datosInfo)
  agregarDatosParticipaEscuela(datosInfo)
  agregarDatosAntecedentesMedicos(datosInfo)

  return datosInfo
}

const limpiarObjetosVacios = (obj) => {
  Object.keys(obj).forEach(key => {
    if (obj[key] === undefined) {
      delete obj[key]
    }
  })
}

const agregarDatosDiagnostico = (datosDeportistaActualizar) => {
  if (!puedeEditarCampo.value.antecedentesMedicos) {
    return
  }

  if (formDataDeportista.value.tiene_enfermedades === true) {
    if (formDataDeportista.value.tipo_enfermedad) {
      datosDeportistaActualizar.tipo_enfermedad = formDataDeportista.value.tipo_enfermedad
    }
    if (formDataDeportista.value.diagnostico && formDataDeportista.value.diagnostico.length > 0) {
      datosDeportistaActualizar.diagnostico = formDataDeportista.value.diagnostico.map(d => parseInt(d))
    }
  } else if (formDataDeportista.value.tiene_enfermedades === false) {
    datosDeportistaActualizar.diagnostico = []
  }
}

const agregarPesoAltura = (datosDeportista) => {
  if (!puedeEditarPesoAltura.value) {
    return
  }

  if (formDataDeportista.value.peso !== null) {
    datosDeportista.peso = parseFloat(formDataDeportista.value.peso)
  }
  if (formDataDeportista.value.altura !== null) {
    datosDeportista.altura = parseFloat(formDataDeportista.value.altura)
  }
}

const actualizarDeportista = async (idDeportista, datosDeportistaActualizar) => {
  try {
    const resultadoDeportista = await deportistasService.actualizarDeportista(
      idDeportista,
      datosDeportistaActualizar
    )

    if (!resultadoDeportista.success) {
      console.warn('Error al actualizar deportista:', resultadoDeportista.message)
    }
  } catch (err) {
    console.error('Error al actualizar datos del deportista:', err)
  }
}

const mostrarExitoYRecargar = async () => {
  mensajeExito.value = 'Información actualizada correctamente'

  await Swal.fire({
    icon: 'success',
    title: 'Cambios guardados',
    text: 'Tu perfil se actualizó correctamente.',
    timer: 1500,
    showConfirmButton: false
  })

  await authStore.loadUserProfileDetail()
  await authStore.loadUserProfile()
  router.push('/perfil')
}

const actualizarInformacion = async () => {
  if (guardando.value) {
    return
  }

  if (!(await confirmarActualizacion())) {
    return
  }

  guardando.value = true
  error.value = null
  mensajeExito.value = null

  try {
    const idUsuario = authStore.user?.id_usuario
    if (!idUsuario) {
      throw new Error('No se pudo obtener el ID del usuario.')
    }

    const datosPersona = prepararDatosPersona()
    const datosUsuario = prepararDatosUsuario()

    const resultado = await authService.updateUser(idUsuario, datosPersona, datosUsuario)

    if (!resultado.success) {
      throw new Error(resultado.error || 'Error al actualizar la información')
    }

    if (esDeportista.value) {
      const idDeportista = authStore.userDetail?.deportista?.id_deportista ||
                          authStore.user?.deportista?.id_deportista

      if (idDeportista) {
        const datosDeportista = prepararDatosDeportistaBasicos()
        const datosInfo = prepararDatosInformacionDeportiva()

        const datosDeportistaActualizar = {
          datos_deportista: datosDeportista,
          datos_informacion_deportiva: datosInfo
        }

        limpiarObjetosVacios(datosDeportistaActualizar.datos_deportista)
        limpiarObjetosVacios(datosDeportistaActualizar.datos_informacion_deportiva)

        agregarDatosDiagnostico(datosDeportistaActualizar)
        agregarPesoAltura(datosDeportistaActualizar.datos_deportista)

        await actualizarDeportista(idDeportista, datosDeportistaActualizar)
      }
    }

    await mostrarExitoYRecargar()
  } catch (err) {
    console.error('Error actualizando información:', err)
    error.value = err.message || 'Error al actualizar la información. Por favor, intenta nuevamente.'
    await Swal.fire({
      icon: 'error',
      title: 'No pudimos actualizar',
      text: err.message || 'Intenta de nuevo en unos minutos.'
    })
  } finally {
    guardando.value = false
  }
}

const cancelar = async () => {
  const result = await Swal.fire({
    icon: 'question',
    title: '¿Descartar cambios?',
    text: 'Los cambios sin guardar se perderán.',
    showCancelButton: true,
    confirmButtonText: 'Sí, salir',
    cancelButtonText: 'Continuar editando'
  })
  if (result.isConfirmed) {
    router.push('/perfil')
  }
}

onMounted(async () => {
  await Promise.all([
    cargarCatalogos(),
    cargarDatosUsuario()
  ])

  // Si es deportista, cargar catálogos específicos
  if (esDeportista.value) {
    await cargarCatalogosDeportista()
  }
})
</script>

