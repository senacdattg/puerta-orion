<template>
  <form class="formulario-datos" @submit.prevent="manejarSubmit">
    <!-- Sección 1: Información Básica -->
    <section class="seccion-formulario" v-show="indiceActual === 0">
      <h3>{{ obtenerTitulo() }}</h3>

      <div class="fila-texto">
        <input v-model="form.nombre1" type="text" placeholder="¿Cuál es su primer nombre?" required
          :readonly="modo === 'ver'" @input="(event) => manejarNombreCampo('nombre1', event)" />
        <input v-model="form.nombre2" type="text" placeholder="¿Cuál es su segundo nombre?"
          :readonly="modo === 'ver'" @input="(event) => manejarNombreCampo('nombre2', event, false)" />
        <input v-model="form.apellido1" type="text" placeholder="¿Cuál es su primer apellido?" required
          :readonly="modo === 'ver'" @input="(event) => manejarNombreCampo('apellido1', event)" />
        <input v-model="form.apellido2" type="text" placeholder="¿Cuál es su segundo apellido?"
          :readonly="modo === 'ver'" @input="(event) => manejarNombreCampo('apellido2', event, false)" />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <select v-model="form.tipoDocumento" required :disabled="modo === 'ver' || cargandoCatalogos">
          <option value="" disabled>¿Cuál es su tipo de documento?</option>
          <option v-for="tipo in tiposDocumento" :key="tipo.id" :value="tipo.id">
            {{ tipo.nombre }}
          </option>
        </select>
        <input v-model="form.numeroDocumento" type="text" placeholder="¿Cuál es su número de documento?" required
          :readonly="modo === 'ver'" @input="manejarDocumento" />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input v-model="form.fechaNacimiento" type="date" :readonly="modo === 'ver'" />
        <select v-model="form.genero" required :disabled="modo === 'ver' || cargandoCatalogos">
          <option value="" disabled>¿Cuál es su género?</option>
          <option v-for="sexo in sexos" :key="sexo.id" :value="sexo.valor">
            {{ sexo.nombre }}
          </option>
        </select>
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input v-model="form.correo" type="email" placeholder="¿Cuál es su correo electrónico?" required
          :readonly="modo === 'ver'" @input="manejarCorreo" />
        <input v-model="form.telefono" type="text" placeholder="¿Cuál es su número telefónico?" required
          :readonly="modo === 'ver'" @input="(event) => manejarTelefonoCampo('telefono', event)" />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input v-model="form.ciudad" type="text" placeholder="¿En qué ciudad reside?" required
          :readonly="modo === 'ver'" @input="(event) => manejarTextoCampo('ciudad', event)" />
        <input v-model="form.direccion" type="text" placeholder="¿Cuál es su dirección?" required
          :readonly="modo === 'ver'" @input="(event) => manejarDireccionCampo('direccion', event)" />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto" style="display: flex; justify-content: center;">
        <input type="password" v-model="form.contrasena" placeholder="Ingrese una contraseña" required
          :readonly="modo === 'ver'" />
        <input type="password" v-model="form.confirmarContrasena" placeholder="Confirme su contraseña" required
          :readonly="modo === 'ver'" />
      </div>

      <!-- Divider line below password fields -->
      <hr class="form-divider" />

      <!-- Botones de navegación - SIEMPRE visibles para poder ver todas las secciones -->
      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguienteSeccion">Siguiente</button>
      </div>

    </section>

    <!-- Sección 2: Información Profesional -->
    <section class="seccion-formulario" v-show="indiceActual === 1">
      <h3>Información Profesional</h3>

      <div class="fila-texto">
        <input v-model="form.profesion" type="text" placeholder="¿Cuál es su profesión?" required
          :readonly="modo === 'ver'" @input="(event) => manejarTextoCampo('profesion', event)" />
        <input v-model="form.especialidad" type="text" placeholder="¿Cuál es su especialidad deportiva?" required
          :readonly="modo === 'ver'" @input="(event) => manejarTextoCampo('especialidad', event)" />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input v-model="form.institucion" type="text" placeholder="¿En qué institución se formó?"
          :readonly="modo === 'ver'" @input="(event) => manejarTextoCampo('institucion', event)" />
        <input v-model="form.anoGraduacion" type="number" placeholder="¿En qué año se graduó?" min="1950" max="2030"
          :readonly="modo === 'ver'" />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input v-model="form.certificaciones" type="text" placeholder="¿Qué certificaciones tiene?"
          :readonly="modo === 'ver'" @input="(event) => manejarTextoCampo('certificaciones', event)" />
        <input v-model="form.experienciaAnos" type="number" placeholder="¿Cuántos años de experiencia tiene?" min="0"
          max="50" :readonly="modo === 'ver'" />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <textarea v-model="form.biografia"
          placeholder="Cuéntenos brevemente sobre su experiencia y logros deportivos..." rows="4"
          :readonly="modo === 'ver'" @input="(event) => manejarTextoCampo('biografia', event)"></textarea>
      </div>
      <hr class="form-divider" />
      <!-- Botones de navegación - SIEMPRE visibles -->
      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario anterior" style="width: 120px;" @click="anteriorSeccion">Anterior</button>
        <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguienteSeccion">Siguiente</button>
      </div>

      <hr class="form-divider" />
    </section>

    <!-- Sección 3: Información Deportiva -->
    <section class="seccion-formulario" v-show="indiceActual === 2">
      <h3>Información Deportiva</h3>

      <div class="fila-texto">
        <select v-model="form.deportes" required :disabled="modo === 'ver'">
          <option value="" disabled>¿Qué deportes entrena?</option>
          <option value="futbol">Fútbol</option>
          <option value="baloncesto">Baloncesto</option>
          <option value="tenis">Tenis</option>
          <option value="natacion">Natación</option>
          <option value="atletismo">Atletismo</option>
          <option value="voleibol">Voleibol</option>
          <option value="otros">Otros</option>
        </select>
        <input v-model="form.nivelEntrenamiento" type="text" placeholder="¿Qué nivel de entrenamiento maneja?" required
          :readonly="modo === 'ver'" @input="(event) => manejarTextoCampo('nivelEntrenamiento', event)" />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input v-model="form.clubesAnteriores" type="text" placeholder="¿En qué clubes ha trabajado anteriormente?"
          :readonly="modo === 'ver'" @input="(event) => manejarTextoCampo('clubesAnteriores', event)" />
        <input v-model="form.logrosEntrenador" type="text" placeholder="¿Qué logros ha obtenido como entrenador?"
          :readonly="modo === 'ver'" @input="(event) => manejarTextoCampo('logrosEntrenador', event)" />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input v-model="form.horariosDisponibles" type="text" placeholder="¿Qué horarios tiene disponibles?" required
          :readonly="modo === 'ver'" @input="(event) => manejarTextoCampo('horariosDisponibles', event)" />
        <input v-model="form.salarioEsperado" type="number" placeholder="¿Cuál es su expectativa salarial?" min="0"
          :readonly="modo === 'ver'" />
      </div>

      <hr class="form-divider" />

      <!-- Botones de navegación - SIEMPRE visibles -->
      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario anterior" style="width: 120px;" @click="anteriorSeccion">Anterior</button>
        <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguienteSeccion">Siguiente</button>
      </div>

      <hr class="form-divider" />
    </section>

    <!-- Sección 4: Información de Contacto de Emergencia -->
    <section class="seccion-formulario" v-show="indiceActual === 3">
      <h3>Contacto de Emergencia</h3>

      <div class="fila-texto">
        <input v-model="form.contactoEmergencia.nombre" type="text" placeholder="Nombre del contacto de emergencia"
          required :readonly="modo === 'ver'" @input="(event) => manejarNombreEmergencia('nombre', event)" />
        <input v-model="form.contactoEmergencia.parentesco" type="text" placeholder="Parentesco" required
          :readonly="modo === 'ver'" @input="(event) => manejarNombreEmergencia('parentesco', event)" />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input v-model="form.contactoEmergencia.telefono" type="text" placeholder="Teléfono de emergencia" required
          :readonly="modo === 'ver'" @input="manejarTelefonoEmergencia" />
        <input v-model="form.contactoEmergencia.correo" type="email" placeholder="Correo de emergencia"
          :readonly="modo === 'ver'" @input="manejarCorreoEmergencia" />
      </div>

      <hr class="form-divider" />

      <!-- Botones de navegación - SIEMPRE visibles -->
      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario anterior" style="width: 120px;" @click="anteriorSeccion">Anterior</button>
        <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguienteSeccion">Siguiente</button>
      </div>

      <hr class="form-divider" />
    </section>

    <!-- Sección 5: Documentos y Referencias -->
    <section class="seccion-formulario" v-show="indiceActual === 4">
      <h3>Documentos y Referencias</h3>

      <div class="fila-texto">
        <div class="file-wrapper">
          <label class="file-label">
            <input @change="manejarArchivo('hojaVida', $event)" type="file" accept=".pdf,.doc,.docx"
              :disabled="modo === 'ver'" class="file-input" />
            <span class="file-button">Hoja de Vida</span>
          </label>
        </div>

        <div class="file-wrapper">
          <label class="file-label">
            <input @change="manejarArchivo('certificaciones', $event)" type="file" accept=".pdf,.doc,.docx"
              :disabled="modo === 'ver'" class="file-input" />
            <span class="file-button">Certificaciones</span>
          </label>
        </div>
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input v-model="form.referencias.nombre1" type="text" placeholder="Nombre de referencia 1"
          :readonly="modo === 'ver'" @input="(event) => manejarNombreReferencia('nombre1', event)" />
        <input v-model="form.referencias.telefono1" type="text" placeholder="Teléfono de referencia 1"
          :readonly="modo === 'ver'" @input="(event) => manejarTelefonoReferencia('telefono1', event)" />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <input v-model="form.referencias.nombre2" type="text" placeholder="Nombre de referencia 2"
          :readonly="modo === 'ver'" @input="(event) => manejarNombreReferencia('nombre2', event)" />
        <input v-model="form.referencias.telefono2" type="text" placeholder="Teléfono de referencia 2"
          :readonly="modo === 'ver'" @input="(event) => manejarTelefonoReferencia('telefono2', event)" />
      </div>

      <hr class="form-divider" />

      <div class="fila-texto">
        <textarea v-model="form.observaciones" placeholder="Observaciones adicionales..." rows="4"
          :readonly="modo === 'ver'" @input="(event) => manejarTextoCampo('observaciones', event)"></textarea>
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
import catalogosService from "@/services/catalogosService";
import Swal from "sweetalert2";
function notificar(icon, title, text) {
  Swal.fire({ icon, title, text });
}

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

