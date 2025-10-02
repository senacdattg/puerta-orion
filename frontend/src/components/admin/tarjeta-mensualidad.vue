<template>
  <div class="tarjeta-mensualidad" @click="verDetalle">
    <div class="header-mensualidad">
      <div class="avatar-deportista">
        <img
          :src="mensualidad.avatar || '/src/assets/imgs/perfil.png'"
          :alt="`Avatar de ${mensualidad.nombre}`"
          @error="imagenPorDefecto"
        />
      </div>
      <div class="estado-badge" :class="mensualidad.estado">
        <span class="estado-icono">{{ getIconoEstado() }}</span>
        {{ mensualidad.estado }}
      </div>
    </div>

    <div class="contenido-mensualidad">
      <h3 class="nombre-deportista">{{ mensualidad.nombre }}</h3>
      <div class="detalles-mensualidad">
        <div class="detalle-item">
          <span class="detalle-label">Mes:</span>
          <span class="detalle-valor">{{ mensualidad.mes }}</span>
        </div>
        <div class="detalle-item">
          <span class="detalle-label">Valor Total:</span>
          <span class="detalle-valor precio">{{ mensualidad.valor }}</span>
        </div>
        <div class="detalle-item">
          <span class="detalle-label">Saldo Pendiente:</span>
          <span class="detalle-valor saldo" :class="getClaseSaldo()">
            {{ calcularSaldoPendiente() }}
          </span>
        </div>
        <div class="detalle-item">
          <span class="detalle-label">Fecha:</span>
          <span class="detalle-valor">{{ mensualidad.fecha }}</span>
        </div>
      </div>
    </div>

    <!-- Botones de acción para ADMINISTRADOR -->
    <div class="acciones-mensualidad">
      <div class="acciones-principales">
        <button
          class="boton-accion boton-principal"
          @click.stop="verDetalleCompleto"
          title="Ver detalles completos"
        >
          <span class="icono-accion">👁️</span>
          <span class="texto-accion">Ver Detalles</span>
        </button>
      </div>

      <div class="acciones-secundarias">
        <button
          class="boton-accion boton-secundario gestionar"
          @click.stop="gestionarMensualidad"
          title="Gestionar mensualidad"
        >
          <span class="icono-accion">⚙️</span>
        </button>
        <button
          class="boton-accion boton-secundario reporte"
          @click.stop="generarReporte"
          title="Generar reporte"
        >
          <span class="icono-accion">📊</span>
        </button>
      </div>
    </div>

    <!-- Indicador de vencimiento -->
    <div class="indicador-vencimiento" :class="claseVencimiento">
      <span class="vencimiento-texto">{{ textoVencimiento }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

// Props
const props = defineProps({
  mensualidad: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      nombre: 'Sin nombre',
      mes: 'Sin mes',
      valor: '$0',
      estado: 'Pendiente',
      fecha: 'Sin fecha',
      vencimiento: null,
      avatar: null,
      pagos: [],
      saldoPendiente: 0
    })
  }
});

// Emits
const emit = defineEmits(['ver-detalle', 'gestionar', 'reporte', 'ver-detalle-completo']);

// Computed properties
const esVencida = computed(() => {
  // Si no hay fechas de pago, no está vencida (no ha pagado)
  if (!props.mensualidad.fechasPago || props.mensualidad.fechasPago.length === 0) {
    return false;
  }

  // Obtener la última fecha de pago
  const ultimaFechaPago = props.mensualidad.fechasPago[props.mensualidad.fechasPago.length - 1];
  if (!ultimaFechaPago) return false;

  // Calcular la fecha de vencimiento (fecha de pago + 1 mes)
  const fechaPago = new Date(ultimaFechaPago);
  const fechaVencimiento = new Date(fechaPago);
  fechaVencimiento.setMonth(fechaVencimiento.getMonth() + 1);

  // Verificar si está vencida
  const hoy = new Date();
  return fechaVencimiento < hoy;
});

