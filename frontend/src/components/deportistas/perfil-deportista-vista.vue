<template>
  <div class="perfil-deportista-vista">
    <div class="modal-header">
      <h2 class="modal-title">{{ isEditing ? '✏️ Editar Deportista' : '📋 Información del Deportista' }}</h2>
      <button class="btn-cerrar" @click="isEditing ? cancelarEdicion() : $emit('cerrar')" :title="isEditing ? 'Cancelar' : 'Cerrar'">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <div class="modal-body" v-if="datos && catalogosCargados">
      <!-- Debug temporal - eliminar en producción -->
      <div style="display: none;">
        <pre>{{ JSON.stringify(datos, null, 2) }}</pre>
      </div>

      <!-- Información Personal -->
      <div class="perfil-card" v-if="datos">
        <div class="card-header">
          <h3>👤 Información Personal</h3>
        </div>
        <div class="card-content">
          <div class="info-grid">
            <div class="info-row">
              <label>Nombre completo:</label>
              <span v-if="!isEditing">{{ obtenerNombreCompleto() || 'No disponible' }}</span>
              <span v-else class="readonly-field">{{ obtenerNombreCompleto() || 'No disponible' }}</span>
            </div>
            <div class="info-row">
              <label>Primer nombre:</label>
              <span v-if="!isEditing">{{ datos.persona?.primer_nombre || datos.nombre1 || '—' }}</span>
              <input
                v-else
                v-model="formData.primer_nombre"
                type="text"
                class="input-editable"
                :disabled="!campoEditable('persona', 'primer_nombre')"
                @input="(event) => campoEditable('persona', 'primer_nombre') && manejarEntradaNombre('primer_nombre', event)"
              />
            </div>
            <div class="info-row">
              <label>Segundo nombre:</label>
              <span v-if="!isEditing">{{ datos.persona?.segundo_nombre || datos.nombre2 || '—' }}</span>
              <input
                v-else
                v-model="formData.segundo_nombre"
                type="text"
                class="input-editable"
                :disabled="!campoEditable('persona', 'segundo_nombre')"
                @input="(event) => campoEditable('persona', 'segundo_nombre') && manejarEntradaNombre('segundo_nombre', event, false)"
              />
            </div>
            <div class="info-row">
              <label>Primer apellido:</label>
              <span v-if="!isEditing">{{ datos.persona?.primer_apellido || datos.apellido1 || '—' }}</span>
              <input
                v-else
                v-model="formData.primer_apellido"
                type="text"
                class="input-editable"
                :disabled="!campoEditable('persona', 'primer_apellido')"
                @input="(event) => campoEditable('persona', 'primer_apellido') && manejarEntradaNombre('primer_apellido', event)"
              />
            </div>
            <div class="info-row">
              <label>Segundo apellido:</label>
              <span v-if="!isEditing">{{ datos.persona?.segundo_apellido || datos.apellido2 || '—' }}</span>
              <input
                v-else
                v-model="formData.segundo_apellido"
                type="text"
                class="input-editable"
                :disabled="!campoEditable('persona', 'segundo_apellido')"
                @input="(event) => campoEditable('persona', 'segundo_apellido') && manejarEntradaNombre('segundo_apellido', event, false)"
              />
            </div>
            <div class="info-row">
              <label>Tipo de documento:</label>
              <span>{{ obtenerTipoDocumento() || '—' }}</span>
            </div>
            <div class="info-row">
              <label>Documento:</label>
              <span v-if="!isEditing">{{ datos.persona?.documento || datos.documento || '—' }}</span>
              <input
                v-else
                v-model="formData.documento"
                type="text"
                class="input-editable"
                :disabled="!campoEditable('persona', 'documento')"
                @input="(event) => campoEditable('persona', 'documento') && manejarDocumento(event)"
              />
            </div>
            <div class="info-row">
              <label>Correo electrónico:</label>
              <span v-if="!isEditing">{{ datos.persona?.correo_electronico || datos.correo || '—' }}</span>
              <input
                v-else
                v-model="formData.correo_electronico"
                type="email"
                class="input-editable"
                :disabled="!campoEditable('persona', 'correo_electronico')"
                @input="manejarCorreo"
              />
            </div>
            <div class="info-row">
              <label>Teléfono:</label>
              <span v-if="!isEditing">{{ datos.persona?.telefono || datos.telefono || '—' }}</span>
              <input
                v-else
                v-model="formData.telefono"
                type="tel"
                class="input-editable"
                :disabled="!campoEditable('persona', 'telefono')"
                @input="manejarTelefono"
              />
            </div>
            <div class="info-row">
              <label>Dirección:</label>
              <span v-if="!isEditing">{{ datos.persona?.direccion || datos.direccion || '—' }}</span>
              <input
                v-else
                v-model="formData.direccion"
                type="text"
                class="input-editable"
                :disabled="!campoEditable('persona', 'direccion')"
                @input="manejarEntradaDireccion"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Información Deportiva -->
      <div class="perfil-card" v-if="datos">
        <div class="card-header">
          <h3>🏃 Información Deportiva</h3>
        </div>
        <div class="card-content">
          <div class="info-grid">
            <div class="info-row">
              <label>Categoría:</label>
              <span>{{ obtenerCategoria() || '—' }}</span>
            </div>
            <div class="info-row">
              <label>Fecha de nacimiento:</label>
              <span v-if="!isEditing">{{ formatearFechaNacimiento(fechaNacimiento) || '—' }}</span>
              <input
                v-else
                v-model="formData.fecha_nacimiento"
                type="date"
                class="input-editable"
              />
            </div>
            <div class="info-row">
              <label>Peso:</label>
              <span v-if="!isEditing">{{ datosDeportista.peso !== undefined && datosDeportista.peso !== null ? datosDeportista.peso + ' kg' : '—' }}</span>
              <div v-else class="input-with-unit">
                <input
                  v-model="formData.peso"
                  type="number"
                  step="0.1"
                  class="input-editable"
                  placeholder="0.0"
                  :disabled="!puedeEditarMedidas"
                />
                <span class="unit">kg</span>
              </div>
            </div>
            <div class="info-row">
              <label>Altura:</label>
              <span v-if="!isEditing">{{ datosDeportista.altura !== undefined && datosDeportista.altura !== null ? datosDeportista.altura + ' m' : '—' }}</span>
              <div v-else class="input-with-unit">
                <input
                  v-model="formData.altura"
                  type="number"
                  step="0.01"
                  class="input-editable"
                  placeholder="0.00"
                  :disabled="!puedeEditarMedidas"
                />
                <span class="unit">m</span>
              </div>
            </div>
            <div class="info-row">
              <label>Tipo sanguíneo:</label>
              <span v-if="!isEditing">{{ obtenerTipoSanguineo() || '—' }}</span>
              <select
                v-else
                v-model="formData.id_tipo_sanguineo"
                class="input-editable"
                :disabled="!campoEditable('datos', 'id_tipo_sanguineo')"
              >
                <option :value="null">Seleccione</option>
                <option
                  v-for="tipo in catalogos.tiposSanguineos"
                  :key="tipo.id_tipo_sangre || tipo.id_tipo_sanguineo || tipo.id"
                  :value="tipo.id_tipo_sangre ?? tipo.id_tipo_sanguineo ?? tipo.id"
                >
                  {{ tipo.tipo_sangre || tipo.nombre || tipo.tipo }}
                </option>
              </select>
            </div>
            <div class="info-row">
              <label>Ciudad de residencia:</label>
              <span v-if="!isEditing">{{ obtenerCiudad() || '—' }}</span>
              <select
                v-else
                v-model="formData.id_ciudad_recidencia"
                class="input-editable"
                :disabled="!campoEditable('datos', 'id_ciudad_recidencia')"
              >
                <option :value="null">Seleccione</option>
                <option
                  v-for="ciudad in catalogos.ciudades"
                  :key="ciudad.id_ciudad || ciudad.id_ciudad_residencia || ciudad.id"
                  :value="ciudad.id_ciudad ?? ciudad.id_ciudad_residencia ?? ciudad.id"
                >
                  {{ ciudad.nombre_ciudad || ciudad.nombre || ciudad.ciudad }}
                </option>
              </select>
            </div>
            <div class="info-row">
              <label>EPS:</label>
              <span v-if="!isEditing">{{ obtenerEPS() || '—' }}</span>
              <select
                v-else
                v-model="formData.id_eps"
                class="input-editable"
                :disabled="!campoEditable('datos', 'id_eps')"
              >
                <option :value="null">Seleccione</option>
                <option
                  v-for="eps in catalogos.eps"
                  :key="eps.id_eps || eps.id"
                  :value="eps.id_eps ?? eps.id"
                >
                  {{ eps.nombre_eps || eps.nombre || eps.eps }}
                </option>
              </select>
            </div>
            <div v-if="isEditing && !puedeEditarMedidas" class="medidas-aviso">
              Solo un entrenador o administrador puede actualizar peso y altura.
            </div>
          </div>

          <!-- Información Deportiva Detallada -->
          <div class="info-subsection" v-if="datos.informacion_deportiva || isEditing">
            <h4>⚽ Detalles Deportivos</h4>
            <div class="info-grid">
              <div class="info-row">
                <label>Deporte principal:</label>
                <span v-if="!isEditing">{{ obtenerDeporte() || '—' }}</span>
                <select
                  v-else
                  v-model="formData.id_deporte"
                  class="input-editable"
                  :disabled="!campoEditable('informacion', 'id_deporte')"
                >
                  <option :value="null">Seleccione</option>
                  <option
                    v-for="deporte in catalogos.deportes"
                    :key="deporte.id_deporte || deporte.id"
                    :value="deporte.id_deporte ?? deporte.id"
                  >
                    {{ deporte.nombre || deporte.nombre_deporte || deporte.deporte }}
                  </option>
                </select>
              </div>
              <div class="info-row">
                <label>Practica otro deporte:</label>
                <span v-if="!isEditing">
                  <span class="badge" :class="datos.informacion_deportiva?.practica_otro_deporte ? 'badge-success' : 'badge-muted'">
                    {{ datos.informacion_deportiva?.practica_otro_deporte !== undefined ? (datos.informacion_deportiva.practica_otro_deporte ? 'Sí' : 'No') : '—' }}
                  </span>
                </span>
                <div v-else class="radio-group">
                  <label class="radio-option">
                    <input
                      type="radio"
                      :value="true"
                      v-model="formData.practica_otro_deporte"
                      :disabled="!campoEditable('informacion', 'practica_otro_deporte')"
                    />
                    Sí
                  </label>
                  <label class="radio-option">
                    <input
                      type="radio"
                      :value="false"
                      v-model="formData.practica_otro_deporte"
                      :disabled="!campoEditable('informacion', 'practica_otro_deporte')"
                    />
                    No
                  </label>
                </div>
              </div>
              <div class="info-row">
                <label>Participa en escuela:</label>
                <span v-if="!isEditing">
                  <span class="badge" :class="datos.informacion_deportiva?.participa_escuela ? 'badge-success' : 'badge-muted'">
                    {{ datos.informacion_deportiva?.participa_escuela !== undefined ? (datos.informacion_deportiva.participa_escuela ? 'Sí' : 'No') : '—' }}
                  </span>
                </span>
                <div v-else class="radio-group">
                  <label class="radio-option">
                    <input
                      type="radio"
                      :value="true"
                      v-model="formData.participa_escuela"
                      :disabled="!campoEditable('informacion', 'participa_escuela')"
                    />
                    Sí
                  </label>
                  <label class="radio-option">
                    <input
                      type="radio"
                      :value="false"
                      v-model="formData.participa_escuela"
                      :disabled="!campoEditable('informacion', 'participa_escuela')"
                    />
                    No
                  </label>
              </div>
              </div>
              <div class="info-row" v-if="isEditing || datos.informacion_deportiva?.participa_escuela">
                <label>Escuela:</label>
                <span v-if="!isEditing">{{ obtenerEscuela() || '—' }}</span>
                <select
                  v-else
                  v-model="formData.id_escuela"
                  class="input-editable"
                  :disabled="!formData.participa_escuela || !campoEditable('informacion', 'id_escuela')"
                >
                  <option :value="null">Seleccione</option>
                  <option
                    v-for="escuela in catalogos.escuelas"
                    :key="escuela.id_escuela || escuela.id"
                    :value="escuela.id_escuela ?? escuela.id"
                  >
                    {{ escuela.nombre_escuela || escuela.nombre || escuela.escuela }}
                  </option>
                </select>
              </div>
              <div class="info-row">
                <label>Institución de registro:</label>
                <span v-if="!isEditing">{{ obtenerInstitucion() || '—' }}</span>
                <select
                  v-else
                  v-model="formData.id_institucion_registro"
                  class="input-editable"
                  :disabled="!campoEditable('informacion', 'id_institucion_registro')"
                >
                  <option :value="null">Seleccione</option>
                  <option
                    v-for="institucion in catalogos.instituciones"
                    :key="institucion.id_institucion_registro || institucion.id_institucion || institucion.id"
                    :value="institucion.id_institucion_registro ?? institucion.id_institucion ?? institucion.id"
                  >
                    {{ institucion.nombre_institucion || institucion.nombre || institucion.institucion }}
                  </option>
                </select>
              </div>
              <div class="info-row">
                <label>Recomendación médica:</label>
                <span v-if="!isEditing">
                  <span class="badge" :class="datos.informacion_deportiva?.recomendacion_medica ? 'badge-warning' : 'badge-success'">
                    {{ datos.informacion_deportiva?.recomendacion_medica !== undefined ? (datos.informacion_deportiva.recomendacion_medica ? 'Sí' : 'No') : '—' }}
                  </span>
                </span>
                <div v-else class="radio-group">
                  <label class="radio-option">
                    <input
                      type="radio"
                      :value="true"
                      v-model="formData.recomendacion_medica"
                      :disabled="!campoEditable('informacion', 'recomendacion_medica')"
                    />
                    Sí
                  </label>
                  <label class="radio-option">
                    <input
                      type="radio"
                      :value="false"
                      v-model="formData.recomendacion_medica"
                      :disabled="!campoEditable('informacion', 'recomendacion_medica')"
                    />
                    No
                  </label>
              </div>
              </div>
              <div class="info-row" v-if="(isEditing && formData.recomendacion_medica) || (!isEditing && datos.informacion_deportiva?.descripcion_recomendacion)">
                <label>Descripción recomendación:</label>
                <span v-if="!isEditing">{{ datos.informacion_deportiva.descripcion_recomendacion || '—' }}</span>
                <textarea
                  v-else
                  v-model="formData.descripcion_recomendacion"
                  class="input-editable"
                  rows="3"
                  :disabled="!campoEditable('informacion', 'descripcion_recomendacion')"
                ></textarea>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Información de Salud - Diagnósticos y Enfermedades -->
      <div
        class="perfil-card"
        v-if="datos && (datos.salud || datos.informacion_deportiva?.recomendacion_medica || isEditing)"
      >
        <div class="card-header">
          <h3>🏥 Información de Salud</h3>
        </div>
        <div class="card-content">
          <div class="info-grid">
            <!-- Tipos de Enfermedad -->
            <div class="info-row" v-if="isEditing || (datos.salud?.tipos_enfermedad_ids && datos.salud.tipos_enfermedad_ids.length > 0)">
              <label>Tipo de enfermedad:</label>
              <div v-if="isEditing">
                <select
                  v-model="formData.id_tipo_enfermedad"
                  class="input-editable"
                  :disabled="!campoEditable('salud', 'id_tipo_enfermedad')"
                >
                  <option :value="null">Seleccione</option>
                  <option
                    v-for="tipo in catalogos.tiposEnfermedad"
                    :key="tipo.id_tipo_enfermedad || tipo.id"
                    :value="tipo.id_tipo_enfermedad ?? tipo.id"
                  >
                    {{ tipo.nombre || tipo.nombre_tipo_enfermedad || tipo.tipo_enfermedad }}
                  </option>
                </select>
              </div>
              <span v-else>
                <span
                  v-for="idTipo in datos.salud?.tipos_enfermedad_ids || []"
                  :key="`tipo-${idTipo}`"
                  class="badge badge-info"
                  style="margin-right: 0.5rem;"
                >
                  {{ obtenerTipoEnfermedad(idTipo) || `ID: ${idTipo}` }}
                </span>
                <span v-if="!datos.salud?.tipos_enfermedad_ids || datos.salud.tipos_enfermedad_ids.length === 0">—</span>
              </span>
            </div>

            <!-- Diagnósticos -->
            <div class="info-row">
              <label>Diagnósticos:</label>
              <template v-if="isEditing">
                <div class="diagnosticos-editor">
                  <template v-if="diagnosticosDisponibles.length > 0">
                    <label
                      v-for="diag in diagnosticosDisponibles"
                      :key="diag.id_diagnostico || diag.id"
                      class="checkbox-line"
                    >
                      <input
                        type="checkbox"
                        :value="diag.id_diagnostico ?? diag.id"
                        v-model="formData.diagnosticos"
                        :disabled="!campoEditable('salud', 'diagnosticos')"
                      />
                      {{ diag.nombre || diag.nombre_diagnostico || diag.diagnostico }}
                    </label>
                  </template>
                  <span v-else class="diagnosticos-vacio">
                    No hay diagnósticos disponibles para el tipo seleccionado.
                  </span>
                </div>
              </template>
              <template v-else>
                <div v-if="datos.salud?.diagnosticos && datos.salud.diagnosticos.length > 0" style="display: flex; flex-direction: column; gap: 0.5rem;">
                  <span
                    v-for="(diagnostico, index) in datos.salud.diagnosticos"
                    :key="diagnostico.id_diagnostico || index"
                    class="badge badge-warning"
                    style="display: inline-block; margin-right: 0.5rem;"
                  >
                    {{ obtenerDiagnostico(diagnostico.id_diagnostico) || `ID: ${diagnostico.id_diagnostico}` }}
                  </span>
                </div>
                <span v-else>No hay diagnósticos registrados</span>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Botones de acción - FUERA del modal-body para que el scroll funcione -->
    <div class="perfil-actions" v-if="datos && catalogosCargados">
      <template v-if="!isEditing">
      <button class="btn-editar-perfil" @click="iniciarEdicion">
          <i class="fas fa-edit"></i> Actualizar
      </button>
      <button class="btn-cerrar-perfil" @click="$emit('cerrar')">
        Cerrar
      </button>
      </template>
      <template v-else>
        <button class="btn-guardar-perfil" @click="guardarCambios" :disabled="guardando">
          <i class="fas fa-save"></i> {{ guardando ? 'Guardando...' : 'Guardar Cambios' }}
        </button>
        <button class="btn-cancelar-perfil" @click="cancelarEdicion" :disabled="guardando">
          Cancelar
        </button>
      </template>
    </div>

    <div v-else-if="!catalogosCargados" class="cargando">
      <p>Cargando catálogos...</p>
    </div>
    <div v-else class="cargando">
      <p>Cargando información del deportista...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import catalogosService from '@/services/catalogosService';
