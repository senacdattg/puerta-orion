<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import Pie from '../components/layout/pie.vue';
import FormularioDeportista from '../components/formularios/formulario-deportista.vue';
import TarjetaPerfil from '../components/ui/tarjeta-perfil.vue';
import TarjetaAcudientesAcudidos from '../components/deportistas/tarjeta-acudientes-acudidos.vue';
import Swal from 'sweetalert2';

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
async function manejarActualizacion(datos) {
  console.log("Datos a actualizar:", datos);
  // Aquí iría la lógica para enviar a la API
  await Swal.fire({
    icon: 'success',
    title: 'Datos actualizados',
    text: 'Se guardaron correctamente los cambios del deportista.',
    timer: 1500,
    showConfirmButton: false
  });
}

// Función para manejar la cancelación
async function manejarCancelacion() {
  const result = await Swal.fire({
    icon: 'question',
    title: '¿Cancelar la actualización?',
    text: 'Los cambios que no hayas guardado se perderán.',
    showCancelButton: true,
    confirmButtonText: 'Sí, cancelar',
    cancelButtonText: 'Seguir editando'
  });
  if (result.isConfirmed) {
    console.log("Actualización cancelada");
  }
}
</script>

<template>
  <main>
    <Encabezado rol="Deportista"/>
    <div class="contenido-principal-tarjetas">
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

