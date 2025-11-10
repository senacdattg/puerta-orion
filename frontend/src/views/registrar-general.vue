<script setup>
import FormularioGeneral from '../components/formularios/formulario-general.vue';
import Swal from 'sweetalert2';

// Función para manejar el registro
async function manejarRegistro(datos) {
  console.log("Datos del nuevo deportista:", datos);
  // Aquí iría la lógica para enviar a la API
  await Swal.fire({
    icon: 'success',
    title: 'Registro exitoso',
    text: 'El deportista se registró correctamente.',
    timer: 1500,
    showConfirmButton: false
  });
}

// Función para manejar la cancelación
async function manejarCancelacion() {
  const resultado = await Swal.fire({
    icon: 'question',
    title: '¿Cancelar registro?',
    text: 'Los datos ingresados se perderán.',
    showCancelButton: true,
    confirmButtonText: 'Sí, cancelar',
    cancelButtonText: 'Continuar llenando'
  });
  if (resultado.isConfirmed) {
    console.log("Registro cancelado");
  }
}
</script>

<template>
  <main>
    <div class="contenido-principal-tarjetas">
      <FormularioGeneral
        :modo="'registrar'"
        @submit="manejarRegistro"
        @cancel="manejarCancelacion"
      />
    </div>
  </main>
</template>
