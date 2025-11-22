<script setup>
defineOptions({
  name: 'VistaDeportistas'
});
import Encabezado from '../components/layout/encabezado.vue';
import ListaDeportistas from '../components/deportistas/lista-deportistas.vue';
import PerfilDeportistaVista from '../components/deportistas/perfil-deportista-vista.vue';
import Pie from '../components/layout/pie.vue';
import { ref, onMounted } from 'vue';
import deportistasService from '@/services/deportistasService';
import usuariosService from '@/services/usuariosService';
import Swal from 'sweetalert2';

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

function eliminarDeportista() {
  // Función deshabilitada - solo se puede ver la información
  console.log('Eliminación deshabilitada - solo modo visualización');
}

async function agregarDeportista() {
  // Función deshabilitada - solo modo visualización
  console.log('Agregar deportista deshabilitado - solo modo visualización');
  await Swal.fire({
    icon: 'info',
    title: 'Funcionalidad no disponible',
    text: 'La creación de deportistas está deshabilitada. Solo se permite visualizar información.'
  });
}

// Funciones para manejar el formulario
function cerrarFormulario() {
  mostrarFormulario.value = false;
  deportistaEditando.value = null;
}

async function manejarSubmitFormulario() {
  try {
    if (modoFormulario.value === 'actualizar') {
      // Recargar la lista de deportistas
      await cargarDeportistas();

      // Recargar los datos del deportista actualizado
      if (deportistaEditando.value) {
        const idDeportista = deportistaEditando.value.id_deportista || deportistaEditando.value.id;
        if (idDeportista) {
          const response = await deportistasService.obtenerDeportistaPorId(idDeportista);
          if ((response.status === 'success' || response.success) && response.data) {
            deportistaEditando.value = response.data;
          }
        }
      }

      // Volver a modo ver (no cerrar el modal)
      cambiarAModoVer();
    }
  } catch (err) {
    console.error('Error al guardar deportista:', err);
    await Swal.fire({
      icon: 'error',
      title: 'No se pudo guardar',
      text: 'Error al guardar deportista. Intenta nuevamente.'
    });
  }
}

function cambiarAModoActualizar() {
  modoFormulario.value = 'actualizar';
}

function cambiarAModoVer() {
  modoFormulario.value = 'ver';
}

// Función para cambiar el estado del deportista (usuario)
async function cambiarEstadoDeportista(deportista) {
  // Verificar que el deportista tenga un usuario asociado
  if (!deportista.id_usuario) {
    await Swal.fire({
      icon: 'info',
      title: 'Estado no disponible',
      text: 'Este deportista no tiene un usuario asociado. No se puede cambiar el estado.'
    });
    return;
  }

  // Confirmar el cambio
  const nuevoEstado = deportista.estado === 'activo' ? false : true;
  const accion = nuevoEstado ? 'activar' : 'desactivar';
  const confirmacion = await Swal.fire({
    icon: 'question',
    title: `¿Deseas ${accion} a ${deportista.nombre}?`,
    text: 'Podrás revertirlo en cualquier momento.',
    showCancelButton: true,
    confirmButtonText: `Sí, ${accion}`,
    cancelButtonText: 'Cancelar'
  });

  if (!confirmacion.isConfirmed) {
    return;
  }

  // Encontrar el índice del deportista en la lista
  const index = deportistas.value.findIndex(d => d.id === deportista.id);
  if (index === -1) {
    await Swal.fire({
      icon: 'error',
      title: 'No se encontró el deportista',
      text: 'Actualiza la tabla e inténtalo nuevamente.'
    });
    return;
  }

  // Guardar el estado anterior por si hay error
  const estadoAnterior = deportistas.value[index].estado;

  try {
    // Actualizar el estado local inmediatamente para feedback visual
    deportistas.value[index].estado = nuevoEstado ? 'activo' : 'inactivo';

    // Llamar al servicio para cambiar el estado del usuario
    const response = await usuariosService.cambiarEstadoUsuario(deportista.id_usuario, nuevoEstado);

    if (response.success || response.status === 'success') {
      // Mostrar mensaje de éxito
      await Swal.fire({
        icon: 'success',
        title: `Usuario ${accion}ado`,
        text: 'El estado se actualizó correctamente.',
        timer: 1500,
        showConfirmButton: false
      });

      // Recargar la lista para asegurar que los datos estén sincronizados
      await cargarDeportistas();
    } else {
      // Revertir el cambio si hubo error
      deportistas.value[index].estado = estadoAnterior;
      throw new Error(response.message || 'Error al cambiar el estado');
    }
  } catch (error) {
    // Revertir el cambio si hubo error
    if (index !== -1) {
      deportistas.value[index].estado = estadoAnterior;
    }
    console.error('Error al cambiar estado:', error);
    await Swal.fire({
      icon: 'error',
      title: `No se pudo ${accion}`,
      text: error.message || 'Error desconocido.'
    });
  }
}

</script>

<template>
  <main class="vista-deportistas">
    <Encabezado rol="Admin" />

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
      @agregar="agregarDeportista" @ver="verDeportista" @cambiar-estado="cambiarEstadoDeportista" />

    <!-- Modal para ver/editar perfil del deportista -->
    <div v-if="mostrarFormulario" class="modal-overlay modal-deportistas-overlay" @click.self="cerrarFormulario">
      <div class="modal-content modal-deportistas modal-xl" @click.stop>
        <!-- Mostrar perfil en modo ver o edición -->
        <PerfilDeportistaVista
          :datos="deportistaEditando"
          :modoEdicion="modoFormulario === 'actualizar'"
          @cerrar="cerrarFormulario"
          @editar="cambiarAModoActualizar"
          @guardar="manejarSubmitFormulario"
          @cancelar="cambiarAModoVer"
        />
      </div>
    </div>

    <Pie />
  </main>
</template>
