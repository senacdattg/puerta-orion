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
            {{ saldoPendienteTexto() }}
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
          class="boton-accion boton-secundario eliminar"
          @click.stop="eliminarMensualidad"
          :title="props.mensualidad.activo ? 'Desactivar mensualidad' : 'Reactivar mensualidad'"
        >
          <span class="icono-accion">{{ props.mensualidad.activo ? '🗑️' : '♻️' }}</span>
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
const emit = defineEmits(['ver-detalle', 'gestionar', 'eliminar', 'ver-detalle-completo']);

// Helpers
function parseISODateLocal(iso) {
  if (!iso) return null;
  if (typeof iso === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(iso)) {
    const [y, m, d] = iso.split('-').map(n => parseInt(n));
    return new Date(y, m - 1, d);
  }
  const d = new Date(iso);
  return isNaN(d) ? null : d;
}

// Computed properties
const esVencida = computed(() => {
  // Preferir fecha de vencimiento cruda del backend
  const fvRaw = props.mensualidad.fecha_vencimiento_raw || props.mensualidad.fecha_vencimiento;
  if (fvRaw) {
    const fv = parseISODateLocal(fvRaw);
    if (!fv) return false;
    const hoy = new Date(); hoy.setHours(0,0,0,0);
    const fv0 = new Date(fv.getFullYear(), fv.getMonth(), fv.getDate());
    return fv0 < hoy;
  }
  // Fallback anterior basado en fechasPago
  if (!props.mensualidad.fechasPago || props.mensualidad.fechasPago.length === 0) return false;
  const ultimo = props.mensualidad.fechasPago[props.mensualidad.fechasPago.length - 1];
  const fechaPago = typeof ultimo === 'object' ? ultimo.fecha : ultimo;
  const fp = parseISODateLocal(fechaPago);
  if (!fp) return false;
  const meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
  const idx = meses.indexOf(props.mensualidad.mes);
  if (idx === -1) return false;
  const fv = new Date(fp.getFullYear(), idx + 1, fp.getDate());
  return fv < new Date();
});

const diasParaVencimiento = computed(() => {
  const fvRaw = props.mensualidad.fecha_vencimiento_raw || props.mensualidad.fecha_vencimiento;
  if (fvRaw) {
    const fv = parseISODateLocal(fvRaw);
    if (!fv) return null;
    const hoy = new Date(); hoy.setHours(0,0,0,0);
    const ms = new Date(fv.getFullYear(), fv.getMonth(), fv.getDate()).getTime() - hoy.getTime();
    return Math.ceil(ms / (1000 * 60 * 60 * 24));
  }
  // Fallback basado en fechasPago y mes
  if (!props.mensualidad.fechasPago || props.mensualidad.fechasPago.length === 0) return null;
  const ultimo = props.mensualidad.fechasPago[props.mensualidad.fechasPago.length - 1];
  const fechaPago = typeof ultimo === 'object' ? ultimo.fecha : ultimo;
  const fp = parseISODateLocal(fechaPago);
  if (!fp) return null;
  const meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
  const idx = meses.indexOf(props.mensualidad.mes);
  if (idx === -1) return null;
  const fv = new Date(fp.getFullYear(), idx + 1, fp.getDate());
  const diff = fv.getTime() - new Date().getTime();
  return Math.ceil(diff / (1000*60*60*24));
});

// Computed para la clase del indicador de vencimiento
const claseVencimiento = computed(() => {
  // Si no hay fecha, no mostramos estados de vence
  if (diasParaVencimiento.value === null) return 'sin-fecha';

  if (esVencida.value) {
    return 'vencido';
  }
  
  const dias = diasParaVencimiento.value;
  
  if (dias === 0) return 'proximo-vencer';
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
  // Si no hay fecha, no mostramos
  if (diasParaVencimiento.value === null) return 'Sin fecha';

  if (esVencida.value) {
    return 'Vencido';
  }

  const dias = diasParaVencimiento.value;
  
  if (dias === 0) return 'Vence hoy';
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

function eliminarMensualidad() {
  emit('eliminar', props.mensualidad);
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
  const monto = Number(props.mensualidad.monto_pago_raw || 0);
  const saldo = Number(props.mensualidad.saldo_pendiente_raw ?? (monto || 0));
  if (saldo <= 0) return 'saldo-completo';
  if (monto <= 0) return 'saldo-alto';
  const ratio = saldo / monto;
  if (ratio <= 0.3) return 'saldo-bajo';
  if (ratio <= 0.7) return 'saldo-medio';
  return 'saldo-alto';
}

function saldoPendienteTexto() {
  const saldo = Number(props.mensualidad.saldo_pendiente_raw);
  if (!isNaN(saldo)) return `$${Math.max(0, saldo).toLocaleString('es-CO')}`;
  // Fallback si no viene del backend
  const monto = Number(props.mensualidad.monto_pago_raw || 0);
  return `$${monto.toLocaleString('es-CO')}`;
}

</script>
