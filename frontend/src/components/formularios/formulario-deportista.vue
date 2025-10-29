<!-- src/components/formulario-deportista.vue -->
<template>
  <form class="formulario-datos" @submit.prevent="manejarSubmit">
    <!-- Formulario Unificado -->
    <section class="seccion-formulario">
      <h3>{{ obtenerTitulo() }}</h3>

      <!-- Datos Básicos del Deportista -->
      <div class="seccion-titulo">Datos Básicos</div>

      <div class="fila-texto">
        <input
          v-model="form.fecha_nacimiento"
          type="number"
          placeholder="Año de nacimiento (ej: 2005)"
          required
          min="1980"
          :max="new Date().getFullYear()"
          :readonly="modo === 'ver'"
        />
        <select
          v-model="form.id_tipo_sanguineo"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>Tipo sanguíneo</option>
          <option v-for="tipo in catalogos.tiposSanguineos" :key="tipo.id_tipo_sangre" :value="tipo.id_tipo_sangre">
            {{ tipo.tipo_sangre }}
          </option>
        </select>
      </div>

      <div class="fila-texto">
        <select
          v-model="form.id_ciudad_residencia"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>Ciudad de residencia</option>
          <option v-for="ciudad in catalogos.ciudades" :key="ciudad.id_ciudad" :value="ciudad.id_ciudad">
            {{ ciudad.nombre_ciudad }}
          </option>
        </select>
        <select
          v-model="form.id_eps"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>EPS</option>
          <option v-for="eps in catalogos.eps" :key="eps.id_eps" :value="eps.id_eps">
            {{ eps.nombre_eps }}
          </option>
        </select>
      </div>

      <hr class="form-divider" />

      <!-- Información Deportiva -->
      <div class="seccion-titulo">Información Escolar</div>

      <div class="fila-texto">
        <select
          v-model="form.id_institucion_registro"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>Institución de registro</option>
          <option v-for="inst in catalogos.institucionesRegistro" :key="inst.id_institucion" :value="inst.id_institucion">
            {{ inst.nombre_institucion }}
          </option>
        </select>
      </div>
      <hr class="form-divider" />

