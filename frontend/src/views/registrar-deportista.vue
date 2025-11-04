<script setup>
import FormularioDeportista from '../components/formularios/formulario-deportista.vue';

// Función para manejar el registro
function manejarRegistro(datos) {
  console.log("Datos del nuevo deportista:", datos);
  // Aquí iría la lógica para enviar a la API
  alert("Deportista registrado exitosamente!");
}

// Función para manejar la cancelación
function manejarCancelacion() {
  if (confirm("¿Está seguro de que desea cancelar el registro?")) {
    // Aquí podrías redirigir o limpiar el formulario
    console.log("Registro cancelado");
  }
}
</script>

<template>
  <main>
    <div class="contenido-principal-tarjetas">
      <FormularioDeportista
        :modo="'registrar'"
        @submit="manejarRegistro"
        @cancel="manejarCancelacion"
      />
    </div>
  </main>
</template>
