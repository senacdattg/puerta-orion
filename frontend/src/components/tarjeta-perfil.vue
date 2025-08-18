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
import { useRouter } from "vue-router";

const router = useRouter()

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

function accionBoton() {
  router.push("/ver-roles");
}
</script>
