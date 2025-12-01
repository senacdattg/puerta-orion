<template>
      <div class="modal-overlay" @click="cerrarModal">
        <div class="modal-content mensualidades-modal modal-lg" @click.stop>
          <div class="modal-header">
            <h2 class="modal-title">
              <i :class="editando ? 'fas fa-edit' : 'fas fa-file-invoice-dollar'"></i>
              {{ editando ? 'Editar Mensualidad' : 'Detalles mensualidad' }}
            </h2>
            <button @click="cerrarModal" class="btn-cerrar">
              <i class="fas fa-times"></i>
            </button>
          </div>

      <div class="modal-body">
        <!-- Información del deportista -->
        <div class="seccion-principal" v-if="!editando">
          <div class="deportista-info">
            <div class="avatar-deportista">
              <img
                :src="mensualidad.avatar || defaultAvatar"
                :alt="`Avatar de ${mensualidad.nombre}`"
              />
            </div>
            <div class="info-basica">
              <h4 class="nombre-deportista">{{ mensualidad.nombre }}</h4>
              <span :class="`estado-actual estado-${(mensualidad.estado_texto || (typeof mensualidad.estado === 'string' ? mensualidad.estado : (mensualidad.estado ? 'Pagado' : 'Pendiente'))).toLowerCase()}`">
                {{ mensualidad.estado_texto || (typeof mensualidad.estado === 'string' ? mensualidad.estado : (mensualidad.estado ? 'Pagado' : 'Pendiente')) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Información general -->
        <div class="seccion-detalles">
          <h5>📋 Información General</h5>

          <!-- Modo vista -->
          <div v-if="!editando" class="grid-detalles">
            <div class="detalle-item">
              <span class="detalle-label">Mes</span>
              <span class="detalle-valor">{{ mesDesdeVencimiento() }}</span>
            </div>
            <div class="detalle-item">
              <span class="detalle-label">Valor Total</span>
              <span class="detalle-valor precio">{{ formatCOP(mensualidad.monto_pago_raw ?? mensualidad.monto_pago ?? 0) }}</span>
            </div>
            <div class="detalle-item">
              <span class="detalle-label">Estado</span>
              <span class="detalle-valor">{{ (mensualidad.estado_bool ?? (mensualidad.estado === 'Pagado')) ? 'Pagado' : 'Pendiente' }}</span>
            </div>
            <div class="detalle-item" style="grid-column: 1 / 4;">
              <span class="detalle-label">Vencimiento</span>
              <span class="detalle-valor vencimiento">{{ mostrarVencimiento() }}</span>
            </div>
          </div>

          <!-- Modo edición -->
          <div v-else class="formulario-edicion">
            <!-- Tabs Edición (se eliminó el tab de Abonos) -->
            <!-- Encabezado contextual (oculto en edición para mostrar solo campos) -->
            <div class="seccion-form" v-if="false">
              <h6>Resumen rápido</h6>
              <div class="grid-detalles" style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;align-items:center;text-align:center;">
                <div class="detalle-item" style="text-align:center;">
                  <span class="detalle-label">Deportista</span>
                  <span class="detalle-valor">{{ mensualidad.nombre }}</span>
                </div>
                <div class="detalle-item" style="text-align:center;">
                  <span class="detalle-label">Estado actual</span>
                  <span class="detalle-valor" :class="`estado-${(mensualidad.estado_texto || (typeof mensualidad.estado === 'string' ? mensualidad.estado : (mensualidad.estado ? 'Pagado' : 'Pendiente'))).toLowerCase()}`">{{ mensualidad.estado_texto || (typeof mensualidad.estado === 'string' ? mensualidad.estado : (mensualidad.estado ? 'Pagado' : 'Pendiente')) }}</span>
                </div>
                <div class="detalle-item" style="text-align:center;">
                  <span class="detalle-label">Valor total</span>
                  <span class="detalle-valor precio">{{ mensualidad.valor }}</span>
                </div>
                <div class="detalle-item" style="text-align:center;">
                  <span class="detalle-label">Vence</span>
                  <span class="detalle-valor vencimiento">{{ mostrarVencimiento() }}</span>
                </div>
                <div class="detalle-item" style="text-align:center; grid-column: 1 / -1;">
                  <span class="detalle-label">Saldo pendiente</span>
                  <span class="detalle-valor saldo">{{ mostrarSaldoPendiente() }}</span>
                </div>
              </div>
            </div>
            <div class="linea-abajo" style="margin:12px 0;"></div>
            <!-- Sección: Datos de pago -->
            <div class="seccion-form">
              <h6>Datos de pago</h6>
              <p class="descripcion-seccion">Configura el método, el estado deseado y los importes.</p>
              <div class="grid-detalles" style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:start;">
                <div class="campo-formulario">
                  <label for="documento-edicion">
                    <i class="fas fa-id-card"></i>
                    Documento *
                  </label>
                  <input
                    id="documento-edicion"
                    v-model="formEdicion.numero_documento"
                    type="text"
                    inputmode="numeric"
                    placeholder="123456789"
                    class="input-edicion"
                    required
                    @input="manejarDocumentoEdicion"
                    @blur="verificarDocumentoEdicion"
                  />
                  <small
                    v-if="estadoDocumentoEdicion.mensaje"
                    :class="['mensaje-documento', estadoDocumentoEdicion.status]"
                  >
                    {{ estadoDocumentoEdicion.mensaje }}
                  </small>
                </div>
                <div class="campo-formulario">
                  <label for="metodo-edicion">
                    <i class="fas fa-money-bill-wave"></i>
                    Método de Pago *
                  </label>
                  <select id="metodo-edicion" v-model.number="formEdicion.id_metodo_pago" class="select-edicion" required>
                    <option disabled value="">Selecciona un método</option>
                    <option v-for="m in metodosPago" :key="m.id" :value="m.id">{{ m.nombre }}</option>
                  </select>
                  <small class="hint">Usa el método por defecto de esta mensualidad.</small>
                </div>
                <div class="campo-formulario">
                  <label for="estado-edicion">
                    <i class="fas fa-info-circle"></i>
                    Estado (visual)
                  </label>
                  <select id="estado-edicion" v-model="formEdicion.estado_ui" class="select-edicion">
                    <option value="Pendiente">Pendiente</option>
                    <option value="Pagado">Pagado</option>
                  </select>
                  <small class="hint">El estado real lo fija el saldo pendiente (0 = Pagado).</small>
                </div>
              </div>
              <div class="grid-detalles" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;align-items:start;margin-top:16px;">
                <div class="campo-formulario">
                  <label for="valor-edicion">
                    <i class="fas fa-dollar-sign"></i>
                    Valor Total *
                  </label>
                  <div class="input-with-symbol">
                    <span class="dollar-symbol">$</span>
                    <input
                      id="valor-edicion"
                      v-model="formEdicion.valorSinSimbolo"
                      type="text"
                      inputmode="decimal"
                      placeholder="80000"
                      class="input-edicion"
                      required
                      @input="manejarValorSinSimbolo($event)"
                    />
                  </div>
                  <small class="hint">Es el valor base de cada mensualidad.</small>
                </div>
                <div class="campo-formulario">
                  <label for="saldo-edicion">
                    <i class="fas fa-balance-scale"></i>
                    Saldo Pendiente
                  </label>
                  <input
                    id="saldo-edicion"
                    v-model="formEdicion.saldo_pendiente"
                    type="text"
                    inputmode="decimal"
                    class="input-edicion"
                    placeholder="0"
                    @input="manejarSaldoPendiente($event)"
                  />
                  <small class="hint">Si eliges “Pagado”, se guardará con saldo 0 automáticamente.</small>
                </div>
              </div>
            </div>
            <div class="linea-abajo" style="margin:12px 0;"></div>

            <!-- Sección: Fechas y estado -->
            <div class="seccion-form">
              <h6>Fechas y vigencia</h6>
              <p class="descripcion-seccion">Controla vigencia y confirma cuándo quedó pago.</p>
              <div class="grid-detalles">
            <div class="campo-formulario">
              <label for="vencimiento-edicion">
                <i class="fas fa-clock"></i>
                Fecha de Vencimiento
              </label>
                  <input id="vencimiento-edicion" v-model="formEdicion.fecha_vencimiento" type="date"
                class="input-edicion" />
            </div>

            <div class="campo-formulario">
                  <label for="fecha_pago">
                    <i class="fas fa-calendar-check"></i>
                    Fecha de Pago
              </label>
                  <input id="fecha_pago" type="date" :value="formEdicion.fecha_pago" class="input-edicion" disabled />
                  <small class="hint">Se llena sola cuando el saldo llega a 0.</small>
            </div>

                <div class="campo-formulario">
                  <label for="activo">
                    <i class="fas fa-toggle-on"></i>
                    Activo
                  </label>
                  <button type="button"
                          class="btn-toggle-activo"
                          :class="{ on: formEdicion.activo }"
                          @click="formEdicion.activo = !formEdicion.activo">
                    {{ formEdicion.activo ? 'Activo' : 'Inactivo' }}
                </button>
                  <small class="hint">Click para activar/desactivar.</small>
                </div>
              </div>
            </div>
            <div class="linea-abajo" style="margin:12px 0;"></div>
          </div>
        </div>



        <!-- Historial de pagos -->
        <div class="seccion-historial" v-if="!editando">
          <h5>📊 Historial de Pagos</h5>
          <div class="historial-pagos-container">
            <div class="resumen-pagos">
            <div class="resumen-item">
              <span class="resumen-label">Valor Total Mensualidad</span>
              <span class="resumen-valor">{{ mensualidad.valor || formatCOP(mensualidad.monto_pago_raw ?? mensualidad.monto_pago ?? 0) }}</span>
            </div>
              <div class="resumen-item">
                <span class="resumen-label">Total Pagado</span>
                <span class="resumen-valor pagado">${{ calcularTotalPagado().toLocaleString('es-CO') }}</span>
              </div>
              <div class="resumen-item">
                <span class="resumen-label">Saldo Pendiente</span>
                <span class="resumen-valor pendiente">${{ calcularSaldoPendienteHistorial().toLocaleString('es-CO') }}</span>
              </div>
            </div>

            <div class="lista-pagos">
              <h6>Fechas de pago y abonos</h6>
              <div v-if="listaPagosYAbonos().length > 0" class="pagos-list">
                <table class="tabla-historial" style="width:100%; border-collapse:collapse;">
                  <caption class="sr-only">Historial de fechas de pago y abonos de la mensualidad</caption>
                  <thead>
                    <tr style="text-align:center; border-bottom:1px solid #e5e7eb;">
                      <th style="padding:8px;">Fecha</th>
                      <th style="padding:8px;">Monto</th>
                      <th style="padding:8px;">Método</th>
                      <th style="padding:8px;">Tipo</th>
                      <th style="padding:8px;">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in listaPagosYAbonos()" :key="index" style="border-bottom:1px solid #f3f4f6;">
                      <td style="padding:8px; text-align:center;">
                        <template v-if="abonoEditIndex===index">
                          <input type="date" v-model="abonoEdit.fecha" class="input-edicion" />
                        </template>
                        <template v-else>
                          {{ formatearFecha(item.fecha) }}
                        </template>
                      </td>
                      <td style="padding:8px; text-align:center;">
                        <template v-if="abonoEditIndex===index">
                          <input type="number" v-model.number="abonoEdit.monto" class="input-edicion" style="max-width:120px;" />
                        </template>
                        <template v-else>
                          {{ item.monto !== undefined ? `$${Number(item.monto).toLocaleString('es-CO')}` : '—' }}
                        </template>
                      </td>
                      <td style="padding:8px; text-align:center;">
                        <template v-if="abonoEditIndex===index">
                          <select v-model.number="abonoEdit.id_metodo_pago" class="select-edicion" style="max-width:140px;">
                            <option :value="undefined">—</option>
                            <option v-for="m in metodosPago" :key="m.id" :value="m.id">{{ m.nombre }}</option>
                          </select>
                        </template>
                        <template v-else>
                          {{ item.metodo || '—' }}
                        </template>
                      </td>
                      <td style="padding:8px; color:#6b7280; text-align:center;">{{ item.tipo }}</td>
                      <td style="padding:8px; text-align:right;">
                        <template v-if="item.id_abono && item.tipo !== 'Creación'">
                          <template v-if="abonoEditIndex===index">
                            <button class="btn btn-primary" style="margin-right:6px;" @click="guardarEdicionAbono()">Guardar</button>
                            <button class="btn btn-secondary" @click="abonoEditIndex=null">Cancelar</button>
                          </template>
                          <template v-else>
                            <button class="btn btn-secondary" style="margin-right:6px;" @click="iniciarEdicionAbono(index)" v-if="puedeEditarAbono">Editar</button>
                            <button class="btn btn-danger" @click="eliminarAbono(index)" v-if="puedeEliminarAbono">Eliminar</button>
                          </template>
                        </template>
                        <template v-else>
                          —
                        </template>
                      </td>
                    </tr>
                    <!-- Fila para agregar nuevo abono -->
                    <!-- Fila para agregar nuevo abono -->
                    <tr v-if="puedeAbonar && abonoEditIndex === -1" style="border-bottom:1px solid #f3f4f6; background-color: #f9fafb;">
                      <td style="padding:8px; text-align:center;">
                        <input type="date" v-model="nuevoAbono.fecha" class="input-edicion" />
                      </td>
                      <td style="padding:8px; text-align:center;">
                        <input type="number" v-model.number="nuevoAbono.monto" class="input-edicion" style="max-width:120px;" placeholder="0" />
                      </td>
                      <td style="padding:8px; text-align:center;">
                        <select v-model.number="nuevoAbono.id_metodo_pago" class="select-edicion" style="max-width:140px;">
                          <option :value="undefined">—</option>
                          <option v-for="m in metodosPago" :key="m.id" :value="m.id" :disabled="String(m.nombre).toLowerCase()==='ninguno'">{{ m.nombre }}</option>
                        </select>
                      </td>
                      <td style="padding:8px; color:#6b7280; text-align:center;">Abono</td>
                      <td style="padding:8px; text-align:right;">
                        <button class="btn btn-primary" style="margin-right:6px;" @click="guardarNuevoAbonoDesdeTabla()">Guardar</button>
                        <button class="btn btn-secondary" @click="cancelarNuevoAbono()">Cancelar</button>
                      </td>
                    </tr>
                    <!-- Botón para agregar nuevo abono -->
                    <tr v-if="puedeAbonar && abonoEditIndex === null">
                      <td colspan="5" style="padding:12px; text-align:center;">
                        <button class="btn btn-secondary" @click="iniciarNuevoAbono()" style="width:100%;">
                          ➕ Agregar Abono
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-else class="sin-pagos">
                <p v-if="!puedeAbonar || abonoEditIndex === -1">No hay pagos ni abonos registrados</p>
                <button v-if="puedeAbonar && abonoEditIndex === null" class="btn btn-secondary" @click="iniciarNuevoAbono()" style="margin-top:1rem;">
                  ➕ Agregar Abono
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <!-- Botones en modo vista -->
        <template v-if="!editando">
          <button @click="toggleEdicion" class="btn btn-edit" v-if="puedeEditarMensualidad">
            ✏️ Editar
          </button>
          <button v-if="saldoPendienteHistNum > 0" @click="pagarConMercadoPago" class="btn btn-primary">
            💳 Pagar con Mercado Pago
          </button>
          <button @click="cerrarModal" class="btn btn-secondary">
            Cerrar
          </button>
        </template>

        <!-- Botones en modo edición -->
        <template v-else>
          <button @click="guardarCambios" class="btn btn-primary">
            Guardar Cambios
          </button>
          <button @click="toggleEdicion" class="btn btn-secondary">
            Cancelar
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { API_CONFIG, LOG_CONFIG } from '@/config/environment';
import mensualidadesService from '@/services/mensualidadesService';
import { useAuthStore } from '@/stores/auth';
import Swal from 'sweetalert2';
import defaultAvatar from '@/assets/imgs/perfil.png';
import { useModalScrollLock } from '@/composables/useModalScrollLock';
import { extraerMensajeError } from '@/utils/error-handling';
import { normalizarDocumento, normalizarMonto, parseMonto, normalizarIdMetodoPago, MIN_DOCUMENTO, MAX_DOCUMENTO } from '@/utils/normalization-forms';
import { esFechaValida } from '@/utils/date-utils';
import { formatoCOP } from '@/utils/formatting';

// Props
const props = defineProps({
  mensualidad: {
    type: Object,
    required: true,
    default: () => ({})
  },
  modoEdicion: {
    type: Boolean,
    default: false
  },
  mostrar: {
    type: Boolean,
    default: true
  }
});

// Emits
const emit = defineEmits(['cerrar', 'gestionar', 'guardar-cambios']);

// Bloquear scroll del body cuando el modal está abierto
useModalScrollLock(computed(() => props.mostrar));

// Estado reactivo
const editando = ref(props.modoEdicion);
const metodosPago = ref([]);
const formEdicion = ref({
  id_metodo_pago: undefined,
  valor: props.mensualidad.valor || '',
  valorSinSimbolo: extraerNumeroDeValor(props.mensualidad.valor),
  numero_documento: '',
  fecha_vencimiento: props.mensualidad.vencimiento ? formatearAInputDate(props.mensualidad.vencimiento) : '',
  saldo_pendiente: undefined,
  estado_ui: props.mensualidad.estado || 'Pendiente',
  activo: true,
  fecha_pago: ''
});
// Guardar estado inicial para comparar cambios
const formEdicionInicial = ref(null);
const documentoOriginal = ref(normalizarDocumento(props.mensualidad.numero_documento || ''));
const estadoDocumentoEdicion = ref({ status: 'idle', mensaje: '' });
const personaDocumentoEdicion = ref(null);
let documentoConsultandoEdicion = null;
const nuevoAbono = ref({ fecha: '', monto: '', id_metodo_pago: undefined });
const abonos = ref([]);
const abonoEditIndex = ref(null);
const abonoEdit = ref({ fecha: '', monto: undefined, id_metodo_pago: undefined });

// Use shared normalization utilities

function actualizarEstadoDocumentoEdicion(status, mensaje) {
  estadoDocumentoEdicion.value = { status, mensaje };
}

function resetDocumentoEdicion() {
  personaDocumentoEdicion.value = null;
  estadoDocumentoEdicion.value = { status: 'idle', mensaje: '' };
  documentoConsultandoEdicion = null;
}

function manejarDocumentoEdicion(event) {
  formEdicion.value.numero_documento = normalizarDocumento(event?.target?.value ?? formEdicion.value.numero_documento ?? '');
  personaDocumentoEdicion.value = null;
  documentoConsultandoEdicion = null;

  if (!formEdicion.value.numero_documento) {
    resetDocumentoEdicion();
    return;
  }

  if (formEdicion.value.numero_documento.length < MIN_DOCUMENTO) {
    actualizarEstadoDocumentoEdicion('indicacion', `Ingresa al menos ${MIN_DOCUMENTO} dígitos para buscar.`);
    return;
  }

  actualizarEstadoDocumentoEdicion('pendiente', 'Documento listo. Sal del campo para verificar.');
}

async function verificarDocumentoEdicion() {
  const documento = formEdicion.value.numero_documento;

  if (!documento) {
    resetDocumentoEdicion();
    return;
  }

  if (documento.length < MIN_DOCUMENTO) {
    actualizarEstadoDocumentoEdicion('indicacion', `Ingresa al menos ${MIN_DOCUMENTO} dígitos para buscar.`);
    return;
  }

  const documentoEnProceso = documento;
  documentoConsultandoEdicion = documentoEnProceso;
  personaDocumentoEdicion.value = null;
  actualizarEstadoDocumentoEdicion('checking', 'Buscando persona...');

  try {
    const respuesta = await mensualidadesService.buscarPersonaPorDocumento(documentoEnProceso);

    if (documentoConsultandoEdicion !== documentoEnProceso) {
      return;
    }

    if (!respuesta?.success) {
      const mensaje = respuesta?.error || 'No fue posible verificar el documento.';
      actualizarEstadoDocumentoEdicion('error', mensaje);
      return;
    }

    if (respuesta.encontrado) {
      personaDocumentoEdicion.value = respuesta.data;
      const nombre = respuesta.data?.nombre_completo || 'Persona encontrada';
      if (respuesta.data?.estado === false) {
        actualizarEstadoDocumentoEdicion('warning', `${nombre} está inactiva. Verifica antes de continuar.`);
      } else {
        actualizarEstadoDocumentoEdicion('found', `${nombre} registrada en el sistema.`);
      }
    } else {
      const mensaje = respuesta?.message || 'No encontramos una persona con ese documento.';
      actualizarEstadoDocumentoEdicion('not-found', mensaje);
    }
  } catch (error) {
    if (documentoConsultandoEdicion !== documentoEnProceso) {
      return;
    }
    const mensaje = error?.message || 'Error al buscar el documento.';
    actualizarEstadoDocumentoEdicion('error', mensaje);
  } finally {
    if (documentoConsultandoEdicion === documentoEnProceso) {
      documentoConsultandoEdicion = null;
    }
  }
}

function inicializarDocumentoEdicion() {
  documentoOriginal.value = normalizarDocumento(props.mensualidad.numero_documento || formEdicion.value.numero_documento || '');
  formEdicion.value.numero_documento = documentoOriginal.value;
  personaDocumentoEdicion.value = null;
  documentoConsultandoEdicion = null;

  if (!documentoOriginal.value) {
    resetDocumentoEdicion();
    return;
  }

  const nombre = props.mensualidad.persona_nombre || props.mensualidad.nombre;
  if (nombre) {
    actualizarEstadoDocumentoEdicion('found', `${nombre} registrada en el sistema.`);
  } else {
    actualizarEstadoDocumentoEdicion('pendiente', 'Documento listo. Sal del campo para verificar.');
  }
}

// Función para normalizar valores para comparación
function normalizarValorParaComparacion(valor) {
  if (valor === null || valor === undefined || valor === '') {
    return ''
  }
  if (typeof valor === 'string') {
    const trimmed = valor.trim()
    // Si es un string numérico, convertirlo a número para comparación
    const num = Number(trimmed)
    if (!Number.isNaN(num) && trimmed !== '') {
      return num
    }
    return trimmed
  }
  if (typeof valor === 'number') {
    return valor
  }
  if (typeof valor === 'boolean') {
    return valor
  }
  return String(valor)
}

// Verificar si hay cambios
function verificarCambios() {
  if (!formEdicionInicial.value) {
    if (LOG_CONFIG && LOG_CONFIG.enabled) {
      console.log('⚠️ [verificarCambios] No hay estado inicial guardado');
    }
    return false
  }

  const campos = [
    'id_metodo_pago', 'valorSinSimbolo', 'numero_documento', 'fecha_vencimiento',
    'saldo_pendiente', 'estado_ui', 'activo'
  ]

  for (const campo of campos) {
    const valorInicial = normalizarValorParaComparacion(formEdicionInicial.value[campo])
    const valorActual = normalizarValorParaComparacion(formEdicion.value[campo])

    // Comparación más robusta
    if (valorInicial !== valorActual) {
      if (LOG_CONFIG && LOG_CONFIG.enabled) {
        console.log(`✅ [verificarCambios] Cambio detectado en campo "${campo}":`, {
          inicial: valorInicial,
          actual: valorActual,
          tipoInicial: typeof valorInicial,
          tipoActual: typeof valorActual
        });
      }
      return true
    }
  }

  if (LOG_CONFIG && LOG_CONFIG.enabled) {
    console.log('ℹ️ [verificarCambios] No se detectaron cambios');
  }
  return false
}

// Helper para obtener el ID de la mensualidad (soporta múltiples formatos)
function obtenerIdMensualidad() {
  return props.mensualidad?.id || props.mensualidad?.id_mensualidad || null;
}

// Helper para mapear abonos del backend al formato del componente
function mapearAbonosDelBackend(abonosData) {
  return (abonosData || [])
    .filter(a => a.id_abono !== null && a.id_abono !== undefined)
    .map(a => ({
      id_abono: a.id_abono,
      monto: Number(a.monto) || 0,
      fecha_abono: a.fecha_abono,
      id_metodo_pago: a.id_metodo_pago,
      es_pago_final: !!a.es_pago_final
    }))
}

// Helper para mapear mensualidad del backend al formato del componente
function mapearMensualidadDelBackend(mensualidadBackend, overrides = {}) {
  const mensualidadId = obtenerIdMensualidad()
  const saldoPendienteBackend = mensualidadBackend.saldo_pendiente_raw ?? mensualidadBackend.saldo_pendiente ?? null
  const montoPagoBackend = mensualidadBackend.monto_pago_raw ?? mensualidadBackend.monto_pago ?? null
  const nombrePersona = mensualidadBackend.persona_nombre || props.mensualidad.persona_nombre || props.mensualidad.nombre

  return {
    ...props.mensualidad,
    ...mensualidadBackend,
    id: mensualidadBackend.id_mensualidad || mensualidadBackend.id || mensualidadId,
    saldo_pendiente_raw: saldoPendienteBackend,
    saldo_pendiente: saldoPendienteBackend,
    saldoPendiente: saldoPendienteBackend,
    monto_pago_raw: montoPagoBackend,
    monto_pago: montoPagoBackend,
    estado_bool: mensualidadBackend.estado,
    estado_texto: mensualidadBackend.estado_texto || (mensualidadBackend.estado ? 'Pagado' : 'Pendiente'),
    estado: mensualidadBackend.estado_texto || (mensualidadBackend.estado ? 'Pagado' : 'Pendiente'),
    fecha_vencimiento_raw: mensualidadBackend.fecha_vencimiento,
    persona_nombre: nombrePersona,
    nombre: nombrePersona,
    ...overrides
  }
}

function configurarFormularioDesdeProps() {
  documentoOriginal.value = normalizarDocumento(props.mensualidad.numero_documento || '');
  formEdicion.value = {
    id_metodo_pago: normalizarIdMetodoPago(props.mensualidad.id_metodo_pago ?? props.mensualidad.idMetodoPago),
    valor: props.mensualidad.valor || '',
    valorSinSimbolo: extraerNumeroDeValor(props.mensualidad.valor),
    numero_documento: documentoOriginal.value,
    fecha_vencimiento: props.mensualidad.vencimiento ? formatearAInputDate(props.mensualidad.vencimiento) : '',
    saldo_pendiente: (() => { // NOSONAR: S3358 - Extract nested ternary to reduce cognitive complexity
      const saldoRaw = props.mensualidad.saldo_pendiente_raw;
        if (saldoRaw !== undefined && saldoRaw !== null) {
          return String(saldoRaw);
        }
        const saldoPendiente = props.mensualidad.saldoPendiente;
        if (saldoPendiente !== undefined && saldoPendiente !== null) {
          return String(saldoPendiente);
        }
        return undefined;
      })(),
    estado_ui: props.mensualidad.estado || 'Pendiente',
    activo: props.mensualidad.activo === undefined ? true : Boolean(props.mensualidad.activo),
    fecha_pago: props.mensualidad.fecha && props.mensualidad.fecha !== 'Pendiente' ? formatearAInputDate(props.mensualidad.fecha) : ''
  };
  inicializarDocumentoEdicion();

  // Si estamos editando, guardar estado inicial
  if (editando.value && !formEdicionInicial.value) {
    formEdicionInicial.value = normalizarFormularioParaGuardar(formEdicion.value);
    if (LOG_CONFIG && LOG_CONFIG.enabled) {
      console.log('💾 [configurarFormularioDesdeProps] Guardando estado inicial:', formEdicionInicial.value);
    }
  }
}

configurarFormularioDesdeProps();

watch(() => props.mensualidad, async (nuevaMensualidad, anteriorMensualidad) => {
  if (LOG_CONFIG && LOG_CONFIG.enabled) {
    console.log('👀 [watch mensualidad] Watch disparado', {
      idNueva: nuevaMensualidad?.id || nuevaMensualidad?.id_mensualidad,
      idAnterior: anteriorMensualidad?.id || anteriorMensualidad?.id_mensualidad,
      saldoPendienteRawNuevo: nuevaMensualidad?.saldo_pendiente_raw,
      saldoPendienteRawAnterior: anteriorMensualidad?.saldo_pendiente_raw
    });
  }

  // Solo ejecutar si realmente cambió la mensualidad (nueva referencia o cambio en campos clave)
  if (!anteriorMensualidad || nuevaMensualidad?.id !== anteriorMensualidad?.id) {
    if (LOG_CONFIG && LOG_CONFIG.enabled) {
      console.log('👀 [watch mensualidad] ID cambió, configurando formulario desde props');
    }
    configurarFormularioDesdeProps();
  }

  // Recargar abonos cuando se actualiza la mensualidad
  // También verificar si cambió el saldo pendiente, estado, o monto para forzar recarga
  const cambioRelevante = anteriorMensualidad && (
    nuevaMensualidad?.saldo_pendiente_raw !== anteriorMensualidad?.saldo_pendiente_raw ||
    nuevaMensualidad?.saldo_pendiente !== anteriorMensualidad?.saldo_pendiente ||
    nuevaMensualidad?.monto_pago_raw !== anteriorMensualidad?.monto_pago_raw ||
    nuevaMensualidad?.monto_pago !== anteriorMensualidad?.monto_pago ||
    nuevaMensualidad?.estado !== anteriorMensualidad?.estado ||
    nuevaMensualidad?.estado_texto !== anteriorMensualidad?.estado_texto
  );

  if (LOG_CONFIG && LOG_CONFIG.enabled) {
    console.log('👀 [watch mensualidad] Cambio relevante detectado:', cambioRelevante);
  }

  // Si hubo un cambio relevante, actualizar el formulario
  if (cambioRelevante) {
    if (LOG_CONFIG && LOG_CONFIG.enabled) {
      console.log('👀 [watch mensualidad] Configurando formulario desde props debido a cambio relevante');
    }
    configurarFormularioDesdeProps();
  }

  const mensualidadId = obtenerIdMensualidad();
  if (mensualidadId && (!anteriorMensualidad || cambioRelevante || nuevaMensualidad?.id !== anteriorMensualidad?.id)) {
    try {
      const respAb = await mensualidadesService.listarAbonos(mensualidadId);
      // Filtrar abonos "fantasma" (sin id_abono) que el backend puede agregar cuando la mensualidad está pagada
      // Solo incluir abonos reales con id_abono
      abonos.value = mapearAbonosDelBackend(respAb.data);
    } catch {
      abonos.value = [];
    }
  }
}, { deep: true, immediate: false });

// Helper functions to reduce cognitive complexity in normalizarFormularioParaGuardar
function _normalizarSaldoPendiente(valor) {
  if (valor !== undefined && valor !== null && valor !== '') {
    return String(valor);
  }
  return undefined;
}

function _normalizarIdMetodoPago(valor) {
  if (valor !== undefined && valor !== null) {
    return Number(valor);
  }
  return undefined;
}

function _normalizarString(valor, defaultValue = '') {
  if (valor !== undefined && valor !== null) {
    return String(valor).trim();
  }
  return defaultValue;
}

// Función auxiliar para normalizar el formulario antes de guardar estado inicial
// Refactored to reduce cognitive complexity by extracting normalization helpers
function normalizarFormularioParaGuardar(form) {
  // Crear un nuevo objeto con solo los campos necesarios (evitar structuredClone que falla con objetos complejos)
  const formNormalizado = {
    id_metodo_pago: _normalizarIdMetodoPago(form.id_metodo_pago),
    valor: form.valor,
    valorSinSimbolo: _normalizarString(form.valorSinSimbolo, ''),
    numero_documento: _normalizarString(form.numero_documento, ''),
    fecha_vencimiento: _normalizarString(form.fecha_vencimiento, ''),
    saldo_pendiente: _normalizarSaldoPendiente(form.saldo_pendiente),
    estado_ui: _normalizarString(form.estado_ui, 'Pendiente'),
    activo: Boolean(form.activo),
    fecha_pago: form.fecha_pago
  };

  return formNormalizado;
}

// Watch para cuando cambia el modo de edición desde props
watch(() => props.modoEdicion, (nuevoModo) => {
  editando.value = nuevoModo;
  if (nuevoModo && !formEdicionInicial.value) {
    // Guardar estado inicial cuando se activa la edición
    formEdicionInicial.value = normalizarFormularioParaGuardar(formEdicion.value);
    if (LOG_CONFIG && LOG_CONFIG.enabled) {
      console.log('💾 [watch modoEdicion] Guardando estado inicial:', formEdicionInicial.value);
    }
  } else if (!nuevoModo) {
    formEdicionInicial.value = null;
  }
});

// Watch para cuando cambia editando internamente
watch(() => editando.value, (nuevoValor) => {
  if (nuevoValor && !formEdicionInicial.value) {
    // Guardar estado inicial cuando se activa la edición
    formEdicionInicial.value = normalizarFormularioParaGuardar(formEdicion.value);
    if (LOG_CONFIG && LOG_CONFIG.enabled) {
      console.log('💾 [watch editando] Guardando estado inicial:', formEdicionInicial.value);
    }
  } else if (!nuevoValor) {
    formEdicionInicial.value = null;
  }
});

// Permisos
const authStore = useAuthStore();
// Verificar el rol activo actual, no todos los roles del usuario
const isSuperOrAdmin = computed(() => {
  const rolActivo = authStore.activeRole;
  return rolActivo === 'SuperAdmin' || rolActivo === 'Administrador';
});
const puedeEditarMensualidad = computed(() => {
  if (isSuperOrAdmin.value) return true;
  try { return !!authStore?.hasPermission?.('editar_mensualidad'); } catch { return false; }
});
const puedeAbonar = computed(() => {
  // Solo Admin/SuperAdmin o permiso explícito pueden registrar abonos manuales
  if (isSuperOrAdmin.value) return true;
  try { return !!authStore?.hasPermission?.('abonar_mensualidad'); } catch { return false; }
});
const puedeEditarAbono = computed(() => {
  // Los abonos siempre se pueden editar si el usuario tiene permisos, independientemente del estado de la mensualidad
  if (isSuperOrAdmin.value) return true;
  try { return !!authStore?.hasPermission?.('editar_abono_mensualidad'); } catch { return false; }
});
const puedeEliminarAbono = computed(() => {
  // Los abonos siempre se pueden eliminar si el usuario tiene permisos, independientemente del estado de la mensualidad
  if (isSuperOrAdmin.value) return true;
  try { return !!authStore?.hasPermission?.('eliminar_abono_mensualidad'); } catch { return false; }
});

onMounted(async () => {
  try {
    const base = API_CONFIG.baseURL || '';
    const resp = await fetch(`${base}/api/catalogos/metodos-pago`, { headers: { 'Accept': 'application/json' } });
    if (resp.ok) {
      const json = await resp.json();
      metodosPago.value = (json.data || []).map(m => {
        const id = normalizarIdMetodoPago(m.id_metodo_pago ?? m.id);
        return { id, nombre: m.nombre || m.nombre_metodo };
      }).filter(m => m.id !== undefined && m.nombre);
    } else {
      metodosPago.value = [];
    }
  } catch {
    metodosPago.value = [];
  }
  // configurarFormularioDesdeProps(); // Moved to top

  // Cargar abonos para totales
  try {
    const mensualidadId = obtenerIdMensualidad();
    if (!mensualidadId) {
      console.warn('No se pudo obtener el ID de la mensualidad');
      abonos.value = [];
      return;
    }
    const respAb = await mensualidadesService.listarAbonos(mensualidadId);
    // Filtrar abonos "fantasma" (sin id_abono) que el backend puede agregar cuando la mensualidad está pagada
    // Solo incluir abonos reales con id_abono
    abonos.value = mapearAbonosDelBackend(respAb.data);
  } catch {
    abonos.value = [];
  }
});

// Computed/Helpers
// eslint-disable-next-line no-unused-vars
function getClaseSaldo() {
  if (props.mensualidad.estado === 'Pagado') return 'saldo-completo';

  const valorTotal = Number.parseFloat(props.mensualidad.valor.replace(/[^0-9.-]+/g, '')); // NOSONAR: S7781 - replaceAll() no acepta regex
  const saldoPendiente = props.mensualidad.saldoPendiente || valorTotal;

  if (saldoPendiente === 0) return 'saldo-completo';
  if (saldoPendiente <= valorTotal * 0.3) return 'saldo-bajo';
  if (saldoPendiente <= valorTotal * 0.7) return 'saldo-medio';
  return 'saldo-alto';
}

const calcularSaldoPendiente = () => {
  if (props.mensualidad.estado === 'Pagado') return '$0';

  const valorTotal = Number.parseFloat(props.mensualidad.valor.replace(/[^0-9.-]+/g, '')); // NOSONAR: S7781 - replaceAll() no acepta regex
  const saldoPendiente = props.mensualidad.saldoPendiente || valorTotal;

  return `$${saldoPendiente.toLocaleString('es-CO')}`;
};

// Funciones de edición
function extraerNumeroDeValor(valor) {
  if (!valor) return '';
  return valor.replace(/[^0-9.-]+/g, ''); // NOSONAR: S7781 - replaceAll() no acepta regex
}

function validarFormularioEdicion() {
  const errores = [];

  const documentoNormalizado = normalizarDocumento(formEdicion.value.numero_documento);
  formEdicion.value.numero_documento = documentoNormalizado;
  if (!documentoNormalizado || documentoNormalizado.length < MIN_DOCUMENTO || documentoNormalizado.length > MAX_DOCUMENTO) {
    errores.push(`El número de documento debe tener entre ${MIN_DOCUMENTO} y ${MAX_DOCUMENTO} dígitos`);
  }

  const monto = parseMonto(formEdicion.value.valorSinSimbolo);
  if (!Number.isFinite(monto) || monto <= 0) {
    errores.push('El valor total debe ser un número mayor a 0');
  }

  let saldoNumero;
  if (formEdicion.value.saldo_pendiente !== undefined && formEdicion.value.saldo_pendiente !== null && formEdicion.value.saldo_pendiente !== '') {
    const normalizadoSaldo = normalizarMonto(formEdicion.value.saldo_pendiente);
    formEdicion.value.saldo_pendiente = normalizadoSaldo;
    saldoNumero = parseMonto(normalizadoSaldo);

    if (!Number.isFinite(saldoNumero) || saldoNumero < 0) {
      errores.push('El saldo pendiente debe ser un número mayor o igual a 0');
    } else if (Number.isFinite(monto) && saldoNumero > monto) {
      errores.push('El saldo pendiente no puede ser mayor que el valor total');
    }
  }

  if (formEdicion.value.fecha_vencimiento && !esFechaValida(formEdicion.value.fecha_vencimiento)) {
    errores.push('La fecha de vencimiento no es válida');
  }

  return {
    errores,
    monto,
    saldo: saldoNumero
  };
}

function manejarValorSinSimbolo(event) {
  const normalizado = normalizarMonto(event?.target?.value ?? formEdicion.value.valorSinSimbolo ?? '');
  formEdicion.value.valorSinSimbolo = normalizado;
  actualizarValorConSimbolo();
}

function manejarSaldoPendiente(event) {
  const valor = event?.target?.value ?? formEdicion.value.saldo_pendiente ?? '';
  if (valor === '' || valor === null || valor === undefined) {
    formEdicion.value.saldo_pendiente = undefined;
  } else {
    const normalizado = normalizarMonto(valor);
    formEdicion.value.saldo_pendiente = normalizado;
  }
}

function formatearAInputDate(valor) {
  // acepta DD/MM/YYYY o YYYY-MM-DD → devuelve YYYY-MM-DD
  if (!valor) return '';
  if (/^\d{4}-\d{2}-\d{2}$/.test(valor)) return valor;
  if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(valor)) {
    const [d, m, y] = valor.split('/').map(x => Number.parseInt(x));
    const mm = String(m).padStart(2, '0');
    const dd = String(d).padStart(2, '0');
    return `${y}-${mm}-${dd}`;
  }
  return '';
}

// Use shared formatting utility
const formatCOP = (n) => `$${formatoCOP(Number(n) || 0)}`

function mesDesdeVencimiento() {
  const raw = props.mensualidad.fecha_vencimiento_raw || props.mensualidad.fecha_vencimiento || props.mensualidad.vencimiento;
  if (!raw) return props.mensualidad.mes || '';
  const match = String(raw).match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (match) {
    const y = Number(match[1]);
    const m = Number(match[2]);
    const date = new Date(y, m - 1, 1); // local first day of month
    return date.toLocaleDateString('es-CO', { month: 'long' }).replace(/^./, x => x.toUpperCase());
  }
  const d = new Date(raw);
  return d.toLocaleDateString('es-CO', { month: 'long' }).replace(/^./, m => m.toUpperCase());
}

function mostrarVencimiento() {
  // Prioriza valor crudo
  const raw = props.mensualidad.fecha_vencimiento_raw || props.mensualidad.fecha_vencimiento || props.mensualidad.fechaVencimiento;
  if (raw) {
    const match = String(raw).match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (match) {
      const y = match[1];
      const m = match[2];
      const d = match[3];
      return `${Number(d).toString().padStart(2, '0')}/${Number(m).toString().padStart(2, '0')}/${y}`;
    }
    try {
      const d = new Date(raw);
      if (!Number.isNaN(d)) return d.toLocaleDateString('es-CO');
    } catch {
      // ignorar formato inválido y caer al fallback
    }
    }
  return props.mensualidad.vencimiento || '—';
}

function mostrarSaldoPendiente() {
  // Usa el valor del backend si existe
  const sp = props.mensualidad.saldo_pendiente ?? props.mensualidad.saldoPendiente;
  if (sp !== undefined && sp !== null) {
    const n = Number(sp);
    if (!Number.isNaN(n)) return `$${n.toLocaleString('es-CO')}`;
  }
  // Fallback al cálculo local
  return calcularSaldoPendiente();
}

function actualizarValorConSimbolo() {
  const normalizado = normalizarMonto(formEdicion.value.valorSinSimbolo);
  formEdicion.value.valorSinSimbolo = normalizado;

  const numero = parseMonto(normalizado);
  formEdicion.value.valor = Number.isFinite(numero)
    ? `$${numero.toLocaleString('es-CO')}`
    : '';
}

async function cerrarModal() {
  // Si está editando, verificar cambios antes de cerrar
  if (editando.value) {
    const tieneCambios = verificarCambios()

    if (tieneCambios) {
      const result = await Swal.fire({
        icon: 'question',
        title: '¿Descartar cambios?',
        text: '¿Estás seguro de que deseas cerrar? Los cambios sin guardar se perderán.',
        showCancelButton: true,
        confirmButtonText: 'Sí, cerrar',
        cancelButtonText: 'Continuar editando',
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d'
      })

      if (!result.isConfirmed) {
        return
      }
    }
  }

  emit('cerrar')
}

function toggleEdicion() {
  if (!editando.value && !puedeEditarMensualidad.value) {
    Swal.fire({
      icon: 'warning',
      title: 'Acción no permitida',
      text: 'No tienes permiso para editar esta mensualidad.'
    });
    return;
  }

  // Si está editando y quiere cancelar, verificar cambios
  if (editando.value) {
    const tieneCambios = verificarCambios()

    if (tieneCambios) {
      Swal.fire({
        icon: 'question',
        title: '¿Descartar cambios?',
        text: '¿Estás seguro de que deseas cancelar? Los cambios sin guardar se perderán.',
        showCancelButton: true,
        confirmButtonText: 'Sí, descartar',
        cancelButtonText: 'Continuar editando',
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d'
      }).then((result) => {
        if (result.isConfirmed) {
          editando.value = false;
          configurarFormularioDesdeProps();
          formEdicionInicial.value = null;
        }
      });
      return;
    }
  }

  editando.value = !editando.value;

  // Si inicia edición, guardar estado inicial
  if (editando.value) {
    formEdicionInicial.value = normalizarFormularioParaGuardar(formEdicion.value);
    if (LOG_CONFIG && LOG_CONFIG.enabled) {
      console.log('💾 [toggleEdicion] Guardando estado inicial:', formEdicionInicial.value);
    }
  } else {
    configurarFormularioDesdeProps();
    formEdicionInicial.value = null;
  }
}

// Helper functions to reduce cognitive complexity in guardarCambios
async function _mostrarSinCambiosMensualidad() {
  await Swal.fire({
    icon: 'info',
    title: 'Sin cambios',
    text: 'No se han realizado modificaciones en la mensualidad. No hay nada que guardar.',
    confirmButtonText: 'Entendido',
    confirmButtonColor: '#004AAD'
  });
}

async function _mostrarErroresMensualidad(errores) {
  await Swal.fire({
    icon: 'error',
    title: 'Corrige los errores',
    html: `<p><strong>Por favor corrige los siguientes errores:</strong></p><p>${errores.join('<br>')}</p>`,
    confirmButtonText: 'Entendido',
    confirmButtonColor: '#dc3545'
  });
}

async function _confirmarActualizacionMensualidad() {
  return await Swal.fire({
    icon: 'question',
    title: '¿Actualizar mensualidad?',
    text: '¿Estás seguro de que deseas guardar los cambios en esta mensualidad?',
    showCancelButton: true,
    confirmButtonText: 'Sí, actualizar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#004AAD',
    cancelButtonColor: '#6c757d'
  });
}

function _construirPayloadActualizacion(monto, saldo, metodoPagoNormalizado, documentoActual) {
  const payloadUpdate = {
    monto_pago: monto,
    fecha_vencimiento: formEdicion.value.fecha_vencimiento || null,
    activo: formEdicion.value.activo
  };

  if (formEdicion.value.id_metodo_pago === '' || formEdicion.value.id_metodo_pago === null) {
    payloadUpdate.id_metodo_pago = null;
  } else if (metodoPagoNormalizado !== undefined) {
    payloadUpdate.id_metodo_pago = metodoPagoNormalizado;
  }

  if (documentoActual && documentoActual.length >= MIN_DOCUMENTO) {
    if (!documentoOriginal.value || documentoActual !== documentoOriginal.value) {
      payloadUpdate.numero_documento = documentoActual;
    }
  }

  // Siempre enviar el saldo_pendiente del formulario, el backend calculará el estado automáticamente
  // Si saldo es undefined, usar el valor actual de la mensualidad para mantener consistencia
  if (saldo === undefined) {
    const saldoActual = props.mensualidad.saldo_pendiente_raw ?? props.mensualidad.saldo_pendiente;
    if (saldoActual !== undefined && saldoActual !== null) {
      payloadUpdate.saldo_pendiente = Number(saldoActual);
    }
  } else {
    payloadUpdate.saldo_pendiente = saldo;
  }

  return payloadUpdate;
}

function _mapearMensualidadActualizada(mensualidadBackend, mensualidadId, monto, documentoActual, nombrePersonaActualizada, idMetodoEnRespuesta) {
  return mapearMensualidadDelBackend(mensualidadBackend, {
    valor: formatCOP(mensualidadBackend.monto_pago || monto),
    numero_documento: documentoActual,
    persona_nombre: nombrePersonaActualizada,
    nombre: nombrePersonaActualizada,
    id_metodo_pago: idMetodoEnRespuesta
  });
}

async function _mostrarExitoActualizacion() {
  Swal.close();
  await Swal.fire({
    icon: 'success',
    title: 'Cambios guardados',
    text: 'La mensualidad se actualizó correctamente.',
    timer: 1500,
    showConfirmButton: false
  });
}

// Refactored to reduce cognitive complexity by extracting helper functions
async function guardarCambios() {
  // Verificar si hay cambios antes de continuar
  const tieneCambios = verificarCambios();
  if (!tieneCambios) {
    await _mostrarSinCambiosMensualidad();
    return;
  }

  const { errores, monto, saldo } = validarFormularioEdicion();
  if (errores.length > 0) {
    await _mostrarErroresMensualidad(errores);
    return;
  }

  // Confirmar antes de actualizar
  const confirmacion = await _confirmarActualizacionMensualidad();
  if (!confirmacion.isConfirmed) {
    return;
  }

  // Mostrar loading mientras se procesa
  Swal.fire({
    title: 'Guardando cambios...',
    text: 'Por favor espera mientras procesamos tu solicitud.',
    allowOutsideClick: false,
    allowEscapeKey: false,
    didOpen: () => {
      Swal.showLoading()
    }
  })

  const metodoPagoNormalizado = normalizarIdMetodoPago(formEdicion.value.id_metodo_pago);
  const documentoActual = formEdicion.value.numero_documento;
  const payloadUpdate = _construirPayloadActualizacion(monto, saldo, metodoPagoNormalizado, documentoActual);

  const nombrePersonaActualizada = personaDocumentoEdicion.value?.nombre_completo || props.mensualidad.persona_nombre || props.mensualidad.nombre;
  const idMetodoEnRespuesta = Object.hasOwn(payloadUpdate, 'id_metodo_pago') ? payloadUpdate.id_metodo_pago : props.mensualidad.id_metodo_pago;

  documentoOriginal.value = documentoActual;
  if (nombrePersonaActualizada) {
    actualizarEstadoDocumentoEdicion('found', `${nombrePersonaActualizada} registrada en el sistema.`);
  }

  try {
    const mensualidadId = obtenerIdMensualidad();
    if (!mensualidadId) {
      throw new Error('No se pudo obtener el ID de la mensualidad');
    }

    // Llamar directamente al backend y esperar la respuesta
    const respuesta = await mensualidadesService.update(mensualidadId, payloadUpdate);
    const mensualidadBackend = respuesta?.data || respuesta;

    // Mapear los datos del backend al formato del modal
    const mensualidadActualizada = _mapearMensualidadActualizada(
      mensualidadBackend,
      mensualidadId,
      monto,
      documentoActual,
      nombrePersonaActualizada,
      idMetodoEnRespuesta
    );

    // Emitir evento con los datos del backend
    emit('guardar-cambios', mensualidadActualizada);

    // Cerrar el loading y mostrar éxito
    await _mostrarExitoActualizacion();

    // Actualizar estado inicial después de guardar exitosamente
    formEdicionInicial.value = normalizarFormularioParaGuardar(formEdicion.value);
    editando.value = false;
  } catch (error) {
    // Cerrar el loading si hay error
    Swal.close();

    // Mostrar error
    await Swal.fire({
      icon: 'error',
      title: 'Error al guardar',
      text: error?.message || 'No se pudieron guardar los cambios. Por favor, intenta nuevamente.',
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    });
  }
}

// Functions for creating abono from table
function iniciarNuevoAbono() {
  // Cancel any ongoing edit
  if (abonoEditIndex.value !== null && abonoEditIndex.value !== -1) {
    abonoEditIndex.value = null;
  }
  // Set to -1 to indicate we're creating a new abono
  abonoEditIndex.value = -1;
  // Initialize nuevoAbono with today's date as default
  nuevoAbono.value = {
    fecha: new Date().toISOString().split('T')[0],
    monto: '',
    id_metodo_pago: undefined
  };
}

function cancelarNuevoAbono() {
  abonoEditIndex.value = null;
  nuevoAbono.value = { fecha: '', monto: '', id_metodo_pago: undefined };
}

// Helper functions to reduce cognitive complexity in guardarNuevoAbonoDesdeTabla
// Tolerance for floating point comparison (to avoid precision issues)
const TOLERANCIA_COMPARACION_MONTO = 0.00001

async function _verificarPermisoAbonar() {
  if (!puedeAbonar.value) {
    await Swal.fire({
      icon: 'warning',
      title: 'Acción no permitida',
      text: 'No tienes permiso para registrar abonos.'
    });
    return false;
  }
  return true;
}

function _validarMontoAbono(monto) {
  const errores = [];
  if (!Number.isFinite(monto) || monto <= 0) {
    errores.push('El monto debe ser mayor a 0');
    return errores;
  }

  const valorTotalMensualidad = Number(props.mensualidad.monto_pago_raw ?? obtenerValorNumericoMensualidad());
  const totalPagadoActual = calcularTotalPagado();
  const totalConNuevoAbono = totalPagadoActual + monto;
  const saldoRestante = Number(saldoPendienteHistNum.value || 0);

  // Validate independently: check both total and remaining balance
  // First check: new total should not exceed the total monthly payment
  if (valorTotalMensualidad > 0 && totalConNuevoAbono > valorTotalMensualidad + TOLERANCIA_COMPARACION_MONTO) {
    errores.push(`El monto excede el valor total de la mensualidad (${formatCOP(valorTotalMensualidad)})`);
  }
  
  // Second check: abono amount should not exceed remaining balance
  if (monto > saldoRestante + TOLERANCIA_COMPARACION_MONTO) {
    errores.push(`El monto excede el saldo pendiente (${formatCOP(saldoRestante)})`);
  }

  return errores;
}

function _validarFechaAbono(fechaAbono) {
  const errores = [];
  if (!fechaAbono) {
    errores.push('La fecha del abono es requerida');
    return errores;
  }

  if (!esFechaValida(fechaAbono)) {
    errores.push('La fecha del abono no es válida');
    return errores;
  }

  // Date is valid, proceed with validation
  const fechaCreacion = props.mensualidad.created_at || props.mensualidad.creado || props.mensualidad.fecha_creacion || props.mensualidad.creada_en;
  if (!fechaCreacion) {
    // If creation date is missing, log warning but still allow (backend should validate)
    if (LOG_CONFIG && LOG_CONFIG.enabled) {
      console.warn('⚠️ No se encontró fecha de creación de la mensualidad para validar el abono');
    }
    // Don't block the abono if creation date is missing - backend should handle this
    return errores;
  }

  try {
    const fechaCreacionDate = new Date(fechaCreacion);
    const fechaAbonoDate = new Date(fechaAbono);

    // Validate dates are valid
    if (Number.isNaN(fechaCreacionDate.getTime()) || Number.isNaN(fechaAbonoDate.getTime())) {
      errores.push('Las fechas no son válidas');
      return errores;
    }

    // Normalize dates to YYYY-MM-DD format for comparison
    const fechaCreacionStr = fechaCreacionDate.toISOString().split('T')[0];
    const fechaAbonoStr = fechaAbonoDate.toISOString().split('T')[0];

    // Allow same day (>=) - only block if strictly before (<)
    if (fechaAbonoStr < fechaCreacionStr) {
      const fechaCreacionFormateada = formatearFecha(fechaCreacion);
      errores.push(`La fecha no puede ser anterior a la creación (${fechaCreacionFormateada})`);
    }
  } catch {
    errores.push('Error al validar la fecha del abono');
  }

  return errores;
}

async function _mostrarErroresAbono(errores) {
  await Swal.fire({
    icon: 'error',
    title: 'Corrige los errores',
    html: errores.join('<br>')
  });
}

// Refactored to reduce cognitive complexity by extracting helper functions
async function guardarNuevoAbonoDesdeTabla() {
  if (!(await _verificarPermisoAbonar())) {
    return;
  }

  // Normalize and validate monto
  const normalizadoMonto = normalizarMonto(nuevoAbono.value.monto ?? '');
  nuevoAbono.value.monto = normalizadoMonto;
  const monto = parseMonto(normalizadoMonto);

  const errores = [];
  errores.push(..._validarMontoAbono(monto));

  // Validate date: must not be before the creation date of the monthly payment
  const fechaAbono = nuevoAbono.value.fecha?.trim();
  errores.push(..._validarFechaAbono(fechaAbono));

  if (errores.length > 0) {
    await _mostrarErroresAbono(errores);
    return;
  }

  try {
    const metodoPagoAbono = normalizarIdMetodoPago(nuevoAbono.value.id_metodo_pago);
    const payloadAbono = {
      monto_abonado: monto,
      fecha_abono: nuevoAbono.value.fecha || undefined,
    };
    if (metodoPagoAbono !== undefined) {
      payloadAbono.id_metodo_pago = metodoPagoAbono;
    }
    const mensualidadId = obtenerIdMensualidad();
    if (!mensualidadId) {
      throw new Error('No se pudo obtener el ID de la mensualidad');
    }
    const respuestaAbono = await mensualidadesService.abonar(mensualidadId, payloadAbono);

    await Swal.fire({
      icon: 'success',
      title: 'Abono registrado',
      text: 'El abono se registró correctamente.',
      timer: 1500,
      showConfirmButton: false
    });

    // Use updated data from backend
    const mensualidadBackend = respuestaAbono?.data || props.mensualidad;
    const mensualidadActualizada = mapearMensualidadDelBackend(mensualidadBackend);

    // Emit updated data to parent
    emit('guardar-cambios', mensualidadActualizada);

    // Reload abonos immediately after registering
    try {
      const mensualidadId = obtenerIdMensualidad();
      if (mensualidadId) {
        const respAb = await mensualidadesService.listarAbonos(mensualidadId);
        abonos.value = mapearAbonosDelBackend(respAb.data);
      }
    } catch {
      // Ignore error refreshing abonos in UI
    }

    // Close the new abono row
    abonoEditIndex.value = null;
    nuevoAbono.value = { fecha: '', monto: '', id_metodo_pago: undefined };
  } catch (e) {
    await Swal.fire({
      icon: 'error',
      title: 'Error al registrar abono',
      text: e?.message || 'No pudimos registrar el abono. Intenta nuevamente.'
    });
  }
}

function iniciarEdicionAbono(index) {
  const lista = listaPagosYAbonos();
  const item = lista[index];
  // Buscar por id_abono, únicamente en abonos editables
  const original = (abonos.value || []).find(a => a.id_abono === item.id_abono);
  if (!original) return;
  abonoEditIndex.value = index;
  abonoEdit.value = {
    id_abono: original.id_abono || original.id,
    fecha: original.fecha_abono || original.fecha,
    monto: Number(original.monto) || 0,
    id_metodo_pago: original.id_metodo_pago
  };
  }

async function guardarEdicionAbono() {
  const ed = abonoEdit.value;
  if (!ed || !ed.id_abono) return;
  if (!puedeEditarAbono.value) {
    Swal.fire({
      icon: 'warning',
      title: 'Acción no permitida',
      text: 'No tienes permiso para editar abonos.'
    });
    return;
  }
  try {
    const mensualidadId = obtenerIdMensualidad();
    if (!mensualidadId) {
      throw new Error('No se pudo obtener el ID de la mensualidad');
    }
    const respuesta = await mensualidadesService.updateAbono(mensualidadId, ed.id_abono, {
      fecha_abono: ed.fecha,
      monto: Number(ed.monto),
      id_metodo_pago: ed.id_metodo_pago
    });
    const respAb = await mensualidadesService.listarAbonos(mensualidadId);
    // Filtrar abonos "fantasma" (sin id_abono) que el backend puede agregar cuando la mensualidad está pagada
    // Solo incluir abonos reales con id_abono
    abonos.value = mapearAbonosDelBackend(respAb.data);
    abonoEditIndex.value = null;

    // Actualizar la mensualidad en el componente padre si el backend devolvió la mensualidad actualizada
    // La respuesta del servicio viene directamente como respuesta.data (el servicio ya parsea el JSON)
    // El backend devuelve: { success: true, data: {...}, mensualidad: {...} }
    const mensualidadBackend = respuesta?.mensualidad || respuesta?.data?.mensualidad;
    if (mensualidadBackend) {
      const mensualidadActualizada = mapearMensualidadDelBackend(mensualidadBackend);
      emit('guardar-cambios', mensualidadActualizada);
    }
  } catch (e) {
    await Swal.fire({
      icon: 'error',
      title: 'Error al guardar abono',
      text: e?.message || 'No pudimos guardar los cambios del abono.'
    });
  }
}

async function eliminarAbono(index) {
  const lista = listaPagosYAbonos();
  const item = lista[index];
  const original = (abonos.value || []).find(a => a.id_abono === item.id_abono);
  if (!original || !original.id_abono) return;
  if (!puedeEliminarAbono.value) {
    Swal.fire({
      icon: 'warning',
      title: 'Acción no permitida',
      text: 'No tienes permiso para eliminar abonos.'
    });
    return;
  }
  const confirmar = await Swal.fire({
    icon: 'question',
    title: '¿Eliminar abono?',
    text: 'Esta acción no se puede deshacer.',
    showCancelButton: true,
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar'
  });
  if (!confirmar.isConfirmed) return;
  try {
    const mensualidadId = obtenerIdMensualidad();
    if (!mensualidadId) {
      throw new Error('No se pudo obtener el ID de la mensualidad');
    }
    const respuesta = await mensualidadesService.deleteAbono(mensualidadId, original.id_abono);
    const respAb = await mensualidadesService.listarAbonos(mensualidadId);
    // Filtrar abonos "fantasma" (sin id_abono) que el backend puede agregar cuando la mensualidad está pagada
    // Solo incluir abonos reales con id_abono
    abonos.value = mapearAbonosDelBackend(respAb.data);

    // Actualizar la mensualidad en el componente padre si el backend devolvió la mensualidad actualizada
    // La respuesta del servicio viene directamente como respuesta.data (el servicio ya parsea el JSON)
    // El backend devuelve: { success: true, mensualidad: {...} }
    const mensualidadBackend = respuesta?.mensualidad || respuesta?.data?.mensualidad;
    if (mensualidadBackend) {
      const mensualidadActualizada = mapearMensualidadDelBackend(mensualidadBackend);
      emit('guardar-cambios', mensualidadActualizada);
    }

    await Swal.fire({
      icon: 'success',
      title: 'Abono eliminado',
      text: 'El abono se eliminó correctamente.',
      timer: 1500,
      showConfirmButton: false
    });
  } catch (e) {
    await Swal.fire({
      icon: 'error',
      title: 'Error al eliminar',
      text: e?.message || 'No pudimos eliminar el abono.'
    });
  }
}

function calcularTotalPagado() {
  // Primero intentar calcular sumando los abonos actuales (más confiable después de crear/eliminar)
  if (abonos.value && abonos.value.length > 0) {
    const totalAbonos = abonos.value.reduce((total, a) => total + (Number(a.monto) || 0), 0);
    if (totalAbonos > 0) {
      return totalAbonos;
    }
  }

  // Si no hay abonos o la suma es 0, usar el cálculo basado en el saldo pendiente del backend
  const totalMensualidad = Number(props.mensualidad.monto_pago_raw ?? obtenerValorNumericoMensualidad());
  const spBackend = props.mensualidad.saldo_pendiente_raw ?? props.mensualidad.saldo_pendiente ?? props.mensualidad.saldoPendiente;
  if (!Number.isNaN(totalMensualidad) && spBackend !== undefined && spBackend !== null && spBackend !== '') {
    const n = Number(spBackend);
    if (!Number.isNaN(n)) {
      // Total pagado = Total mensualidad - Saldo pendiente
      return Math.max(0, totalMensualidad - n);
    }
  }

  // Último fallback: usar fechasPago si están disponibles
  if (!props.mensualidad.fechasPago || props.mensualidad.fechasPago.length === 0) return 0;
  return props.mensualidad.fechasPago.reduce((total, pago) => total + obtenerMontoPago(pago), 0);
}

function obtenerMontoPago(pago) {
  if (typeof pago === 'object' && pago.monto !== undefined) {
    return Number.parseFloat(pago.monto) || 0;
  }
  return 0;
}

function calcularSaldoPendienteHistorial() {
  // 1) Priorizar el valor proveniente del backend para mantener consistencia con la tarjeta
  const spBackend = props.mensualidad.saldo_pendiente_raw ?? props.mensualidad.saldo_pendiente ?? props.mensualidad.saldoPendiente;
  
  if (LOG_CONFIG && LOG_CONFIG.enabled) {
    console.log('💰 [calcularSaldoPendienteHistorial] Valores:', {
      saldo_pendiente_raw: props.mensualidad.saldo_pendiente_raw,
      saldo_pendiente: props.mensualidad.saldo_pendiente,
      saldoPendiente: props.mensualidad.saldoPendiente,
      spBackendUsado: spBackend,
      mensualidadId: obtenerIdMensualidad()
    });
  }

  if (spBackend !== undefined && spBackend !== null && spBackend !== '') {
    const n = Number(spBackend);
    if (!Number.isNaN(n)) {
      if (LOG_CONFIG && LOG_CONFIG.enabled) {
        console.log('💰 [calcularSaldoPendienteHistorial] Retornando saldo del backend:', n);
      }
      return Math.max(0, n);
    }
  }

  // 2) Fallback: calcular con (valor total - total pagado) cuando no hay saldo del backend
  const totalMensualidad = Number(props.mensualidad.monto_pago_raw ?? obtenerValorNumericoMensualidad());
  const totalPagado = calcularTotalPagado();
  const saldo = totalMensualidad - totalPagado;
  if (LOG_CONFIG && LOG_CONFIG.enabled) {
    console.log('💰 [calcularSaldoPendienteHistorial] Retornando saldo calculado:', saldo, { totalMensualidad, totalPagado });
  }
  return Math.max(0, saldo);
}


const saldoPendienteHistNum = computed(() => calcularSaldoPendienteHistorial());

function obtenerValorNumericoMensualidad() {
  if (!props.mensualidad.valor) return 0;
  return Number.parseFloat(props.mensualidad.valor.replace(/[^0-9.-]+/g, '')); // NOSONAR: S7781 - replaceAll() no acepta regex
}

function formatearFechaDDMMYYYY(fechaStr) {
  const [año, mes, dia] = fechaStr.split('-');
  return `${Number.parseInt(dia)}/${Number.parseInt(mes)}/${año}`;
}

function crearFechaObjDesdeString(fechaStr) {
  if (fechaStr.includes('-')) {
    const [año, mes, dia] = fechaStr.split('-');
    return new Date(Number.parseInt(año), Number.parseInt(mes) - 1, Number.parseInt(dia));
  }
  return new Date(fechaStr + 'T00:00:00');
}

function formatearFechaObj(fechaObj) {
  if (Number.isNaN(fechaObj.getTime())) return null;
  const dia = fechaObj.getDate();
  const mes = fechaObj.getMonth() + 1;
  const año = fechaObj.getFullYear();
  return `${dia}/${mes}/${año}`;
}

function formatearFecha(fecha) {
  if (!fecha) return '';
  try {
    if (typeof fecha === 'string' && /^\d{1,2}\/\d{1,2}\/\d{4}$/.test(fecha)) {
      return fecha;
    }
    if (typeof fecha === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
      return formatearFechaDDMMYYYY(fecha);
    }
    const fechaObj = typeof fecha === 'string'
      ? crearFechaObjDesdeString(fecha)
      : new Date(fecha);
    const fechaFormateada = formatearFechaObj(fechaObj);
    return fechaFormateada || fecha;
  } catch {
    return fecha;
  }
}

function obtenerNombreMetodoPago(idMetodo) {
  if (!idMetodo) return undefined;
  const found = (metodosPago.value || []).find(x => x.id === idMetodo);
  return found ? found.nombre : `Método ${idMetodo}`;
}

function mapearAbonoAItem(abono) {
  const metodo = obtenerNombreMetodoPago(abono.id_metodo_pago);
  const tipo = abono.es_pago_final ? 'Pago' : 'Abono';
  return {
    id_abono: abono.id_abono,
    fecha: abono.fecha_abono || abono.fecha || abono.f,
    monto: abono.monto,
    metodo,
    tipo
  };
}

function buscarAbonoInicial(abonosList, fechaCreacion) {
  // Buscar si hay un abono en la fecha de creación para mostrar su monto en el registro de creación
  // Pero siempre mostrar la fecha de creación como registro separado
  if (!fechaCreacion || abonosList.length === 0) return null;
  const fechaCreacionStr = String(fechaCreacion).slice(0, 10);
  return abonosList.find(a => String(a.fecha).slice(0, 10) === fechaCreacionStr);
}

function obtenerMetodoCreacion(abonoInicial) {
  if (abonoInicial && abonoInicial.metodo) {
    return abonoInicial.metodo;
  }
  const idm = props.mensualidad.id_metodo_pago;
  if (!idm) return 'Ninguno';
  return obtenerNombreMetodoPago(idm);
}

function agregarRegistroCreacion(items, fechaCreacion, abonoInicial) {
  if (!fechaCreacion) return;
  const metodoCreacion = obtenerMetodoCreacion(abonoInicial);
  const montoCreacion = abonoInicial ? abonoInicial.monto : undefined;
  items.push({
    id_abono: abonoInicial?.id_abono,
    fecha: fechaCreacion,
    monto: montoCreacion,
    metodo: metodoCreacion,
    tipo: 'Creación'
  });
}

function agregarAbonosNoIniciales(items, abonosList) {
  // Agregar todos los abonos, incluso si hay uno en la fecha de creación
  // La fecha de creación se muestra como registro separado, y los abonos se muestran normalmente
  if (abonosList.length === 0) return;
  for (const a of abonosList) {
    // No excluir el abono inicial, mostrarlo también como abono normal
    items.push(a);
  }
}

// NOSONAR: S3776 - Complexity reduced through helper functions extraction
function agregarFechasPagoHeredadas(items, fechasPago) {
  // No agregar fechas de pago heredadas si ya hay abonos en la lista
  // Las fechas de pago heredadas solo se usan cuando no hay abonos registrados
  if (!fechasPago || fechasPago.length === 0) return;
  // Solo agregar fechas de pago heredadas si no hay abonos reales en la lista
  const hayAbonosReales = items.some(x => x.id_abono !== undefined);
  if (hayAbonosReales) return; // Si hay abonos reales, no usar fechas heredadas

  for (const p of fechasPago) {
    const fecha = (typeof p === 'object' && p.fecha) ? p.fecha : p;
    const yaExiste = items.some(x => String(x.fecha).slice(0, 10) === String(fecha).slice(0, 10));
    if (yaExiste) continue;
    const monto = (typeof p === 'object' && p.monto !== undefined) ? p.monto : undefined;
    items.push({ id_abono: undefined, fecha, monto, metodo: undefined, tipo: 'Pago' });
  }
}

// NOSONAR: S3776 - Complexity reduced through helper functions extraction
function listaPagosYAbonos() {
  const items = [];
  const abonosList = (abonos.value || []).map(mapearAbonoAItem);
  const fechaCreacion = props.mensualidad.created_at || props.mensualidad.creado || props.mensualidad.fecha_creacion || props.mensualidad.creada_en;
  const abonoInicial = buscarAbonoInicial(abonosList, fechaCreacion);

  agregarRegistroCreacion(items, fechaCreacion, abonoInicial);
  agregarAbonosNoIniciales(items, abonosList);
  agregarFechasPagoHeredadas(items, props.mensualidad.fechasPago); // NOSONAR: S3776

  return items.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));
}

