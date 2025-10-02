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
    valor: '$150,000',
    estado: 'Pagado',
    fecha: '2024-08-15',
    fechasPago: ['2024-08-15'],
    vencimiento: '31/08/2024',
    avatar: null,
    observaciones: 'Pago completo realizado'
  },
  {
    id: 2,
    nombre: 'Ana Martínez',
    mes: 'Agosto',
    valor: '$150,000',
    estado: 'Pagado',
    fecha: '2024-08-20',
    fechasPago: ['2024-08-20'],
    vencimiento: '31/08/2024',
    avatar: null,
    observaciones: 'Pago puntual'
  },
  {
    id: 3,
    nombre: 'Luis García',
    mes: 'Agosto',
    valor: '$150,000',
    estado: 'Pendiente',
    fecha: 'Pendiente',
    fechasPago: [],
    vencimiento: '31/08/2024',
    avatar: null,
    observaciones: 'Pendiente de pago'
  },
  {
    id: 4,
    nombre: 'María López',
    mes: 'Septiembre',
    valor: '$150,000',
    estado: 'Pendiente',
    fecha: 'Pendiente',
    fechasPago: [],
    vencimiento: '30/09/2024',
    avatar: null,
    observaciones: 'Por pagar'
  },
  {
    id: 5,
    nombre: 'Juan Pérez',
    mes: 'Septiembre',
    valor: '$150,000',
    estado: 'Pagado',
    fecha: '2024-09-01',
    fechasPago: ['2024-09-01'],
    vencimiento: '30/09/2024',
    avatar: null,
    observaciones: 'Pago anticipado'
  },
  {
    id: 6,
    nombre: 'Sofia Torres',
    mes: 'Septiembre',
    valor: '$150,000',
    estado: 'Pendiente',
    fecha: 'Pendiente',
    fechasPago: [],
    vencimiento: '30/09/2024',
    avatar: null,
    observaciones: 'En proceso de pago'
  },
  {
    id: 7,
    nombre: 'Pedro Ramírez',
    mes: 'Agosto',
    valor: '$150,000',
    estado: 'Pagado',
    fecha: '2024-08-10',
    fechasPago: ['2024-08-10'],
    vencimiento: '31/08/2024',
    avatar: null,
    observaciones: 'Pago completo'
  },
  {
    id: 8,
    nombre: 'Carmen Vega',
    mes: 'Septiembre',
    valor: '$150,000',
    estado: 'Vencido',
    fecha: 'Pendiente',
    fechasPago: [],
    vencimiento: '30/09/2024',
    avatar: null,
    observaciones: 'Vencido - requiere seguimiento'
  },
  {
    id: 9,
    nombre: 'Roberto Silva',
    mes: 'Agosto',
    valor: '$150,000',
    estado: 'Pendiente',
    fecha: '2024-08-25',
    fechasPago: ['2024-08-25'],
    vencimiento: '31/08/2024',
    avatar: null,
    observaciones: 'Pago parcial - falta $75,000'
  },
  {
    id: 10,
    nombre: 'Elena Morales',
    mes: 'Septiembre',
    valor: '$150,000',
    estado: 'Pendiente',
    fecha: '2024-09-15',
    fechasPago: ['2024-09-15'],
    vencimiento: '30/09/2024',
    avatar: null,
    observaciones: 'Primera cuota pagada'
  }
]);

// Funciones para manejar eventos

function editarMensualidad(mensualidadActualizada) {
  console.log('Editar mensualidad:', mensualidadActualizada);
  
  // Encontrar la mensualidad en el array y actualizarla
  const index = mensualidades.value.findIndex(m => m.id === mensualidadActualizada.id);
  if (index !== -1) {
    // Actualizar la mensualidad con los nuevos datos
    Object.assign(mensualidades.value[index], mensualidadActualizada);
    console.log('Mensualidad actualizada:', mensualidades.value[index]);
  }
}

function eliminarMensualidad(mensualidad) {
  console.log('Eliminar mensualidad:', mensualidad);
  
  const confirmacion = confirm(
    `¿Estás seguro de eliminar la mensualidad de ${mensualidad.nombre}?\n\nEsta acción no se puede deshacer.`
  );
  
  if (confirmacion) {
    const index = mensualidades.value.findIndex(m => m.id === mensualidad.id);
    if (index !== -1) {
      mensualidades.value.splice(index, 1);
      console.log('Mensualidad eliminada');
    }
  }
}

function marcarComoPagado(mensualidad) {
  console.log('Marcar como pagado:', mensualidad);
  
  const confirmacion = confirm(
    `¿Marcar como pagado la mensualidad de ${mensualidad.nombre}?`
  );
  
  if (confirmacion) {
    mensualidad.estado = 'Pagado';
    mensualidad.fecha = new Date().toISOString().split('T')[0];
    if (!mensualidad.fechasPago) {
      mensualidad.fechasPago = [];
    }
    // Solo agregar fecha si no existe ya
    const fechaActual = new Date().toISOString().split('T')[0];
    if (!mensualidad.fechasPago.includes(fechaActual)) {
      mensualidad.fechasPago.push(fechaActual);
    }
    console.log('Mensualidad marcada como pagada');
  }
}

function nuevaMensualidad(nuevaMensualidad) {
  console.log('Nueva mensualidad recibida:', nuevaMensualidad);
  
  // Agregar la nueva mensualidad al array
  mensualidades.value.push(nuevaMensualidad);
  
  console.log('Total de mensualidades:', mensualidades.value.length);
  console.log('Array actualizado:', mensualidades.value);
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
