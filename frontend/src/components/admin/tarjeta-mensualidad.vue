<template>
  <div class="tarjeta-mensualidad" @click="verDetalle">
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
    </div>

    <!-- Botones de acción (visibilidad según permisos) -->
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

      <div class="acciones-secundarias">
        <button
          class="boton-accion boton-secundario gestionar"
          @click.stop="gestionarMensualidad"
          title="Gestionar mensualidad"
          v-if="puedeEditarMensualidad"
        >
          <span class="icono-accion">⚙️</span>
        </button>
        <button
          class="boton-accion boton-secundario eliminar"
          @click.stop="eliminarMensualidad"
          :title="props.mensualidad.activo ? 'Desactivar mensualidad' : 'Reactivar mensualidad'"
          v-if="puedeToggleMensualidad"
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
import { useAuthStore } from '@/stores/auth';
import { API_CONFIG } from '@/config/environment';
import Swal from 'sweetalert2';
import avatarDefault from '@/assets/imgs/perfil.png';

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

// Permisos
const authStore = useAuthStore();
const roleNames = computed(() => (authStore.user?.roles || []).map(r => typeof r === 'string' ? r : r?.nombre_rol));
const isSuperOrAdmin = computed(() => roleNames.value.includes('SuperAdmin') || roleNames.value.includes('Administrador'));

const puedeEditarMensualidad = computed(() => {
  if (isSuperOrAdmin.value) return true;
  try { return !!authStore?.hasPermission?.('editar_mensualidad'); } catch { return false; }
});
const puedeToggleMensualidad = computed(() => {
  if (isSuperOrAdmin.value) return true;
  try {
    return !!authStore?.hasPermission?.('desactivar_mensualidad') || !!authStore?.hasPermission?.('reactivar_mensualidad');
  } catch { return false; }
});

// Pago: permitir a Deportista/Acudiente iniciar pago
const roles = roleNames; // alias
const puedeIniciarPago = computed(() => roles.value.includes('Deportista') || roles.value.includes('Acudiente'));
const saldoPendientePositivo = computed(() => {
  const spRaw = props.mensualidad.saldo_pendiente_raw ?? props.mensualidad.saldoPendiente;
  const spNum = Number(spRaw);
  if (!isNaN(spNum)) return spNum > 0;
  // Fallback si no viene saldo: mostrar pagar si no está pagado
  return props.mensualidad.estado !== 'Pagado';
});

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
  if (!isNaN(saldo)) return `$${Math.max(0, saldo).toLocaleString('es-CO')}`;
  // Fallback si no viene del backend
  const monto = Number(props.mensualidad.monto_pago_raw || 0);
  return `$${monto.toLocaleString('es-CO')}`;
}

function totalPagadoTexto() {
  const monto = Number(props.mensualidad.monto_pago_raw);
  const saldo = Number(props.mensualidad.saldo_pendiente_raw);
  if (!isNaN(monto) && !isNaN(saldo)) {
    const pagado = Math.max(0, monto - saldo);
    return `$${pagado.toLocaleString('es-CO')}`;
  }
  // Fallback: si no hay datos crudos, asumir 0
  return `$${(0).toLocaleString('es-CO')}`;
}

async function pagarConMercadoPago() {
  try {
    const base = API_CONFIG.baseURL || '';
    const nombre_pagador = authStore?.user?.nombres ? `${authStore.user.nombres} ${authStore.user.apellidos || ''}`.trim() : 'Cliente';
    const email_pagador = authStore?.user?.email || 'sin-email@example.com';
    const numero_documento = authStore?.user?.documento || undefined;
    const tipo_documento = authStore?.user?.tipo_documento || undefined;

    const resp = await fetch(`${base}/api/mercadopago/crear-preferencia`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      },
      body: JSON.stringify({
        tipo_pago: 'mensualidad',
        id_mensualidad: props.mensualidad.id,
        nombre_pagador,
        email_pagador,
        numero_documento,
        tipo_documento
      })
    });
    const text = await resp.text();
    let json;
    try { json = text ? JSON.parse(text) : {}; } catch { json = {}; }
    if (!resp.ok || !json.success) {
      const msg = json.error || json.message || text || 'No se pudo crear la preferencia';
      await Swal.fire({
        icon: 'error',
        title: 'No se pudo iniciar el pago',
        text: msg
      });
      return;
    }
    const url = json.init_point || json.preference_url || json.initPoint || json.url;
    if (!url) throw new Error('Preferencia creada sin URL de inicio');
    window.location.href = url;
  } catch (e) {
    try {
      if (typeof e === 'object' && e !== null && e.message) {
        await Swal.fire({
          icon: 'error',
          title: 'Error en el pago',
          text: e.message
        });
  } else {
        await Swal.fire({
          icon: 'error',
          title: 'Error en el pago',
          text: typeof e === 'string' ? e : JSON.stringify(e)
        });
      }
    } catch {
      await Swal.fire({
        icon: 'error',
        title: 'Error iniciando pago con Mercado Pago'
      });
    }
  }
}

</script>


