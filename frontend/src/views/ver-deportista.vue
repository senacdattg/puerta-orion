<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import Encabezado from '../components/layout/encabezado.vue';
import Pie from '../components/layout/pie.vue';
import FormularioDeportista from '../components/formularios/formulario-deportista.vue';
import TarjetaPerfil from '../components/ui/tarjeta-perfil.vue';
import TarjetaAcudientesAcudidos from '../components/deportistas/tarjeta-acudientes-acudidos.vue';

const route = useRoute();
const deportistaId = route.params.id;
const datosUsuario = ref({});
const cargando = ref(true);

// Datos simulados de deportistas (en un caso real vendrían de una API)
const deportistas = {
  1: {
    nombre1: "Carlos",
    nombre2: "Alberto",
  apellido1: "Rodríguez",
  apellido2: "Martínez",
    tipoDocumento: "Cédula",
    numeroDocumento: "12345678",
    fechaNacimiento: "2000-05-15",
    genero: "Masculino",
    correo: "carlos.rodriguez@email.com",
    telefono: "3001234567",
    ciudad: "Retorno",
    direccion: "Calle 5 #10-20",
    eps: "Nueva EPS",
    grupoSanguineo: "A+",
    recomendacionMedica: "no",
    descripcionRecomendacion: "",
    institucion: "SENA",
    practicaOtroDeporte: "si",
    deporteCual: "Fútbol",
    participaEscuela: "no",
    escuelaCual: "",
    acudienteNombre1: "María",
    acudienteNombre2: "Elena",
    acudienteApellido1: "Rodríguez",
    acudienteApellido2: "Gómez",
    parentesco: "Madre",
    acudienteFechaNac: "1975-03-20",
    acudienteTipoDoc: "Cédula",
    acudienteNumeroDoc: "87654321",
    acudienteCorreo: "maria.rodriguez@email.com",
    acudienteTelefono: "3009876543"
  },
  2: {
    nombre1: "Ana",
    nombre2: "María",
    apellido1: "Martínez",
    apellido2: "López",
  tipoDocumento: "Tarjeta de identidad",
  numeroDocumento: "98765432",
    fechaNacimiento: "2002-08-22",
  genero: "Femenino",
    correo: "ana.martinez@email.com",
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
    acudienteApellido1: "Martínez",
  acudienteApellido2: "Gómez",
  parentesco: "Madre",
  acudienteFechaNac: "1975-12-10",
  acudienteTipoDoc: "Cédula",
  acudienteNumeroDoc: "54321678",
    acudienteCorreo: "ana.martinez@email.com",
  acudienteTelefono: "3004445678"
  },
  3: {
    nombre1: "Luis",
    nombre2: "Fernando",
    apellido1: "García",
    apellido2: "Pérez",
    tipoDocumento: "Cédula",
    numeroDocumento: "11223344",
    fechaNacimiento: "1995-03-10",
    genero: "Masculino",
    correo: "luis.garcia@email.com",
    telefono: "3007778888",
    ciudad: "Retorno",
    direccion: "Carrera 3 #15-25",
    eps: "Nueva EPS",
    grupoSanguineo: "B+",
    recomendacionMedica: "no",
    descripcionRecomendacion: "",
    institucion: "SENA",
    practicaOtroDeporte: "si",
    deporteCual: "Básquetbol",
    participaEscuela: "no",
    escuelaCual: "",
    acudienteNombre1: "Carmen",
    acudienteNombre2: "Rosa",
    acudienteApellido1: "García",
    acudienteApellido2: "Hernández",
    parentesco: "Esposa",
    acudienteFechaNac: "1990-07-15",
    acudienteTipoDoc: "Cédula",
    acudienteNumeroDoc: "99887766",
    acudienteCorreo: "carmen.garcia@email.com",
    acudienteTelefono: "3009998888"
  },
  4: {
    nombre1: "María",
    nombre2: "Fernanda",
    apellido1: "López",
    apellido2: "Silva",
    tipoDocumento: "Tarjeta de identidad",
    numeroDocumento: "55667788",
    fechaNacimiento: "2001-11-30",
    genero: "Femenino",
    correo: "maria.lopez@email.com",
    telefono: "3006665555",
    ciudad: "San Jose",
    direccion: "Calle 7 #20-30",
    eps: "PONAL",
    grupoSanguineo: "AB+",
    recomendacionMedica: "si",
    descripcionRecomendacion: "Suspensión temporal por lesión en hombro",
    institucion: "SANTANDER",
    practicaOtroDeporte: "no",
    deporteCual: "",
    participaEscuela: "si",
    escuelaCual: "Escuela de Voleibol San José",
    acudienteNombre1: "Roberto",
    acudienteNombre2: "Carlos",
    acudienteApellido1: "López",
    acudienteApellido2: "Mendoza",
    parentesco: "Padre",
    acudienteFechaNac: "1970-04-12",
    acudienteTipoDoc: "Cédula",
    acudienteNumeroDoc: "44556677",
    acudienteCorreo: "roberto.lopez@email.com",
    acudienteTelefono: "3005556666"
  },
  5: {
    nombre1: "Juan",
    nombre2: "David",
    apellido1: "Pérez",
    apellido2: "Torres",
    tipoDocumento: "Tarjeta de identidad",
    numeroDocumento: "33445566",
    fechaNacimiento: "2008-06-18",
    genero: "Masculino",
    correo: "juan.perez@email.com",
    telefono: "3004443333",
    ciudad: "Retorno",
    direccion: "Carrera 1 #5-10",
    eps: "Nueva EPS",
    grupoSanguineo: "O-",
    recomendacionMedica: "no",
    descripcionRecomendacion: "",
    institucion: "SENA",
    practicaOtroDeporte: "si",
    deporteCual: "Fútbol",
    participaEscuela: "no",
    escuelaCual: "",
    acudienteNombre1: "Patricia",
    acudienteNombre2: "Isabel",
    acudienteApellido1: "Pérez",
    acudienteApellido2: "Vega",
    parentesco: "Madre",
    acudienteFechaNac: "1980-09-25",
    acudienteTipoDoc: "Cédula",
    acudienteNumeroDoc: "22334455",
    acudienteCorreo: "patricia.perez@email.com",
    acudienteTelefono: "3003334444"
  },
  6: {
    nombre1: "Sofia",
    nombre2: "Alejandra",
    apellido1: "Torres",
    apellido2: "Ramírez",
    tipoDocumento: "Cédula",
    numeroDocumento: "77889900",
    fechaNacimiento: "1998-12-05",
    genero: "Femenino",
    correo: "sofia.torres@email.com",
    telefono: "3002221111",
    ciudad: "San Jose",
    direccion: "Calle 9 #25-35",
    eps: "PONAL",
    grupoSanguineo: "A-",
    recomendacionMedica: "no",
    descripcionRecomendacion: "",
    institucion: "SANTANDER",
    practicaOtroDeporte: "si",
    deporteCual: "Tenis",
    participaEscuela: "no",
    escuelaCual: "",
    acudienteNombre1: "Alejandro",
    acudienteNombre2: "Miguel",
    acudienteApellido1: "Torres",
    acudienteApellido2: "Castro",
    parentesco: "Padre",
    acudienteFechaNac: "1965-01-20",
    acudienteTipoDoc: "Cédula",
    acudienteNumeroDoc: "11223344",
    acudienteCorreo: "alejandro.torres@email.com",
    acudienteTelefono: "3001112222"
  }
};

