<!-- src/components/formulario-deportista.vue -->
<template>
  <form class="formulario-datos" @submit.prevent="manejarSubmit" novalidate>
    <!-- Formulario Unificado -->
    <section class="seccion-formulario">
      <h3>{{ obtenerTitulo() }}</h3>

      <!-- Datos Básicos del Deportista -->
      <div class="seccion-titulo">Datos Básicos</div>

      <div class="fila-texto">
        <input
          v-model="form.fecha_nacimiento"
          type="date"
          placeholder="Fecha de nacimiento *"
          required
          :max="new Date().toISOString().split('T')[0]"
          :readonly="modo === 'ver'"
        />
        <select
          v-model="form.id_tipo_sanguineo"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>Tipo sanguíneo *</option>
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
          <option value="" disabled>Ciudad de residencia *</option>
          <option v-for="ciudad in catalogos.ciudades" :key="ciudad.id_ciudad" :value="ciudad.id_ciudad">
            {{ ciudad.nombre_ciudad }}
          </option>
        </select>
        <select
          v-model="form.id_eps"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>EPS *</option>
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
          <option value="" disabled>Institución de registro *</option>
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

      <!-- el bloque de antecedentes médicos (se muestra solo si marca "Sí") -->
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
      <!-- Solo mostrar en modo ver un botón para cerrar -->
      <div v-if="modo === 'ver'" class="botones-formulario" style="justify-content: center; gap: 10px; margin-top: 20px;">
        <button
          type="button"
          class="boton-formulario"
          style="width: 150px; background: #6c757d;"
          @click="cancelar"
        >
          Cerrar
        </button>
      </div>
      <div v-else-if="modo !== 'ver'" class="botones-formulario" style="justify-content: center; gap: 10px; margin-top: 20px;">
        <button
          v-if="modo === 'registrar'"
          type="button"
          class="boton-formulario"
          style="width: 150px; background: #6c757d;"
          @click="volverAtras"
          :disabled="isSubmitting"
        >
          <i class="fas fa-arrow-left" style="margin-right: 5px;"></i>
          Volver
        </button>
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
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import catalogosService from '@/services/catalogosService';
import deportistasService from '@/services/deportistasService';
import Swal from 'sweetalert2';

const route = useRoute();
const router = useRouter();
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
// Variables de acudiente eliminadas - ya no se usa en el registro

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
      '/api/deportistas/catalogos/grupos-sanguineos',
      '/api/deportistas/catalogos/ciudades-residencia',
      '/api/deportistas/catalogos/eps',
      '/api/deportistas/catalogos/deportes',
      '/api/deportistas/catalogos/escuelas',
      '/api/deportistas/catalogos/instituciones-registro',
      '/api/catalogos/tipos-enfermedad',
      '/api/deportistas/catalogos/diagnosticos',
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

// Funciones relacionadas con acudiente eliminadas - ya no se usan en el registro

function obtenerIconoPorTitulo(titulo) {
  if (titulo === 'Éxito') return 'success';
  if (titulo === 'Advertencia') return 'warning';
  return 'error';
}

function mostrarModal(titulo, mensaje) {
  const icon = obtenerIconoPorTitulo(titulo);
  const html = (mensaje || '').replace(/\n/g, '<br>');
  const confirmButtonText = titulo === 'Éxito' ? 'Continuar' : 'Cerrar';
  return Swal.fire({
    icon,
    title: titulo,
    html,
    confirmButtonText
  });
}

