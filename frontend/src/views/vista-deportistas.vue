<script setup>
defineOptions({
  name: 'VistaDeportistas'
});
import Encabezado from '../components/layout/encabezado.vue';
import tituloClub from '@/components/ui/titulo-club.vue';
import ListaDeportistas from '../components/deportistas/lista-deportistas.vue';
import PerfilDeportistaVista from '../components/deportistas/perfil-deportista-vista.vue';
import FormularioDeportista from '../components/formularios/formulario-deportista.vue';
import Pie from '../components/ui/pie.vue';
import { ref, onMounted } from 'vue';
import deportistasService from '@/services/deportistasService';

// Estado de deportistas cargados desde el backend
const deportistas = ref([]);
const cargando = ref(false);
const error = ref(null);

// Cargar deportistas desde el backend
const cargarDeportistas = async () => {
  cargando.value = true;
  error.value = null;
  try {
    const response = await deportistasService.listarDeportistas(1, 100);
    if (response.success) {
      // Mapear datos del backend al formato esperado por el componente
      deportistas.value = response.data.map(deportista => {
        // Normalizar categoría - puede venir de categoria_info o categoria directo
        let categoria = 'sin categoria';
        if (deportista.categoria_info?.nombre_categoria) {
          categoria = deportista.categoria_info.nombre_categoria.toLowerCase().trim();
        } else if (deportista.categoria) {
          categoria = deportista.categoria.toLowerCase().trim();
        }

        // Normalizar estado
        let estado = deportista.estado ? deportista.estado.toLowerCase().trim() : 'activo';
        // Si el estado es booleano, convertirlo a string
        if (typeof deportista.persona?.estado === 'boolean') {
          estado = deportista.persona.estado ? 'activo' : 'inactivo';
        }

        return {
          id: deportista.id_deportista,
          id_deportista: deportista.id_deportista,
          nombre: deportista.nombre || 'Sin nombre',
          categoria: categoria,
          estado: estado,
          imagen: null,
          // Mantener información de categoría completa para comparación
          categoria_info: deportista.categoria_info,
          // Datos completos para el perfil y edición
          nombre1: deportista.nombre1 || deportista.persona?.primer_nombre || '',
          nombre2: deportista.nombre2 || deportista.persona?.segundo_nombre || '',
          apellido1: deportista.apellido1 || deportista.persona?.primer_apellido || '',
          apellido2: deportista.apellido2 || deportista.persona?.segundo_apellido || '',
          documento: deportista.documento || deportista.persona?.documento || '',
          correo: deportista.correo || deportista.persona?.correo_electronico || '',
          telefono: deportista.telefono || deportista.persona?.telefono || '',
          direccion: deportista.direccion || deportista.persona?.direccion || '',
          // Datos del deportista completos para edición
          ...deportista
        };
      });
    } else {
      error.value = response.message || 'Error al cargar deportistas';
      deportistas.value = [];
    }
  } catch (err) {
    console.error('Error al cargar deportistas:', err);
    error.value = 'No se pudo cargar la lista de deportistas. Por favor, intenta más tarde.';
    deportistas.value = [];
  } finally {
    cargando.value = false;
  }
};

// Cargar deportistas al montar el componente
onMounted(() => {
  cargarDeportistas();
});

// Estado para controlar el modal del formulario
const mostrarFormulario = ref(false);
const modoFormulario = ref('registrar');
const deportistaEditando = ref(null);

// Funciones para manejar eventos de deportistas
// Solo modo visualización - edición y eliminación deshabilitadas
function editarDeportista(deportista) {
  // Función deshabilitada - solo se puede ver la información
  // Al intentar editar, se abre en modo ver
  verDeportista(deportista);
}

