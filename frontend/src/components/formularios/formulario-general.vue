<template>
  <form class="formulario-datos" @submit.prevent="manejarSubmit">
  <section class="seccion-formulario" v-show="indiceActual === 0">
    <h3>{{  obtenerTitulo() }}</h3>
    
    <!-- Nombres -->
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
  
    <!-- Fecha de nacimiento y género -->
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
        <option value="" disabled hidden>¿Cuál es su género?</option>
        <option value="masculino">Masculino</option>
        <option value="femenino">Femenino</option>
      </select>
    </div>

    <hr class="form-divider" />
    <!-- Documento -->
    <div class="fila-texto">
      <select 
      v-model="form.tipoDocumento"
      required
      :disabled="modo === 'ver'"
      >
        <option value="" disabled hidden>¿Cuál es su tipo de documento?</option>
        <option value="cc">Cédula de ciudadanía</option>
        <option value="ti">Tarjeta de identidad</option>
        <option value="ce">Cédula de extranjería</option>
        <option value="pasaporte">Pasaporte</option>
      </select>
      <input 
      type="text" 
      v-model="form.numeroDocumento" 
      placeholder="Número de documento" 
      required 
      :readonly="modo === 'ver'"
      />
    </div>
    
    <hr class="form-divider" />
  
    <!-- Correo y teléfono -->
    <div class="fila-texto">
      <input 
      type="email" 
      v-model="form.correo" 
      placeholder="¿Cuál es su correo electrónico?" 
      :readonly="modo === 'ver'"
      />
      <input 
      type="text" 
      v-model="form.telefono" 
      placeholder="¿Cuál es su número telefónico?" 
      required 
      :readonly="modo === 'ver'"
      />
    </div>
  
    <!-- Contraseña -->
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
    <hr class="form-divider" />

    <!-- Botón -->
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
  contrasena: "", confirmarContrasena: "",
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
    Object.keys(nuevosDatos).forEach(key => {
      if (form.value.hasOwnProperty(key)) {
        form.value[key] = nuevosDatos[key];
      }
    });
  }
}, { deep: true });

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