const diasParaVencimiento = computed(() => {
  // Si no hay fechas de pago, no hay vencimiento calculado
  if (!props.mensualidad.fechasPago || props.mensualidad.fechasPago.length === 0) {
    return null;
  }

  // Obtener la última fecha de pago
  const ultimaFechaPago = props.mensualidad.fechasPago[props.mensualidad.fechasPago.length - 1];
  if (!ultimaFechaPago) return null;

  // Calcular la fecha de vencimiento (fecha de pago + 1 mes)
  const fechaPago = new Date(ultimaFechaPago);
  const fechaVencimiento = new Date(fechaPago);
  fechaVencimiento.setMonth(fechaVencimiento.getMonth() + 1);

  // Calcular días restantes
  const hoy = new Date();
  const diffTime = fechaVencimiento - hoy;
  const diasRestantes = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  return diasRestantes;
});

// Computed para la clase del indicador de vencimiento
const claseVencimiento = computed(() => {
  // Si no hay fechas de pago, no hay vencimiento
  if (!props.mensualidad.fechasPago || props.mensualidad.fechasPago.length === 0) {
    return 'sin-pagos';
  }

  if (esVencida.value) {
    return 'vencido';
  }
  
  const dias = diasParaVencimiento.value;
  
  if (dias === null) {
    return 'sin-fecha';
  }
  if (dias <= 3) {
    return 'proximo-vencer';
  }
  if (dias <= 7) {
    return 'advertencia';
  }
  return 'normal';
});

// Computed para el texto del indicador de vencimiento
const textoVencimiento = computed(() => {
  // Si no hay fechas de pago, no hay vencimiento
  if (!props.mensualidad.fechasPago || props.mensualidad.fechasPago.length === 0) {
    return 'Sin pagos';
  }

  if (esVencida.value) {
    return 'Vencido';
  }

  const dias = diasParaVencimiento.value;
  
  if (dias === null) {
    return 'Sin fecha';
  }
  if (dias <= 3) {
    return `Vence en ${dias} día${dias !== 1 ? 's' : ''}`;
  }
  if (dias <= 7) {
    return `Vence en ${dias} días`;
  }
  return `Vence en ${dias} días`;
});

// Funciones
function verDetalle() {
  emit('ver-detalle', props.mensualidad);
}

function verDetalleCompleto() {
  emit('ver-detalle-completo', props.mensualidad);
}

function gestionarMensualidad() {
  emit('gestionar', props.mensualidad);
}

function generarReporte() {
  emit('reporte', props.mensualidad);
}

function imagenPorDefecto(event) {
  event.target.src = '/src/assets/imgs/perfil.png';
}

function getIconoEstado() {
  const iconos = {
    'Pagado': '✓',
    'Pendiente': '⏳',
    'Parcial': '💰',
    'Vencido': '⚠️'
  };
  return iconos[props.mensualidad.estado] || '❓';
}

function getClaseSaldo() {
  const totalMensualidad = 150000;
  const numPagos = props.mensualidad.fechasPago ? props.mensualidad.fechasPago.length : 0;
  
  if (numPagos === 0) return 'saldo-alto'; // Sin pagos
  
  // Calcular saldo pendiente
  let totalPagado = 0;
  if (numPagos === 1) {
    totalPagado = totalMensualidad; // Pago completo
  } else {
    const montoPorPago = Math.floor(totalMensualidad / numPagos);
    totalPagado = numPagos * montoPorPago;
  }
  
  const saldoPendiente = totalMensualidad - totalPagado;
  
  if (saldoPendiente === 0) return 'saldo-completo';
  if (saldoPendiente <= totalMensualidad * 0.3) return 'saldo-bajo';
  if (saldoPendiente <= totalMensualidad * 0.7) return 'saldo-medio';
  return 'saldo-alto';
}

function calcularSaldoPendiente() {
  const totalMensualidad = 150000;
  const numPagos = props.mensualidad.fechasPago ? props.mensualidad.fechasPago.length : 0;
  
  if (numPagos === 0) {
    return `$${totalMensualidad.toLocaleString('es-CO')}`;
  }
  
  // Calcular total pagado
  let totalPagado = 0;
  if (numPagos === 1) {
    totalPagado = totalMensualidad; // Si hay solo un pago, es el total completo
  } else {
    // Si hay múltiples pagos, dividir equitativamente
    const montoPorPago = Math.floor(totalMensualidad / numPagos);
    totalPagado = numPagos * montoPorPago;
  }
  
  const saldoPendiente = totalMensualidad - totalPagado;
  return `$${Math.max(0, saldoPendiente).toLocaleString('es-CO')}`;
}

</script>