<!-- INFORMACIÓN DEPORTIVA DEL DEPORTISTA -->
      <div class="seccion-titulo">Información Deportiva</div>

      <!-- Campo de deporte principal -->
      <div class="fila-texto">
        <select
          v-model="form.id_deporte"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>Deporte principal *</option>
          <option v-for="deporte in catalogos.deportes" :key="deporte.id_deporte" :value="deporte.id_deporte">
            {{ deporte.nombre }}
          </option>
        </select>
      </div>

      <div class="bloque-radio">
        <label>¿Practica otro deporte además del principal?</label>
        <div class="opciones">
          <input
            type="radio"
            id="practica-si"
            name="practica-deporte"
            :value="true"
            v-model="form.practica_otro_deporte"
            :disabled="modo === 'ver'"
          />
          <label for="practica-si">Sí</label>
          <input
            type="radio"
            id="practica-no"
            name="practica-deporte"
            :value="false"
            v-model="form.practica_otro_deporte"
            :disabled="modo === 'ver'"
          />
          <label for="practica-no">No</label>
        </div>
      </div>

      <div v-if="form.practica_otro_deporte" class="campo-condicional">
        <select
          v-model="form.id_deporte_secundario"
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>Seleccione el otro deporte</option>
          <option v-for="deporte in catalogos.deportes" :key="deporte.id_deporte" :value="deporte.id_deporte">
            {{ deporte.nombre }}
          </option>
        </select>
      </div>

      <hr class="form-divider" />

      <div class="bloque-radio">
        <label>¿Participa en escuela de formación?</label>
        <div class="opciones">
          <input
            type="radio"
            id="participa-si"
            name="participa-escuela"
            :value="true"
            v-model="form.participa_escuela"
            :disabled="modo === 'ver'"
          />
          <label for="participa-si">Sí</label>
          <input
            type="radio"
            id="participa-no"
            name="participa-escuela"
            :value="false"
            v-model="form.participa_escuela"
            :disabled="modo === 'ver'"
          />
          <label for="participa-no">No</label>
        </div>
      </div>

      <div v-if="form.participa_escuela" class="campo-condicional">
        <select
          v-model="form.id_escuela"
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>Seleccione la escuela de formación</option>
          <option v-for="escuela in catalogos.escuelas" :key="escuela.id_escuela" :value="escuela.id_escuela">
            {{ escuela.nombre }}
          </option>
        </select>
      </div>

      <hr class="form-divider" />

      <!-- Información Médica -->
      <div class="seccion-titulo">Antecedentes Médicos</div>

      <!-- Panel principal de enfermedades -->
      <div class="panel-enfermedades">
        <div class="panel-enfermedades-contenido">
          <label class="panel-pregunta">¿Tiene alguna enfermedad o condición médica?</label>
          <div class="panel-opciones">
            <button
              type="button"
              @click="seleccionarEnfermedades(true)"
              :class="['boton-si-no', { activo: form.tiene_enfermedades === true }]"
              :disabled="modo === 'ver'"
            >
              Sí
            </button>
            <button
              type="button"
              @click="seleccionarEnfermedades(false)"
              :class="['boton-si-no', { activo: form.tiene_enfermedades === false }]"
              :disabled="modo === 'ver'"
            >
              No
            </button>
          </div>
        </div>
      </div>

      <!-- Todo el bloque de antecedentes médicos (se muestra solo si marca "Sí") -->
      <div v-if="form.tiene_enfermedades === true">
        <!-- Campos de diagnóstico -->
        <div class="fila-texto">
          <select
            v-model="form.tipo_enfermedad"
            :disabled="modo === 'ver'"
          >
            <option :value="null">Seleccione tipo de enfermedad (opcional)</option>
            <option v-for="tipo in catalogos.tiposEnfermedad" :key="tipo.id_tipo_enfermedad" :value="tipo.id_tipo_enfermedad">
              {{ tipo.nombre }}
            </option>
          </select>
        </div>

        <div v-if="form.tipo_enfermedad" class="diagnosticos-container">
          <label>Seleccione los diagnósticos (puede elegir múltiples):</label>
          <div class="multiselect-container">
            <div
              v-for="diagnostico in diagnosticosDisponibles"
              :key="diagnostico.id_diagnostico"
              class="checkbox-item"
            >
              <input
                type="checkbox"
                :id="`diag-${diagnostico.id_diagnostico}`"
                :value="diagnostico.id_diagnostico"
                v-model="form.diagnostico"
                :disabled="modo === 'ver'"
              />
              <label :for="`diag-${diagnostico.id_diagnostico}`">
                {{ diagnostico.nombre }}
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Panel de recomendación médica (al final del frame) -->
      <div v-if="form.tiene_enfermedades === true" class="panel-recomendacion">
        <div class="panel-recomendacion-contenido">
          <label class="panel-pregunta">¿Existe alguna recomendación médica?</label>
          <div class="panel-opciones">
            <button
              type="button"
              @click="form.recomendacion_medica = true"
              :class="['boton-si-no', { activo: form.recomendacion_medica === true }]"
              :disabled="modo === 'ver'"
            >
              Sí
            </button>
            <button
              type="button"
              @click="form.recomendacion_medica = false"
              :class="['boton-si-no', { activo: form.recomendacion_medica === false }]"
              :disabled="modo === 'ver'"
            >
              No
            </button>
          </div>

          <div class="campo-condicional" v-show="form.recomendacion_medica === true">
            <label for="descripcion-recomendacion">Describa la recomendación:</label>
            <textarea
              id="descripcion-recomendacion"
              v-model="form.descripcion_recomendacion"
              placeholder="Escriba aquí..."
              :readonly="modo === 'ver'"
            ></textarea>
          </div>
        </div>
      </div>

      <hr class="form-divider" />

      <!-- Sección de Acudientes (Obligatorio) -->
      <div class="seccion-titulo">Información de Acudiente *</div>

      <div class="campo-busqueda-acudiente">
        <label for="buscar-cedula">Buscar acudiente por número de cédula:</label>
        <div class="busqueda-row">
          <input
            id="buscar-cedula"
            v-model="cedulaBuscada"
            type="text"
            placeholder="Ingrese número de cédula (ej: 1234567890)"
            :disabled="modo === 'ver' || isSearchingAcudiente"
            @keyup.enter="buscarAcudientePorCedula"
          />
          <button
            type="button"
            @click="buscarAcudientePorCedula"
            :disabled="modo === 'ver' || isSearchingAcudiente || !cedulaBuscada"
            class="boton-buscar"
          >
            {{ isSearchingAcudiente ? 'Buscando...' : 'Buscar' }}
          </button>
        </div>

        <!-- Mensaje de resultado de búsqueda -->
        <div v-if="mensajeBusquedaAcudiente"
             :class="['mensaje-busqueda', mensajeBusquedaAcudiente.tipo]">
          <p><strong>{{ mensajeBusquedaAcudiente.titulo }}</strong></p>
          <p>{{ mensajeBusquedaAcudiente.mensaje }}</p>
          <p v-if="mensajeBusquedaAcudiente.sugerencia" class="sugerencia">
            {{ mensajeBusquedaAcudiente.sugerencia }}
          </p>
        </div>

        <!-- Información del acudiente encontrado -->
        <div v-if="acudienteEncontrado" class="info-acudiente-encontrado">
          <div class="acudiente-card">
            <h4>✓ Acudiente encontrado:</h4>
            <p><strong>Nombre:</strong> {{ acudienteEncontrado.persona?.nombre_completo }}</p>
            <p><strong>Cédula:</strong> {{ acudienteEncontrado.persona?.documento }}</p>
            <p><strong>Email:</strong> {{ acudienteEncontrado.persona?.correo_electronico }}</p>
          </div>
        </div>
      </div>

      <!-- Campos de parentesco y responsabilidad -->
      <div v-if="acudienteEncontrado" class="campo-condicional">
        <div class="fila-texto">
          <select
            v-model="form.id_parentesco"
            required
            :disabled="modo === 'ver'"
          >
            <option value="" disabled>Seleccione el parentesco *</option>
            <option v-for="parentesco in catalogos.parentescos" :key="parentesco.id_parentesco" :value="parentesco.id_parentesco">
              {{ parentesco.nombre }}
            </option>
          </select>
        </div>

        <div class="bloque-radio">
          <label>¿Es el acudiente responsable? *</label>
          <div class="opciones">
            <input
              type="radio"
              id="es-responsable-si"
              name="es-responsable"
              :value="true"
              v-model="form.es_responsable"
              :disabled="modo === 'ver'"
              required
            />
            <label for="es-responsable-si">Sí</label>
            <input
              type="radio"
              id="es-responsable-no"
              name="es-responsable"
              :value="false"
              v-model="form.es_responsable"
              :disabled="modo === 'ver'"
              required
            />
            <label for="es-responsable-no">No</label>
          </div>
        </div>
      </div>

      <hr class="form-divider" />

      <!-- Botones de acción -->
      <div v-if="modo !== 'ver'" class="botones-formulario" style="justify-content: center; gap: 10px; margin-top: 20px;">
        <button type="submit" class="boton-formulario" :disabled="isSubmitting" style="width: 150px;">
          {{ isSubmitting ? 'Enviando...' : obtenerTextoBoton() }}
        </button>
        <button
          v-if="modo === 'actualizar'"
          type="button"
          class="boton-formulario"
          style="width: 120px;"
          @click="cancelar"
        >
          Cancelar
        </button>
      </div>
    </section>
  </form>

  <!-- Modal de éxito/error -->
  <div v-if="showModal" class="modal-overlay" @click="cerrarModal">
    <div class="modal-content" :class="modalTitle === 'Éxito' ? 'success-modal' : 'error-modal'" @click.stop>
      <h3>{{ modalTitle }}</h3>
      <p>{{ modalMessage }}</p>
      <button @click="cerrarModal">{{ modalTitle === 'Éxito' ? 'Continuar' : 'Cerrar' }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import catalogosService from '@/services/catalogosService';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

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
});

