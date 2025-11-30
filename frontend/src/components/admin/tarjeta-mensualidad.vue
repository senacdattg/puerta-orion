<template>
  <div class="tarjeta-mensualidad" @click="verDetalleCompleto">
    <div class="header-mensualidad">
      <div class="avatar-deportista">
        <img
          :src="avatarDefault"
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
          <span class="detalle-label">Pagado:</span>
          <span class="detalle-valor precio">{{ totalPagadoTexto() }}</span>
        </div>
      </div>
      <button
        v-if="puedeToggleMensualidad"
        class="estado-mensualidad"
        :class="mensualidad.activo !== false ? 'activo' : 'inactivo'"
        @click.stop="cambiarEstado"
        :disabled="cambiandoEstado"
        :title="mensualidad.activo !== false ? 'Desactivar mensualidad' : 'Activar mensualidad'"
      >
        {{ mensualidad.activo !== false ? 'ACTIVO' : 'INACTIVO' }}
      </button>
    </div>

    <!-- Botones de acción (visibilidad según permisos) -->
    <div class="acciones-mensualidad">
      <div class="acciones-principales">
        <button
          class="boton-accion boton-principal"
          v-if="puedeIniciarPago && saldoPendientePositivo"
          @click.stop="pagarConMercadoPago"
          title="Pagar mensualidad"
        >
          <span class="icono-accion">💳</span>
          <span class="texto-accion">Pagar</span>
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
import { computed, ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import Swal from 'sweetalert2';
import avatarDefault from '@/assets/imgs/perfil.png';
import { parseISODateLocal } from '@/utils/date-utils';
import { iniciarPagoMercadoPago } from '@/utils/mercadopago';

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
const emit = defineEmits(['eliminar', 'ver-detalle-completo']);

// Permisos
const authStore = useAuthStore();
// Verificar el rol activo actual, no todos los roles del usuario
const isSuperOrAdmin = computed(() => {
  const rolActivo = authStore.activeRole;
  return rolActivo === 'SuperAdmin' || rolActivo === 'Administrador';
});

// Solo Administrador y SuperAdministrador pueden editar y desactivar mensualidades
const puedeEditarMensualidad = computed(() => isSuperOrAdmin.value);
const puedeToggleMensualidad = computed(() => isSuperOrAdmin.value);

// Pago: permitir a Deportista/Acudiente iniciar pago
// Para el pago, verificamos el rol activo actual
const puedeIniciarPago = computed(() => {
  const rolActivo = authStore.activeRole;
  return rolActivo === 'Deportista' || rolActivo === 'Acudiente';
});
const saldoPendientePositivo = computed(() => {
  const spRaw = props.mensualidad.saldo_pendiente_raw ?? props.mensualidad.saldoPendiente;
  const spNum = Number(spRaw);
  if (!Number.isNaN(spNum)) return spNum > 0;
  // Fallback si no viene saldo: mostrar pagar si no está pagado
  return props.mensualidad.estado !== 'Pagado';
});

// Use shared date utilities

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
  const diff = fv.getTime() - Date.now();
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
    return `Vence en ${dias} día${dias === 1 ? '' : 's'}`;
  }
  if (dias <= 7) {
    return `Vence en ${dias} días`;
  }
  return `Vence en ${dias} días`;
});

// Estado para controlar el cambio de estado
const cambiandoEstado = ref(false);

// Funciones
function verDetalleCompleto() {
  emit('ver-detalle-completo', props.mensualidad);
}

function cambiarEstado() {
  // Evitar múltiples clics mientras se procesa
  if (cambiandoEstado.value) return;
  emit('eliminar', props.mensualidad);
}

function imagenPorDefecto(event) {
  event.target.src = avatarDefault;
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
  if (!Number.isNaN(saldo)) return `$${Math.max(0, saldo).toLocaleString('es-CO')}`;
  // Fallback si no viene del backend
  const monto = Number(props.mensualidad.monto_pago_raw || 0);
  return `$${monto.toLocaleString('es-CO')}`;
}

function totalPagadoTexto() {
  const monto = Number(props.mensualidad.monto_pago_raw);
  const saldo = Number(props.mensualidad.saldo_pendiente_raw);
  if (!Number.isNaN(monto) && !Number.isNaN(saldo)) {
    const pagado = Math.max(0, monto - saldo);
    return `$${pagado.toLocaleString('es-CO')}`;
  }
  // Fallback: si no hay datos crudos, asumir 0
  return `$${(0).toLocaleString('es-CO')}`;
}

async function pagarConMercadoPago() {
  const nombre_pagador = authStore?.user?.nombres
    ? `${authStore.user.nombres} ${authStore.user.apellidos || ''}`.trim()
    : 'Cliente'
  const email_pagador = authStore?.user?.email || 'sin-email@example.com'
  const numero_documento = authStore?.user?.documento || undefined
  const tipo_documento = authStore?.user?.tipo_documento || undefined

  await iniciarPagoMercadoPago({
    id_mensualidad: props.mensualidad.id,
    nombre_pagador,
    email_pagador,
    numero_documento,
    tipo_documento
  })
}

</script>