// Helper functions to reduce cognitive complexity in pagarConMercadoPago
function _obtenerDatosPagador() {
  const nombres = authStore?.user?.nombres || '';
  const apellidos = authStore?.user?.apellidos || '';
  // Extract nested ternary to reduce cognitive complexity
  let nombreCompleto = 'Cliente';
  if (nombres && apellidos) {
    nombreCompleto = `${nombres} ${apellidos}`.trim();
  } else if (nombres) {
    nombreCompleto = nombres;
  }

  return {
    nombre_pagador: nombreCompleto,
    email_pagador: authStore?.user?.email || 'sin-email@example.com',
    numero_documento: authStore?.user?.documento || undefined,
    tipo_documento: authStore?.user?.tipo_documento || undefined
  };
}

function _construirPayloadPago(datosPagador) {
  return {
    tipo_pago: 'mensualidad',
    id_mensualidad: props.mensualidad.id,
    ...datosPagador
  };
}

function _obtenerHeadersPago() {
  const token = localStorage.getItem('token') || '';
  return {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}

async function _crearPreferenciaPago(baseURL, payload, headers) {
  const url = `${baseURL}/api/mercadopago/crear-preferencia`;
  const response = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload)
  });
  return response;
}

function _parsearRespuestaPago(text) {
  try {
    return text ? JSON.parse(text) : {};
  } catch {
    return {};
  }
}

