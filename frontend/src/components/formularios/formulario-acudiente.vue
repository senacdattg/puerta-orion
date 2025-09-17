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

    <!-- Sección 2: Información Familiar -->
    <section class="seccion-formulario" v-show="indiceActual === 1">
      <h3>Información Familiar</h3>

      <div class="fila-texto">
        <select
          v-model="form.estadoCivil"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>¿Cuál es su estado civil?</option>
          <option value="soltero">Soltero/a</option>
          <option value="casado">Casado/a</option>
          <option value="union_libre">Unión libre</option>
          <option value="divorciado">Divorciado/a</option>
          <option value="viudo">Viudo/a</option>
        </select>
        <input
          v-model="form.ocupacion"
          type="text"
          placeholder="¿Cuál es su ocupación?"
          required
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.empresa"
          type="text"
          placeholder="¿En qué empresa trabaja?"
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.cargo"
          type="text"
          placeholder="¿Qué cargo desempeña?"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.ingresosMensuales"
          type="number"
          placeholder="¿Cuáles son sus ingresos mensuales?"
          min="0"
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.nivelEducativo"
          type="text"
          placeholder="¿Cuál es su nivel educativo?"
          :readonly="modo === 'ver'"
        />
      </div>
    </section>

    <!-- Sección 3: Información de Contacto Adicional -->
    <section class="seccion-formulario" v-show="indiceActual === 2">
      <h3>Contacto Adicional</h3>

      <div class="fila-texto">
        <input
          v-model="form.telefonoTrabajo"
          type="text"
          placeholder="¿Cuál es su teléfono del trabajo?"
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.correoTrabajo"
          type="email"
          placeholder="¿Cuál es su correo del trabajo?"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.telefonoEmergencia"
          type="text"
          placeholder="¿Cuál es su teléfono de emergencia?"
          required
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.parentescoEmergencia"
          type="text"
          placeholder="¿Cuál es su parentesco con el contacto de emergencia?"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <textarea
          v-model="form.observacionesFamilia"
          placeholder="Observaciones sobre su situación familiar..."
          rows="4"
          :readonly="modo === 'ver'"
        ></textarea>
      </div>
    </section>

    <!-- Sección 4: Información del Deportista -->
    <section class="seccion-formulario" v-show="indiceActual === 3">
      <h3>Información del Deportista</h3>

      <div class="fila-texto">
        <input
          v-model="form.deportista.nombre"
          type="text"
          placeholder="¿Cuál es el nombre del deportista?"
          required
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.deportista.apellido"
          type="text"
          placeholder="¿Cuál es el apellido del deportista?"
          required
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.deportista.fechaNacimiento"
          type="date"
          :readonly="modo === 'ver'"
        />
        <select
          v-model="form.deportista.genero"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>¿Cuál es el género del deportista?</option>
          <option value="masculino">Masculino</option>
          <option value="femenino">Femenino</option>
        </select>
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.deportista.tipoDocumento"
          type="text"
          placeholder="¿Cuál es el tipo de documento del deportista?"
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.deportista.numeroDocumento"
          type="text"
          placeholder="¿Cuál es el número de documento del deportista?"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <textarea
          v-model="form.deportista.observaciones"
          placeholder="Observaciones sobre el deportista..."
          rows="4"
          :readonly="modo === 'ver'"
        ></textarea>
      </div>
    </section>

    <!-- Sección 5: Documentos y Autorizaciones -->
    <section class="seccion-formulario" v-show="indiceActual === 4">
      <h3>Documentos y Autorizaciones</h3>

      <div class="fila-texto">
        <input
          @change="manejarArchivo('cedula', $event)"
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          :disabled="modo === 'ver'"
        />
        <input
          @change="manejarArchivo('certificadoLaboral', $event)"
          type="file"
          accept=".pdf,.doc,.docx"
          :disabled="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          @change="manejarArchivo('certificadoBancario', $event)"
          type="file"
          accept=".pdf,.doc,.docx"
          :disabled="modo === 'ver'"
        />
        <input
          @change="manejarArchivo('otros', $event)"
          type="file"
          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
          :disabled="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="autorizaciones">
        <h4>Autorizaciones</h4>

        <div class="checkbox-item">
          <input
            type="checkbox"
            id="autorizacionDeportiva"
            v-model="form.autorizaciones.deportiva"
            :disabled="modo === 'ver'"
          />
          <label for="autorizacionDeportiva">
            Autorizo la participación del deportista en actividades deportivas
          </label>
        </div>

        <div class="checkbox-item">
          <input
            type="checkbox"
            id="autorizacionMedica"
            v-model="form.autorizaciones.medica"
            :disabled="modo === 'ver'"
          />
          <label for="autorizacionMedica">
            Autorizo la atención médica en caso de emergencia
          </label>
        </div>

        <div class="checkbox-item">
          <input
            type="checkbox"
            id="autorizacionImagen"
            v-model="form.autorizaciones.imagen"
            :disabled="modo === 'ver'"
          />
          <label for="autorizacionImagen">
            Autorizo el uso de imágenes del deportista para fines promocionales
          </label>
        </div>

        <div class="checkbox-item">
          <input
            type="checkbox"
            id="autorizacionViajes"
            v-model="form.autorizaciones.viajes"
            :disabled="modo === 'ver'"
          />
          <label for="autorizacionViajes">
            Autorizo la participación en viajes y competencias fuera de la ciudad
          </label>
        </div>
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <textarea
          v-model="form.observacionesGenerales"
          placeholder="Observaciones generales..."
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

  // Familiar
  estadoCivil: "", ocupacion: "",
  empresa: "", cargo: "",
  ingresosMensuales: "", nivelEducativo: "",

  // Contacto adicional
  telefonoTrabajo: "", correoTrabajo: "",
  telefonoEmergencia: "", parentescoEmergencia: "",
  observacionesFamilia: "",

  // Deportista
  deportista: {
    nombre: "", apellido: "",
    fechaNacimiento: "", genero: "",
    tipoDocumento: "", numeroDocumento: "",
    observaciones: ""
  },

  // Documentos
  documentos: {
    cedula: "", certificadoLaboral: "",
    certificadoBancario: "", otros: ""
  },

  // Autorizaciones
  autorizaciones: {
    deportiva: false,
    medica: false,
    imagen: false,
    viajes: false
  },

  observacionesGenerales: ""
});

