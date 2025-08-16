<script setup>
import Encabezado from '../components/encabezado.vue';
import Pie from '../components/pie.vue';
import FormularioActualizarDeportista from '../components/formulario-actualizar-deportista.vue';
</script>

<template>
  <main>
    <Encabezado rol="Deportista"/>
    <FormularioActualizarDeportista />
    <RouterView />
    <Pie />
  </main>
</template>