// Estado para catálogos
const cargandoCatalogos = ref(false);
const tiposDocumento = ref([]);
const sexos = ref([]);

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
  deportes: "", nivelEntrenamiento: "",
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

const LOCALE_COL = 'es-CO';
const NAME_REGEX = /^[A-ZÁÉÍÓÚÜÑ ]+$/;
const EMAIL_REGEX = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i;
const MIN_DOCUMENTO = 6;
const MAX_DOCUMENTO = 10;
const MIN_TELEFONO = 10;
const MAX_TELEFONO = 10;
const MAX_TEXTO = 500;

function aMayusculas(valor = '') {
  return valor ? valor.toLocaleUpperCase(LOCALE_COL) : '';
}

function sanitizarNombre(valor = '', obligatorio = true) {
  const mayus = aMayusculas(valor || '');
  const limpio = mayus.replace(/[^A-ZÁÉÍÓÚÜÑ\s]/g, '').replace(/\s{2,}/g, ' ').trim();
  return obligatorio ? limpio : limpio || '';
}

function sanitizarDocumento(valor = '') {
  return (valor || '').toString().replace(/\D/g, '').slice(0, MAX_DOCUMENTO);
}

function sanitizarTelefono(valor = '') {
  return (valor || '').toString().replace(/\D/g, '').slice(0, MAX_TELEFONO);
}

