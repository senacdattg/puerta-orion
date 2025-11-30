<script setup>
import { ref, onMounted } from 'vue';
import Encabezado from '../components/layout/encabezado.vue';
import ListaMensualidades from '../components/admin/lista-mensualidades.vue';
import Pie from '../components/layout/pie.vue';
import mensualidadesService from '@/services/mensualidadesService';
import Swal from 'sweetalert2';
import { formatoCOP, nombreMes, obtenerNombrePersonaDesdeObjeto } from '@/utils/formatting';
import { iniciarPagoMercadoPago } from '@/utils/mercadopago';

defineOptions({ name: 'MensualidadesView' });

const mensualidades = ref([]);
const loading = ref(false);
const errorMsg = ref('');

// Use shared formatting utilities

function mapMensualidadToCard(m) {
  const estadoTxt = m.estado_texto || (m.estado ? 'Pagado' : 'Pendiente');
  const vencRaw = m.fecha_vencimiento || m.vencimiento;
  const venc = vencRaw ? new Date(vencRaw).toLocaleDateString('es-CO') : '';
  return {
    id: m.id_mensualidad,
    nombre: m.persona_nombre || obtenerNombrePersonaDesdeObjeto(m.persona, m.id_persona),
    persona_nombre: m.persona_nombre || obtenerNombrePersonaDesdeObjeto(m.persona, m.id_persona),
    numero_documento: m.numero_documento || (m.persona ? String(m.persona.documento || '') : null),
    mes: nombreMes(vencRaw),
    valor: `$${formatoCOP(m.monto_pago)}`,
    estado: estadoTxt,
    fecha: m.fecha_pago || 'Pendiente',
    fechasPago: m.fecha_pago ? [m.fecha_pago] : [],
    vencimiento: venc,
    avatar: null,
    observaciones: '',
    activo: m.activo === undefined ? true : !!m.activo,
    // datos crudos del backend para el modal
    monto_pago_raw: m.monto_pago,
    saldo_pendiente_raw: m.saldo_pendiente,
    estado_bool: m.estado,
    fecha_vencimiento_raw: vencRaw,
    // para fila de creación y método base
    created_at: m.created_at || m.fecha_creacion || m.creado,
    id_metodo_pago: m.id_metodo_pago
  };
}

async function cargarMensualidades() {
  loading.value = true;
  errorMsg.value = '';
  try {
    console.log('🔄 [Mensualidades] Iniciando carga de mensualidades...');
    const res = await mensualidadesService.list();
    console.log('📥 [Mensualidades] Respuesta del servicio:', res);

    if (!res) {
      throw new Error('No se recibió respuesta del servidor');
    }

    if (!res.success && res.error) {
      throw new Error(res.error || 'Error al cargar mensualidades');
    }

    const items = res.data || [];
    console.log('📊 [Mensualidades] Items recibidos:', items.length);
    mensualidades.value = items.map(mapMensualidadToCard);
    console.log('✅ [Mensualidades] Mensualidades cargadas exitosamente:', mensualidades.value.length);
  } catch (e) {
    console.error('❌ [Mensualidades] Error al cargar:', e);
    errorMsg.value = e?.message || 'Error cargando mensualidades';
    // Mostrar mensaje de error más descriptivo
    if (e?.message?.includes('403') || e?.message?.includes('Forbidden')) {
      await Swal.fire({
        icon: 'warning',
        title: 'Sin permisos',
        text: 'No tienes permisos para ver mensualidades. Por favor, contacta al administrador.'
      });
    } else if (e?.message?.includes('401') || e?.message?.includes('Unauthorized')) {
      await Swal.fire({
        icon: 'info',
        title: 'Sesión expirada',
        text: 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.'
      });
    } else {
      await Swal.fire({
        icon: 'error',
        title: 'Error al cargar mensualidades',
        text: e?.message || 'Error desconocido'
      });
    }
  } finally {
    loading.value = false;
  }
}

async function iniciarPago(m) {
  await iniciarPagoMercadoPago({
    id_mensualidad: m.id,
    nombre_pagador: 'Tester',
    email_pagador: 'test_user_xxx@testuser.com',
    numero_documento: '12345678',
    tipo_documento: 'CC'
  })
}

