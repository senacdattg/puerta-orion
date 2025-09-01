<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import Pie from '../components/layout/pie.vue';
import FormularioGeneral from '../components/formularios/formulario-general.vue';
import TarjetaPerfil from '../components/ui/tarjeta-perfil.vue';
import TarjetaAcudientesAcudidos from '../components/deportistas/tarjeta-acudientes-acudidos.vue';

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
    <Encabezado rol="Aspirante"/>
    <div class="contenido-principal-tarjetas">
      <div class="contenedor-tarjetas">
        <TarjetaPerfil rol="Aspirante" />
        <TarjetaAcudientesAcudidos rol="Aspirante" />
      </div>
      <FormularioGeneral
        :modo="'ver'"
        :datos="datosUsuario"
      />
    </div>
    <Pie />
  </main>
</template>
