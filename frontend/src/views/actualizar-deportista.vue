<script setup>
import Encabezado from '../components/encabezado.vue';
import Pie from '../components/pie.vue';
import FormularioActualizarDeportista from '../components/formulario-actualizar-deportista.vue';
import TarjetaPerfil from '../components/tarjeta-perfil.vue';
import TarjetaAcudientesAcudidos from '@/components/tarjeta-acudientes-acudidos.vue';
</script>

<template>
  <main>
    <Encabezado rol="Deportista"/>
    <div class="contenido-principal">
      <div class="contenedor-tarjetas">
        <TarjetaPerfil rol="Deportista" :mostrarBoton="false" />
        <TarjetaAcudientesAcudidos rol="Deportista" :mostrarVer="false" :mostrarAgregar="false" />
      </div>
      <FormularioActualizarDeportista />
    </div>
    <Pie />
  </main>
</template>