const emit = defineEmits(['submit', 'cancel']);

const isSubmitting = ref(false);
const showModal = ref(false);
const modalTitle = ref('');
const modalMessage = ref('');
const isSearchingAcudiente = ref(false);
const cedulaBuscada = ref('');
const acudienteEncontrado = ref(null);
const mensajeBusquedaAcudiente = ref(null);

const catalogos = ref({
  tiposDocumento: [],
  sexos: [],
  tiposSanguineos: [],
  ciudades: [],
  eps: [],
  deportes: [],
  escuelas: [],
  institucionesRegistro: [],
  tiposEnfermedad: [],
  diagnosticos: [],
  acudientes: [],
  parentescos: []
});

const form = ref({
  // Datos del deportista
  fecha_nacimiento: "",
  id_tipo_sanguineo: "",
  id_ciudad_residencia: "",
  id_eps: "",

  // Información deportiva
  id_deporte: "", // Deporte principal (requerido)
  id_deporte_secundario: "",
  id_escuela: "",
  id_institucion_registro: "",
  practica_otro_deporte: false,
  participa_escuela: false,
  recomendacion_medica: false,
  descripcion_recomendacion: "",

  // Información médica
  tiene_enfermedades: null, // null = no seleccionado, true = sí, false = no
  tipo_enfermedad: null,
  diagnostico: [],

  // Información de acudiente
  id_acudiente: "",
  id_parentesco: "",
  es_responsable: null  // null = no seleccionado, true = sí, false = no
});