async function verDeportista(deportista) {
  console.log('Ver detalles de deportista:', deportista);
  // Siempre abrir en modo ver - solo visualización
  modoFormulario.value = 'ver';

  try {
    // Cargar información completa del deportista desde el backend
    const idDeportista = deportista.id_deportista || deportista.id;
    const response = await deportistasService.obtenerDeportistaPorId(idDeportista);

    // El backend puede devolver 'status: success' o 'success: true'
    if ((response.status === 'success' || response.success) && response.data) {
      console.log('Datos completos del deportista:', response.data);
      // Usar los datos completos del backend
      deportistaEditando.value = response.data;
    } else {
      console.warn('No se recibieron datos completos, usando datos básicos:', deportista);
      // Si falla, usar los datos que ya tenemos
      deportistaEditando.value = deportista;
    }
  } catch (error) {
    console.error('Error al cargar detalles del deportista:', error);
    // Si hay error, usar los datos que ya tenemos
    deportistaEditando.value = deportista;
  }

  mostrarFormulario.value = true;
}

function eliminarDeportista(deportista) {
  // Función deshabilitada - solo se puede ver la información
  console.log('Eliminación deshabilitada - solo modo visualización');
}

function agregarDeportista() {
  // Función deshabilitada - solo modo visualización
  console.log('Agregar deportista deshabilitado - solo modo visualización');
  alert('La funcionalidad de agregar deportistas está deshabilitada. Solo se permite visualizar información.');
}

// Funciones para manejar el formulario
function cerrarFormulario() {
  mostrarFormulario.value = false;
  deportistaEditando.value = null;
}

async function manejarSubmitFormulario(resultado) {
  try {
    if (modoFormulario.value === 'actualizar') {
      // Si el resultado indica éxito
      if (resultado && resultado.success) {
        // Recargar la lista de deportistas
        await cargarDeportistas();
        
        // Cerrar el formulario y volver a modo ver
        cerrarFormulario();
        
        // Mostrar mensaje de éxito
        alert('Deportista actualizado exitosamente');
      } else {
        // Manejar error si viene en el resultado
        const mensajeError = resultado?.message || 'Error al actualizar deportista';
        alert(mensajeError);
      }
    }
  } catch (err) {
    console.error('Error al guardar deportista:', err);
    alert('Error al guardar deportista. Por favor, intenta de nuevo.');
  }
}

function cambiarAModoActualizar() {
  modoFormulario.value = 'actualizar';
}

function cambiarAModoVer() {
  modoFormulario.value = 'ver';
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
  padding: 1rem;
}

.modal-perfil-wrapper {
  width: 100%;
  max-width: 900px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  max-height: 90vh;
  overflow: auto;
}

.mensaje-error {
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem;
  text-align: center;
  color: #c33;
}

.btn-reintentar {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 0.5rem;
}

.btn-reintentar:hover {
  background: #0056b3;
}

.cargando {
  text-align: center;
  padding: 2rem;
  color: #666;
}
</style>
<template>
  <main class="vista-deportistas">
    <Encabezado rol="Admin" />
    <tituloClub></tituloClub>

    <!-- Mensaje de error -->
    <div v-if="error" class="mensaje-error">
      <p>{{ error }}</p>
      <button @click="cargarDeportistas" class="btn-reintentar">Reintentar</button>
    </div>

    <!-- Indicador de carga -->
    <div v-if="cargando" class="cargando">
      <p>Cargando deportistas...</p>
    </div>

    <!-- Lista de deportistas -->
    <ListaDeportistas v-else :deportistas="deportistas" @editar="editarDeportista" @eliminar="eliminarDeportista"
      @agregar="agregarDeportista" @ver="verDeportista" />

    <!-- Modal para ver/editar perfil del deportista -->
    <div v-if="mostrarFormulario" class="modal-overlay-deportistas">
      <div class="modal-perfil-wrapper" @click.stop>
        <!-- Mostrar perfil en modo ver -->
        <PerfilDeportistaVista 
          v-if="modoFormulario === 'ver'"
          :datos="deportistaEditando" 
          @cerrar="cerrarFormulario"
          @editar="cambiarAModoActualizar"
        />
        <!-- Mostrar formulario en modo actualizar -->
        <FormularioDeportista
          v-else-if="modoFormulario === 'actualizar'"
          :modo="'actualizar'"
          :datos="deportistaEditando"
          @submit="manejarSubmitFormulario"
          @cancel="cambiarAModoVer"
        />
      </div>
    </div>

    <Pie />
  </main>
</template>
