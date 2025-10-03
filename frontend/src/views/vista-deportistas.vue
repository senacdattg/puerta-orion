<script setup>
// Sí, puedes cambiar el nombre directamente al archivo para cumplir con la convención de nombres de Vue.
// Por ejemplo, en vez de "deportistas.vue", usa "vista-deportistas.vue" o "lista-deportistas-vista.vue".
// Además, es recomendable definir el nombre del componente dentro del script para mayor claridad:
defineOptions({
  name: 'VistaDeportistas'
});
import Encabezado from '../components/layout/encabezado.vue';
import tituloClub from '@/components/ui/titulo-club.vue';
import ListaDeportistas from '../components/deportistas/lista-deportistas.vue';
import FormularioDeportista from '../components/formularios/formulario-deportista.vue';
import Pie from '../components/ui/pie.vue';
import { ref } from 'vue';

// Datos de ejemplo para demostrar la funcionalidad
const deportistas = ref([
  {
    id: 1,
    nombre: 'Carlos Alberto Rodríguez Martínez',
    categoria: 'juvenil',
    estado: 'activo',
    imagen: null,
    // Datos completos para el perfil
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
  {
    id: 2,
    nombre: 'Ana María Martínez López',
    categoria: 'infantil',
    estado: 'activo',
    imagen: null,
    // Datos completos para el perfil
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
  {
    id: 3,
    nombre: 'Luis Fernando García Pérez',
    categoria: 'adulto',
    estado: 'inactivo',
    imagen: null,
    // Datos completos para el perfil
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
  {
    id: 4,
    nombre: 'María Fernanda López Silva',
    categoria: 'juvenil',
    estado: 'suspendido',
    imagen: null,
    // Datos completos para el perfil
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
  {
    id: 5,
    nombre: 'Juan David Pérez Torres',
    categoria: 'infantil',
    estado: 'activo',
    imagen: null,
    // Datos completos para el perfil
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
  {
    id: 6,
    nombre: 'Sofia Alejandra Torres Ramírez',
    categoria: 'adulto',
    estado: 'activo',
    imagen: null,
    // Datos completos para el perfil
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
]);

// Estado para controlar el modal del formulario
const mostrarFormulario = ref(false);
const modoFormulario = ref('registrar');
const deportistaEditando = ref(null);

// Funciones para manejar eventos de deportistas
function editarDeportista(deportista) {
  console.log('Editar deportista:', deportista);

  // Configurar el modal para edición
  modoFormulario.value = 'actualizar';
  deportistaEditando.value = deportista;
  mostrarFormulario.value = true;
}

function eliminarDeportista(deportista) {
  console.log('Eliminar deportista:', deportista);

  const confirmacion = confirm(
    `¿Estás seguro de eliminar a ${deportista.nombre}?\n\nEsta acción no se puede deshacer.`
  );

  if (confirmacion) {
    const index = deportistas.value.findIndex(d => d.id === deportista.id);
    if (index !== -1) {
      deportistas.value.splice(index, 1);
      console.log('Deportista eliminado');
    }
  }
}

function agregarDeportista() {
  console.log('Abrir formulario para agregar deportista');

  // Configurar el modal para registro
  modoFormulario.value = 'registrar';
  deportistaEditando.value = null;
  mostrarFormulario.value = true;
}

// Funciones para manejar el formulario
function cerrarFormulario() {
  mostrarFormulario.value = false;
  deportistaEditando.value = null;
}

function manejarSubmitFormulario(datos) {
  if (modoFormulario.value === 'registrar') {
    // Agregar nuevo deportista
    const nuevoDeportista = {
      id: Date.now(), // ID temporal
      nombre: `${datos.nombre1} ${datos.apellido1}`,
      categoria: 'juvenil', // Categoría por defecto
      estado: 'activo',
      imagen: null,
      ...datos
    };
    deportistas.value.push(nuevoDeportista);
    console.log('Deportista agregado:', nuevoDeportista);
  } else if (modoFormulario.value === 'actualizar') {
    // Actualizar deportista existente
    const index = deportistas.value.findIndex(d => d.id === deportistaEditando.value.id);
    if (index !== -1) {
      deportistas.value[index] = {
        ...deportistas.value[index],
        nombre: `${datos.nombre1} ${datos.apellido1}`,
        ...datos
      };
      console.log('Deportista actualizado:', deportistas.value[index]);
    }
  }
  cerrarFormulario();
}

</script>

<style>
.modal-deportistas {
  border-radius: 10px;
  box-shadow: 0 rgba(0, 0, 0, 0.15);
  max-width: 750px;
  width: 800px;
  max-height: 100vh;
  overflow-y: auto;
  animation: modalEntrada 0.3s ease-out;
  position: relative;
}

.btn-cerrar-deportista {
  background: #e70000;
  border: none;
  color: #343a40;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transicion);
  position: absolute;
  top: 15px;
  right: 15px;
  z-index: 10;
}

.btn-cerrar-deportista:hover {
  background: #e70000;
  color: black;
  transform: scale(1.1);
}

.modal-overlay-deportistas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  padding: 0.5rem;
}
</style>
<template>
  <main class="vista-deportistas">
    <Encabezado rol="Admin" />
    <tituloClub></tituloClub>
    <ListaDeportistas :deportistas="deportistas" @editar="editarDeportista" @eliminar="eliminarDeportista"
      @agregar="agregarDeportista" />

    <!-- Modal para formulario de deportista -->
    <div v-if="mostrarFormulario" class="modal-overlay-deportistas">
      <div class="modal-deportistas" @click.stop>
        <button class="btn-cerrar-deportista" title="Cerrar" @click="cerrarFormulario">
          <i class="fas fa-times"></i>
        </button>
        <div class="modal-body">
          <FormularioDeportista :modo="modoFormulario" :datos="deportistaEditando" @submit="manejarSubmitFormulario"
            @cancel="cerrarFormulario" />
        </div>
      </div>
    </div>

    <Pie />
  </main>
</template>
