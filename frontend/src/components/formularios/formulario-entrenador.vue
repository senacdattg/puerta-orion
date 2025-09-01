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
          :readonly="modo === 'ver'"
        />
        <select
          v-model="form.genero"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>¿Cuál es su género?</option>
          <option value="masculino">Masculino</option>
          <option value="femenino">Femenino</option>
        </select>
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.correo"
          type="email"
          placeholder="¿Cuál es su correo electrónico?"
          required
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.telefono"
          type="text"
          placeholder="¿Cuál es su número telefónico?"
          required
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.ciudad"
          type="text"
          placeholder="¿En qué ciudad reside?"
          required
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.direccion"
          type="text"
          placeholder="¿Cuál es su dirección?"
          required
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto" style="display: flex; justify-content: center;">
        <input
          type="password"
          v-model="form.contrasena"
          placeholder="Ingrese una contraseña"
          required
          :readonly="modo === 'ver'"
        />
        <input
          type="password"
          v-model="form.confirmarContrasena"
          placeholder="Confirme su contraseña"
          required
          :readonly="modo === 'ver'"
        />
      </div>
    </section>

    <!-- Sección 2: Información Profesional -->
    <section class="seccion-formulario" v-show="indiceActual === 1">
      <h3>Información Profesional</h3>

      <div class="fila-texto">
        <input
          v-model="form.profesion"
          type="text"
          placeholder="¿Cuál es su profesión?"
          required
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.especialidad"
          type="text"
          placeholder="¿Cuál es su especialidad deportiva?"
          required
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.institucion"
          type="text"
          placeholder="¿En qué institución se formó?"
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.anoGraduacion"
          type="number"
          placeholder="¿En qué año se graduó?"
          min="1950"
          max="2030"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.certificaciones"
          type="text"
          placeholder="¿Qué certificaciones tiene?"
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.experienciaAnos"
          type="number"
          placeholder="¿Cuántos años de experiencia tiene?"
          min="0"
          max="50"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <textarea
          v-model="form.biografia"
          placeholder="Cuéntenos brevemente sobre su experiencia y logros deportivos..."
          rows="4"
          :readonly="modo === 'ver'"
        ></textarea>
      </div>
    </section>

    <!-- Sección 3: Información Deportiva -->
    <section class="seccion-formulario" v-show="indiceActual === 2">
      <h3>Información Deportiva</h3>

      <div class="fila-texto">
        <select
          v-model="form.deportes"
          multiple
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>¿Qué deportes entrena?</option>
          <option value="futbol">Fútbol</option>
          <option value="baloncesto">Baloncesto</option>
          <option value="tenis">Tenis</option>
          <option value="natacion">Natación</option>
          <option value="atletismo">Atletismo</option>
          <option value="voleibol">Voleibol</option>
          <option value="otros">Otros</option>
        </select>
        <input
          v-model="form.nivelEntrenamiento"
          type="text"
          placeholder="¿Qué nivel de entrenamiento maneja?"
          required
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.clubesAnteriores"
          type="text"
          placeholder="¿En qué clubes ha trabajado anteriormente?"
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.logrosEntrenador"
          type="text"
          placeholder="¿Qué logros ha obtenido como entrenador?"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.horariosDisponibles"
          type="text"
          placeholder="¿Qué horarios tiene disponibles?"
          required
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.salarioEsperado"
          type="number"
          placeholder="¿Cuál es su expectativa salarial?"
          min="0"
          :readonly="modo === 'ver'"
        />
      </div>
    </section>

    <!-- Sección 4: Información de Contacto de Emergencia -->
    <section class="seccion-formulario" v-show="indiceActual === 3">
      <h3>Contacto de Emergencia</h3>

      <div class="fila-texto">
        <input
          v-model="form.contactoEmergencia.nombre"
          type="text"
          placeholder="Nombre del contacto de emergencia"
          required
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.contactoEmergencia.parentesco"
          type="text"
          placeholder="Parentesco"
          required
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.contactoEmergencia.telefono"
          type="text"
          placeholder="Teléfono de emergencia"
          required
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.contactoEmergencia.correo"
          type="email"
          placeholder="Correo de emergencia"
          :readonly="modo === 'ver'"
        />
      </div>
    </section>

    <!-- Sección 5: Documentos y Referencias -->
    <section class="seccion-formulario" v-show="indiceActual === 4">
      <h3>Documentos y Referencias</h3>

      <div class="fila-texto">
        <input
          @change="manejarArchivo('hojaVida', $event)"
          type="file"
          accept=".pdf,.doc,.docx"
          :disabled="modo === 'ver'"
        />
        <input
          @change="manejarArchivo('certificaciones', $event)"
          type="file"
          accept=".pdf,.doc,.docx"
          :disabled="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.referencias.nombre1"
          type="text"
          placeholder="Nombre de referencia 1"
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.referencias.telefono1"
          type="text"
          placeholder="Teléfono de referencia 1"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.referencias.nombre2"
          type="text"
          placeholder="Nombre de referencia 2"
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.referencias.telefono2"
          type="text"
          placeholder="Teléfono de referencia 2"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <textarea
          v-model="form.observaciones"
          placeholder="Observaciones adicionales..."
          rows="4"
          :readonly="modo === 'ver'"
        ></textarea>
      </div>
    </section>

    <!-- Navegación entre secciones -->
    <div class="navegacion-secciones">
      <button
        v-if="indiceActual > 0"
        type="button"
        class="btn-navegacion btn-anterior"
        @click="anteriorSeccion"
        :disabled="modo === 'ver'"
      >
        <i class="fas fa-arrow-left"></i>
        Anterior
      </button>

      <button
        v-if="indiceActual < totalSecciones - 1"
        type="button"
        class="btn-navegacion btn-siguiente"
        @click="siguienteSeccion"
        :disabled="modo === 'ver'"
      >
        Siguiente
        <i class="fas fa-arrow-right"></i>
      </button>
    </div>

    <!-- Indicador de progreso -->
    <div class="indicador-progreso">
      <div class="progreso-barra">
        <div
          class="progreso-fill"
          :style="{ width: `${((indiceActual + 1) / totalSecciones) * 100}%` }"
        ></div>
      </div>
      <span class="progreso-texto">{{ indiceActual + 1 }} de {{ totalSecciones }}</span>
    </div>

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
  contrasena: "", confirmarContrasena: "",

  // Profesional
  profesion: "", especialidad: "",
  institucion: "", anoGraduacion: "",
  certificaciones: "", experienciaAnos: "",
  biografia: "",

  // Deportiva
  deportes: [], nivelEntrenamiento: "",
  clubesAnteriores: "", logrosEntrenador: "",
  horariosDisponibles: "", salarioEsperado: "",

  // Contacto de emergencia
  contactoEmergencia: {
    nombre: "", parentesco: "",
    telefono: "", correo: ""
  },

  // Documentos y referencias
  documentos: {
    hojaVida: "", certificaciones: ""
  },
  referencias: {
    nombre1: "", telefono1: "",
    nombre2: "", telefono2: ""
  },
  observaciones: ""
});

