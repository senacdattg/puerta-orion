<template>
  <div class="modal-overlay" @click="$emit('cerrar')">
    <div class="modal-contenido" @click.stop>
      <div class="modal-header">
        <h3>Detalles Completos de Mensualidad</h3>
        <button @click="$emit('cerrar')" class="btn-cerrar">✕</button>
      </div>

      <div class="modal-body">
        <!-- Información del deportista -->
        <div class="seccion-principal">
          <div class="deportista-info">
            <div class="avatar-deportista">
              <img
                :src="mensualidad.avatar || '/src/assets/imgs/perfil.png'"
                :alt="`Avatar de ${mensualidad.nombre}`"
              />
            </div>
            <div class="info-basica">
              <h4 class="nombre-deportista">{{ mensualidad.nombre }}</h4>
              <span :class="`estado-actual estado-${mensualidad.estado.toLowerCase()}`">
                {{ mensualidad.estado }}
              </span>
            </div>
          </div>
        </div>

        <!-- Información general -->
        <div class="seccion-detalles">
          <h5>📋 Información General</h5>
          <div class="grid-detalles">
            <div class="detalle-item">
              <span class="detalle-label">Mes</span>
              <span class="detalle-valor">{{ mensualidad.mes }}</span>
            </div>
            <div class="detalle-item">
              <span class="detalle-label">Valor Total</span>
              <span class="detalle-valor precio">{{ mensualidad.valor }}</span>
            </div>
            <div class="detalle-item">
              <span class="detalle-label">Fecha</span>
              <span class="detalle-valor">{{ mensualidad.fecha }}</span>
            </div>
            <div v-if="mensualidad.vencimiento" class="detalle-item">
              <span class="detalle-label">Vencimiento</span>
              <span class="detalle-valor vencimiento">{{ mensualidad.vencimiento }}</span>
            </div>
          </div>
        </div>

        <!-- Resumen financiero -->
        <div class="seccion-financiera">
          <h5>💰 Resumen Financiero</h5>
          <div class="resumen-grid">
            <div class="resumen-item">
              <span class="resumen-label">Valor Total</span>
              <span class="resumen-valor">{{ mensualidad.valor }}</span>
            </div>
            <div class="resumen-item">
              <span class="resumen-label">Saldo Pendiente</span>
              <span class="resumen-valor saldo" :class="getClaseSaldo()">
                {{ calcularSaldoPendiente() }}
              </span>
            </div>
          </div>
        </div>

        <!-- Historial de pagos -->
        <div class="seccion-historial">
          <h5>📊 Historial de Pagos</h5>
          <HistorialPagos
            :mensualidad="mensualidad"
            :pagos="mensualidad.pagos || []"
          />
        </div>
      </div>

      <div class="modal-footer">
        <button @click="$emit('gestionar', mensualidad)" class="btn btn-info">
          Gestionar
        </button>
        <button @click="$emit('reporte', mensualidad)" class="btn btn-warning">
          Generar Reporte
        </button>
        <button @click="$emit('cerrar')" class="btn btn-secondary">
          Cerrar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import HistorialPagos from './historial-pagos.vue';

// Props
const props = defineProps({
  mensualidad: {
    type: Object,
    required: true,
    default: () => ({})
  }
});

// Emits
const emit = defineEmits(['cerrar', 'gestionar', 'reporte']);

// Computed properties
const getClaseSaldo = () => {
  if (props.mensualidad.estado === 'Pagado') return 'saldo-completo';

  const valorTotal = parseFloat(props.mensualidad.valor.replace(/[^0-9.-]+/g, ''));
  const saldoPendiente = props.mensualidad.saldoPendiente || valorTotal;

  if (saldoPendiente === 0) return 'saldo-completo';
  if (saldoPendiente <= valorTotal * 0.3) return 'saldo-bajo';
  if (saldoPendiente <= valorTotal * 0.7) return 'saldo-medio';
  return 'saldo-alto';
};

const calcularSaldoPendiente = () => {
  if (props.mensualidad.estado === 'Pagado') return '$0';

  const valorTotal = parseFloat(props.mensualidad.valor.replace(/[^0-9.-]+/g, ''));
  const saldoPendiente = props.mensualidad.saldoPendiente || valorTotal;

  return `$${saldoPendiente.toLocaleString('es-CO')}`;
};
</script>
