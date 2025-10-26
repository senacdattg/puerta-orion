<!-- src/components/formulario-deportista.vue -->
<template>
  <form class="formulario-datos" @submit.prevent="manejarSubmit">
    <!-- Sección 1: Información Básica -->
    <section class="seccion-formulario" v-show="indiceActual === 0">
      <h3>{{ obtenerTitulo() }}</h3>

      <div class="fila-texto">
        <input
          v-model="form.nombre1"
          type="text"
          placeholder="¿Cuál es su primer nombre?"
          required
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.nombre2"
          type="text"
          placeholder="¿Cuál es su segundo nombre?"
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.apellido1"
          type="text"
          placeholder="¿Cuál es su primer apellido?"
          required
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.apellido2"
          type="text"
          placeholder="¿Cuál es su segundo apellido?"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <select
          v-model="form.tipoDocumento"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>¿Cuál es su tipo de documento?</option>
          <option>Cédula</option>
          <option>Tarjeta de identidad</option>
          <option>Pasaporte</option>
        </select>
        <input
          v-model="form.numeroDocumento"
          type="text"
          placeholder="¿Cuál es su número de documento?"
          required
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.fechaNacimiento"
          type="date"
          placeholder="¿En qué fecha nació?"
          required
          :readonly="modo === 'ver'"
        />
        <select
          v-model="form.genero"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>¿Cuál es su género?</option>
          <option>Masculino</option>
          <option>Femenino</option>
        </select>
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.correo"
          type="text"
          placeholder="¿Cuál es su correo electrónico?"
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.telefono"
          type="text"
          placeholder="¿Cuál es su número telefónico?"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <select
          v-model="form.ciudad"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>¿Cuál es su ciudad de residencia?</option>
          <option>Retorno</option>
          <option>San Jose</option>
          <option>Otro</option>
        </select>
        <input
          v-model="form.direccion"
          type="text"
          placeholder="¿Cuál es su dirección de residencia?"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div v-if="modo !== 'ver'">
        <div class="fila-texto">
          <input
            v-model="form.password"
            type="password"
            placeholder="Contraseña"
            :readonly="modo === 'ver'"
          />
          <input
            v-model="form.password2"
            type="password"
            placeholder="Confirmar contraseña"
            :readonly="modo === 'ver'"
          />
        </div>

        <!-- Divider line below password fields -->
        <hr class="form-divider" />
      </div>

      <!-- Botones de navegación - SIEMPRE visibles para poder ver todas las secciones -->
      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguiente">Siguiente</button>
      </div>

      <hr class="form-divider" />
    </section>

    <!-- Sección 2: Antecedentes Médicos -->
    <section class="seccion-formulario" v-show="indiceActual === 1">
      <h3>Antecedentes Médicos</h3>

      <div class="fila-texto">
        <select
          v-model="form.eps"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>¿A que EPS está afiliado?</option>
          <option>Nueva EPS</option>
          <option>PONAL</option>
          <option>Otro</option>
        </select>
      </div>

      <hr class="form-divider" />

      <div class="fila-texto bloque-radio">
        <label>¿Existe algún tipo de recomendación médica que se deba tener presente para la actividad deportiva?</label>
        <div class="opciones">
          <input
            type="radio"
            id="reco-si"
            name="recomendacion-medica"
            value="si"
            v-model="form.recomendacionMedica"
            :disabled="modo === 'ver'"
          />
          <label for="reco-si">Sí</label>
          <input
            type="radio"
            id="reco-no"
            name="recomendacion-medica"
            value="no"
            v-model="form.recomendacionMedica"
            :disabled="modo === 'ver'"
          />
          <label for="reco-no">No</label>
        </div>

        <div class="campo-condicional" v-show="form.recomendacionMedica === 'si'">
          <label for="recomendacion-medica-texto">Describa la recomendación:</label>
          <textarea
            id="recomendacion-medica-texto"
            v-model="form.descripcionRecomendacion"
            placeholder="Escriba aquí..."
            :readonly="modo === 'ver'"
          ></textarea>
        </div>
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <select
          v-model="form.grupoSanguineo"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>¿Cuál es su grupo sanguíneo?</option>
          <option>A+</option>
          <option>A-</option>
          <option>Otro</option>
        </select>
      </div>

      <hr class="form-divider" />

      <!-- Botones de navegación - SIEMPRE visibles -->
      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario anterior" style="width: 120px;" @click="anterior">Anterior</button>
        <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguiente">Siguiente</button>
      </div>

      <hr class="form-divider" />
    </section>

    <!-- Sección 3: Información Escolar -->
    <section class="seccion-formulario" v-show="indiceActual === 2">
      <h3>Información Escolar</h3>

      <div class="fila-texto">
        <select
          v-model="form.institucion"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>¿En qué institución educativa estudia actualmente?</option>
          <option>SENA</option>
          <option>SANTANDER</option>
          <option>Otro</option>
        </select>
      </div>

      <hr class="form-divider" />

      <!-- Botones de navegación - SIEMPRE visibles -->
      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario anterior" style="width: 120px;" @click="anterior">Anterior</button>
        <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguiente">Siguiente</button>
      </div>

      <hr class="form-divider" />
    </section>

    <!-- Sección 4: Información Deportiva -->
    <section class="seccion-formulario" v-show="indiceActual === 3">
      <h3>Información Deportiva</h3>

      <div class="bloque-radio">
        <label for="radio-deporte-si">¿Practica o ha practicado antes otro deporte además del voleibol?</label>
        <div class="opciones">
          <input
            type="radio"
            id="deporte-si"
            name="deporte"
            value="si"
            v-model="form.practicaOtroDeporte"
            :disabled="modo === 'ver'"
          />
          <label for="deporte-si">Sí</label>
          <input
            type="radio"
            id="deporte-no"
            name="deporte"
            value="no"
            v-model="form.practicaOtroDeporte"
            :disabled="modo === 'ver'"
          />
          <label for="deporte-no">No</label>
        </div>

        <div class="campo-condicional" v-show="form.practicaOtroDeporte === 'si'">
          <label for="deporte-texto">¿Cuál deporte?</label>
          <textarea
            id="deporte-texto"
            v-model="form.deporteCual"
            placeholder="Escriba aquí..."
            :readonly="modo === 'ver'"
          ></textarea>
        </div>
      </div>

      <hr class="form-divider" />

      <div class="bloque-radio">
        <label for="escuela-si">¿Participa o ha participado en otras escuelas de formación?</label>
        <div class="opciones">
          <input
            type="radio"
            id="escuela-si"
            name="escuela-formacion"
            value="si"
            v-model="form.participaEscuela"
            :disabled="modo === 'ver'"
          />
          <label for="escuela-si">Sí</label>

          <input
            type="radio"
            id="escuela-no"
            name="escuela-formacion"
            value="no"
            v-model="form.participaEscuela"
            :disabled="modo === 'ver'"
          />
          <label for="escuela-no">No</label>
        </div>

        <div class="campo-condicional" v-show="form.participaEscuela === 'si'">
          <label for="escuela-texto">¿En cuál escuela ha participado?</label>
          <textarea
            id="escuela-texto"
            v-model="form.escuelaCual"
            placeholder="Escriba aquí..."
            :readonly="modo === 'ver'"
          ></textarea>
        </div>
      </div>

      <hr class="form-divider" />

      <!-- Botones de navegación - SIEMPRE visibles -->
      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario anterior" style="width: 120px;" @click="anterior">Anterior</button>
        <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguiente">Siguiente</button>
      </div>

      <hr class="form-divider" />
    </section>

    <!-- Sección 5: Información del Acudiente -->
    <section class="seccion-formulario" v-show="indiceActual === 4">
      <h3>Información del Acudiente</h3>

      <div class="fila-texto">
        <input
          v-model="form.acudienteNombre1"
          type="text"
          placeholder="¿Cuál es el primer nombre de su acudiente?"
          required
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.acudienteNombre2"
          type="text"
          placeholder="¿Cuál es el segundo nombre de su acudiente?"
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.acudienteApellido1"
          type="text"
          placeholder="¿Cuál es el primer apellido de su acudiente?"
          required
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.acudienteApellido2"
          type="text"
          placeholder="¿Cuál es el segundo apellido de su acudiente?"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto fila-centro">
        <select
          v-model="form.parentesco"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>¿Qué parentesco tienen?</option>
          <option>Padre</option>
          <option>Madre</option>
          <option>Hermano</option>
          <option>Otro</option>
        </select>
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.acudienteFechaNac"
          type="date"
          placeholder="¿En qué fecha nació el acudiente?"
          required
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <select
          v-model="form.acudienteTipoDoc"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>¿Cuál es el tipo de documento de su acudiente?</option>
          <option>Cédula</option>
          <option>Contraseña</option>
          <option>Pasaporte</option>
        </select>
        <input
          v-model="form.acudienteNumeroDoc"
          type="text"
          placeholder="¿Cuál es el número de documento de su acudiente?"
          required
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.acudienteCorreo"
          type="text"
          placeholder="¿Cuál es el correo electrónico de su acudiente?"
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.acudienteTelefono"
          type="text"
          placeholder="¿Cuál es el número telefónico de su acudiente?"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <!-- Botones de navegación - SIEMPRE visibles -->
      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario anterior" style="width: 120px;" @click="anterior">Anterior</button>
      </div>

      <hr class="form-divider" />

      <!-- Botones de acción - SOLO en modos actualizar y registrar -->
      <div v-if="modo !== 'ver'" class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="submit" class="boton-formulario" style="width: 120px;">
          {{ obtenerTextoBoton() }}
        </button>
        <button
          v-if="modo === 'actualizar'"
          type="button"
          class="boton-formulario"
          style="width: 120px;"
          @click="cancelar"
        >
          Cancelar actualización
        </button>
      </div>
    </section>
  </form>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";

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
});

