<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import Pie from '../components/layout/pie.vue';
import FormularioGeneral from '../components/formularios/formulario-general.vue';
import TarjetaPerfil from '../components/ui/tarjeta-perfil.vue';
import tarjetaAcudientesAcudidos from '../components/deportistas/tarjeta-acudientes-acudidos.vue';


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

// Función para manejar la actualización
function manejarActualizacion(datos) {
  console.log("Datos a actualizar:", datos);
  // Aquí iría la lógica para enviar a la API
  alert("Datos actualizados exitosamente!");
}

// Función para manejar la cancelación
function manejarCancelacion() {
  if (confirm("¿Está seguro de que desea cancelar la actualización?")) {
    // Aquí podrías redirigir o limpiar el formulario
    console.log("Actualización cancelada");
  }
}
</script>

<template>
  <main>
    <Encabezado rol="Admin"/>
    <div class="contenido-principal-tarjetas">
      <div class="contenedor-tarjetas">
        <TarjetaPerfil rol="Admin"/>
        <tarjetaAcudientesAcudidos rol="" :mostrarVer="false" :mostrarAgregar="false" />
      </div>
      <FormularioGeneral
        :modo="'actualizar'"
        :datos="datosUsuario"
      />
    </div>
    <Pie />
  </main>
</template>
