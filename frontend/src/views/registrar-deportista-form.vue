<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import Pie from '../components/layout/pie.vue';
import FormularioDeportista from '../components/formularios/formulario-deportista.vue';

// Función para manejar el registro de deportista
function manejarRegistroDeportista(datos) {
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
    <Encabezado :sinMenu="true"/>
    <div class="contenido-principal-tarjetas">
      <FormularioDeportista
        :modo="'registrar'"
        @submit="manejarRegistroDeportista"
        @cancel="manejarCancelacion"
      />
    </div>
    <Pie />
  </main>
</template>

<style scoped>
.contenido-principal-tarjetas {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