// Emitir eventos al componente padre
const emit = defineEmits(['submit', 'cancel']);

const indiceActual = ref(0);
const totalSecciones = 5;

const form = ref({
  // Básicos
  nombre1: "", nombre2: "", apellido1: "", apellido2: "",
  tipoDocumento: "", numeroDocumento: "",
  fechaNacimiento: "", genero: "",
  correo: "", telefono: "",
  ciudad: "", direccion: "",
  password: "", password2: "",

  // Médicos
  eps: "", grupoSanguineo: "",
  recomendacionMedica: "", descripcionRecomendacion: "",

  // Escolar
  institucion: "",

  // Deportivos
  practicaOtroDeporte: "", deporteCual: "",
  participaEscuela: "", escuelaCual: "",

  // Acudiente
  acudienteNombre1: "", acudienteNombre2: "",
  acudienteApellido1: "", acudienteApellido2: "",
  parentesco: "", acudienteFechaNac: "",
  acudienteTipoDoc: "", acudienteNumeroDoc: "",
  acudienteCorreo: "", acudienteTelefono: ""
});

// Función para obtener el título según el modo
function obtenerTitulo() {
  switch (props.modo) {
    case 'registrar':
      return 'Registrarse';
    case 'actualizar':
      return 'Actualizar perfil';
    case 'ver':
      return 'Información del deportista';
    default:
      return 'Formulario';
  }
}