async function editarMensualidad(mActualizada) {
  // Si la mensualidad actualizada viene del backend (tiene todos los campos), actualizar directamente el array
  // Esto es más eficiente que recargar todas las mensualidades
  if (mActualizada.saldo_pendiente_raw !== undefined || mActualizada.monto_pago_raw !== undefined || mActualizada.saldo_pendiente !== undefined) {
    const index = mensualidades.value.findIndex(m => m.id === mActualizada.id || m.id === mActualizada.id_mensualidad);
    if (index !== -1) {
      // Preservar los campos existentes de la mensualidad actual y combinar con los nuevos datos
      const mensualidadExistente = mensualidades.value[index];
      // Combinar los datos existentes con los actualizados del backend
      const datosCombinados = {
        ...mensualidadExistente,
        ...mActualizada,
        // Asegurar que el ID sea correcto
        id: mActualizada.id || mActualizada.id_mensualidad || mensualidadExistente.id
      };
      // Mapear la mensualidad combinada al formato de la tarjeta
      const mensualidadMapeada = mapMensualidadToCard(datosCombinados);
      // Crear una nueva referencia para forzar la reactividad
      mensualidades.value[index] = mensualidadMapeada;
      return; // No hacer la llamada al backend si ya tenemos los datos actualizados
    }
  }

  // Si no tiene los campos crudos, hacer la actualización normal
  const payload = {};
  if (mActualizada.id_metodo_pago !== undefined) payload.id_metodo_pago = mActualizada.id_metodo_pago;
  if (mActualizada.numero_documento !== undefined) payload.numero_documento = mActualizada.numero_documento;
  if (mActualizada.monto_pago !== undefined) payload.monto_pago = mActualizada.monto_pago;
  if (mActualizada.fecha_vencimiento !== undefined) payload.fecha_vencimiento = mActualizada.fecha_vencimiento;
  if (mActualizada.saldo_pendiente !== undefined) payload.saldo_pendiente = mActualizada.saldo_pendiente;
  if (mActualizada.activo !== undefined) payload.activo = mActualizada.activo;
  try {
    await mensualidadesService.update(mActualizada.id, payload);
    await cargarMensualidades();
  } catch (e) {
    console.error('Error al actualizar mensualidad:', e);
    // El servicio ahora lanza errores con el mensaje del backend
    const mensajeError = e?.message || 'No se pudo actualizar la mensualidad.';
    await Swal.fire({
      icon: 'error',
      title: 'Error al actualizar mensualidad',
      text: mensajeError,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    });
  }
}

async function eliminarMensualidad(m) {
  try {
    if (m.activo) {
      await mensualidadesService.desactivar(m.id);
    } else {
      await mensualidadesService.reactivar(m.id);
    }
    await cargarMensualidades();
  } catch (e) {
    await Swal.fire({
      icon: 'error',
      title: 'Error al cambiar estado',
      text: e?.message || 'No se pudo cambiar el estado de la mensualidad.'
    });
  }
}

async function nuevaMensualidad(payload) {
  try {
    await mensualidadesService.create({
      numero_documento: payload.numero_documento,
      id_metodo_pago: payload.id_metodo_pago,
      monto_pago: payload.monto_pago,
      fecha_vencimiento: payload.fecha_vencimiento,
      activo: payload.activo,
      estado_ui: payload.estado_ui,
      saldo_pendiente: payload.saldo_pendiente
    });
    await cargarMensualidades();
    await Swal.fire({
      icon: 'success',
      title: '¡Mensualidad creada exitosamente!',
      text: 'La mensualidad se ha creado correctamente en el sistema.',
      confirmButtonText: 'Aceptar',
      confirmButtonColor: '#004AAD'
    });
  } catch (e) {
    const mensajeError = typeof e === 'string' ? e : (e?.message || 'No se pudo crear la mensualidad.');
    await Swal.fire({
      icon: 'error',
      title: 'Error al crear mensualidad',
      html: `<p><strong>No se pudo crear la mensualidad.</strong></p><p>${mensajeError}</p>`,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    });
  }
}

onMounted(cargarMensualidades);
</script>

<template>
  <main>
    <Encabezado />
    <ListaMensualidades
      :mensualidades="mensualidades"
      @editar="editarMensualidad"
      @eliminar="eliminarMensualidad"
      @pagar="iniciarPago"
      @nueva="nuevaMensualidad"
      @recargar="cargarMensualidades"
      :loading="loading"
      :error="errorMsg"
    />
    <Pie />
  </main>
</template>
