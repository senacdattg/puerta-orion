<template>
  <div class="tarjeta-deportista" @click="verDetalle">
    <div class="imagen-deportista">
      <img
        :src="avatarDefault"
        :alt="`Perfil de ${deportista.nombre}`"
        @error="imagenPorDefecto"
      />
    </div>
    <div class="contenido-deportista">
      <h3 class="nombre-deportista">{{ deportista.nombre }}</h3>
      <p class="categoria-deportista">{{ deportista.categoria }}</p>
      <button
        v-if="deportista.id_usuario"
        class="estado-deportista"
        :class="deportista.estado"
        @click.stop="cambiarEstado"
        :disabled="cambiandoEstado"
        :title="deportista.estado === 'activo' ? 'Desactivar deportista' : 'Activar deportista'"
      >
        {{ deportista.estado === 'activo' ? 'ACTIVO' : 'INACTIVO' }}
      </button>
      <p v-else class="estado-deportista" :class="deportista.estado">
        {{ deportista.estado === 'activo' ? 'ACTIVO' : 'INACTIVO' }}
      </p>
    </div>
    <!-- Botones de acción deshabilitados - solo vista -->
    <div class="acciones-deportista" style="display: none;">
      <!-- Los botones están ocultos para permitir solo visualización -->
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import avatarDefault from '@/assets/imgs/perfil.png';

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
const emit = defineEmits(['editar', 'eliminar', 'ver', 'cambiar-estado']);

// Estado para controlar el cambio de estado
const cambiandoEstado = ref(false);

// Funciones simples y específicas (KISS)
function verDetalle() {
  emit('ver', props.deportista);
}

function cambiarEstado() {
  // Evitar múltiples clics mientras se procesa
  if (cambiandoEstado.value) return;

  emit('cambiar-estado', props.deportista);
}

function imagenPorDefecto(event) {
  event.target.src = avatarDefault;
}

// Exponer cambiandoEstado para que el padre pueda controlarlo
defineExpose({
  cambiandoEstado
});
</script>
