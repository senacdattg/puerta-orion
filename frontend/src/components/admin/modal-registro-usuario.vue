<template>
  <div v-if="mostrar" class="modal-overlay modal-registro-overlay" @click="cerrarModal">
    <div class="modal-content modal-registro" @click.stop>
      <!-- Header del Modal -->
      <div class="modal-header">
        <h2 class="modal-title">
          <i class="fas fa-user-plus"></i>
          Registro de Nuevo Usuario
        </h2>
        <button class="btn-cerrar" @click="cerrarModal">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- Formulario de Registro -->
      <div class="modal-body">
        <FormularioGeneral
          :modo="'registrar'"
          :mostrar-boton-login="false"
          texto-boton-registrar="Registrar"
          @submit="manejarRegistro"
          @cancel="cancelarRegistro"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import FormularioGeneral from '../formularios/formulario-general.vue';
import Swal from 'sweetalert2';
import { useModalScrollLock } from '@/composables/useModalScrollLock';

// Props
const props = defineProps({
  mostrar: {
    type: Boolean,
    default: false
  }
});

// Emits
const emit = defineEmits(['cerrar', 'usuario-registrado']);

// Bloquear scroll del body cuando el modal está abierto
useModalScrollLock(computed(() => props.mostrar));

function cerrarModal() {
  emit('cerrar');
}

async function cancelarRegistro() {
  const result = await Swal.fire({
    icon: 'question',
    title: '¿Cancelar registro?',
    text: 'Los datos ingresados se perderán.',
    showCancelButton: true,
    confirmButtonText: 'Sí, cancelar',
    cancelButtonText: 'Seguir registrando'
  });
  if (result.isConfirmed) {
    cerrarModal();
  }
}

async function manejarRegistro(datos) {
  const datosCompletos = {
    ...datos,
    rol: 'usuario',
    tipoUsuario: 'general'
  };

  // Emitir evento con los datos completos
  emit('usuario-registrado', datosCompletos);

  await Swal.fire({
    icon: 'success',
    title: 'Usuario registrado',
    text: 'El nuevo usuario fue registrado correctamente.',
    timer: 1500,
    showConfirmButton: false
  });

  // Cerrar modal y resetear
  cerrarModal();
}
</script>


