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
                  @input="(event) => puedeEditarCampo.primerNombre && manejarEntradaNombre('primer_nombre', event)"
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
                  @input="(event) => puedeEditarCampo.segundoNombre && manejarEntradaNombre('segundo_nombre', event, false)"
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
                  @input="(event) => puedeEditarCampo.primerApellido && manejarEntradaNombre('primer_apellido', event)"
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
                  @input="(event) => puedeEditarCampo.segundoApellido && manejarEntradaNombre('segundo_apellido', event, false)"
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
                  @input="(event) => puedeEditarCampo.numeroDocumento && manejarDocumento(event)"
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
                  @input="manejarCorreo"
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
                  @input="manejarTelefono"
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
                @input="manejarEntradaDireccion"
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
                @input="manejarUsuario"
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
              <label for="practica-otro-deporte-group">¿Practica otro deporte además del principal?</label>
              <div id="practica-otro-deporte-group" style="display: flex; gap: 1rem; margin-top: 0.5rem;" role="radiogroup" aria-labelledby="practica-otro-deporte-label">
                <label for="practica-otro-deporte-si" style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                  <input
                    id="practica-otro-deporte-si"
                    type="radio"
                    v-model="formDataDeportista.practica_otro_deporte"
                    :value="true"
                  >
                  Sí
                </label>
                <label for="practica-otro-deporte-no" style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                  <input
                    id="practica-otro-deporte-no"
                    type="radio"
                    v-model="formDataDeportista.practica_otro_deporte"
                    :value="false"
                  >
                  No
                </label>
              </div>
            </div>

            <div class="form-group">
              <label for="participa-escuela-group">¿Participa en escuela de formación?</label>
              <div id="participa-escuela-group" style="display: flex; gap: 1rem; margin-top: 0.5rem;" role="radiogroup" aria-labelledby="participa-escuela-label">
                <label for="participa-escuela-si" style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                  <input
                    id="participa-escuela-si"
                    type="radio"
                    v-model="formDataDeportista.participa_escuela"
                    :value="true"
                    :disabled="!puedeEditarCampo.participaEscuela"
                  >
                  Sí
                </label>
                <label for="participa-escuela-no" style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                  <input
                    id="participa-escuela-no"
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
              <label for="tiene-enfermedades-group">¿Tiene alguna enfermedad o condición médica?</label>
              <div id="tiene-enfermedades-group" style="display: flex; gap: 1rem; margin-top: 0.5rem;" role="radiogroup" aria-labelledby="tiene-enfermedades-label">
                <label for="tiene-enfermedades-si" style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                  <input
                    id="tiene-enfermedades-si"
                    type="radio"
                    v-model="formDataDeportista.tiene_enfermedades"
                    :value="true"
                    :disabled="!puedeEditarCampo.antecedentesMedicos"
                  >
                  Sí
                </label>
                <label for="tiene-enfermedades-no" style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                  <input
                    id="tiene-enfermedades-no"
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
                <fieldset id="diagnosticos-group" style="max-height: 200px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px; padding: 10px; margin-top: 10px;"
                         :style="!puedeEditarCampo.antecedentesMedicos ? 'background-color: #f5f5f5; cursor: not-allowed;' : ''">
                  <legend>Diagnósticos:</legend>
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
                </fieldset>
              </div>

              <div class="form-group">
                <label for="recomendacion-medica-group">¿Existe alguna recomendación médica?</label>
                <div id="recomendacion-medica-group" style="display: flex; gap: 1rem; margin-top: 0.5rem;" role="radiogroup" aria-labelledby="recomendacion-medica-label">
                  <label for="recomendacion-medica-si" style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                    <input
                      id="recomendacion-medica-si"
                      type="radio"
                      v-model="formDataDeportista.recomendacion_medica"
                      :value="true"
                      :disabled="!puedeEditarCampo.antecedentesMedicos"
                    >
                    Sí
                  </label>
                  <label for="recomendacion-medica-no" style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                    <input
                      id="recomendacion-medica-no"
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
import { extraerMensajeError } from '@/utils/error-handling'
import { sanitizarNombre, sanitizarDireccion, sanitizarString } from '@/utils/sanitization'

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

