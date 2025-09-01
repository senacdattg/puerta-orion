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
    <div v-if="mensualidad.vencimiento" class="indicador-vencimiento" :class="getClaseVencimiento()">
      <span class="vencimiento-texto">{{ getTextoVencimiento() }}</span>
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
  if (!props.mensualidad.vencimiento) return false;
  return new Date(props.mensualidad.vencimiento) < new Date();
});

const diasParaVencimiento = computed(() => {
  if (!props.mensualidad.vencimiento) return null;
  const hoy = new Date();
  const vencimiento = new Date(props.mensualidad.vencimiento);
  const diffTime = vencimiento - hoy;
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
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
  const saldo = props.mensualidad.saldoPendiente || 0;
  if (saldo === 0) return 'saldo-completo';

  const valorTotal = parseFloat(props.mensualidad.valor.replace(/[^0-9.-]+/g, ''));
  if (saldo <= valorTotal * 0.3) return 'saldo-bajo';
  if (saldo <= valorTotal * 0.7) return 'saldo-medio';
  return 'saldo-alto';
}

function calcularSaldoPendiente() {
  if (props.mensualidad.estado === 'Pagado') return '$0';

  const valorTotal = parseFloat(props.mensualidad.valor.replace(/[^0-9.-]+/g, ''));
  const saldoPendiente = props.mensualidad.saldoPendiente || valorTotal;

  return `$${saldoPendiente.toLocaleString('es-CO')}`;
}

function getClaseVencimiento() {
  if (!props.mensualidad.vencimiento) return '';
  if (esVencida.value) return 'vencido';
  if (diasParaVencimiento.value <= 3) return 'proximo-vencer';
  if (diasParaVencimiento.value <= 7) return 'advertencia';
  return 'normal';
}

function getTextoVencimiento() {
  if (!props.mensualidad.vencimiento) return '';
  if (esVencida.value) return 'Vencido';
  return `Vence en ${diasParaVencimiento.value} días`;
}
</script>