// Función para obtener el título según el modo
function obtenerTitulo() {
  switch (props.modo) {
    case 'registrar':
      return 'Registro de Entrenador';
    case 'actualizar':
      return 'Actualizar Entrenador';
    case 'ver':
      return 'Información del Entrenador';
    default:
      return 'Entrenador';
  }
}

// Función para obtener el texto del botón según el modo
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

// Navegación entre secciones
function siguienteSeccion() {
  if (indiceActual.value < totalSecciones - 1) {
    indiceActual.value++;
  }
}

function anteriorSeccion() {
  if (indiceActual.value > 0) {
    indiceActual.value--;
  }
}

// Manejo del formulario
function manejarSubmit() {
  // Validar contraseñas
  if (form.value.contrasena !== form.value.confirmarContrasena) {
    alert("Las contraseñas no coinciden");
    return;
  }

  // Validar campos requeridos
  if (!form.value.nombre1 || !form.value.apellido1 || !form.value.tipoDocumento ||
      !form.value.numeroDocumento || !form.value.correo || !form.value.telefono ||
      !form.value.ciudad || !form.value.direccion || !form.value.contrasena) {
    alert("Por favor complete todos los campos obligatorios");
    return;
  }

  // Emitir evento con los datos del formulario
  emit('submit', { ...form.value });
}

function cancelar() {
  emit('cancel');
}

// Función para manejar archivos
function manejarArchivo(campo, event) {
  const file = event.target.files[0];
  if (file) {
    form.value.documentos[campo] = file;
  }
}

// Cargar datos si se proporcionan
onMounted(() => {
  if (props.datos && Object.keys(props.datos).length > 0) {
    form.value = { ...form.value, ...props.datos };
  }
});

// Observar cambios en los datos
watch(() => props.datos, (nuevosDatos) => {
  if (nuevosDatos && Object.keys(nuevosDatos).length > 0) {
    form.value = { ...form.value, ...nuevosDatos };
  }
}, { deep: true });
</script>

<style scoped>
/* Estilos específicos para el formulario de entrenador */
.formulario-datos {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.seccion-formulario {
  margin-bottom: 30px;
}

.seccion-formulario h3 {
  color: #0047ab;
  font-size: 1.5rem;
  margin-bottom: 20px;
  text-align: center;
  border-bottom: 2px solid #0047ab;
  padding-bottom: 10px;
}

.fila-texto {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.fila-texto input,
.fila-texto select,
.fila-texto textarea {
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.fila-texto input:focus,
.fila-texto select:focus,
.fila-texto textarea:focus {
  outline: none;
  border-color: #0047ab;
  box-shadow: 0 0 0 3px rgba(0, 71, 171, 0.1);
}

.fila-texto textarea {
  resize: vertical;
  min-height: 100px;
}

.form-divider {
  border: none;
  height: 1px;
  background: linear-gradient(to right, transparent, #0047ab, transparent);
  margin: 25px 0;
}

/* Navegación entre secciones */
.navegacion-secciones {
  display: flex;
  justify-content: space-between;
  margin: 30px 0;
}

.btn-navegacion {
  background: #0047ab;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-navegacion:hover:not(:disabled) {
  background: #003d91;
  transform: translateY(-2px);
}

.btn-navegacion:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Indicador de progreso */
.indicador-progreso {
  text-align: center;
  margin: 30px 0;
}

.progreso-barra {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progreso-fill {
  height: 100%;
  background: linear-gradient(90deg, #0047ab, #0d47a1);
  transition: width 0.3s ease;
}

.progreso-texto {
  color: #666;
  font-size: 0.9rem;
}

/* Botones del formulario */
.botones-formulario {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
}

.boton-formulario {
  background: #0047ab;
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.boton-formulario:hover {
  background: #003d91;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 71, 171, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .fila-texto {
    grid-template-columns: 1fr;
  }

  .navegacion-secciones {
    flex-direction: column;
    gap: 15px;
  }

  .btn-navegacion {
    width: 100%;
    justify-content: center;
  }
}
</style>