const diagnosticosDisponibles = computed(() => {
  if (!form.value.tipo_enfermedad) return [];
  return catalogos.value.diagnosticos.filter(d => d.id_tipo_enfermedad === form.value.tipo_enfermedad);
});

function obtenerTitulo() {
  switch (props.modo) {
    case 'registrar':
      return 'Registro de Deportista';
    case 'actualizar':
      return 'Actualizar Deportista';
    case 'ver':
      return 'Información del Deportista';
    default:
      return 'Formulario';
  }
}

function obtenerTextoBoton() {
  switch (props.modo) {
    case 'registrar':
      return 'Registrar';
    case 'actualizar':
      return 'Actualizar';
    default:
      return 'Enviar';
  }
}

async function cargarCatalogos() {
  try {
    console.log('🔄 Cargando catálogos...');

    // Catálogos básicos
    const catalogosBasicos = await catalogosService.cargarCatalogosFormulario();
    catalogos.value.tiposDocumento = catalogosBasicos.tiposDocumento || [];
    catalogos.value.sexos = catalogosBasicos.sexos || [];

    // Catálogos específicos de deportistas
    const baseURL = 'http://localhost:5000';
    const endpoints = [
      '/api/catalogos/grupos-sanguineos',
      '/api/catalogos/ciudades-residencia',
      '/api/catalogos/eps',
      '/api/catalogos/deportes',
      '/api/catalogos/escuelas',
      '/api/catalogos/instituciones-registro',
      '/api/catalogos/tipos-enfermedad',
      '/api/catalogos/diagnosticos',
      '/api/catalogos/acudientes',
      '/api/catalogos/parentescos'
    ];

    const responses = await Promise.all(
      endpoints.map(endpoint => fetch(`${baseURL}${endpoint}`))
    );

    // Procesar respuestas con validación
    const processResponse = async (res, index) => {
      try {
        const data = await res.json();

        if (!res.ok) {
          console.error(`❌ Error en endpoint ${index} (${res.status}):`, data);
          return [];
        }

        console.log(`✅ Endpoint ${index} respondió:`, data);
        return data.data || [];
      } catch (e) {
        console.error(`❌ Error al procesar respuesta ${index}:`, e);
        return [];
      }
    };

    const resultados = await Promise.all([
      processResponse(responses[0], 0),
      processResponse(responses[1], 1),
      processResponse(responses[2], 2),
      processResponse(responses[3], 3),
      processResponse(responses[4], 4),
      processResponse(responses[5], 5),
      processResponse(responses[6], 6),
      processResponse(responses[7], 7),
      processResponse(responses[8], 8),
      processResponse(responses[9], 9)
    ]);

    catalogos.value.tiposSanguineos = resultados[0];
    catalogos.value.ciudades = resultados[1];
    catalogos.value.eps = resultados[2];
    catalogos.value.deportes = resultados[3];
    catalogos.value.escuelas = resultados[4];
    catalogos.value.institucionesRegistro = resultados[5];
    catalogos.value.tiposEnfermedad = resultados[6];
    catalogos.value.diagnosticos = resultados[7];
    catalogos.value.acudientes = resultados[8];
    catalogos.value.parentescos = resultados[9];

    console.log('✅ Catálogos cargados exitosamente');
    console.log('📋 Deportes cargados:', catalogos.value.deportes.length);
    console.log('📋 Escuelas cargadas:', catalogos.value.escuelas.length);
    console.log('📋 Tipos de enfermedad cargados:', catalogos.value.tiposEnfermedad.length);
    console.log('📋 Diagnosticos cargados:', catalogos.value.diagnosticos.length);
    console.log('📋 Parentescos cargados:', catalogos.value.parentescos.length);
    console.log('📋 Parentescos datos:', catalogos.value.parentescos);
  } catch (error) {
    console.error('❌ Error cargando catálogos:', error);
    mostrarModal('Error', 'No se pudieron cargar los catálogos. Por favor, recargue la página.');
  }
}

