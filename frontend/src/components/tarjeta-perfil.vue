<template>
  <div class="tarjeta-perfil">
    <div class="imagen-usuario">
      <img src="@/assets/imgs/perfil.png" alt="usuario" />
    </div>
    <div class="contenido-perfil">
      <h2>{{ rol }}</h2>

      <!-- Botón dinámico (solo aparece si mostrarBoton es true) -->
      <button 
        v-if="mostrarBoton" 
        class="boton-perfil" 
        @click="accionBoton"
      >
        {{ textoBoton }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from "vue";

// Props para reutilizar el componente
const props = defineProps({
  rol: {
    type: String,
    required: true
  },
  textoBoton: {
    type: String,
    default: "Roles"
  },
  mostrarBoton: {
    type: Boolean,
    default: true   // Por defecto sí se muestra
  }
});

// Emitir eventos hacia el padre
const emit = defineEmits(["clickBoton"]);

function accionBoton() {
  emit("clickBoton", props.rol);
}
</script>
