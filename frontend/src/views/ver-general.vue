<script setup>
import Encabezado from '../components/encabezado.vue';
import Pie from '../components/pie.vue';
import FormularioGeneral from '../components/formulario-general.vue';
import TarjetaPerfil from '../components/tarjeta-perfil.vue';
import TarjetaAcudientesAcudidos from '@/components/tarjeta-acudientes-acudidos.vue';

const datosUsuario = {
  nombre1: "Juan",
  nombre2: "Carlos",
  apellido1: "Pérez",
  apellido2: "García",
  fechaNacimiento: "1995-05-15",
  genero: "Masculino",
  tipoDocumento: "Cédula de ciudadanía",
  numeroDocumento: "1234567890",
  correo: "juan.perez@gmail.com",
  telefono: "3178901234",
  contrasena: "1234567890",
  confirmarContrasena: "1234567890",
};
</script>

<template>
  <main>
    <Encabezado rol="Admin"/>
    <div class="contenido-principal-tarjetas">
      <div class="contenedor-tarjetas">
        <TarjetaPerfil rol="Admin" />
        <TarjetaAcudientesAcudidos rol="" />
      </div>
      <FormularioGeneral 
        :modo="'ver'"
        :datos="datosUsuario"
      />
    </div>
    <Pie />
  </main>
</template>