function seleccionarEnfermedades(tiene) {
  form.value.tiene_enfermedades = tiene;

  // Si marca "No", limpiar todos los antecedentes médicos
  if (!tiene) {
    form.value.tipo_enfermedad = null;
    form.value.diagnostico = [];
    form.value.recomendacion_medica = false;
    form.value.descripcion_recomendacion = '';
  }
}

async function buscarAcudientePorCedula() {
  if (!cedulaBuscada.value || !cedulaBuscada.value.trim()) {
    mensajeBusquedaAcudiente.value = {
      tipo: 'error',
      titulo: 'Error',
      mensaje: 'Por favor ingrese un número de cédula'
    };
    return;
  }

  isSearchingAcudiente.value = true;
  mensajeBusquedaAcudiente.value = null;
  acudienteEncontrado.value = null;

  try {
    const baseURL = 'http://localhost:5000';
    const response = await fetch(`${baseURL}/api/catalogos/acudientes?cedula=${cedulaBuscada.value}`);
    const result = await response.json();

    if (response.ok && result.success) {
      // Acudiente encontrado
      acudienteEncontrado.value = result.data;
      form.value.id_acudiente = result.data.id_acudiente;

      mensajeBusquedaAcudiente.value = {
        tipo: 'success',
        titulo: '✓ Éxito',
        mensaje: 'Acudiente encontrado exitosamente'
      };
    } else {
      // Acudiente no encontrado
      mensajeBusquedaAcudiente.value = {
        tipo: 'warning',
        titulo: '⚠ Acudiente no encontrado',
        mensaje: result.message || 'No se encontró un acudiente con ese documento',
        sugerencia: result.sugerencia || 'El acudiente debe registrarse primero en el sistema'
      };
      acudienteEncontrado.value = null;
      form.value.id_acudiente = "";
      form.value.id_parentesco = "";
      form.value.es_responsable = null;
    }
  } catch (error) {
    console.error('Error al buscar acudiente:', error);
    mensajeBusquedaAcudiente.value = {
      tipo: 'error',
      titulo: 'Error',
      mensaje: 'Error al buscar acudiente. Por favor, intente de nuevo.'
    };
  } finally {
    isSearchingAcudiente.value = false;
  }
}