function sanitizarDireccion(valor = '') {
  const mayus = aMayusculas(valor || '');
  return mayus.replace(/[^A-Z0-9ÁÉÍÓÚÜÑ#\-\.\s]/g, '').replace(/\s{2,}/g, ' ').trim();
}

function sanitizarTexto(valor = '', maxLength = MAX_TEXTO) {
  const mayus = aMayusculas(valor || '');
  return mayus.replace(/\s{2,}/g, ' ').trim().slice(0, maxLength);
}

function manejarNombreCampo(campo, event, obligatorio = true) {
  const valor = event?.target?.value ?? form.value[campo];
  form.value[campo] = sanitizarNombre(valor, obligatorio);
}

function manejarNombreReferencia(campo, event) {
  const valor = event?.target?.value ?? form.value.referencias[campo];
  form.value.referencias[campo] = sanitizarNombre(valor, false);
}

function manejarNombreEmergencia(campo, event, obligatorio = true) {
  const valor = event?.target?.value ?? form.value.contactoEmergencia[campo];
  form.value.contactoEmergencia[campo] = sanitizarNombre(valor, obligatorio);
}

function manejarDocumento(event) {
  const valor = event?.target?.value ?? form.value.numeroDocumento;
  form.value.numeroDocumento = sanitizarDocumento(valor);
}

function manejarTelefonoCampo(campo, event) {
  const valor = event?.target?.value ?? form.value[campo];
  form.value[campo] = sanitizarTelefono(valor);
}

function manejarTelefonoReferencia(campo, event) {
  const valor = event?.target?.value ?? form.value.referencias[campo];
  form.value.referencias[campo] = sanitizarTelefono(valor);
}

function manejarTelefonoEmergencia(event) {
  const valor = event?.target?.value ?? form.value.contactoEmergencia.telefono;
  form.value.contactoEmergencia.telefono = sanitizarTelefono(valor);
}

function manejarDireccionCampo(campo, event) {
  const valor = event?.target?.value ?? form.value[campo];
  form.value[campo] = sanitizarDireccion(valor);
}

function manejarTextoCampo(campo, event, maxLength = MAX_TEXTO) {
  const valor = event?.target?.value ?? form.value[campo];
  form.value[campo] = sanitizarTexto(valor, maxLength);
}

function manejarCorreo(event) {
  const valor = event?.target?.value ?? form.value.correo;
  form.value.correo = valor ? valor.trim().toLowerCase() : '';
}

function manejarCorreoEmergencia(event) {
  const valor = event?.target?.value ?? form.value.contactoEmergencia.correo;
  form.value.contactoEmergencia.correo = valor ? valor.trim().toLowerCase() : '';
}

function normalizarFormulario() {
  manejarNombreCampo('nombre1');
  manejarNombreCampo('nombre2', null, false);
  manejarNombreCampo('apellido1');
  manejarNombreCampo('apellido2', null, false);
  manejarDocumento(null);
  manejarTelefonoCampo('telefono', null);
  manejarDireccionCampo('direccion', null);
  manejarTextoCampo('ciudad', null);
  manejarTextoCampo('profesion', null);
  manejarTextoCampo('especialidad', null);
  manejarTextoCampo('institucion', null);
  manejarTextoCampo('certificaciones', null);
  manejarTextoCampo('biografia', null);
  manejarTextoCampo('nivelEntrenamiento', null);
  manejarTextoCampo('clubesAnteriores', null);
  manejarTextoCampo('logrosEntrenador', null);
  manejarTextoCampo('horariosDisponibles', null);
  manejarTextoCampo('observaciones', null);
  manejarNombreEmergencia('nombre', null);
  manejarNombreEmergencia('parentesco', null);
  manejarTelefonoEmergencia(null);
  manejarCorreoEmergencia(null);
  manejarNombreReferencia('nombre1', null);
  manejarNombreReferencia('nombre2', null);
  manejarTelefonoReferencia('telefono1', null);
  manejarTelefonoReferencia('telefono2', null);
  manejarCorreo(null);
}

function validarFormulario() {
  if (!form.value.nombre1 || !NAME_REGEX.test(form.value.nombre1)) {
    notificar('warning', 'Dato inválido', 'El primer nombre solo debe contener letras y espacios');
    return false;
  }

  if (form.value.nombre2 && !NAME_REGEX.test(form.value.nombre2)) {
    notificar('warning', 'Dato inválido', 'El segundo nombre solo debe contener letras y espacios');
    return false;
  }

  if (!form.value.apellido1 || !NAME_REGEX.test(form.value.apellido1)) {
    notificar('warning', 'Dato inválido', 'El primer apellido solo debe contener letras y espacios');
    return false;
  }

  if (form.value.apellido2 && !NAME_REGEX.test(form.value.apellido2)) {
    notificar('warning', 'Dato inválido', 'El segundo apellido solo debe contener letras y espacios');
    return false;
  }

  if (!form.value.numeroDocumento || form.value.numeroDocumento.length < MIN_DOCUMENTO || form.value.numeroDocumento.length > MAX_DOCUMENTO) {
    notificar('warning', 'Documento inválido', `El documento debe tener entre ${MIN_DOCUMENTO} y ${MAX_DOCUMENTO} dígitos`);
    return false;
  }

  if (!/^\d+$/.test(form.value.numeroDocumento)) {
    notificar('warning', 'Documento inválido', 'El documento solo debe contener dígitos');
    return false;
  }

  if (!form.value.telefono || form.value.telefono.length !== MIN_TELEFONO) {
    notificar('warning', 'Teléfono inválido', `El teléfono debe tener exactamente ${MIN_TELEFONO} dígitos`);
    return false;
  }

  if (!/^\d{10}$/.test(form.value.telefono)) {
    notificar('warning', 'Teléfono inválido', 'El teléfono solo debe contener 10 dígitos');
    return false;
  }

  if (!EMAIL_REGEX.test(form.value.correo)) {
    notificar('warning', 'Correo inválido', 'Ingrese un correo electrónico válido');
    return false;
  }

  const telefonoEmergencia = form.value.contactoEmergencia.telefono;
  if (!telefonoEmergencia || telefonoEmergencia.length !== MIN_TELEFONO || !/^\d{10}$/.test(telefonoEmergencia)) {
    notificar('warning', 'Teléfono de emergencia inválido', 'Debe contener exactamente 10 dígitos');
    return false;
  }

  if (form.value.contactoEmergencia.correo && !EMAIL_REGEX.test(form.value.contactoEmergencia.correo)) {
    notificar('warning', 'Correo de emergencia inválido', 'Ingrese un correo válido para el contacto de emergencia');
    return false;
  }

  const telefono1 = form.value.referencias.telefono1;
  if (telefono1 && !/^\d{10}$/.test(telefono1)) {
    notificar('warning', 'Teléfono de referencia inválido', 'El teléfono de referencia 1 debe contener exactamente 10 dígitos');
    return false;
  }

  const telefono2 = form.value.referencias.telefono2;
  if (telefono2 && !/^\d{10}$/.test(telefono2)) {
    notificar('warning', 'Teléfono de referencia inválido', 'El teléfono de referencia 2 debe contener exactamente 10 dígitos');
    return false;
  }

  return true;
}

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

// Función para cargar catálogos desde la base de datos
async function cargarCatalogos() {
  cargandoCatalogos.value = true;
  
  try {
    console.log('🔄 Cargando catálogos para formulario de entrenador...');
    
    // Usar el servicio de catálogos que ya está configurado
    const catalogos = await catalogosService.cargarCatalogosFormulario();
    
    tiposDocumento.value = catalogos.tiposDocumento || [];
    sexos.value = catalogos.sexos || [];
    
    console.log('✅ Tipos de documento cargados:', tiposDocumento.value.length);
    console.log('✅ Sexos cargados:', sexos.value.length);
    
    console.log('✅ Catálogos cargados exitosamente');
  } catch (error) {
    console.error('❌ Error cargando catálogos:', error);
    
    // Datos de fallback
    tiposDocumento.value = [
      { id: 1, nombre: "Cédula de Ciudadanía" },
      { id: 2, nombre: "Tarjeta de Identidad" },
      { id: 3, nombre: "Cédula de Extranjería" },
      { id: 4, nombre: "Pasaporte" }
    ];
    
    sexos.value = [
      { id: 1, valor: "masculino", nombre: "Masculino" },
      { id: 2, valor: "femenino", nombre: "Femenino" },
      { id: 3, valor: "otro", nombre: "Otro" }
    ];
  } finally {
    cargandoCatalogos.value = false;
  }
}

// Manejo del formulario
function manejarSubmit() {
  normalizarFormulario();

  // Validar contraseñas
  if (form.value.contrasena !== form.value.confirmarContrasena) {
    notificar('warning', 'Validación', 'Las contraseñas no coinciden');
    return;
  }

  // Validar campos requeridos
  if (!form.value.nombre1 || !form.value.apellido1 || !form.value.tipoDocumento ||
    !form.value.numeroDocumento || !form.value.correo || !form.value.telefono ||
    !form.value.ciudad || !form.value.direccion || !form.value.contrasena) {
    notificar('warning', 'Campos incompletos', 'Por favor completa todos los campos obligatorios.');
    return;
  }

  if (!validarFormulario()) {
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
onMounted(async () => {
  // Cargar catálogos desde la base de datos
  await cargarCatalogos();

  // Cargar datos del formulario si se proporcionan
  if (props.datos && Object.keys(props.datos).length > 0) {
    form.value = { ...form.value, ...props.datos };
    normalizarFormulario();
  }
});

// Observar cambios en los datos
watch(() => props.datos, (nuevosDatos) => {
  if (nuevosDatos && Object.keys(nuevosDatos).length > 0) {
    form.value = { ...form.value, ...nuevosDatos };
    normalizarFormulario();
  }
}, { deep: true });
</script>