import deportistasService from '@/services/deportistasService';
import personasService from '@/services/personasService';
import { getApiUrl } from '@/config/environment';
import { useAuthStore } from '@/stores/auth';
import Swal from 'sweetalert2';

defineOptions({
  name: 'PerfilDeportistaVista'
});

const props = defineProps({
  datos: {
    type: Object,
    default: null
  },
  modoEdicion: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['cerrar', 'editar', 'guardar', 'cancelar']);

const authStore = useAuthStore();

// Catálogos para mapear IDs a nombres
const catalogos = ref({
  tiposSanguineos: [],
  ciudades: [],
  eps: [],
  deportes: [],
  escuelas: [],
  instituciones: [],
  categorias: [],
  tiposEnfermedad: [],
  diagnosticos: [],
  tiposDocumento: []
});

// Estado de carga de catálogos
const catalogosCargados = ref(false);

const guardando = ref(false);
const formData = ref(crearEstadoInicial(props.datos));
// Guardar estado inicial para comparar cambios
const formDataInicial = ref(null);

// Constantes para validación (igual que en formulario-general.vue)
const LOCALE_COL = 'es-CO';
const REGEX_NOMBRE = /^[A-ZÁÉÍÓÚÜÑ ]+$/;
const REGEX_CORREO = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i;
const MAX_DOCUMENTO = 20;
const MIN_DOCUMENTO = 6;
const MAX_TELEFONO = 15;
const MIN_TELEFONO = 7;

// Función para transformar a mayúsculas (igual que en formulario-general.vue)
function transformarMayusculas(valor = '') {
  return valor ? valor.toLocaleUpperCase(LOCALE_COL) : '';
}

// Función para sanitizar nombres (igual que en formulario-general.vue)
function sanitizarNombre(valor = '', obligatorio = true) {
  const mayus = transformarMayusculas(valor);
  const limpio = mayus.replace(/[^A-ZÁÉÍÓÚÜÑ\s]/g, '').replace(/\s{2,}/g, ' ');
  if (!obligatorio && !limpio.trim()) {
    return '';
  }
  return limpio.trimStart();
}

// Función para sanitizar dirección (igual que en formulario-general.vue)
function sanitizarDireccion(valor = '') {
  const mayus = transformarMayusculas(valor);
  return mayus.replace(/[^A-Z0-9ÁÉÍÓÚÜÑ#\-.\s]/g, '').replace(/\s{2,}/g, ' ').trimStart();
}

// Handlers para validación en tiempo real (igual que en formulario-general.vue)
function manejarEntradaNombre(campo, event, obligatorio = true) {
  if (!event || !event.target) return;
  const valor = event.target.value || '';
  const valorSanitizado = sanitizarNombre(valor, obligatorio);
  // Forzar actualización del valor sanitizado
  formData.value[campo] = valorSanitizado;
  // Asegurar que el input también muestre el valor sanitizado
  if (event.target.value !== valorSanitizado) {
    event.target.value = valorSanitizado;
  }
}

function manejarDocumento(event) {
  if (!event || !event.target) return;
  const valor = event.target.value || '';
  const digitos = valor.replace(/\D/g, '').slice(0, MAX_DOCUMENTO);
  formData.value.documento = digitos;
  // Asegurar que el input también muestre el valor sanitizado
  if (event.target.value !== digitos) {
    event.target.value = digitos;
  }
}

function manejarTelefono(event) {
  if (!event || !event.target) return;
  const valor = event.target.value || '';
  const digitos = valor.replace(/\D/g, '').slice(0, MAX_TELEFONO);
  formData.value.telefono = digitos;
  // Asegurar que el input también muestre el valor sanitizado
  if (event.target.value !== digitos) {
    event.target.value = digitos;
  }
}

function manejarEntradaDireccion(event) {
  if (!event || !event.target) return;
  const valor = event.target.value || '';
  const valorSanitizado = sanitizarDireccion(valor);
  formData.value.direccion = valorSanitizado;
  // Asegurar que el input también muestre el valor sanitizado
  if (event.target.value !== valorSanitizado) {
    event.target.value = valorSanitizado;
  }
}

function manejarCorreo(event) {
  if (!event || !event.target) return;
  const valor = event.target.value || '';
  const valorSanitizado = valor.trim().toLowerCase();
  formData.value.correo_electronico = valorSanitizado;
  // Asegurar que el input también muestre el valor sanitizado
  if (event.target.value !== valorSanitizado) {
    event.target.value = valorSanitizado;
  }
}

const isEditing = computed(() => !!props.modoEdicion);

const idPersona = computed(() => props.datos?.persona?.id_persona ?? null);
const idDeportista = computed(() => props.datos?.id ?? props.datos?.id_deportista ?? null);

const PRIORIDAD_ROLES = ['SuperAdmin', 'Administrador', 'Entrenador', 'Acudiente', 'Deportista', 'Usuario'];
const PERMISOS_POR_ROL = {
  SuperAdmin: { persona: '*', datos: '*', informacion: '*', salud: '*' },
  Administrador: { persona: '*', datos: '*', informacion: '*', salud: '*' },
  Entrenador: {
    persona: ['telefono', 'correo_electronico', 'direccion'],
    datos: ['peso', 'altura', 'fecha_nacimiento', 'id_tipo_sanguineo', 'id_ciudad_recidencia', 'id_eps', 'id_categoria'],
    informacion: ['id_deporte', 'practica_otro_deporte', 'participa_escuela', 'id_escuela', 'id_institucion_registro', 'recomendacion_medica', 'descripcion_recomendacion'],
    salud: ['id_tipo_enfermedad', 'diagnosticos']
  },
  Acudiente: {
    persona: ['telefono', 'correo_electronico', 'direccion'],
    datos: ['id_ciudad_recidencia', 'id_eps'],
    informacion: ['recomendacion_medica', 'descripcion_recomendacion'],
    salud: ['id_tipo_enfermedad', 'diagnosticos']
  },
  Deportista: { persona: [], datos: [], informacion: [], salud: [] },
  Usuario: { persona: [], datos: [], informacion: [], salud: [] }
};

const rolesUsuario = computed(() => {
  const roles = authStore.user?.roles ?? [];
  return roles.map(rol => {
    if (typeof rol === 'string') return rol;
    if (rol?.nombre_rol) return rol.nombre_rol;
    if (rol?.rol) return rol.rol;
    return String(rol ?? '');
  });
});

const rolActivo = computed(() => {
  const activo = authStore.activeRole;
  if (activo) return activo;
  const encontrado = PRIORIDAD_ROLES.find(rol => rolesUsuario.value.includes(rol));
  return encontrado || rolesUsuario.value[0] || 'Usuario';
});

const permisosRol = computed(() => PERMISOS_POR_ROL[rolActivo.value] || PERMISOS_POR_ROL.Usuario);

const campoEditable = (tipo, campo) => {
  const permisos = permisosRol.value[tipo];
  if (!permisos) return false;
  if (permisos === '*') return true;
  return permisos.includes(campo);
};

const puedeEditarMedidas = computed(() => campoEditable('datos', 'peso') && campoEditable('datos', 'altura'));

const diagnosticosDisponibles = computed(() => {
  const tipoSeleccionado = formData.value.id_tipo_enfermedad;
  if (!tipoSeleccionado) {
    return catalogos.value.diagnosticos || [];
  }
  return (catalogos.value.diagnosticos || []).filter(diag => {
    const idTipo = diag.id_tipo_enfermedad || diag.tipo_enfermedad?.id_tipo_enfermedad;
    return Number(idTipo) === Number(tipoSeleccionado);
  });
});

watch(
  () => props.datos,
  (nuevo) => {
    formData.value = crearEstadoInicial(nuevo);
    // Si no estamos editando, actualizar también el estado inicial
    if (!isEditing.value) {
      formDataInicial.value = JSON.parse(JSON.stringify(formData.value));
    }
  },
  { immediate: true }
);

watch(
  () => props.modoEdicion,
  (nuevo) => {
    if (nuevo) {
      inicializarFormulario();
    }
  }
);

watch(
  () => formData.value.participa_escuela,
  (nuevo) => {
    if (!campoEditable('informacion', 'participa_escuela')) {
      return;
    }
    if (!nuevo) {
      formData.value.id_escuela = null;
    }
  }
);

watch(
  () => formData.value.recomendacion_medica,
  (nuevo) => {
    if (!campoEditable('informacion', 'recomendacion_medica')) {
      return;
    }
    if (!nuevo) {
      formData.value.descripcion_recomendacion = '';
      formData.value.id_tipo_enfermedad = null;
      formData.value.diagnosticos = [];
    } else {
      if (!formData.value.id_tipo_enfermedad && catalogos.value.tiposEnfermedad.length > 0) {
        formData.value.id_tipo_enfermedad = catalogos.value.tiposEnfermedad[0].id_tipo_enfermedad ?? catalogos.value.tiposEnfermedad[0].id ?? null;
      }
    }
  }
);

watch(
  () => formData.value.id_tipo_enfermedad,
  () => {
    if (!campoEditable('salud', 'id_tipo_enfermedad')) {
      return;
    }
    if (!formData.value.id_tipo_enfermedad) {
      formData.value.diagnosticos = [];
      return;
    }
    const disponibles = diagnosticosDisponibles.value.map(diag => diag.id_diagnostico ?? diag.id);
    formData.value.diagnosticos = (formData.value.diagnosticos || []).filter(id => disponibles.includes(id));
  }
);

function crearEstadoInicial(origen = null) {
  const datos = origen ?? props.datos ?? {};
  const persona = datos.persona ?? {};
  const info = datos.informacion_deportiva ?? {};
  const datosDeportista = datos.datos_deportista ?? datos.deportista ?? {};
  const diagnosticosSalud = Array.isArray(datos.salud?.diagnosticos) ? datos.salud.diagnosticos : [];
  const tiposEnfermedadIds = Array.isArray(datos.salud?.tipos_enfermedad_ids) ? datos.salud.tipos_enfermedad_ids : [];

  let tipoEnfermedadInicial = tiposEnfermedadIds.length > 0 ? tiposEnfermedadIds[0] : null;
  if (!tipoEnfermedadInicial && diagnosticosSalud.length > 0) {
    const posibleTipo = diagnosticosSalud[0]?.id_tipo_enfermedad ?? diagnosticosSalud[0]?.diagnostico?.id_tipo_enfermedad;
    tipoEnfermedadInicial = posibleTipo ?? null;
  }

  return {
    primer_nombre: sanitizarNombre(persona.primer_nombre || datos.nombre1 || ''),
    segundo_nombre: sanitizarNombre(persona.segundo_nombre || datos.nombre2 || '', false),
    primer_apellido: sanitizarNombre(persona.primer_apellido || datos.apellido1 || ''),
    segundo_apellido: sanitizarNombre(persona.segundo_apellido || datos.apellido2 || '', false),
    documento: (persona.documento || datos.documento || '').replace(/\D/g, ''),
    correo_electronico: (persona.correo_electronico || datos.correo || '').trim().toLowerCase(),
    telefono: (persona.telefono || datos.telefono || '').replace(/\D/g, ''),
    direccion: sanitizarDireccion(persona.direccion || datos.direccion || ''),
    fecha_nacimiento: normalizarFechaParaInput(
      persona.fecha_nacimiento ||
      datosDeportista.fecha_nacimiento ||
      datos.fecha_nacimiento ||
      null
    ),
    peso: normalizarNumeroParaInput(datosDeportista.peso),
    altura: normalizarNumeroParaInput(datosDeportista.altura),
    practica_otro_deporte: info.practica_otro_deporte ?? false,
    participa_escuela: info.participa_escuela ?? false,
    recomendacion_medica: info.recomendacion_medica ?? false,
    descripcion_recomendacion: info.descripcion_recomendacion || '',
    id_tipo_sanguineo: persona.id_tipo_sanguineo ?? datosDeportista.id_tipo_sanguineo ?? datos.id_tipo_sanguineo ?? null,
    id_ciudad_recidencia: persona.id_ciudad_recidencia ?? datosDeportista.id_ciudad_recidencia ?? datos.id_ciudad_recidencia ?? null,
    id_eps: persona.id_eps ?? datosDeportista.id_eps ?? datos.id_eps ?? null,
    id_deporte: info.id_deporte ?? null,
    id_escuela: info.id_escuela ?? null,
    id_institucion_registro: info.id_institucion_registro ?? null,
    id_categoria: info.id_categoria ?? datosDeportista.id_categoria ?? datos.id_categoria ?? null,
    id_tipo_enfermedad: tipoEnfermedadInicial ? Number(tipoEnfermedadInicial) : null,
    diagnosticos: diagnosticosSalud
      .map(item => item?.id_diagnostico)
      .filter(id => id !== undefined && id !== null)
      .map(id => Number(id))
  };
}

function inicializarFormulario() {
  formData.value = crearEstadoInicial(props.datos);
}

function normalizarNumeroParaInput(valor) {
  if (valor === null || valor === undefined) return '';
  const numero = Number(valor);
  return Number.isFinite(numero) ? numero.toString() : '';
}

function normalizarFechaParaInput(valor) {
  if (!valor) return '';

  if (typeof valor === 'number') {
    return `${valor}-01-01`;
  }

  if (typeof valor === 'string') {
    const trimmed = valor.trim();
    if (!trimmed) return '';
    if (/^\d{4}$/.test(trimmed)) {
      return `${trimmed}-01-01`;
    }
    if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
      return trimmed;
    }
    const parsed = new Date(trimmed);
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.toISOString().slice(0, 10);
    }
    return '';
  }

  if (valor instanceof Date && !Number.isNaN(valor.getTime())) {
    return valor.toISOString().slice(0, 10);
  }

  return '';
}

function prepararFechaParaEnvio(valor) {
  if (!valor) return null;

  if (typeof valor === 'number') {
    return `${valor}-01-01`;
  }

  if (typeof valor === 'string') {
    const trimmed = valor.trim();
    if (!trimmed) return null;
    if (/^\d{4}$/.test(trimmed)) {
      return `${trimmed}-01-01`;
    }
    if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
      return trimmed;
    }
    const parsed = new Date(trimmed);
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.toISOString().slice(0, 10);
    }
    return null;
  }

  if (valor instanceof Date && !Number.isNaN(valor.getTime())) {
    return valor.toISOString().slice(0, 10);
  }

  return null;
}