function mostrarModal(titulo, mensaje) {
  modalTitle.value = titulo;
  modalMessage.value = mensaje;
  showModal.value = true;
}

function cerrarModal() {
  showModal.value = false;
}

async function manejarSubmit() {
  isSubmitting.value = true;

  try {
    // Requiere sesión iniciada: el backend obtiene id_persona desde el token
    const token = localStorage.getItem('token');
    if (!token || token === 'null' || token === 'undefined') {
      mostrarModal('Error', 'Debe iniciar sesión para registrar un deportista.');
      isSubmitting.value = false;
      return;
    }

    // Validaciones básicas
    if (!form.value.fecha_nacimiento) {
      mostrarModal('Error', 'El año de nacimiento es obligatorio.');
      isSubmitting.value = false;
      return;
    }

    if (!form.value.id_deporte) {
      mostrarModal('Error', 'Debe seleccionar un deporte principal.');
      isSubmitting.value = false;
      return;
    }

    if (!form.value.id_institucion_registro) {
      mostrarModal('Error', 'Debe seleccionar una institución de registro.');
      isSubmitting.value = false;
      return;
    }

    // Validaciones de campos condicionales
    if (form.value.participa_escuela && !form.value.id_escuela) {
      mostrarModal('Error', 'Si participa en escuela de formación, debe seleccionar una escuela.');
      isSubmitting.value = false;
      return;
    }

    if (form.value.tiene_enfermedades === true && form.value.tipo_enfermedad && form.value.diagnostico.length === 0) {
      mostrarModal('Error', 'Si selecciona un tipo de enfermedad, debe seleccionar al menos un diagnóstico.');
      isSubmitting.value = false;
      return;
    }

    if (form.value.recomendacion_medica && !form.value.descripcion_recomendacion) {
      mostrarModal('Error', 'Si existe recomendación médica, debe describirla.');
      isSubmitting.value = false;
      return;
    }

    // Validación de acudiente (OBLIGATORIO)
    if (!acudienteEncontrado.value || !form.value.id_acudiente) {
      mostrarModal('Error', 'Debe buscar y encontrar un acudiente por número de cédula para continuar.');
      isSubmitting.value = false;
      return;
    }

    if (!form.value.id_parentesco) {
      mostrarModal('Error', 'Debe especificar el parentesco con el acudiente.');
      isSubmitting.value = false;
      return;
    }

    // Validar que se haya seleccionado si es responsable o no
    if (form.value.es_responsable === null || form.value.es_responsable === undefined || form.value.es_responsable === '') {
      mostrarModal('Error', 'Debe indicar si el acudiente es responsable o no.');
      isSubmitting.value = false;
      return;
    }

    // 2. Estructurar datos según el endpoint
    const datosEnvio = {
      datos_deportista: {
        fecha_nacimiento: parseInt(form.value.fecha_nacimiento),
        id_tipo_sanguineo: parseInt(form.value.id_tipo_sanguineo) || null,
        id_ciudad_recidencia: parseInt(form.value.id_ciudad_residencia) || null,
        id_eps: parseInt(form.value.id_eps) || null
      },
      informacion_deportiva: {
        practica_otro_deporte: form.value.practica_otro_deporte || false,
        participa_escuela: form.value.participa_escuela || false,
        recomendacion_medica: form.value.tiene_enfermedades === true ? form.value.recomendacion_medica : false,
        descripcion_recomendacion: form.value.tiene_enfermedades === true && form.value.recomendacion_medica ? form.value.descripcion_recomendacion : null,
        id_escuela: form.value.participa_escuela && form.value.id_escuela ? parseInt(form.value.id_escuela) : null,
        id_deporte: parseInt(form.value.id_deporte) || null,
        id_institucion_registro: parseInt(form.value.id_institucion_registro) || null
      }
    };

    // Agregar información de diagnóstico solo si marcó "Sí" a tener enfermedades
    if (form.value.tiene_enfermedades === true) {
      datosEnvio.tipo_enfermedad = form.value.tipo_enfermedad || null;
      datosEnvio.diagnostico = form.value.diagnostico && form.value.diagnostico.length > 0 ? form.value.diagnostico : [];
    } else {
      // Si marcó "No", no enviar campos de diagnóstico
      datosEnvio.diagnostico = [];
    }

    // Agregar información de acudiente (OBLIGATORIO)
    // Si viene de "Asignar Acudido", el acudiente será el usuario actual
    const acudienteData = {
      id_acudiente: parseInt(form.value.id_acudiente),
      id_parentesco: parseInt(form.value.id_parentesco),
      es_responsable: form.value.es_responsable
    };

    datosEnvio.acudientes = [acudienteData];

    // Agregar metadata para identificar contexto
    if (route.query.asignarAcudiente === 'true') {
      datosEnvio._metadata = {
        desde_asignar_acudido: true
      };
    }

    console.log('Datos a enviar:', datosEnvio);

    // Enviar al endpoint
    const response = await fetch('http://localhost:5000/api/deportistas/registrar', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(datosEnvio)
    });

    const result = await response.json();

    if (response.ok && result.status === 'success') {
      mostrarModal('Éxito', `Deportista registrado exitosamente.\nCategoría: ${result.data.categoria}\nNombre: ${result.data.nombre_persona}`);
      emit('submit', result);

      // Limpiar formulario después de 3 segundos
      setTimeout(() => {
        showModal.value = false;
        // Resetear formulario
        Object.keys(form.value).forEach(key => {
          if (key === 'diagnostico') {
            form.value[key] = [];
          } else if (key === 'tiene_enfermedades' || key === 'es_responsable') {
            form.value[key] = null;
          } else if (typeof form.value[key] === 'boolean') {
            form.value[key] = false;
          } else {
            form.value[key] = '';
          }
        });
        acudienteEncontrado.value = null;
        cedulaBuscada.value = '';
        mensajeBusquedaAcudiente.value = null;
      }, 3000);
    } else {
      // Manejo de errores del backend
      const mensajeError = result.message || result.error || 'Error al registrar deportista';
      throw new Error(mensajeError);
    }

  } catch (error) {
    console.error('Error:', error);
    const mensajeError = error.message || 'Error al procesar el registro. Por favor, intente de nuevo.';
    mostrarModal('Error', mensajeError);
  } finally {
    isSubmitting.value = false;
  }
}