// Guardar datos iniciales para comparar cambios
const formDataInicial = ref({
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

const formDataDeportistaInicial = ref({
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
  const nombresRoles = new Set(userRoles.map(rol => {
    if (typeof rol === 'string') return rol
    if (rol.nombre_rol) return rol.nombre_rol
    return rol.toString()
  }))

  // Prioridad: Entrenador > Deportista > Acudiente
  if (nombresRoles.has('Entrenador') || nombresRoles.has('Administrador') || nombresRoles.has('SuperAdmin')) {
    return 'Entrenador'
  }
  if (nombresRoles.has('Deportista')) {
    return 'Deportista'
  }
  if (nombresRoles.has('Acudiente')) {
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

// Constantes para validación (igual que en formulario-general.vue)
const REGEX_NOMBRE = /^[A-ZÁÉÍÓÚÜÑ ]+$/
const REGEX_CORREO = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i
const MAX_DOCUMENTO = 20
const MIN_DOCUMENTO = 6
const MAX_TELEFONO = 15
const MIN_TELEFONO = 7

// Handlers para validación en tiempo real (igual que en formulario-general.vue)
function manejarEntradaNombre(campo, event, obligatorio = true) {
  if (!event || !event.target) return
  const valor = event.target.value || ''
  const valorSanitizado = sanitizarNombre(valor, obligatorio)
  // Forzar actualización del valor sanitizado
  formData.value[campo] = valorSanitizado
  // Asegurar que el input también muestre el valor sanitizado
  if (event.target.value !== valorSanitizado) {
    event.target.value = valorSanitizado
  }
}

function manejarDocumento(event) {
  if (!event || !event.target) return
  const valor = event.target.value || ''
  const digitos = valor.replace(/\D/g, '').slice(0, MAX_DOCUMENTO) // NOSONAR: S7781 - replaceAll no acepta regex
  formData.value.documento = digitos
  // Asegurar que el input también muestre el valor sanitizado
  if (event.target.value !== digitos) {
    event.target.value = digitos
  }
}

function manejarTelefono(event) {
  if (!event || !event.target) return
  const valor = event.target.value || ''
  const digitos = valor.replace(/\D/g, '').slice(0, MAX_TELEFONO) // NOSONAR: S7781 - replaceAll no acepta regex
  formData.value.telefono = digitos
  // Asegurar que el input también muestre el valor sanitizado
  if (event.target.value !== digitos) {
    event.target.value = digitos
  }
}

function manejarEntradaDireccion(event) {
  if (!event || !event.target) return
  const valor = event.target.value || ''
  const valorSanitizado = sanitizarDireccion(valor)
  formData.value.direccion = valorSanitizado
  // Asegurar que el textarea también muestre el valor sanitizado
  if (event.target.value !== valorSanitizado) {
    event.target.value = valorSanitizado
  }
}

function manejarCorreo(event) {
  if (!event || !event.target) return
  const valor = event.target.value || ''
  const valorSanitizado = valor.trim().toLowerCase()
  formData.value.correo_electronico = valorSanitizado
  // Asegurar que el input también muestre el valor sanitizado
  if (event.target.value !== valorSanitizado) {
    event.target.value = valorSanitizado
  }
}

function manejarUsuario(event) {
  if (!event || !event.target) return
  const valor = event.target.value || ''
  const valorSanitizado = valor.trim()
  formData.value.usuario = valorSanitizado
  // Asegurar que el input también muestre el valor sanitizado
  if (event.target.value !== valorSanitizado) {
    event.target.value = valorSanitizado
  }
}

const cargarDatosPersona = (persona) => {
  if (!persona) return

  formData.value.primer_nombre = sanitizarNombre(persona.primer_nombre)
  formData.value.segundo_nombre = sanitizarNombre(persona.segundo_nombre, false)
  formData.value.primer_apellido = sanitizarNombre(persona.primer_apellido)
  formData.value.segundo_apellido = sanitizarNombre(persona.segundo_apellido, false)
  formData.value.correo_electronico = (persona.correo_electronico || '').trim().toLowerCase()
  formData.value.telefono = (persona.telefono || '').replace(/\D/g, '') // NOSONAR: S7781 - replaceAll no acepta regex
  formData.value.direccion = sanitizarDireccion(persona.direccion || '')
  formData.value.documento = (persona.documento || '').replace(/\D/g, '') // NOSONAR: S7781 - replaceAll no acepta regex
  formData.value.id_tipo_documento = persona.id_tipo_documento || null
  formData.value.id_sexo = persona.id_sexo || null
}

const cargarDatosUsuarioForm = (detalle, usuario) => {
  if (detalle?.usuario) {
    formData.value.usuario = (detalle.usuario.usuario || '').trim()
  } else if (usuario) {
    formData.value.usuario = (usuario.usuario || usuario.username || '').trim()
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
    formDataDeportista.value.descripcion_recomendacion = sanitizarString(info.descripcion_recomendacion)
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

    // Guardar datos iniciales después de cargar
    try {
      formDataInicial.value = structuredClone(formData.value)
      formDataDeportistaInicial.value = structuredClone(formDataDeportista.value)
    } catch {
      // Fallback to JSON method if structuredClone fails (e.g., with Vue reactive objects)
      formDataInicial.value = JSON.parse(JSON.stringify(formData.value)) // NOSONAR: S7784
      formDataDeportistaInicial.value = JSON.parse(JSON.stringify(formDataDeportista.value)) // NOSONAR: S7784
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

// Función para normalizar valores para comparación
function normalizarValorParaComparacion(valor) {
  if (valor === null || valor === undefined) {
    return ''
  }
  if (typeof valor === 'string') {
    return sanitizarString(valor)
  }
  if (typeof valor === 'number') {
    return valor
  }
  if (typeof valor === 'boolean') {
    return valor
  }
  if (Array.isArray(valor)) {
    return valor.map(v => typeof v === 'object' ? v.id_diagnostico || v : v).sort()
  }
  return valor
}

// Verificar si hay cambios
function verificarCambios() {
  // Comparar datos de persona
  const camposPersona = ['primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
                          'correo_electronico', 'telefono', 'direccion', 'usuario', 'id_sexo']

  for (const campo of camposPersona) {
    const valorInicial = normalizarValorParaComparacion(formDataInicial.value[campo])
    const valorActual = normalizarValorParaComparacion(formData.value[campo])
    if (valorInicial !== valorActual) {
      return true
    }
  }

  // Comparar datos de deportista si es deportista
  if (esDeportista.value) {
    const camposDeportista = ['id_tipo_sanguineo', 'id_ciudad_residencia', 'id_eps', 'id_categoria',
                              'peso', 'altura', 'id_deporte', 'id_escuela', 'id_institucion_registro',
                              'practica_otro_deporte', 'participa_escuela', 'tiene_enfermedades',
                              'tipo_enfermedad', 'recomendacion_medica', 'descripcion_recomendacion']

    for (const campo of camposDeportista) {
      const valorInicial = normalizarValorParaComparacion(formDataDeportistaInicial.value[campo])
      const valorActual = normalizarValorParaComparacion(formDataDeportista.value[campo])
      if (valorInicial !== valorActual) {
        return true
      }
    }

    // Comparar diagnóstico (array)
    const diagnosticoInicial = normalizarValorParaComparacion(formDataDeportistaInicial.value.diagnostico)
    const diagnosticoActual = normalizarValorParaComparacion(formDataDeportista.value.diagnostico)
    if (JSON.stringify(diagnosticoInicial) !== JSON.stringify(diagnosticoActual)) {
      return true
    }
  }

  return false
}

// Helper functions to reduce cognitive complexity in validarFormulario
// Extracted individual validation functions following SRP (Single Responsibility Principle)
function _validarCampoNombre(campo, nombreCampo, errores) {
  if (!campo) return
  if (!REGEX_NOMBRE.test(campo)) {
    errores.push(`El ${nombreCampo} solo debe contener letras y espacios`)
  }
}

function _validarNombresEntrenador(errores) {
  if (rolUsuario.value !== 'Entrenador') return

  if (puedeEditarCampo.value.primerNombre && formData.value.primer_nombre) {
    _validarCampoNombre(formData.value.primer_nombre, 'primer nombre', errores)
  }
  if (puedeEditarCampo.value.primerApellido && formData.value.primer_apellido) {
    _validarCampoNombre(formData.value.primer_apellido, 'primer apellido', errores)
  }
  if (puedeEditarCampo.value.segundoNombre && formData.value.segundo_nombre) {
    _validarCampoNombre(formData.value.segundo_nombre, 'segundo nombre', errores)
  }
  if (puedeEditarCampo.value.segundoApellido && formData.value.segundo_apellido) {
    _validarCampoNombre(formData.value.segundo_apellido, 'segundo apellido', errores)
  }
}

function _validarCorreo(errores) {
  if (formData.value.correo_electronico && !REGEX_CORREO.test(formData.value.correo_electronico)) {
    errores.push('Ingrese un correo electrónico válido')
  }
}

function _validarTelefono(errores) {
  if (!puedeEditarCampo.value.telefono || !formData.value.telefono) return
  const telefonoLimpio = formData.value.telefono.replace(/\D/g, '') // NOSONAR: S7781 - replaceAll no acepta regex
  if (telefonoLimpio.length < MIN_TELEFONO || telefonoLimpio.length > MAX_TELEFONO) {
    errores.push(`El teléfono debe tener entre ${MIN_TELEFONO} y ${MAX_TELEFONO} dígitos`)
  }
}

function _validarDocumento(errores) {
  if (!puedeEditarCampo.value.numeroDocumento || !formData.value.documento) return
  const documentoLimpio = formData.value.documento.replace(/\D/g, '') // NOSONAR: S7781 - replaceAll no acepta regex
  if (documentoLimpio.length < MIN_DOCUMENTO || documentoLimpio.length > MAX_DOCUMENTO) {
    errores.push(`El número de documento debe tener entre ${MIN_DOCUMENTO} y ${MAX_DOCUMENTO} dígitos`)
  }
}

function _validarUsuario(errores) {
  if (!formData.value.usuario) return
  const usuarioLimpio = formData.value.usuario.trim()
  if (usuarioLimpio.length < 3) {
    errores.push('El nombre de usuario debe tener al menos 3 caracteres')
  }
  if (usuarioLimpio.length > 200) {
    errores.push('El nombre de usuario no puede exceder 200 caracteres')
  }
}

// Función para validar formulario antes de guardar (igual que en formulario-general.vue)
// Refactored to reduce cognitive complexity by extracting helper functions
function validarFormulario() {
  const errores = []
  _validarNombresEntrenador(errores)
  _validarCorreo(errores)
  _validarTelefono(errores)
  _validarDocumento(errores)
  _validarUsuario(errores)
  return errores
}

const confirmarActualizacion = async () => {
  const confirmacion = await Swal.fire({
    icon: 'question',
    title: '¿Guardar cambios?',
    text: '¿Estás seguro de que deseas guardar los cambios en tu perfil?',
    showCancelButton: true,
    confirmButtonText: 'Sí, guardar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#004AAD',
    cancelButtonColor: '#6c757d'
  })
  return confirmacion.isConfirmed
}

const prepararDatosPersona = () => {
  const datosPersona = {
    correo_electronico: (formData.value.correo_electronico || '').trim().toLowerCase()
  }

  if (puedeEditarCampo.value.telefono && formData.value.telefono) {
    datosPersona.telefono = formData.value.telefono.replace(/\D/g, '') // NOSONAR: S7781 - replaceAll no acepta regex
  }
  if (puedeEditarCampo.value.direccion && formData.value.direccion) {
    datosPersona.direccion = sanitizarDireccion(formData.value.direccion)
  }

  if (rolUsuario.value === 'Entrenador') {
    datosPersona.primer_nombre = sanitizarNombre(formData.value.primer_nombre)
    datosPersona.primer_apellido = sanitizarNombre(formData.value.primer_apellido)
    datosPersona.id_sexo = formData.value.id_sexo

    if (formData.value.segundo_nombre) {
      datosPersona.segundo_nombre = sanitizarNombre(formData.value.segundo_nombre, false)
    }
    if (formData.value.segundo_apellido) {
      datosPersona.segundo_apellido = sanitizarNombre(formData.value.segundo_apellido, false)
    }
  }

  return datosPersona
}

const prepararDatosUsuario = () => {
  return {
    usuario: (formData.value.usuario || '').trim()
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
  const descripcion = calcularDescripcionRecomendacion()
  if (descripcion) {
    datosInfo.descripcion_recomendacion = sanitizarString(descripcion)
  }
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
      datosDeportistaActualizar.diagnostico = formDataDeportista.value.diagnostico.map(d => Number.parseInt(d, 10))
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
    datosDeportista.peso = Number.parseFloat(formDataDeportista.value.peso)
  }
  if (formDataDeportista.value.altura !== null) {
    datosDeportista.altura = Number.parseFloat(formDataDeportista.value.altura)
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
    title: '¡Perfil actualizado exitosamente!',
    text: 'Tu información se ha guardado correctamente en el sistema.',
    confirmButtonText: 'Aceptar',
    confirmButtonColor: '#004AAD'
  })

  await authStore.loadUserProfileDetail()
  await authStore.loadUserProfile()

  // Actualizar datos iniciales con los nuevos datos guardados
  try {
    formDataInicial.value = structuredClone(formData.value)
    formDataDeportistaInicial.value = structuredClone(formDataDeportista.value)
  } catch {
    // Fallback to JSON method if structuredClone fails (e.g., with Vue reactive objects)
    try {
      formDataInicial.value = structuredClone(formData.value)
      formDataDeportistaInicial.value = structuredClone(formDataDeportista.value)
    } catch {
      // Fallback to JSON method if structuredClone fails (e.g., with Vue reactive objects)
      formDataInicial.value = JSON.parse(JSON.stringify(formData.value)) // NOSONAR: S7784
      formDataDeportistaInicial.value = JSON.parse(JSON.stringify(formDataDeportista.value)) // NOSONAR: S7784
    }
  }

  router.push('/perfil')
}

const actualizarInformacion = async () => {
  if (guardando.value) {
    return
  }

  // Verificar si hay cambios antes de continuar
  const tieneCambios = verificarCambios()

  if (!tieneCambios) {
    await Swal.fire({
      icon: 'info',
      title: 'Sin cambios',
      text: 'No se han realizado modificaciones en tu perfil. No hay nada que guardar.',
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#004AAD'
    })
    return
  }

  // Validar formulario antes de continuar
  const erroresValidacion = validarFormulario()
  if (erroresValidacion.length > 0) {
    await Swal.fire({
      icon: 'error',
      title: 'Corrige los errores',
      html: `<p><strong>Por favor corrige los siguientes errores:</strong></p><p>${erroresValidacion.join('<br>')}</p>`,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    })
    return
  }

  if (!(await confirmarActualizacion())) {
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

    // Cerrar el loading
    Swal.close()

    if (!resultado.success) {
      const mensajeError = extraerMensajeError(resultado.error)
      await Swal.fire({
        icon: 'error',
        title: 'Error al actualizar perfil',
        html: `<p><strong>No se pudieron guardar los cambios.</strong></p><p>${mensajeError}</p>`,
        confirmButtonText: 'Entendido',
        confirmButtonColor: '#dc3545'
      })
      error.value = mensajeError
      return
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
    // Cerrar el loading si aún está abierto
    Swal.close()

    console.error('Error actualizando información:', err)
    const mensajeError = extraerMensajeError(err)
    error.value = mensajeError

    await Swal.fire({
      icon: 'error',
      title: 'Error al actualizar perfil',
      html: `<p><strong>Ocurrió un error inesperado.</strong></p><p>${mensajeError}</p>`,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    })
  } finally {
    guardando.value = false
  }
}


const cancelar = async () => {
  // Verificar si hay cambios sin guardar
  const tieneCambios = verificarCambios()

  if (tieneCambios) {
    const result = await Swal.fire({
      icon: 'question',
      title: '¿Descartar cambios?',
      text: '¿Estás seguro de que deseas salir? Los cambios sin guardar se perderán.',
      showCancelButton: true,
      confirmButtonText: 'Sí, salir',
      cancelButtonText: 'Continuar editando',
      confirmButtonColor: '#dc3545',
      cancelButtonColor: '#6c757d'
    })
    if (result.isConfirmed) {
      router.push('/perfil')
    }
  } else {
    // Si no hay cambios, solo confirmar salida
    const result = await Swal.fire({
      icon: 'question',
      title: '¿Salir de la edición?',
      text: '¿Estás seguro de que deseas salir sin guardar cambios?',
      showCancelButton: true,
      confirmButtonText: 'Sí, salir',
      cancelButtonText: 'Continuar',
      confirmButtonColor: '#6c757d',
      cancelButtonColor: '#004AAD'
    })
    if (result.isConfirmed) {
      router.push('/perfil')
    }
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

