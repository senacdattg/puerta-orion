<template>
  <div class="historial-pagos">
    <div class="header-historial">
      <h4>Historial de Pagos</h4>
      <div class="resumen-total">
        <span class="label">Total Pagado:</span>
        <span class="valor total-pagado">{{ totalPagadoFormateado }}</span>
      </div>
    </div>

    <div class="lista-pagos" v-if="pagos.length > 0">
      <div
        v-for="pago in pagosOrdenados"
        :key="pago.id"
        class="item-pago"
        :class="pago.tipoPago"
      >
        <div class="header-pago">
          <div class="tipo-pago">
            <span class="icono">{{ getIconoTipoPago(pago.tipoPago) }}</span>
            <span class="texto">{{ getTextoPago(pago.tipoPago) }}</span>
          </div>
          <div class="fecha-pago">{{ formatearFecha(pago.fecha) }}</div>
        </div>

        <div class="detalles-pago">
          <div class="detalle-item">
            <span class="label">Monto:</span>
            <span class="valor monto">{{ formatearMonto(pago.monto) }}</span>
          </div>
          <div class="detalle-item">
            <span class="label">Método:</span>
            <span class="valor metodo">{{ getTextoMetodo(pago.metodoPago) }}</span>
          </div>
          <div class="detalle-item">
            <span class="label">Referencia:</span>
            <span class="valor referencia">{{ pago.referencia }}</span>
          </div>
          <div class="detalle-item" v-if="pago.observaciones">
            <span class="label">Observaciones:</span>
            <span class="valor observaciones">{{ pago.observaciones }}</span>
          </div>
        </div>

        <div class="estado-pago">
          <span class="badge" :class="getClaseEstado(pago)">{{ pago.nuevoEstado }}</span>
        </div>
      </div>
    </div>

    <div class="sin-pagos" v-else>
      <p>No hay pagos registrados para esta mensualidad</p>
    </div>

    <!-- Resumen final -->
    <div class="resumen-final">
      <div class="resumen-item">
        <span class="label">Valor Total Mensualidad:</span>
        <span class="valor">{{ mensualidad.valor }}</span>
      </div>
      <div class="resumen-item">
        <span class="label">Total Pagado:</span>
        <span class="valor total-pagado">{{ totalPagadoFormateado }}</span>
      </div>
      <div class="resumen-item">
        <span class="label">Saldo Pendiente:</span>
        <span class="valor saldo-pendiente" :class="claseSaldoPendiente">
          {{ saldoPendienteFormateado }}
        </span>
      </div>
      <div class="resumen-item">
        <span class="label">Estado Actual:</span>
        <span class="valor estado" :class="mensualidad.estado">{{ mensualidad.estado }}</span>
      </div>
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
      valor: '$0',
      estado: 'Pendiente',
      pagos: []
    })
  },
  pagos: {
    type: Array,
    required: true,
    default: () => []
  }
});

// Constantes
const ICONOS_TIPO_PAGO = {
  completo: '💳',
  parcial: '💰'
};

const TEXTOS_TIPO_PAGO = {
  completo: 'Pago Completo',
  parcial: 'Abono Parcial'
};

const METODOS_PAGO = {
  efectivo: 'Efectivo',
  transferencia: 'Transferencia',
  tarjeta: 'Tarjeta',
  cheque: 'Cheque',
  otro: 'Otro'
};

// Computed properties
const pagosOrdenados = computed(() =>
  [...props.pagos].sort((a, b) => new Date(b.fecha) - new Date(a.fecha))
);

const totalPagado = computed(() =>
  props.pagos.reduce((sum, pago) => sum + pago.monto, 0)
);

const totalPagadoFormateado = computed(() =>
  formatearMonto(totalPagado.value)
);

const valorTotal = computed(() =>
  parseFloat(props.mensualidad.valor.replace(/[^0-9.-]+/g, ''))
);

const saldoPendiente = computed(() =>
  Math.max(0, valorTotal.value - totalPagado.value)
);

const saldoPendienteFormateado = computed(() =>
  formatearMonto(saldoPendiente.value)
);

const claseSaldoPendiente = computed(() => {
  if (saldoPendiente.value === 0) return 'saldo-completo';
  if (saldoPendiente.value <= valorTotal.value * 0.3) return 'saldo-bajo';
  if (saldoPendiente.value <= valorTotal.value * 0.7) return 'saldo-medio';
  return 'saldo-alto';
});

// Funciones
function getIconoTipoPago(tipo) {
  return ICONOS_TIPO_PAGO[tipo] || '📝';
}

function getTextoPago(tipo) {
  return TEXTOS_TIPO_PAGO[tipo] || 'Pago';
}

function getTextoMetodo(metodo) {
  return METODOS_PAGO[metodo] || metodo;
}

function getClaseEstado(pago) {
  const clases = {
    'Pagado': 'estado-pagado',
    'Parcial': 'estado-parcial'
  };
  return clases[pago.nuevoEstado] || 'estado-pendiente';
}

function formatearFecha(fecha) {
  return new Date(fecha).toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function formatearMonto(monto) {
  return `$${monto.toLocaleString('es-CO')}`;
}
</script>
