<script setup>
import Encabezado from '../components/encabezado.vue';
import Pie from '../components/pie.vue';
import FormularioDeportista from '../components/formulario-deportista.vue';
import TarjetaPerfil from '../components/tarjeta-perfil.vue';
import TarjetaAcudientesAcudidos from '@/components/tarjeta-acudientes-acudidos.vue';

// Datos simulados del usuario (en un caso real vendrían de una API)
const datosUsuario = {
  nombre1: "Juan",
  nombre2: "Carlos",
  apellido1: "Pérez",
  apellido2: "García",
  tipoDocumento: "Cédula",
  numeroDocumento: "12345678",
  fechaNacimiento: "1995-05-15",
  genero: "Masculino",
  correo: "juan.perez@email.com",
  telefono: "3001234567",
  ciudad: "Retorno",
  direccion: "Calle 15 #23-45",
  eps: "Nueva EPS",
  grupoSanguineo: "A+",
  recomendacionMedica: "no",
  descripcionRecomendacion: "",
  institucion: "SENA",
  practicaOtroDeporte: "si",
  deporteCual: "Fútbol y baloncesto",
  participaEscuela: "no",
  escuelaCual: "",
  acudienteNombre1: "Pedro",
  acudienteNombre2: "",
  acudienteApellido1: "Pérez",
  acudienteApellido2: "López",
  parentesco: "Padre",
  acudienteFechaNac: "1970-03-20",
  acudienteTipoDoc: "Cédula",
  acudienteNumeroDoc: "87654321",
  acudienteCorreo: "pedro.perez@email.com",
  acudienteTelefono: "3009876543"
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
    <Encabezado rol="Deportista"/>
    <div class="contenido-principal">
      <div class="contenedor-tarjetas">
        <TarjetaPerfil rol="Deportista" :mostrarBoton="false" />
        <TarjetaAcudientesAcudidos rol="Deportista" :mostrarVer="false" :mostrarAgregar="false" />
      </div>
      <FormularioDeportista 
        :modo="'actualizar'"
        :datos="datosUsuario"
        @submit="manejarActualizacion"
        @cancel="manejarCancelacion"
      />
    </div>
    <Pie />
  </main>
</template>

