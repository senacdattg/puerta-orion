<script setup>
import { defineOptions } from 'vue';
import Encabezado from '../components/layout/encabezado.vue';
import ListaMensualidades from '../components/admin/lista-mensualidades.vue';
import Pie from '../components/layout/pie.vue';
import { ref, onMounted } from 'vue';
import mensualidadesService from '@/services/mensualidadesService';

defineOptions({ name: 'MensualidadesView' });

const mensualidades = ref([]);
const loading = ref(false);
const errorMsg = ref('');

function formatoCOP(valor) {
  try { return new Intl.NumberFormat('es-CO').format(Number(valor)); } catch { return String(valor); }
}

function nombreMes(fechaISO) {
  if (!fechaISO) return '';
  const d = new Date(fechaISO);
  return d.toLocaleDateString('es-CO', { month: 'long' }).replace(/^./, m => m.toUpperCase());
}

function obtenerNombrePersonaDesdeObjeto(persona, fallbackId) {
  if (!persona) return `Persona #${fallbackId}`;
  // Intentar múltiples convenciones de nombre
  const posibles = [
    persona.nombre,
    persona.nombres,
    persona.nombre_persona,
    persona.nombre_completo,
    persona.full_name,
    persona.display_name
  ].filter(Boolean);
  if (posibles.length > 0) return String(posibles[0]);
  // Combinar nombre + apellido si existen
  const nombre = persona.primer_nombre || persona.nombre1 || persona.nombre;
  const apellido = persona.primer_apellido || persona.apellido1 || persona.apellidos || persona.apellido;
  if (nombre && apellido) return `${nombre} ${apellido}`;
  if (nombre) return String(nombre);
  return `Persona #${fallbackId}`;
}

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
      alert('No tienes permisos para ver mensualidades. Por favor, contacta al administrador.');
    } else if (e?.message?.includes('401') || e?.message?.includes('Unauthorized')) {
      alert('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.');
    } else {
      alert(`Error al cargar mensualidades: ${e?.message || 'Error desconocido'}`);
    }
  } finally {
    loading.value = false;
  }
}

async function iniciarPago(m) {
  try {
    const resp = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/mercadopago/crear-preferencia`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')||''}` },
      body: JSON.stringify({
      id_mensualidad: m.id,
      nombre_pagador: 'Tester',
      email_pagador: 'test_user_xxx@testuser.com',
      numero_documento: '12345678',
      tipo_documento: 'CC'
      })
    });
    const text = await resp.text();
    let json; try { json = text ? JSON.parse(text) : {}; } catch { json = {}; }
    if (!resp.ok || !json.success) { alert(json.error || json.message || text || 'Error iniciando pago'); return; }
    const url = json.init_point || json.sandbox_init_point || json.preference_url || json.initPoint;
    if (url) window.location.href = url; else alert('No se obtuvo link de pago');
  } catch (e) {
    try {
      if (typeof e === 'object' && e !== null && e.message) {
        alert(e.message);
      } else {
        alert(typeof e === 'string' ? e : JSON.stringify(e));
      }
    } catch {
      alert('Error iniciando pago');
    }
  }
}

async function editarMensualidad(mActualizada) {
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
    console.error(e);
    alert(e?.message || 'Error actualizando mensualidad');
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
    alert(e?.message || 'Error eliminando mensualidad');
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
  } catch (e) {
    alert(e?.message || 'Error creando mensualidad');
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

<style>
/* Importamos el CSS moderno para mensualidades */
@import '../assets/css/mensualidades.css';
</style>
