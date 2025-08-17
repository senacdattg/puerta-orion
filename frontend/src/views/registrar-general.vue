<script setup>
import Encabezado from '../components/encabezado.vue';
import Pie from '../components/pie.vue';
import FormularioGeneral from '../components/formulario-general.vue';

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
    <Encabezado rol="Administrador"/>
    <div class="contenido-principal">
      <FormularioGeneral 
        :modo="'registrar'"
        @submit="manejarRegistro"
        @cancel="manejarCancelacion"
      />
    </div>
    <Pie />
  </main>
</template>