// Función para obtener el texto del botón según el modo
function obtenerTextoBoton() {
  switch (props.modo) {
    case 'registrar':
      return 'Registrarse';
    case 'actualizar':
      return 'Aceptar actualización';
    default:
      return 'Enviar';
  }
}

// Cargar datos cuando se proporcionen
onMounted(() => {
  if (props.datos && Object.keys(props.datos).length > 0) {
    Object.keys(props.datos).forEach(key => {
      if (form.value.hasOwnProperty(key)) {
        form.value[key] = props.datos[key];
      }
    });
  }
});

// Observar cambios en los datos
watch(() => props.datos, (nuevosDatos) => {
  if (nuevosDatos && Object.keys(nuevosDatos).length > 0) {
    console.log('Datos recibidos en formulario deportista:', nuevosDatos);

    // Mapear datos del usuario a campos del formulario
    const mapeoDatos = {
      // Información personal - mapeo correcto desde la estructura del backend
      'persona.primer_nombre': 'nombre1',
      'persona.segundo_nombre': 'nombre2',
      'persona.primer_apellido': 'apellido1',
      'persona.segundo_apellido': 'apellido2',
      'persona.documento': 'numeroDocumento',
      'persona.correo_electronico': 'correo',
      'persona.telefono': 'telefono',
      'persona.fecha_nacimiento': 'fechaNacimiento',
      'persona.direccion': 'direccion',

      // Datos deportivos
      peso: 'peso',
      altura: 'altura',
      categoria: 'categoria',
      tipo_sangre: 'tipoSangre',
      eps: 'eps',

      // Datos médicos
      alergias: 'alergias',
      medicamentos: 'medicamentos',
      condiciones_medicas: 'condicionesMedicas',

      // Datos escolares
      institucion_educativa: 'institucionEducativa',
      grado: 'grado',
      jornada: 'jornada'
    };

    // Función helper para obtener valor anidado
    const obtenerValorAnidado = (obj, path) => {
      return path.split('.').reduce((current, key) => current?.[key], obj);
    };

    // Aplicar mapeo con soporte para rutas anidadas
    Object.keys(mapeoDatos).forEach(datoKey => {
      const formKey = mapeoDatos[datoKey];
      const valor = obtenerValorAnidado(nuevosDatos, datoKey);

      if (valor && form.value.hasOwnProperty(formKey)) {
        form.value[formKey] = valor;
        console.log(`Mapeado ${datoKey} -> ${formKey}: ${valor}`);
      }
    });

    // Mapear datos directos si existen (para compatibilidad)
    Object.keys(nuevosDatos).forEach(key => {
      if (form.value.hasOwnProperty(key)) {
        form.value[key] = nuevosDatos[key];
      }
    });

    // Mapear datos de persona si existen directamente
    if (nuevosDatos.persona) {
      const persona = nuevosDatos.persona;
      if (persona.primer_nombre && form.value.hasOwnProperty('nombre1')) {
        form.value.nombre1 = persona.primer_nombre;
      }
      if (persona.segundo_nombre && form.value.hasOwnProperty('nombre2')) {
        form.value.nombre2 = persona.segundo_nombre;
      }
      if (persona.primer_apellido && form.value.hasOwnProperty('apellido1')) {
        form.value.apellido1 = persona.primer_apellido;
      }
      if (persona.segundo_apellido && form.value.hasOwnProperty('apellido2')) {
        form.value.apellido2 = persona.segundo_apellido;
      }
      if (persona.documento && form.value.hasOwnProperty('numeroDocumento')) {
        form.value.numeroDocumento = persona.documento;
      }
      if (persona.correo_electronico && form.value.hasOwnProperty('correo')) {
        form.value.correo = persona.correo_electronico;
      }
      if (persona.telefono && form.value.hasOwnProperty('telefono')) {
        form.value.telefono = persona.telefono;
      }
      if (persona.direccion && form.value.hasOwnProperty('direccion')) {
        form.value.direccion = persona.direccion;
      }
    }
  }
}, { deep: true, immediate: true });

function siguiente() {
  if (indiceActual.value < totalSecciones - 1) indiceActual.value++;
}

function anterior() {
  if (indiceActual.value > 0) indiceActual.value--;
}

function manejarSubmit() {
  emit('submit', form.value);
}

function cancelar() {
  emit('cancel');
}
</script>
