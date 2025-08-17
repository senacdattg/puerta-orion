<template>
  <div class="tarjeta-acudiente" v-if="esValido">
    <h2>{{ titulo }}</h2>

    <div id="lista-acudidos" class="lista-acudidos">
      <div
        v-for="(persona, index) in personas"
        :key="index"
        class="contenido-acudiente"
      >
        <div class="imagen-acudiente">
          <img src="@/assets/imgs/user.png" alt="user" />
        </div>
        <input type="text" :value="persona.nombre" readonly />
        <button v-if="mostrarVer" class="boton-acudiente" @click="verPersona(persona)">
          Ver
        </button>
      </div>
    </div>

    <button v-if="mostrarAgregar" class="boton-acudiente" @click="agregar" style="margin-bottom: 10px;">
      Agregar
    </button>
  </div>
</template>

<script setup>
import { defineProps, ref, computed } from "vue";

const props = defineProps({
  rol: {
    type: String,
    required: true,
  },
  mostrarAgregar: {
    type: Boolean,
    default: true,
  },
  mostrarVer: {
    type: Boolean,
    default: true,
  },
});

// Verificar que el rol sea válido
const esValido = computed(() => props.rol === "Acudiente" || props.rol === "Deportista");

// Título dinámico
const titulo = computed(() =>
  props.rol === "Deportista" ? "Acudientes" : "Acudidos"
);

// Personas simuladas
const personas = ref(
  props.rol === "Deportista"
    ? [
        { nombre: "Pedro Ramírez (Acudiente)" },
        { nombre: "Laura Torres (Acudiente)" },
      ]
    : [
        { nombre: "Kevin Santiago Prada Castellanos" },
        { nombre: "María Fernanda Ruiz Pérez" },
      ]
);

// Métodos
function verPersona(persona) {
  alert(`Mostrando información de: ${persona.nombre}`);
}

function agregar() {
  alert("Agregar nuevo registro");
}
</script>
