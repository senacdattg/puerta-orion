<template>
  <div class="tarjeta-deportista" @click="verDetalle">
    <div class="imagen-deportista">
      <img
        :src="deportista.imagen || '/src/assets/imgs/perfil.png'"
        :alt="`Perfil de ${deportista.nombre}`"
        @error="imagenPorDefecto"
      />
    </div>
    <div class="contenido-deportista">
      <h3 class="nombre-deportista">{{ deportista.nombre }}</h3>
      <p class="categoria-deportista">{{ deportista.categoria }}</p>
      <p class="estado-deportista" :class="deportista.estado">
        {{ deportista.estado }}
      </p>
    </div>
    <div class="acciones-deportista">
      <button
        class="boton-accion editar"
        @click.stop="editarDeportista"
        title="Editar deportista"
      >
        ✏️
      </button>
      <button
        class="boton-accion eliminar"
        @click.stop="eliminarDeportista"
        title="Eliminar deportista"
      >
        🗑️
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

// Props siguiendo SRP - solo recibe datos del deportista
const props = defineProps({
  deportista: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      nombre: 'Sin nombre',
      categoria: 'Sin categoría',
      estado: 'activo',
      imagen: null
    })
  }
});

// Emits para comunicación con el componente padre
const emit = defineEmits(['editar', 'eliminar']);

// Funciones simples y específicas (KISS)
function verDetalle() {
  router.push(`/ver-deportista/${props.deportista.id}`);
}

function editarDeportista() {
  emit('editar', props.deportista);
}

function eliminarDeportista() {
  emit('eliminar', props.deportista);
}

function imagenPorDefecto(event) {
  event.target.src = '/src/assets/imgs/perfil.png';
}
</script>
