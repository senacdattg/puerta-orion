<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import ListaMensualidades from '../components/admin/lista-mensualidades.vue';
import Pie from '../components/layout/pie.vue';
import { ref } from 'vue';

// Datos de ejemplo para demostrar la funcionalidad
const mensualidades = ref([
  {
    id: 1,
    nombre: 'Carlos Rodríguez',
    mes: 'Agosto',
    valor: '$80.000',
    estado: 'Pagado',
    fecha: '15/08/2024',
    vencimiento: '31/08/2024',
    avatar: null
  },
  {
    id: 2,
    nombre: 'Ana Martínez',
    mes: 'Agosto',
    valor: '$80.000',
    estado: 'Pendiente',
    fecha: 'Pendiente',
    vencimiento: '31/08/2024',
    avatar: null
  },
  {
    id: 3,
    nombre: 'Luis García',
    mes: 'Agosto',
    valor: '$90.000',
    estado: 'Vencido',
    fecha: 'Pendiente',
    vencimiento: '31/08/2024',
    avatar: null
  },
  {
    id: 4,
    nombre: 'María López',
    mes: 'Septiembre',
    valor: '$85.000',
    estado: 'Pendiente',
    fecha: 'Pendiente',
    vencimiento: '30/09/2024',
    avatar: null
  },
  {
    id: 5,
    nombre: 'Juan Pérez',
    mes: 'Septiembre',
    valor: '$80.000',
    estado: 'Pagado',
    fecha: '01/09/2024',
    vencimiento: '30/09/2024',
    avatar: null
  },
  {
    id: 6,
    nombre: 'Sofia Torres',
    mes: 'Septiembre',
    valor: '$90.000',
    estado: 'Pendiente',
    fecha: 'Pendiente',
    vencimiento: '30/09/2024',
    avatar: null
  },
  {
    id: 7,
    nombre: 'Pedro Ramírez',
    mes: 'Agosto',
    valor: '$75.000',
    estado: 'Pagado',
    fecha: '20/08/2024',
    vencimiento: '31/08/2024',
    avatar: null
  },
  {
    id: 8,
    nombre: 'Carmen Vega',
    mes: 'Septiembre',
    valor: '$85.000',
    estado: 'Pendiente',
    fecha: 'Pendiente',
    vencimiento: '30/09/2024',
    avatar: null
  }
]);

// Funciones para manejar eventos
function editarMensualidad(mensualidad) {
  console.log('Editar mensualidad:', mensualidad);
  // Aquí se puede implementar la lógica para editar
  // Por ejemplo, abrir un modal o navegar a una página de edición
}

function eliminarMensualidad(mensualidad) {
  console.log('Eliminar mensualidad:', mensualidad);
  // Aquí se puede implementar la lógica para eliminar
  // Por ejemplo, mostrar confirmación y eliminar de la base de datos
}

function marcarComoPagado(mensualidad) {
  console.log('Marcar como pagado:', mensualidad);
  // Aquí se puede implementar la lógica para marcar como pagado
  // Por ejemplo, actualizar el estado en la base de datos
  mensualidad.estado = 'Pagado';
  mensualidad.fecha = new Date().toLocaleDateString('es-CO');
}

function nuevaMensualidad() {
  console.log('Crear nueva mensualidad');
  // Aquí se puede implementar la lógica para crear nueva mensualidad
  // Por ejemplo, abrir un modal o navegar a una página de creación
}
</script>

<template>
  <main>
    <Encabezado rol="Admin"/>
    <ListaMensualidades
      :mensualidades="mensualidades"
      @editar="editarMensualidad"
      @eliminar="eliminarMensualidad"
      @pagar="marcarComoPagado"
      @nueva="nuevaMensualidad"
    />
    <Pie />
  </main>
</template>

<style>
/* Importamos el CSS moderno para mensualidades */
@import '../assets/css/features/mensualidades/index.css';
</style>
