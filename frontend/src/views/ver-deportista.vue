<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import Pie from '../components/ui/pie.vue';
import FormularioDeportista from '../components/formularios/formulario-deportista.vue';
import TarjetaPerfil from '../components/ui/tarjeta-perfil.vue';
import TarjetaAcudientesAcudidos from '../components/deportistas/tarjeta-acudientes-acudidos.vue';

// Datos simulados del usuario (en un caso real vendrían de una API)
const datosUsuario = {
  nombre1: "María",
  nombre2: "Fernanda",
  apellido1: "Rodríguez",
  apellido2: "Martínez",
  tipoDocumento: "Tarjeta de identidad",
  numeroDocumento: "98765432",
  fechaNacimiento: "2000-08-22",
  genero: "Femenino",
  correo: "maria.rodriguez@email.com",
  telefono: "3005551234",
  ciudad: "San Jose",
  direccion: "Carrera 8 #12-34",
  eps: "PONAL",
  grupoSanguineo: "O+",
  recomendacionMedica: "si",
  descripcionRecomendacion: "Evitar ejercicios de alto impacto por lesión en rodilla",
  institucion: "SANTANDER",
  practicaOtroDeporte: "no",
  deporteCual: "",
  participaEscuela: "si",
  escuelaCual: "Escuela de Voleibol San José",
  acudienteNombre1: "Ana",
  acudienteNombre2: "Sofía",
  acudienteApellido1: "Rodríguez",
  acudienteApellido2: "Gómez",
  parentesco: "Madre",
  acudienteFechaNac: "1975-12-10",
  acudienteTipoDoc: "Cédula",
  acudienteNumeroDoc: "54321678",
  acudienteCorreo: "ana.rodriguez@email.com",
  acudienteTelefono: "3004445678"
};
</script>

<template>
  <main>
    <Encabezado rol="Deportista"/>
    <div class="contenido-principal-tarjetas">
      <div class="contenedor-tarjetas">
        <TarjetaPerfil rol="Deportista" />
        <TarjetaAcudientesAcudidos rol="Deportista" />
      </div>
      <FormularioDeportista
        :modo="'ver'"
        :datos="datosUsuario"
      />
    </div>
    <Pie />
  </main>
</template>