function cancelar() {
  emit('cancel');
}

onMounted(async () => {
  await cargarCatalogos();

  // Si viene de "Asignar Acudido", pre-cargar el acudiente del usuario actual
  if (route.query.asignarAcudiente === 'true' && authStore.user?.id_usuario) {
    try {
      // Obtener el acudiente del usuario actual
      const response = await fetch(`http://localhost:5000/api/catalogos/acudientes?cedula=${authStore.user?.persona?.documento || ''}`);
      const result = await response.json();

      if (response.ok && result.success && result.data) {
        acudienteEncontrado.value = result.data;
        form.value.id_acudiente = result.data.id_acudiente;

        mensajeBusquedaAcudiente.value = {
          tipo: 'success',
          titulo: '✓ Tu información como acudiente',
          mensaje: 'Se pre-cargó tu información como acudiente. Puedes editar el parentesco si es necesario.'
        };
      }
    } catch (error) {
      console.error('Error pre-cargando acudiente:', error);
    }
  }

  if (props.datos && Object.keys(props.datos).length > 0) {
    Object.keys(props.datos).forEach(key => {
      if (Object.prototype.hasOwnProperty.call(form.value, key)) {
        form.value[key] = props.datos[key];
      }
    });
  }
});
</script>

<style scoped>
.multiselect-container {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  margin-top: 10px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  padding: 5px 0;
}

.checkbox-item input[type="checkbox"] {
  margin-right: 8px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 400px;
  text-align: center;
}

.modal-content h3 {
  margin-bottom: 1rem;
  color: #333;
}

.modal-content p {
  margin-bottom: 1.5rem;
  color: #666;
  white-space: pre-line;
}