onMounted(() => {
  // Simular carga de datos
  setTimeout(() => {
    if (deportistas[deportistaId]) {
      datosUsuario.value = deportistas[deportistaId];
    } else {
      // Si no encuentra el deportista, mostrar datos por defecto
      datosUsuario.value = {
        nombre1: "Deportista",
        nombre2: "",
        apellido1: "No encontrado",
        apellido2: "",
        tipoDocumento: "",
        numeroDocumento: "",
        fechaNacimiento: "",
        genero: "",
        correo: "",
        telefono: "",
        ciudad: "",
        direccion: "",
        eps: "",
        grupoSanguineo: "",
        recomendacionMedica: "",
        descripcionRecomendacion: "",
        institucion: "",
        practicaOtroDeporte: "",
        deporteCual: "",
        participaEscuela: "",
        escuelaCual: "",
        acudienteNombre1: "",
        acudienteNombre2: "",
        acudienteApellido1: "",
        acudienteApellido2: "",
        parentesco: "",
        acudienteFechaNac: "",
        acudienteTipoDoc: "",
        acudienteNumeroDoc: "",
        acudienteCorreo: "",
        acudienteTelefono: ""
      };
    }
    cargando.value = false;
  }, 500);
});
</script>

<template>
  <main>
    <Encabezado rol="Deportista"/>
    <div v-if="cargando" class="cargando">
      <p>Cargando perfil del deportista...</p>
    </div>
    <div v-else class="contenido-principal-tarjetas">
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

<style scoped>
.cargando {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 18px;
  color: #666;
}
</style>
