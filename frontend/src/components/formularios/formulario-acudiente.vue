<template>
  <form class="formulario-datos" @submit.prevent="manejarSubmit">

    <!-- Sección 1: Información Personal -->
    <section class="seccion-formulario" v-show="indiceActual === 0">
      <h3>{{ obtenerTitulo() }}</h3>

      <div class="fila-texto">
        <input
          v-model="form.primer_nombre"
          type="text"
          placeholder="¿Cuál es su primer nombre?"
          required
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.segundo_nombre"
          type="text"
          placeholder="¿Cuál es su segundo nombre?"
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.primer_apellido"
          type="text"
          placeholder="¿Cuál es su primer apellido?"
          required
          :readonly="modo === 'ver'"
        />
        <input
          v-model="form.segundo_apellido"
          type="text"
          placeholder="¿Cuál es su segundo apellido?"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <select
          v-model="form.id_tipo_documento"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled selected>Seleccione el tipo de documento</option>
          <option v-for="tipo in tiposDocumento" :key="tipo.id_tipo_documento" :value="tipo.id_tipo_documento">
            {{ tipo.nombre_documento }}
          </option>
        </select>
        <input
          v-model="form.documento"
          type="number"
          placeholder="¿Cuál es su número de documento?"
          required
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <select
          v-model="form.id_sexo"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled selected>Seleccione el género</option>
          <option v-for="sexo in sexos" :key="sexo.id_sexo" :value="sexo.id_sexo">
            {{ sexo.sexo ? 'Masculino' : 'Femenino' }}
          </option>
        </select>
        <input
          v-model="form.correo_electronico"
          type="email"
          placeholder="¿Cuál es su correo electrónico?"
          required
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input
          v-model="form.telefono"
          type="number"
          placeholder="¿Cuál es su número telefónico?"
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
          v-model="form.password_hash"
          placeholder="Ingrese una contraseña"
          required
          :readonly="modo === 'ver'"
        />
        <input
          type="password"
          v-model="form.confirmar_password"
          placeholder="Confirme su contraseña"
          required
          :readonly="modo === 'ver'"
        />
      </div>

      <!-- Divider line below password fields -->
      <hr class="form-divider" />

      <!-- Botones de navegación - SIEMPRE visibles para poder ver todas las secciones -->
      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguienteSeccion">Siguiente</button>
      </div>

      <hr class="form-divider" />
    </section>

    <!-- Sección 2: Información del Acudiente -->
    <section class="seccion-formulario" v-show="indiceActual === 1">
      <h3>Información del Acudiente</h3>

      <div class="fila-texto">
        <select
          v-model="form.estado"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled>Seleccione el estado del acudiente</option>
          <option value="1">Activo</option>
          <option value="0">Inactivo</option>
        </select>
        <input
          v-model="form.observaciones_acudiente"
          type="text"
          placeholder="Información adicional sobre el acudiente (opcional)"
          :readonly="modo === 'ver'"
        />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <textarea
          v-model="form.informacion_contacto_emergencia"
          placeholder="Información de contacto de emergencia..."
          rows="4"
          :readonly="modo === 'ver'"
        ></textarea>
      </div>

      <hr class="form-divider" />

      <!-- Botones de navegación - SIEMPRE visibles -->
      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario anterior" style="width: 120px;" @click="anteriorSeccion">Anterior</button>
        <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguienteSeccion">Siguiente</button>
      </div>

      <hr class="form-divider" />
    </section>

    <!-- Sección 3: Relación con Deportista -->
    <section class="seccion-formulario" v-show="indiceActual === 2">
      <h3>Relación con Deportista</h3>

      <div class="fila-texto">
        <select
          v-model="form.id_deportista"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled selected>Seleccione el deportista</option>
          <option v-for="deportista in deportistas" :key="deportista.id_deportista" :value="deportista.id_deportista">
            {{ deportista.persona.primer_nombre }} {{ deportista.persona.primer_apellido }}
          </option>
        </select>
        <select
          v-model="form.id_parentesco"
          required
          :disabled="modo === 'ver'"
        >
          <option value="" disabled selected>Seleccione el parentesco</option>
          <option v-for="parentesco in parentescos" :key="parentesco.id_parentesco" :value="parentesco.id_parentesco">
            {{ parentesco.nombre }}
          </option>
        </select>
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <div class="checkbox-item">
          <input
            type="checkbox"
            id="es_responsable"
            v-model="form.es_responsable"
            :disabled="modo === 'ver'"
          />
          <label for="es_responsable">
            ¿Es responsable legal del deportista?
          </label>
        </div>
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <textarea
          v-model="form.observaciones_relacion"
          placeholder="Observaciones sobre la relación con el deportista..."
          rows="4"
          :readonly="modo === 'ver'"
        ></textarea>
      </div>

      <hr class="form-divider" />

      <!-- Botones de navegación - SIEMPRE visibles -->
      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario anterior" style="width: 120px;" @click="anteriorSeccion">Anterior</button>
        <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguienteSeccion">Siguiente</button>
      </div>

      <hr class="form-divider" />
    </section>

    <!-- Sección 4: Autorizaciones -->
    <section class="seccion-formulario" v-show="indiceActual === 3">
      <h3>Autorizaciones</h3>

      <div class="autorizaciones">
        <div class="checkbox-item">
          <input
            type="checkbox"
            id="autorizacionDeportiva"
            v-model="form.autorizacion_deportiva"
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
            v-model="form.autorizacion_medica"
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
            v-model="form.autorizacion_imagen"
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
            v-model="form.autorizacion_viajes"
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
          v-model="form.observaciones_generales"
          
          placeholder="Observaciones generales..."
          rows="4"
          :readonly="modo === 'ver'"
        ></textarea>
      </div>

      <hr class="form-divider" />

      <!-- Botones de navegación - SIEMPRE visibles -->
      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario anterior" style="width: 120px;" @click="anteriorSeccion">Anterior</button>
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
const totalSecciones = 4;