.modal-content button {
  padding: 0.5rem 1.5rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.modal-content button:hover {
  background: #0056b3;
}

/* Estilo para el modal de éxito */
.modal-content h3 {
  font-size: 1.5rem;
  font-weight: bold;
}

/* Estilo para mensajes de error en modal */
.modal-content.error-modal h3 {
  color: #dc3545;
}

.modal-content.success-modal h3 {
  color: #28a745;
}

.campo-condicional {
  margin-top: 10px;
}

.campo-condicional select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.campo-condicional textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-top: 10px;
  resize: vertical;
  min-height: 80px;
}

.seccion-titulo {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
  margin: 20px 0 10px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #007bff;
}

/* Estilos para el panel de enfermedades */
.panel-enfermedades {
  margin: 20px 0;
  padding: 5px;
  border: 3px dashed #ffd700; /* Amarillo punteado */
  border-radius: 12px;
  background-color: #fff;
}

.panel-enfermedades-contenido {
  background-color: white;
  border-radius: 8px;
  padding: 25px 20px;
  text-align: center;
}

.panel-pregunta {
  display: block;
  font-size: 1.1rem;
  font-weight: bold;
  color: #1a365d;
  margin-bottom: 20px;
}

.panel-opciones {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.boton-si-no {
  min-width: 120px;
  padding: 12px 30px;
  border: 2px solid #007bff;
  border-radius: 8px;
  background-color: white;
  color: #007bff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.boton-si-no:hover:not(:disabled) {
  background-color: #f0f8ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.2);
}

.boton-si-no.activo {
  background-color: #007bff;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.4);
}

.boton-si-no:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

/* Estilos para el panel de recomendación médica */
.panel-recomendacion {
  margin: 20px 0;
  padding: 5px;
  border: 3px dashed #ffd700; /* Amarillo punteado */
  border-radius: 12px;
  background-color: #fff;
}

.panel-recomendacion-contenido {
  background-color: white;
  border-radius: 8px;
  padding: 25px 20px;
  text-align: center;
}

.panel-recomendacion-contenido .campo-condicional {
  margin-top: 20px;
  text-align: left;
}

.panel-recomendacion-contenido .campo-condicional label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.panel-recomendacion-contenido .campo-condicional textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-family: inherit;
  resize: vertical;
  min-height: 100px;
  transition: border-color 0.3s ease;
}

.panel-recomendacion-contenido .campo-condicional textarea:focus {
  outline: none;
  border-color: #007bff;
}

/* Estilos para búsqueda de acudiente */
.campo-busqueda-acudiente {
  margin: 20px 0;
}

.campo-busqueda-acudiente label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.busqueda-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.busqueda-row input {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.busqueda-row input:focus {
  outline: none;
  border-color: #007bff;
}

.boton-buscar {
  padding: 0.75rem 1.5rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.3s ease;
}

.boton-buscar:hover:not(:disabled) {
  background: #0056b3;
}

.boton-buscar:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Mensajes de búsqueda */
.mensaje-busqueda {
  margin-top: 15px;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid;
}

.mensaje-busqueda.success {
  background-color: #d4edda;
  border-color: #28a745;
  color: #155724;
}

.mensaje-busqueda.warning {
  background-color: #fff3cd;
  border-color: #ffc107;
  color: #856404;
}

.mensaje-busqueda.error {
  background-color: #f8d7da;
  border-color: #dc3545;
  color: #721c24;
}

.mensaje-busqueda p {
  margin: 5px 0;
}

.mensaje-busqueda .sugerencia {
  font-style: italic;
  margin-top: 10px;
  font-weight: 500;
}

/* Info de acudiente encontrado */
.info-acudiente-encontrado {
  margin-top: 20px;
}

.acudiente-card {
  background-color: #f8f9fa;
  border: 2px solid #28a745;
  border-radius: 8px;
  padding: 15px;
}

.acudiente-card h4 {
  color: #28a745;
  margin-bottom: 10px;
}

.acudiente-card p {
  margin: 5px 0;
  color: #333;
}
</style>
