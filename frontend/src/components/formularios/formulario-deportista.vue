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
            {{ deporte.nombre_deporte }}
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
            {{ escuela.nombre_escuela }}
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
  <div v-if="showModal" class="modal-overlay" @click="showModal = false">
    <div class="modal-content" @click.stop>
      <h3>{{ modalTitle }}</h3>
      <p>{{ modalMessage }}</p>
      <button @click="showModal = false">Cerrar</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import catalogosService from '@/services/catalogosService';

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
  diagnosticos: []
});

const form = ref({
  // Datos del deportista
  fecha_nacimiento: "",
  id_tipo_sanguineo: "",
  id_ciudad_residencia: "",
  id_eps: "",

  // Información deportiva
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
  diagnostico: []
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
      '/api/catalogos/diagnosticos'
    ];

    const responses = await Promise.all(
      endpoints.map(endpoint => fetch(`${baseURL}${endpoint}`))
    );

    // Procesar respuestas con validación
    const processResponse = async (res) => {
      if (!res.ok) {
        console.error(`Error: ${res.status} ${res.statusText}`);
        return [];
      }
      const data = await res.json();
      return data.data || [];
    };

    catalogos.value.tiposSanguineos = await processResponse(responses[0]);
    catalogos.value.ciudades = await processResponse(responses[1]);
    catalogos.value.eps = await processResponse(responses[2]);
    catalogos.value.deportes = await processResponse(responses[3]);
    catalogos.value.escuelas = await processResponse(responses[4]);
    catalogos.value.institucionesRegistro = await processResponse(responses[5]);
    catalogos.value.tiposEnfermedad = await processResponse(responses[6]);
    catalogos.value.diagnosticos = await processResponse(responses[7]);

    console.log('✅ Catálogos cargados exitosamente');
    console.log('📋 Tipos de enfermedad cargados:', catalogos.value.tiposEnfermedad);
    console.log('📋 Diagnosticos cargados:', catalogos.value.diagnosticos);
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

function mostrarModal(titulo, mensaje) {
  modalTitle.value = titulo;
  modalMessage.value = mensaje;
  showModal.value = true;
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

    // 2. Estructurar datos según el endpoint
    const datosEnvio = {
      datos_deportista: {
        fecha_nacimiento: parseInt(form.value.fecha_nacimiento),
        id_tipo_sanguineo: parseInt(form.value.id_tipo_sanguineo),
        id_ciudad_recidencia: parseInt(form.value.id_ciudad_residencia),
        id_eps: parseInt(form.value.id_eps)
      },
      informacion_deportiva: {
        practica_otro_deporte: form.value.practica_otro_deporte,
        participa_escuela: form.value.participa_escuela,
        recomendacion_medica: form.value.tiene_enfermedades === false ? false : form.value.recomendacion_medica,
        descripcion_recomendacion: form.value.tiene_enfermedades === false ? null : (form.value.recomendacion_medica ? form.value.descripcion_recomendacion : null),
        id_escuela: form.value.participa_escuela ? parseInt(form.value.id_escuela) : null,
        id_institucion_registro: parseInt(form.value.id_institucion_registro)
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
      mostrarModal('Éxito', `Deportista registrado exitosamente. ID: ${result.data.id_deportista}`);
      emit('submit', result);

      // Limpiar formulario después de 2 segundos
      setTimeout(() => {
        showModal.value = false;
        // Resetear formulario
        Object.keys(form.value).forEach(key => {
          if (key !== 'diagnostico') {
            form.value[key] = typeof form.value[key] === 'boolean' ? false : '';
          } else {
            form.value[key] = [];
          }
        });
      }, 2000);
    } else {
      throw new Error(result.message || 'Error al registrar deportista');
    }

  } catch (error) {
    console.error('Error:', error);
    mostrarModal('Error', error.message || 'Error al procesar el registro');
  } finally {
    isSubmitting.value = false;
  }
}

function cancelar() {
  emit('cancel');
}

onMounted(async () => {
  await cargarCatalogos();

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
</style>