function validarToken() {
  const token = localStorage.getItem('token');
  console.log('🔑 Token encontrado:', token ? 'Sí' : 'No');
  if (!token || token === 'null' || token === 'undefined') {
    console.error('❌ No hay token válido');
    mostrarModal('Error', 'Debe iniciar sesión para realizar esta acción.');
    return false;
  }
  return token;
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

function validarEdadMinima() {
  if (!form.value.fecha_nacimiento) {
    mostrarModal('Error', 'La fecha de nacimiento es obligatoria.');
    return false;
  }
  const edad = calcularEdad(form.value.fecha_nacimiento);
  if (edad < 5) {
    mostrarModal('Error', 'El deportista debe tener mínimo 5 años de edad para poder registrarse. La edad mínima de la categoría Pre-infantil es 5 años.');
    return false;
  }
  return true;
}

function validarCamposObligatorios() {
  if (!form.value.id_tipo_sanguineo) {
    mostrarModal('Error', 'Debe seleccionar un tipo sanguíneo.');
    return false;
  }
  if (!form.value.id_ciudad_residencia) {
    mostrarModal('Error', 'Debe seleccionar una ciudad de residencia.');
    return false;
  }
  if (!form.value.id_eps) {
    mostrarModal('Error', 'Debe seleccionar una EPS.');
    return false;
  }
  if (!form.value.id_deporte) {
    mostrarModal('Error', 'Debe seleccionar un deporte principal.');
    return false;
  }
  if (!form.value.id_institucion_registro) {
    mostrarModal('Error', 'Debe seleccionar una institución de registro.');
    return false;
  }
  return true;
}

function validarCamposCondicionales() {
  if (form.value.participa_escuela && !form.value.id_escuela) {
    mostrarModal('Error', 'Si participa en escuela de formación, debe seleccionar una escuela.');
    return false;
  }
  if (form.value.tiene_enfermedades === true && form.value.tipo_enfermedad && form.value.diagnostico.length === 0) {
    mostrarModal('Error', 'Si selecciona un tipo de enfermedad, debe seleccionar al menos un diagnóstico.');
    return false;
  }
  if (form.value.recomendacion_medica && !form.value.descripcion_recomendacion) {
    mostrarModal('Error', 'Si existe recomendación médica, debe describirla.');
    return false;
  }
  return true;
}

function construirDatosDeportista() {
  return {
    fecha_nacimiento: form.value.fecha_nacimiento,
    id_tipo_sanguineo: form.value.id_tipo_sanguineo ? parseInt(form.value.id_tipo_sanguineo) : null,
    id_ciudad_recidencia: form.value.id_ciudad_residencia ? parseInt(form.value.id_ciudad_residencia) : null,
    id_eps: form.value.id_eps ? parseInt(form.value.id_eps) : null
  };
}

function obtenerRecomendacionMedica() {
  return form.value.tiene_enfermedades === true ? form.value.recomendacion_medica : false;
}

function obtenerDescripcionRecomendacion() {
  const tieneEnfermedades = form.value.tiene_enfermedades === true;
  const tieneRecomendacion = form.value.recomendacion_medica;
  return tieneEnfermedades && tieneRecomendacion ? form.value.descripcion_recomendacion : null;
}

function obtenerIdEscuela() {
  return form.value.participa_escuela && form.value.id_escuela ? parseInt(form.value.id_escuela) : null;
}

function construirInformacionDeportiva() {
  return {
    practica_otro_deporte: form.value.practica_otro_deporte || false,
    participa_escuela: form.value.participa_escuela || false,
    recomendacion_medica: obtenerRecomendacionMedica(),
    descripcion_recomendacion: obtenerDescripcionRecomendacion(),
    id_escuela: obtenerIdEscuela(),
    id_deporte: form.value.id_deporte ? parseInt(form.value.id_deporte) : null,
    id_institucion_registro: form.value.id_institucion_registro ? parseInt(form.value.id_institucion_registro) : null
  };
}

function agregarDiagnosticos(datosEnvio) {
  if (form.value.tiene_enfermedades === true) {
    if (form.value.tipo_enfermedad) {
      datosEnvio.tipo_enfermedad = parseInt(form.value.tipo_enfermedad);
    }
    if (form.value.diagnostico && form.value.diagnostico.length > 0) {
      datosEnvio.diagnostico = form.value.diagnostico.map(d => parseInt(d));
    }
  } else if (form.value.tiene_enfermedades === false) {
    datosEnvio.diagnostico = [];
  }
}

function construirDatosActualizacion() {
  const datosEnvio = {
    datos_deportista: construirDatosDeportista(),
    datos_informacion_deportiva: construirInformacionDeportiva()
  };
  agregarDiagnosticos(datosEnvio);
  return datosEnvio;
}

function construirDatosRegistro() {
  const datosEnvio = {
    datos_deportista: {
      fecha_nacimiento: form.value.fecha_nacimiento,
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

  if (form.value.tiene_enfermedades === true) {
    datosEnvio.tipo_enfermedad = form.value.tipo_enfermedad || null;
    datosEnvio.diagnostico = form.value.diagnostico && form.value.diagnostico.length > 0 ? form.value.diagnostico : [];
  } else {
    datosEnvio.diagnostico = [];
  }

  datosEnvio.acudientes = [];

  if (route.query.asignarAcudiente === 'true') {
    datosEnvio._metadata = {
      desde_asignar_acudido: true
    };
  }

  return datosEnvio;
}

async function procesarActualizacion() {
  const datosEnvio = construirDatosActualizacion();
  console.log('Datos a actualizar:', datosEnvio);

  const idDeportista = props.datos?.id_deportista || props.datos?.id;
  if (!idDeportista) {
    mostrarModal('Error', 'No se pudo identificar el deportista a actualizar.');
    return false;
  }

  const result = await deportistasService.actualizarDeportista(idDeportista, datosEnvio);
  if (result.success) {
    await mostrarModal('Éxito', 'Deportista actualizado exitosamente.');
    emit('submit', result);
    return true;
  } else {
    const mensajeError = result.message || 'Error al actualizar deportista';
    throw new Error(mensajeError);
  }
}

async function procesarRegistro(token) {
  const datosEnvio = construirDatosRegistro();
  console.log('📤 Datos a registrar:', datosEnvio);
  console.log('🌐 Enviando a: http://localhost:5000/api/deportistas/registrar');

  const response = await fetch('http://localhost:5000/api/deportistas/registrar', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(datosEnvio)
  });

  console.log('📥 Respuesta recibida, status:', response.status);
  const result = await response.json();
  console.log('Respuesta del servidor:', response.status, result);

  // Verificar si la respuesta es exitosa: el backend devuelve success: true
  if (response.ok && result.success === true) {
    if (props.modo !== 'registrar') {
      await mostrarModal('Éxito', `Deportista registrado exitosamente.\nCategoría: ${result.data.categoria}\nNombre: ${result.data.nombre_persona}`);
    }
    emit('submit', result);

    setTimeout(() => {
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
    }, 3000);
    return true;
  } else {
    console.error('Error en respuesta:', {
      status: response.status,
      statusText: response.statusText,
      result: result
    });

    let mensajeError = 'Error al registrar deportista';
    if (result.message) {
      mensajeError = result.message;
    } else if (result.error) {
      mensajeError = result.error;
    } else if (result.success === false) {
      mensajeError = result.message || result.error || 'Error desconocido del servidor';
    }

    throw new Error(mensajeError);
  }
}

async function manejarSubmit(event) {
  // Prevenir el comportamiento por defecto del formulario
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  console.log('🚀 Iniciando manejarSubmit');
  console.log('📋 Estado del formulario:', JSON.parse(JSON.stringify(form.value)));

  isSubmitting.value = true;

  try {
    const token = validarToken();
    if (!token) {
      isSubmitting.value = false;
      return;
    }

    if (!validarEdadMinima() || !validarCamposObligatorios() || !validarCamposCondicionales()) {
      isSubmitting.value = false;
      return;
    }

    if (props.modo === 'actualizar') {
      await procesarActualizacion();
    } else {
      await procesarRegistro(token);
    }

  } catch (error) {
    console.error('Error completo:', error);
    console.error('Stack:', error.stack);
    const mensajeError = error.message || 'Error al procesar la solicitud. Por favor, intente de nuevo.';
    console.error('Mostrando modal con error:', mensajeError);
      mostrarModal('Error', mensajeError);
    // NO redirigir ni resetear el formulario aquí - solo mostrar el error
  } finally {
    isSubmitting.value = false;
  }
}

function cancelar() {
  emit('cancel');
}

// Función para volver atrás
function volverAtras() {
  // Si hay una ruta anterior en el historial, volver
  if (window.history.length > 1) {
    router.go(-1);
  } else {
    // Si no hay historial, redirigir a home o login según el caso
    if (authStore.isAuthenticated) {
      router.push('/home');
    } else {
      router.push('/login');
    }
  }
}

function mapearCampoFormulario(campo, valorDeportista, valorInfoDeportiva, valorDirecto) {
  if (valorDeportista !== undefined && valorDeportista !== null && valorDeportista !== '') {
    form.value[campo] = typeof valorDeportista === 'number' ? valorDeportista.toString() : valorDeportista;
  } else if (valorInfoDeportiva !== undefined && valorInfoDeportiva !== null && valorInfoDeportiva !== '') {
    form.value[campo] = typeof valorInfoDeportiva === 'number' ? valorInfoDeportiva.toString() : valorInfoDeportiva;
  } else if (valorDirecto !== undefined && valorDirecto !== null && valorDirecto !== '') {
    form.value[campo] = typeof valorDirecto === 'number' ? valorDirecto.toString() : valorDirecto;
  }
}

function mapearDatosDeportista(datosDeportista) {
  mapearCampoFormulario('fecha_nacimiento', datosDeportista.fecha_nacimiento, null, props.datos.fecha_nacimiento);
  mapearCampoFormulario('id_tipo_sanguineo', datosDeportista.id_tipo_sanguineo, null, props.datos.id_tipo_sanguineo);

  const ciudadResidencia = datosDeportista.id_ciudad_recidencia || props.datos.id_ciudad_recidencia || props.datos.id_ciudad_residencia;
  if (ciudadResidencia) {
    form.value.id_ciudad_residencia = ciudadResidencia.toString();
  }

  mapearCampoFormulario('id_eps', datosDeportista.id_eps, null, props.datos.id_eps);
}

function mapearInformacionDeportiva(infoDeportiva) {
  mapearCampoFormulario('id_deporte', null, infoDeportiva.id_deporte, props.datos.id_deporte);
  mapearCampoFormulario('id_escuela', null, infoDeportiva.id_escuela, props.datos.id_escuela);
  mapearCampoFormulario('id_institucion_registro', null, infoDeportiva.id_institucion_registro, props.datos.id_institucion_registro);

  if (infoDeportiva.practica_otro_deporte !== undefined) {
    form.value.practica_otro_deporte = infoDeportiva.practica_otro_deporte;
  } else if (props.datos.practica_otro_deporte !== undefined) {
    form.value.practica_otro_deporte = props.datos.practica_otro_deporte;
  }

  if (infoDeportiva.participa_escuela !== undefined) {
    form.value.participa_escuela = infoDeportiva.participa_escuela;
  } else if (props.datos.participa_escuela !== undefined) {
    form.value.participa_escuela = props.datos.participa_escuela;
  }

  if (infoDeportiva.recomendacion_medica !== undefined) {
    form.value.recomendacion_medica = infoDeportiva.recomendacion_medica;
    form.value.tiene_enfermedades = infoDeportiva.recomendacion_medica ? true : false;
  }

  mapearCampoFormulario('descripcion_recomendacion', null, infoDeportiva.descripcion_recomendacion, props.datos.descripcion_recomendacion);
}

function mapearDiagnosticos() {
  if (props.datos.salud?.diagnosticos && Array.isArray(props.datos.salud.diagnosticos)) {
    form.value.diagnostico = props.datos.salud.diagnosticos.map(d =>
      typeof d === 'object' ? d.id_diagnostico : d
    );
  } else if (props.datos.diagnosticos && Array.isArray(props.datos.diagnosticos)) {
    form.value.diagnostico = props.datos.diagnosticos.map(d =>
      typeof d === 'object' ? d.id_diagnostico : d
    );
  }
}

function mapearTipoEnfermedad() {
  if (props.datos.salud?.tipos_enfermedad_ids && props.datos.salud.tipos_enfermedad_ids.length > 0) {
    form.value.tipo_enfermedad = props.datos.salud.tipos_enfermedad_ids[0];
    form.value.tiene_enfermedades = true;
  } else if (props.datos.tipo_enfermedad) {
    form.value.tipo_enfermedad = props.datos.tipo_enfermedad;
    form.value.tiene_enfermedades = true;
  }
}

function mapearCamposDirectos() {
  Object.keys(props.datos).forEach(key => {
    if (Object.prototype.hasOwnProperty.call(form.value, key) &&
        (form.value[key] === '' || form.value[key] === null || form.value[key] === undefined)) {
      const valor = props.datos[key];
      if (valor !== null && valor !== undefined && valor !== '') {
        form.value[key] = valor;
      }
    }
  });
}

onMounted(async () => {
  await cargarCatalogos();

  if (props.datos && Object.keys(props.datos).length > 0) {
    const datosDeportista = props.datos.datos_deportista || props.datos.deportista || props.datos;
    const infoDeportiva = props.datos.informacion_deportiva || props.datos.datos_informacion_deportiva || {};

    mapearDatosDeportista(datosDeportista);
    mapearInformacionDeportiva(infoDeportiva);
    mapearDiagnosticos();
    mapearTipoEnfermedad();
    mapearCamposDirectos();
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
  font-size: 1.5rem;
  font-weight: bold;
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