function _extraerMensajeError(json, text) {
  // Try to extract from json first using shared utility
  if (json) {
    const errorFromJson = extraerMensajeError(json)
    if (errorFromJson && errorFromJson !== 'No se pudo completar la operación. Por favor, intenta nuevamente.') {
      return errorFromJson
    }
  }
  // Fallback to text if json doesn't have error info
  if (text && typeof text === 'string') {
    return text
  }
  return 'No se pudo crear la preferencia'
}

async function _mostrarErrorPago(mensaje) {
  await Swal.fire({
    icon: 'error',
    title: 'No se pudo iniciar el pago',
    text: mensaje
  });
}

function _obtenerUrlPreferencia(json) {
  return json.init_point || json.preference_url || json.initPoint || json.url;
}

async function _manejarErrorPago(error) {
  try {
    // Extract nested ternary to reduce cognitive complexity
    let mensaje;
    if (typeof error === 'object' && error !== null && error.message) {
      mensaje = error.message;
    } else if (typeof error === 'string') {
      mensaje = error;
    } else {
      mensaje = JSON.stringify(error);
    }

    await Swal.fire({
      icon: 'error',
      title: 'Error en el pago',
      text: mensaje
    });
  } catch {
    await Swal.fire({
      icon: 'error',
      title: 'Error iniciando pago con Mercado Pago'
    });
  }
}

// Pago con Mercado Pago
// Refactored to reduce cognitive complexity by extracting helper functions
// NOSONAR: S3776 - Complexity reduced through helper functions extraction
async function pagarConMercadoPago() {
  try {
    const base = API_CONFIG.baseURL || '';
    const datosPagador = _obtenerDatosPagador();
    const payload = _construirPayloadPago(datosPagador);
    const headers = _obtenerHeadersPago();

    const resp = await _crearPreferenciaPago(base, payload, headers);
    const text = await resp.text();
    const json = _parsearRespuestaPago(text);

    if (!resp.ok || !json.success) {
      const mensaje = _extraerMensajeError(json, text);
      await _mostrarErrorPago(mensaje);
      return;
    }

    const url = _obtenerUrlPreferencia(json);
    if (!url) {
      throw new Error('Preferencia creada sin URL de inicio');
    }

    globalThis.location.href = url;
  } catch (error) {
    await _manejarErrorPago(error);
  }
}
</script>