// Función para obtener el título según el modo
function obtenerTitulo() {
  switch (props.modo) {
    case 'registrar':
      return 'Registro de Acudiente';
    case 'actualizar':
      return 'Actualizar Acudiente';
    case 'ver':
      return 'Información del Acudiente';
    default:
      return 'Acudiente';
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
      !form.value.ciudad || !form.value.direccion || !form.value.contrasena ||
      !form.value.estadoCivil || !form.value.ocupacion || !form.value.telefonoEmergencia ||
      !form.value.deportista.nombre || !form.value.deportista.apellido) {
    alert("Por favor complete todos los campos obligatorios");
    return;
  }

  // Validar autorizaciones mínimas
  if (!form.value.autorizaciones.deportiva || !form.value.autorizaciones.medica) {
    alert("Debe autorizar la participación deportiva y la atención médica");
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
/* Estilos específicos para el formulario de acudiente */
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

/* Autorizaciones */
.autorizaciones {
  margin: 20px 0;
}

.autorizaciones h4 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.checkbox-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #0047ab;
}

.checkbox-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin-top: 2px;
  accent-color: #0047ab;
}

.checkbox-item label {
  flex: 1;
  font-size: 0.95rem;
  line-height: 1.4;
  color: #333;
  cursor: pointer;
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

  .checkbox-item {
    flex-direction: column;
    gap: 8px;
  }
}
</style>