function limpiarTexto(valor) {
  if (valor === null || valor === undefined) return '';
  return String(valor).trim();
}

function convertirEntero(valor) {
  if (valor === null || valor === undefined || valor === '') return null;
  const numero = parseInt(valor, 10);
  return Number.isNaN(numero) ? null : numero;
}

function convertirDecimal(valor) {
  if (valor === null || valor === undefined || valor === '') return null;
  const numero = parseFloat(String(valor).replace(',', '.'));
  return Number.isNaN(numero) ? null : numero;
}

function limpiarObjeto(obj, opciones = {}) {
  const resultado = {};
  const mantenerBooleanos = opciones.mantenerBooleanos ?? false;
  Object.entries(obj).forEach(([clave, valor]) => {
    if (mantenerBooleanos && typeof valor === 'boolean') {
      resultado[clave] = valor;
      return;
    }
    if (valor !== null && valor !== undefined && valor !== '') {
      resultado[clave] = valor;
    }
  });
  return resultado;
}

function filtrarCamposPermitidos(payload, tipo, opciones = {}) {
  const permisos = permisosRol.value[tipo];
  if (!permisos) return {};
  if (permisos === '*') {
    return limpiarObjeto(payload, opciones);
  }

  const filtrado = {};
  permisos.forEach(campo => {
    if (campo in payload) {
      filtrado[campo] = payload[campo];
    }
  });

  return limpiarObjeto(filtrado, opciones);
}