const form = ref({
  // Campos de la tabla Personas
  primer_nombre: "",
  segundo_nombre: "",
  primer_apellido: "",
  segundo_apellido: "",
  documento: "",
  correo_electronico: "",
  direccion: "",
  telefono: "",
  password_hash: "",
  confirmar_password: "",
  estado: "",
  fecha_registro: new Date().toISOString().split('T')[0],
  id_tipo_documento: "",
  id_sexo: "",

  // Campos de la tabla Acudiente
  observaciones_acudiente: "",
  informacion_contacto_emergencia: "",

  // Campos de la tabla DeportistaAcudiente
  id_deportista: "",
  id_parentesco: "",
  es_responsable: false,
  observaciones_relacion: "",

  // Autorizaciones (campos adicionales)
  autorizacion_deportiva: false,
  autorizacion_medica: false,
  autorizacion_imagen: false,
  autorizacion_viajes: false,
  observaciones_generales: ""
});

// Datos para los selects
const tiposDocumento = ref([]);
const sexos = ref([]);
const deportistas = ref([]);
const parentescos = ref([]);

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
  if (form.value.password_hash !== form.value.confirmar_password) {
    alert("Las contraseñas no coinciden");
    return;
  }

  // Validar campos requeridos
  if (!form.value.primer_nombre || !form.value.primer_apellido || !form.value.id_tipo_documento ||
      !form.value.documento || !form.value.correo_electronico || !form.value.telefono ||
      !form.value.direccion || !form.value.password_hash || !form.value.id_sexo ||
      !form.value.id_deportista || !form.value.id_parentesco) {
    alert("Por favor complete todos los campos obligatorios");
    return;
  }

  // Validar autorizaciones mínimas
  if (!form.value.autorizacion_deportiva || !form.value.autorizacion_medica) {
    alert("Debe autorizar la participación deportiva y la atención médica");
    return;
  }

  // Emitir evento con los datos del formulario
  emit('submit', { ...form.value });
}

function cancelar() {
  emit('cancel');
}

// Función para cargar datos de los selects
async function cargarDatosSelects() {
  try {
    // Aquí se harían las llamadas a la API para cargar los datos
    // Por ahora se simulan con datos estáticos
    tiposDocumento.value = [
      { id_tipo_documento: 1, nombre_documento: "Cédula" },
      { id_tipo_documento: 2, nombre_documento: "Tarjeta de identidad" },
      { id_tipo_documento: 3, nombre_documento: "Pasaporte" }
    ];

    sexos.value = [
      { id_sexo: 1, sexo: true }, // Masculino
      { id_sexo: 2, sexo: false }  // Femenino
    ];

    parentescos.value = [
      { id_parentesco: 1, nombre: "Padre" },
      { id_parentesco: 2, nombre: "Madre" },
      { id_parentesco: 3, nombre: "Tutor" },
      { id_parentesco: 4, nombre: "Abuelo/a" },
      { id_parentesco: 5, nombre: "Tío/a" }
    ];

    // Los deportistas se cargarían desde la API
    deportistas.value = [
      // Ejemplo de estructura esperada
      // { id_deportista: 1, persona: { primer_nombre: "Juan", primer_apellido: "Pérez" } }
    ];
  } catch (error) {
    console.error("Error cargando datos de selects:", error);
  }
}

// Cargar datos si se proporcionan
onMounted(async () => {
  // Cargar datos de los selects
  await cargarDatosSelects();
  
  // Cargar datos del formulario si se proporcionan
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

/* Responsive */
@media (max-width: 768px) {
  .checkbox-item {
    flex-direction: column;
    gap: 8px;
  }
}
</style>