// Función para normalizar valores para comparación
function normalizarValorParaComparacion(valor) {
  if (valor === null || valor === undefined) {
    return ''
  }
  if (typeof valor === 'string') {
    return valor.trim()
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
  if (!formDataInicial.value) {
    return false
  }

  const campos = [
    'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
    'documento', 'correo_electronico', 'telefono', 'direccion',
    'fecha_nacimiento', 'peso', 'altura', 'practica_otro_deporte',
    'participa_escuela', 'recomendacion_medica', 'descripcion_recomendacion',
    'id_tipo_sanguineo', 'id_ciudad_recidencia', 'id_eps', 'id_deporte',
    'id_escuela', 'id_institucion_registro', 'id_categoria', 'id_tipo_enfermedad'
  ]

  for (const campo of campos) {
    const valorInicial = normalizarValorParaComparacion(formDataInicial.value[campo])
    const valorActual = normalizarValorParaComparacion(formData.value[campo])
    if (valorInicial !== valorActual) {
      return true
    }
  }

  // Comparar diagnosticos (array)
  const diagnosticosInicial = normalizarValorParaComparacion(formDataInicial.value.diagnosticos)
  const diagnosticosActual = normalizarValorParaComparacion(formData.value.diagnosticos)
  if (JSON.stringify(diagnosticosInicial) !== JSON.stringify(diagnosticosActual)) {
    return true
  }

  return false
}

// Extraer mensaje de error de manera legible
function extraerMensajeError(error) {
  if (!error) {
    return 'No se pudo completar la actualización. Por favor, intenta nuevamente.'
  }

  if (typeof error === 'string') {
    return error
  }

  if (error.message) {
    return error.message
  }

  if (error.error) {
    return typeof error.error === 'string' ? error.error : JSON.stringify(error.error)
  }

  if (error.details) {
    return typeof error.details === 'string' ? error.details : JSON.stringify(error.details)
  }

  if (typeof error === 'object') {
    try {
      const errorStr = JSON.stringify(error)
      if (errorStr.length > 200) {
        return 'Error al procesar la solicitud. Verifica que todos los datos sean correctos.'
      }
      return errorStr
    } catch {
      return 'Error desconocido. Por favor, intenta nuevamente.'
    }
  }

  return 'Error desconocido. Por favor, intenta nuevamente.'
}

function iniciarEdicion() {
  inicializarFormulario()
  // Guardar estado inicial cuando se inicia la edición
  formDataInicial.value = JSON.parse(JSON.stringify(formData.value))
  emit('editar')
}

async function cancelarEdicion() {
  // Verificar si hay cambios sin guardar
  const tieneCambios = verificarCambios()
  
  if (tieneCambios) {
    const result = await Swal.fire({
      icon: 'question',
      title: '¿Descartar cambios?',
      text: '¿Estás seguro de que deseas cancelar? Los cambios sin guardar se perderán.',
      showCancelButton: true,
      confirmButtonText: 'Sí, descartar',
      cancelButtonText: 'Continuar editando',
      confirmButtonColor: '#dc3545',
      cancelButtonColor: '#6c757d'
    })
    
    if (!result.isConfirmed) {
      return
    }
  }
  
  inicializarFormulario()
  formDataInicial.value = null
  emit('cancelar')
}

async function validarIdentificadores() {
  if (!idPersona.value || !idDeportista.value) {
    await Swal.fire({
      icon: 'error',
      title: 'No se puede actualizar',
      text: 'No encontramos los identificadores del deportista.'
    });
    return false;
  }
  return true;
}

// Función para validar formulario antes de guardar
function validarFormulario() {
  const errores = [];

  // Validar nombres obligatorios
  if (campoEditable('persona', 'primer_nombre') && formData.value.primer_nombre) {
    if (!REGEX_NOMBRE.test(formData.value.primer_nombre)) {
      errores.push('El primer nombre solo debe contener letras y espacios');
    }
  }

  if (campoEditable('persona', 'primer_apellido') && formData.value.primer_apellido) {
    if (!REGEX_NOMBRE.test(formData.value.primer_apellido)) {
      errores.push('El primer apellido solo debe contener letras y espacios');
    }
  }

  if (campoEditable('persona', 'segundo_nombre') && formData.value.segundo_nombre) {
    if (formData.value.segundo_nombre && !REGEX_NOMBRE.test(formData.value.segundo_nombre)) {
      errores.push('El segundo nombre solo debe contener letras y espacios');
    }
  }

  if (campoEditable('persona', 'segundo_apellido') && formData.value.segundo_apellido) {
    if (formData.value.segundo_apellido && !REGEX_NOMBRE.test(formData.value.segundo_apellido)) {
      errores.push('El segundo apellido solo debe contener letras y espacios');
    }
  }

  // Validar correo electrónico
  if (formData.value.correo_electronico && !REGEX_CORREO.test(formData.value.correo_electronico)) {
    errores.push('Ingrese un correo electrónico válido');
  }

  // Validar teléfono (solo números y longitud)
  if (campoEditable('persona', 'telefono') && formData.value.telefono) {
    const telefonoLimpio = formData.value.telefono.replace(/\D/g, '');
    if (telefonoLimpio.length < MIN_TELEFONO || telefonoLimpio.length > MAX_TELEFONO) {
      errores.push(`El teléfono debe tener entre ${MIN_TELEFONO} y ${MAX_TELEFONO} dígitos`);
    }
  }

  // Validar documento (solo números y longitud) - solo si se puede editar
  if (campoEditable('persona', 'documento') && formData.value.documento) {
    const documentoLimpio = formData.value.documento.replace(/\D/g, '');
    if (documentoLimpio.length < MIN_DOCUMENTO || documentoLimpio.length > MAX_DOCUMENTO) {
      errores.push(`El número de documento debe tener entre ${MIN_DOCUMENTO} y ${MAX_DOCUMENTO} dígitos`);
    }
  }

  return errores;
}

async function validarCamposObligatorios() {
  const camposObligatorios = [
    { campo: 'primer_nombre', etiqueta: 'primer nombre' },
    { campo: 'primer_apellido', etiqueta: 'primer apellido' },
    { campo: 'documento', etiqueta: 'documento' },
    { campo: 'correo_electronico', etiqueta: 'correo electrónico' },
    { campo: 'telefono', etiqueta: 'teléfono' }
  ];

  const faltantes = camposObligatorios.filter(({ campo }) => {
    const valor = formData.value[campo];
    return !valor || (typeof valor === 'string' && !valor.trim());
  });
  
  if (faltantes.length > 0) {
    const lista = faltantes.map(item => item.etiqueta).join(', ');
    await Swal.fire({
      icon: 'warning',
      title: 'Campos obligatorios',
      text: `Completa: ${lista}.`
    });
    return false;
  }
  
  // Validar formato de campos
  const erroresValidacion = validarFormulario();
  if (erroresValidacion.length > 0) {
    await Swal.fire({
      icon: 'error',
      title: 'Corrige los errores',
      html: `<p><strong>Por favor corrige los siguientes errores:</strong></p><p>${erroresValidacion.join('<br>')}</p>`,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    });
    return false;
  }
  
  return true;
}

async function validarRecomendacionMedica() {
  if (!formData.value.recomendacion_medica) {
    return true;
  }

  if (!formData.value.id_tipo_enfermedad) {
    await Swal.fire({
      icon: 'info',
      title: 'Dato requerido',
      text: 'Selecciona un tipo de enfermedad para la recomendación médica.'
    });
    return false;
  }

  if (!formData.value.diagnosticos || formData.value.diagnosticos.length === 0) {
    await Swal.fire({
      icon: 'info',
      title: 'Dato requerido',
      text: 'Selecciona al menos un diagnóstico asociado.'
    });
    return false;
  }

  return true;
}

function calcularEdad(fechaNacimiento) {
  const fecha = new Date(fechaNacimiento);
  const hoy = new Date();
  let edad = hoy.getFullYear() - fecha.getFullYear();
  const mesDiferencia = hoy.getMonth() - fecha.getMonth();

  if (mesDiferencia < 0 || (mesDiferencia === 0 && hoy.getDate() < fecha.getDate())) {
    edad--;
  }

  return edad;
}

async function validarEdadMinima() {
  if (!formData.value.fecha_nacimiento) {
    return true;
  }

  const edad = calcularEdad(formData.value.fecha_nacimiento);
  if (edad < 5) {
    await Swal.fire({
      icon: 'error',
      title: 'Edad inválida',
      text: 'El deportista debe tener mínimo 5 años de edad. La edad mínima de la categoría Pre-infantil es 5 años.'
    });
    return false;
  }

  return true;
}

async function actualizarPersona() {
  const payloadPersona = construirPayloadPersona();
  if (Object.keys(payloadPersona).length > 0) {
    await personasService.actualizarPersona(idPersona.value, payloadPersona);
  }
}

function construirDatosActualizacionDeportista() {
  const payloadDatosDeportista = construirPayloadDatosDeportista();
  const payloadInformacionDeportiva = construirPayloadInformacionDeportiva();
  const payloadSalud = construirPayloadSalud();

  const tieneCambios =
    Object.keys(payloadDatosDeportista).length > 0 ||
    Object.keys(payloadInformacionDeportiva).length > 0 ||
    payloadSalud.necesitaActualizacion;

  if (!tieneCambios) {
    return null;
  }

  const datosActualizacion = {
    datos_deportista: payloadDatosDeportista,
    datos_informacion_deportiva: payloadInformacionDeportiva
  };

  if (payloadSalud.necesitaActualizacion) {
    if ('tipo_enfermedad' in payloadSalud) {
      datosActualizacion.tipo_enfermedad = payloadSalud.tipo_enfermedad;
    }
    if ('diagnostico' in payloadSalud) {
      datosActualizacion.diagnostico = payloadSalud.diagnostico;
    }
  }

  return datosActualizacion;
}

async function guardarCambios() {
  if (!props.datos) {
    return;
  }

  // Verificar si hay cambios antes de continuar
  const tieneCambios = verificarCambios()
  
  if (!tieneCambios) {
    await Swal.fire({
      icon: 'info',
      title: 'Sin cambios',
      text: 'No se han realizado modificaciones en el deportista. No hay nada que guardar.',
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#004AAD'
    })
    return
  }

  // Confirmación antes de guardar
  const confirmacion = await Swal.fire({
    icon: 'question',
    title: '¿Guardar cambios?',
    text: '¿Estás seguro de que deseas guardar los cambios en el deportista?',
    showCancelButton: true,
    confirmButtonText: 'Sí, guardar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#004AAD',
    cancelButtonColor: '#6c757d'
  })

  if (!confirmacion.isConfirmed) {
    return
  }

  if (!(await validarIdentificadores())) {
    return;
  }

  if (!(await validarCamposObligatorios())) {
    return;
  }

  if (!(await validarRecomendacionMedica())) {
    return;
  }

  if (!(await validarEdadMinima())) {
    return;
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

  guardando.value = true;

  try {
    await actualizarPersona();

    const datosActualizacion = construirDatosActualizacionDeportista();
    const respuestaActualizacion = datosActualizacion
      ? await deportistasService.actualizarDeportista(idDeportista.value, datosActualizacion)
      : null;

    // Cerrar el loading
    Swal.close()

    inicializarFormulario();
    // Actualizar estado inicial después de guardar exitosamente
    formDataInicial.value = JSON.parse(JSON.stringify(formData.value))

    await Swal.fire({
      icon: 'success',
      title: '¡Deportista actualizado exitosamente!',
      text: 'La información del deportista se ha guardado correctamente en el sistema.',
      confirmButtonText: 'Aceptar',
      confirmButtonColor: '#004AAD'
    });
    emit('guardar', respuestaActualizacion);
  } catch (error) {
    // Cerrar el loading si aún está abierto
    Swal.close()
    
    console.error('Error al guardar cambios del deportista:', error);
    const mensajeError = extraerMensajeError(error)
    
    await Swal.fire({
      icon: 'error',
      title: 'Error al actualizar deportista',
      html: `<p><strong>No se pudieron guardar los cambios.</strong></p><p>${mensajeError}</p>`,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    });
  } finally {
    guardando.value = false;
  }
}

function construirPayloadPersona() {
  const payload = {};
  const mapaCampos = {
    primer_nombre: 'primer_nombre',
    segundo_nombre: 'segundo_nombre',
    primer_apellido: 'primer_apellido',
    segundo_apellido: 'segundo_apellido',
    direccion: 'direccion'
  };

  Object.entries(mapaCampos).forEach(([campoFormulario, campoBackend]) => {
    const valor = formData.value[campoFormulario];
    if (campoFormulario === 'direccion') {
      // Sanitizar dirección
      const valorSanitizado = sanitizarDireccion(valor || '');
      if (valorSanitizado) {
        payload[campoBackend] = valorSanitizado;
      }
    } else {
      // Sanitizar nombres
      const esObligatorio = campoFormulario === 'primer_nombre' || campoFormulario === 'primer_apellido';
      const valorSanitizado = sanitizarNombre(valor || '', esObligatorio);
      if (valorSanitizado) {
        payload[campoBackend] = valorSanitizado;
      }
    }
  });

  const documento = formData.value.documento;
  if (documento) {
    payload.documento = documento.replace(/\D/g, '');
  }

  const correo = formData.value.correo_electronico;
  if (correo) {
    payload.correo_electronico = correo.trim().toLowerCase();
  }

  const telefono = formData.value.telefono;
  if (telefono) {
    payload.telefono = telefono.replace(/\D/g, '');
  }

  return filtrarCamposPermitidos(payload, 'persona');
}

function construirPayloadDatosDeportista() {
  const payload = {
    peso: convertirDecimal(formData.value.peso),
    altura: convertirDecimal(formData.value.altura),
    fecha_nacimiento: prepararFechaParaEnvio(formData.value.fecha_nacimiento),
    id_categoria: convertirEntero(formData.value.id_categoria),
    id_tipo_sanguineo: convertirEntero(formData.value.id_tipo_sanguineo),
    id_ciudad_recidencia: convertirEntero(formData.value.id_ciudad_recidencia),
    id_eps: convertirEntero(formData.value.id_eps)
  };

  return filtrarCamposPermitidos(payload, 'datos');
}

function construirPayloadInformacionDeportiva() {
  const payload = {
    practica_otro_deporte: !!formData.value.practica_otro_deporte,
    participa_escuela: !!formData.value.participa_escuela,
    recomendacion_medica: !!formData.value.recomendacion_medica,
    descripcion_recomendacion: formData.value.recomendacion_medica
      ? limpiarTexto(formData.value.descripcion_recomendacion) || null
      : null,
    id_escuela: formData.value.participa_escuela ? convertirEntero(formData.value.id_escuela) : null,
    id_deporte: convertirEntero(formData.value.id_deporte),
    id_institucion_registro: convertirEntero(formData.value.id_institucion_registro),
    id_categoria: convertirEntero(formData.value.id_categoria)
  };

  return filtrarCamposPermitidos(payload, 'informacion', { mantenerBooleanos: true });
}

function construirPayloadSalud() {
  const puedeEditarTipo = campoEditable('salud', 'id_tipo_enfermedad');
  const puedeEditarDiagnosticos = campoEditable('salud', 'diagnosticos');

  if (!puedeEditarTipo && !puedeEditarDiagnosticos) {
    return { necesitaActualizacion: false };
  }

  const recomendacion = !!formData.value.recomendacion_medica;
  const tipo = convertirEntero(formData.value.id_tipo_enfermedad);
  const diagnosticosSeleccionados = Array.isArray(formData.value.diagnosticos)
    ? formData.value.diagnosticos
        .map(id => convertirEntero(id))
        .filter(id => id !== null && id !== undefined)
    : [];

  if (!recomendacion) {
    return {
      necesitaActualizacion: true,
      tipo_enfermedad: null,
      diagnostico: []
    };
  }

  return {
    necesitaActualizacion: tipo !== null || diagnosticosSeleccionados.length > 0,
    ...(puedeEditarTipo && tipo !== null ? { tipo_enfermedad: tipo } : {}),
    ...(puedeEditarDiagnosticos ? { diagnostico: diagnosticosSeleccionados } : {})
  };
}

// Cargar catálogos al montar el componente
onMounted(async () => {
  try {
    await cargarCatalogos();
    inicializarFormulario();
    // catalogosCargados se establece dentro de cargarCatalogos()
    // Si ya estamos en modo edición y hay datos, inicializar
    if (isEditing.value && props.datos) {
      console.log('🔄 onMounted: Inicializando formulario en modo edición');
    }
  } catch (error) {
    console.error('Error crítico al cargar catálogos:', error);
    // Aún así, permitir que se muestre el componente
    catalogosCargados.value = true;
  }
});

async function cargarCatalogos() {
  try {
    console.log('🔗 Base URL para catálogos:', getApiUrl(''));

    // Cargar todos los catálogos necesarios desde las rutas de deportistas
    const endpoints = [
      { url: getApiUrl('/api/deportistas/catalogos/grupos-sanguineos'), name: 'grupos-sanguineos' },
      { url: getApiUrl('/api/deportistas/catalogos/ciudades-residencia'), name: 'ciudades-residencia' },
      { url: getApiUrl('/api/deportistas/catalogos/eps'), name: 'eps' },
      { url: getApiUrl('/api/deportistas/catalogos/deportes'), name: 'deportes' },
      { url: getApiUrl('/api/deportistas/catalogos/escuelas'), name: 'escuelas' },
      { url: getApiUrl('/api/deportistas/catalogos/instituciones-registro'), name: 'instituciones-registro' },
      { url: getApiUrl('/api/deportistas/catalogos/tipos-enfermedad'), name: 'tipos-enfermedad' },
      { url: getApiUrl('/api/deportistas/catalogos/diagnosticos'), name: 'diagnosticos' },
      { url: getApiUrl('/api/catalogos/tipos-documento'), name: 'tipos-documento' }
    ];

    // Obtener token de autenticación
    const token = localStorage.getItem('token');
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const resultados = await Promise.all(
      endpoints.map(async (endpoint) => {
        try {
          console.log(`📡 Cargando catálogo: ${endpoint.name} desde ${endpoint.url}`);
          const response = await fetch(endpoint.url);
          const data = await response.json();
          console.log(`✅ ${endpoint.name} cargado:`, response.ok);
          return { name: endpoint.name, ok: response.ok, data };
        } catch (error) {
          console.error(`❌ Error al cargar ${endpoint.name}:`, error);
          return { name: endpoint.name, ok: false, data: null, error: error.message };
        }
      })
    );

    // También cargar categorías usando el servicio
    let categorias = [];
    try {
      categorias = await catalogosService.getCategorias();
      console.log('✅ Categorías cargadas:', categorias);
    } catch (error) {
      console.error('❌ Error al cargar categorías:', error);
    }

    const [sangre, ciudades, eps, deportes, escuelas, instituciones, tiposEnfermedad, diagnosticos, tiposDocumento] = resultados.map(r => r.data);

    // Mapear respuestas - algunas vienen con 'success', otras con 'data' directamente
    const procesarCatalogo = (respuesta, valorPorDefecto = []) => {
      if (!respuesta) return valorPorDefecto;
      if (Array.isArray(respuesta)) return respuesta;
      if (respuesta.success && Array.isArray(respuesta.data)) return respuesta.data;
      if (Array.isArray(respuesta.data)) return respuesta.data;
      return valorPorDefecto;
    };

    catalogos.value.tiposSanguineos = procesarCatalogo(sangre);
    catalogos.value.ciudades = procesarCatalogo(ciudades);
    catalogos.value.eps = procesarCatalogo(eps);
    catalogos.value.deportes = procesarCatalogo(deportes);
    catalogos.value.escuelas = procesarCatalogo(escuelas);
    catalogos.value.instituciones = procesarCatalogo(instituciones);
    catalogos.value.categorias = Array.isArray(categorias) ? categorias : [];
    catalogos.value.tiposEnfermedad = procesarCatalogo(tiposEnfermedad);
    catalogos.value.diagnosticos = procesarCatalogo(diagnosticos);
    catalogos.value.tiposDocumento = procesarCatalogo(tiposDocumento);

    // Logs de debugging
    console.log('📋 ========== RESUMEN DE CATÁLOGOS CARGADOS ==========');
    console.log('📋 Tipos sanguíneos:', catalogos.value.tiposSanguineos.length);
    console.log('📋 Ciudades:', catalogos.value.ciudades.length);
    console.log('📋 EPS:', catalogos.value.eps.length);
    console.log('📋 Deportes:', catalogos.value.deportes.length);
    console.log('📋 Escuelas:', catalogos.value.escuelas.length);
    console.log('📋 Instituciones:', catalogos.value.instituciones.length);
    console.log('📋 Categorías:', catalogos.value.categorias.length);
    console.log('📋 Tipos de enfermedad:', catalogos.value.tiposEnfermedad.length);
    console.log('📋 Diagnósticos:', catalogos.value.diagnosticos.length);
    console.log('📋 Tipos de documento:', catalogos.value.tiposDocumento.length);

    if (catalogos.value.tiposEnfermedad.length > 0) {
      console.log('📋 Ejemplo tipo enfermedad:', catalogos.value.tiposEnfermedad[0]);
    }
    if (catalogos.value.diagnosticos.length > 0) {
      console.log('📋 Ejemplo diagnóstico:', catalogos.value.diagnosticos[0]);
    }
    if (catalogos.value.tiposDocumento.length > 0) {
      console.log('📋 Ejemplo tipo documento:', catalogos.value.tiposDocumento[0]);
    }

    console.log('✅ Catálogos cargados completamente');
    // Marcar como cargado incluso si algunos catálogos fallaron
    catalogosCargados.value = true;
  } catch (error) {
    console.error('Error al cargar catálogos:', error);
    // Aún así, marcar como cargado para que el componente se muestre
    // El perfil puede funcionar sin todos los catálogos
    catalogosCargados.value = true;
  }
}

function obtenerNombreCompleto() {
  if (props.datos?.persona?.nombre_completo) {
    return props.datos.persona.nombre_completo;
  }
  if (props.datos?.persona) {
    const p = props.datos.persona;
    return `${p.primer_nombre || ''} ${p.segundo_nombre || ''} ${p.primer_apellido || ''} ${p.segundo_apellido || ''}`.trim();
  }
  if (props.datos?.nombre) {
    return props.datos.nombre;
  }
  if (props.datos?.nombre1 || props.datos?.apellido1) {
    return `${props.datos.nombre1 || ''} ${props.datos.nombre2 || ''} ${props.datos.apellido1 || ''} ${props.datos.apellido2 || ''}`.trim();
  }
  return null;
}

function obtenerTipoSanguineo() {
  const idTipo =
    props.datos?.persona?.id_tipo_sanguineo ||
    props.datos?.deportista?.id_tipo_sanguineo ||
    props.datos?.datos_deportista?.id_tipo_sanguineo ||
    props.datos?.id_tipo_sanguineo;
  if (!idTipo) return null;
  const tipo = catalogos.value.tiposSanguineos.find(t =>
    t.id_tipo_sangre === idTipo ||
    t.id_tipo_sanguineo === idTipo ||
    t.id === idTipo
  );
  return tipo?.tipo_sangre || tipo?.nombre || tipo?.tipo || null;
}

function obtenerCiudad() {
  const idCiudad =
    props.datos?.persona?.id_ciudad_recidencia ||
    props.datos?.deportista?.id_ciudad_recidencia ||
    props.datos?.datos_deportista?.id_ciudad_recidencia ||
    props.datos?.id_ciudad_recidencia;
  if (!idCiudad) return null;
  const ciudad = catalogos.value.ciudades.find(c =>
    c.id_ciudad === idCiudad ||
    c.id === idCiudad ||
    c.id_ciudad_residencia === idCiudad
  );
  return ciudad?.nombre_ciudad || ciudad?.nombre || ciudad?.ciudad || null;
}

function obtenerEPS() {
  const idEPS =
    props.datos?.persona?.id_eps ||
    props.datos?.deportista?.id_eps ||
    props.datos?.datos_deportista?.id_eps ||
    props.datos?.id_eps;
  if (!idEPS) return null;
  const eps = catalogos.value.eps.find(e =>
    e.id_eps === idEPS ||
    e.id === idEPS
  );
  return eps?.nombre_eps || eps?.nombre || eps?.eps || null;
}

function obtenerDeporte() {
  const idDeporte = props.datos?.informacion_deportiva?.id_deporte ||
                    props.datos?.deportista?.id_deporte;
  if (!idDeporte) return null;
  const deporte = catalogos.value.deportes.find(d =>
    d.id_deporte === idDeporte ||
    d.id === idDeporte
  );
  return deporte?.nombre || deporte?.nombre_deporte || deporte?.deporte || null;
}

function obtenerEscuela() {
  const idEscuela = props.datos?.informacion_deportiva?.id_escuela;
  if (!idEscuela) return null;
  const escuela = catalogos.value.escuelas.find(e =>
    e.id_escuela === idEscuela ||
    e.id === idEscuela
  );
  return escuela?.nombre_escuela || escuela?.nombre || escuela?.escuela || null;
}

function obtenerInstitucion() {
  const idInst = props.datos?.informacion_deportiva?.id_institucion_registro;
  if (!idInst) return null;
  const inst = catalogos.value.instituciones.find(i =>
    i.id_institucion === idInst ||
    i.id_institucion_registro === idInst ||
    i.id === idInst
  );
  return inst?.nombre_institucion || inst?.nombre || inst?.institucion || null;
}

function obtenerCategoria() {
  const idCategoria = props.datos?.informacion_deportiva?.id_categoria ||
                      props.datos?.id_categoria ||
                      props.datos?.deportista?.id_categoria;
  if (!idCategoria) return props.datos?.categoria || null;
  const categoria = catalogos.value.categorias.find(c => c.id_categoria === idCategoria);
  return categoria?.nombre_categoria || props.datos?.categoria || null;
}


// Acceso a datos del deportista (puede venir en diferentes estructuras)
const datosDeportista = computed(() => {
  if (isEditing.value) {
    // En modo edición, usar formData
    return {
      peso: formData.value.peso,
      altura: formData.value.altura,
      fecha_nacimiento: formData.value.fecha_nacimiento
    };
  }
  // El backend devuelve datos en 'datos_deportista' según obtener_informacion_completa_deportista
  return props.datos?.datos_deportista || props.datos?.deportista || props.datos || {};
});

const fechaNacimiento = computed(() => {
  if (isEditing.value) {
    return formData.value.fecha_nacimiento;
  }
  // Buscar fecha de nacimiento en diferentes ubicaciones según la estructura del backend
  return props.datos?.persona?.fecha_nacimiento ||
         props.datos?.datos_deportista?.fecha_nacimiento ||
         datosDeportista.value?.fecha_nacimiento ||
         props.datos?.deportista?.fecha_nacimiento ||
         props.datos?.fecha_nacimiento ||
         null;
});

// Función auxiliar para formatear una fecha Date a DD/MM/YYYY
function formatearDateADDMYYYY(dateObj) {
  const dia = dateObj.getDate().toString().padStart(2, '0');
  const mes = (dateObj.getMonth() + 1).toString().padStart(2, '0');
  const año = dateObj.getFullYear();
  return `${dia}/${mes}/${año}`;
}

// Función auxiliar para validar si un año es válido
function esAnoValido(ano) {
  const anoActual = new Date().getFullYear();
  return ano >= 1900 && ano <= anoActual;
}

// Función auxiliar para formatear un número (año) a fecha
function formatearNumeroComoFecha(fecha) {
  if (!esAnoValido(fecha)) {
    return fecha.toString();
  }
  const fechaCompleta = new Date(fecha, 0, 1);
  return formatearDateADDMYYYY(fechaCompleta);
}

// Función auxiliar para formatear un string que es solo un año
function formatearStringAno(fecha) {
  const año = parseInt(fecha);
  if (!esAnoValido(año)) {
    return null;
  }
  return `01/01/${año}`;
}

// Función auxiliar para formatear un string como fecha ISO
function formatearStringFecha(fecha) {
  try {
    const dateObj = new Date(fecha);
    if (!isNaN(dateObj.getTime())) {
      return formatearDateADDMYYYY(dateObj);
    }
  } catch (error) {
    console.warn('Error al formatear fecha:', error);
  }
  return null;
}

// Función para formatear fecha de nacimiento
function formatearFechaNacimiento(fecha) {
  if (!fecha) return null;

  if (typeof fecha === 'number') {
    return formatearNumeroComoFecha(fecha);
  }

  if (typeof fecha === 'string') {
    return formatearFechaString(fecha);
  }

  if (fecha instanceof Date && !isNaN(fecha.getTime())) {
    return formatearDateADDMYYYY(fecha);
  }

  return fecha;
}

// Función auxiliar para formatear strings de fecha
function formatearFechaString(fecha) {
  if (/^\d{4}$/.test(fecha)) {
    const fechaFormateada = formatearStringAno(fecha);
    if (fechaFormateada) {
      return fechaFormateada;
    }
  }
  const fechaFormateada = formatearStringFecha(fecha);
  return fechaFormateada || fecha;
}

function obtenerTipoEnfermedad(idTipoEnfermedad) {
  if (!idTipoEnfermedad) return null;

  // Si los catálogos aún no están cargados, retornar null
  if (!catalogosCargados.value || !catalogos.value.tiposEnfermedad || catalogos.value.tiposEnfermedad.length === 0) {
    console.warn('⚠️ Catálogos de tipos de enfermedad aún no cargados');
    return null;
  }

  // Convertir ID a número para comparación
  const idBuscado = Number(idTipoEnfermedad);

  // Intentar encontrar el tipo de enfermedad por diferentes campos posibles
  const tipo = catalogos.value.tiposEnfermedad.find(t => {
    if (!t) return false;
    const idTipo = Number(t.id_tipo_enfermedad || t.id || 0);
    return idTipo === idBuscado;
  });

  if (!tipo) {
    console.warn('⚠️ Tipo de enfermedad no encontrado para ID:', idTipoEnfermedad, 'Catálogos disponibles:', catalogos.value.tiposEnfermedad.map(t => ({ id: t.id_tipo_enfermedad || t.id, nombre: t.nombre || t.nombre_tipo_enfermedad })));
    return null;
  }

  // El backend retorna el campo 'nombre' según el modelo TipoEnfermedad
  const nombre = tipo.nombre || tipo.nombre_tipo_enfermedad || tipo.tipo_enfermedad || tipo.tipo || tipo.descripcion || null;
  console.log('✅ Tipo de enfermedad encontrado:', { id: idBuscado, nombre });
  return nombre;
}

function obtenerDiagnostico(idDiagnostico) {
  if (!idDiagnostico) return null;

  // Si los catálogos aún no están cargados, retornar null
  if (!catalogosCargados.value || !catalogos.value.diagnosticos || catalogos.value.diagnosticos.length === 0) {
    console.warn('⚠️ Catálogos de diagnósticos aún no cargados');
    return null;
  }

  // Convertir ID a número para comparación
  const idBuscado = Number(idDiagnostico);

  // Intentar encontrar el diagnóstico por diferentes campos posibles
  const diagnostico = catalogos.value.diagnosticos.find(d => {
    if (!d) return false;
    const idDiag = Number(d.id_diagnostico || d.id || 0);
    return idDiag === idBuscado;
  });

  if (!diagnostico) {
    console.warn('⚠️ Diagnóstico no encontrado para ID:', idDiagnostico, 'Catálogos disponibles:', catalogos.value.diagnosticos.map(d => ({ id: d.id_diagnostico || d.id, nombre: d.nombre || d.nombre_diagnostico })));
    return null;
  }

  // El backend retorna el campo 'nombre' según el modelo Diagnostico
  const nombre = diagnostico.nombre || diagnostico.nombre_diagnostico || diagnostico.diagnostico || diagnostico.descripcion || null;
  console.log('✅ Diagnóstico encontrado:', { id: idBuscado, nombre });
  return nombre;
}

function obtenerTipoDocumento() {
  const idTipoDocumento =
    props.datos?.persona?.id_tipo_documento ||
    props.datos?.id_tipo_documento ||
    props.datos?.deportista?.id_tipo_documento;

  if (!idTipoDocumento) return null;

  const tipoDocumento = catalogos.value.tiposDocumento.find(t =>
    t.id_tipo_documento === idTipoDocumento ||
    t.id_documento === idTipoDocumento ||
    t.id === idTipoDocumento
  );

  return tipoDocumento?.nombre || tipoDocumento?.nombre_documento || tipoDocumento?.tipo || null;
}
</script>


