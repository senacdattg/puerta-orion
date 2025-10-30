<template>
  <div class="modal-overlay" @click="$emit('cerrar')">
    <div class="modal-contenido" @click.stop>
      <div class="modal-header">
        <h3>{{ editando ? 'Editar Mensualidad' : 'Detalles Completos de Mensualidad' }}</h3>
        <div class="header-actions">
          <button @click="$emit('cerrar')" class="btn-cerrar">✕</button>
        </div>
      </div>

      <div class="modal-body">
        <!-- Información del deportista -->
        <div class="seccion-principal" v-if="!editando">
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
            <!-- Tabs Edición / Abonos -->
            <div class="tabs-edicion">
              <button type="button" class="tab-btn" :class="{ active: activeTab==='editar' }" @click="activeTab='editar'">Editar</button>
              <button type="button" class="tab-btn" :class="{ active: activeTab==='abonos' }" @click="activeTab='abonos'">Abonos</button>
            </div>
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
                  <span class="detalle-valor" :class="`estado-${mensualidad.estado.toLowerCase()}`">{{ mensualidad.estado }}</span>
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
            <div class="linea-abajo" style="margin:12px 0;" v-if="false"></div>

            <!-- Sección: Datos de pago -->
            <div class="seccion-form" v-if="activeTab==='editar'">
              <h6>Datos de pago</h6>
              <p class="descripcion-seccion">Configura el método, el estado deseado y los importes.</p>
              <div class="grid-detalles" style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:start;">
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

                <div class="campo-formulario">
                  <label for="valor-edicion">
                    <i class="fas fa-dollar-sign"></i>
                    Valor Total *
                  </label>
                  <div class="input-with-symbol">
                    <span class="dollar-symbol">$</span>
                    <input id="valor-edicion" v-model="formEdicion.valorSinSimbolo" type="number" placeholder="80000"
                      class="input-edicion" required @input="actualizarValorConSimbolo" />
                  </div>
                  <small class="hint">Es el valor base de cada mensualidad.</small>
                </div>

                <div class="campo-formulario" style="grid-column:1 / -1;max-width:360px;margin:0 auto;">
                  <label for="saldo-edicion">
                    <i class="fas fa-balance-scale"></i>
                    Saldo Pendiente
                  </label>
                  <input id="saldo-edicion" v-model.number="formEdicion.saldo_pendiente" type="number" class="input-edicion" placeholder="0" />
                  <small class="hint">Si eliges “Pagado”, se guardará con saldo 0 automáticamente.</small>
                </div>
              </div>
            </div>
            <div class="linea-abajo" style="margin:12px 0;"></div>

            <!-- Sección: Fechas y estado -->
            <div class="seccion-form" v-if="activeTab==='editar'">
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
                  <label>
                    <i class="fas fa-calendar-check"></i>
                    Fecha de Pago
                  </label>
                  <input type="date" :value="formEdicion.fecha_pago" class="input-edicion" disabled />
                  <small class="hint">Se llena sola cuando el saldo llega a 0.</small>
                </div>

                <div class="campo-formulario">
                  <label>
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

            <!-- Sección: Registrar abono -->
            <div class="seccion-form seccion-abono" v-if="activeTab==='abonos'">
              <h6>Registrar abono</h6>
              <p class="descripcion-seccion">Añade un abono con su fecha para mantener el historial al día.</p>
              <div class="grid-detalles">
                <div class="campo-formulario">
                  <label for="abono-fecha">
                    <i class="fas fa-calendar-plus"></i>
                    Fecha del abono
                  </label>
                  <input id="abono-fecha" v-model="nuevoAbono.fecha" type="date" class="input-edicion" />
                </div>
                <div class="campo-formulario">
                  <label for="abono-monto">
                    <i class="fas fa-dollar-sign"></i>
                    Monto del abono
                  </label>
                  <input id="abono-monto" v-model.number="nuevoAbono.monto" type="number" class="input-edicion" placeholder="0" />
                </div>
                <div class="campo-formulario">
                  <label for="abono-metodo">
                    <i class="fas fa-money-bill-wave"></i>
                    Método de pago
                  </label>
                  <select id="abono-metodo" v-model.number="nuevoAbono.id_metodo_pago" class="select-edicion">
                    <option :value="undefined">—</option>
                    <option v-for="m in metodosPago" :key="m.id" :value="m.id">{{ m.nombre }}</option>
                  </select>
                </div>
                <div class="campo-formulario" style="align-self:end;">
                  <button type="button" class="btn btn-primary" @click="registrarAbono">Registrar Abono</button>
                </div>
              </div>
            </div>
            <div class="linea-abajo" style="margin:12px 0;" v-if="activeTab==='abonos'"></div>
          </div>
        </div>

       

        <!-- Historial de pagos -->
        <div class="seccion-historial" v-if="!editando">
          <h5>📊 Historial de Pagos</h5>
          <div class="historial-pagos-container">
            <div class="resumen-pagos">
            <div class="resumen-item">
              <span class="resumen-label">Valor Total Mensualidad</span>
              <span class="resumen-valor">{{ mensualidad.valor }}</span>
            </div>
              <div class="resumen-item">
                <span class="resumen-label">Total Pagado</span>
                <span class="resumen-valor pagado">${{ calcularTotalPagado().toLocaleString('es-CO') }}</span>
              </div>
              <div class="resumen-item">
                <span class="resumen-label">Saldo Pendiente</span>
                <span class="resumen-valor pendiente">${{ calcularSaldoPendienteHistorial().toLocaleString('es-CO') }}</span>
              </div>
              <div class="resumen-item">
                <span class="resumen-label">Estado Actual</span>
                <span class="resumen-valor estado" :class="getClaseEstado()">{{ getEstadoPago() }}</span>
              </div>
            </div>

            <div class="lista-pagos">
              <h6>Fechas de pago y abonos</h6>
              <div v-if="listaPagosYAbonos().length > 0" class="pagos-list">
                <table class="tabla-historial" style="width:100%; border-collapse:collapse;">
                  <thead>
                    <tr style="text-align:left; border-bottom:1px solid #e5e7eb;">
                      <th style="padding:8px;">Fecha</th>
                      <th style="padding:8px;">Monto</th>
                      <th style="padding:8px;">Método</th>
                      <th style="padding:8px;">Tipo</th>
                      <th style="padding:8px; text-align:right;">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in listaPagosYAbonos()" :key="index" style="border-bottom:1px solid #f3f4f6;">
                      <td style="padding:8px;">
                        <template v-if="abonoEditIndex===index">
                          <input type="date" v-model="abonoEdit.fecha" class="input-edicion" />
                        </template>
                        <template v-else>
                          {{ formatearFecha(item.fecha) }}
                        </template>
                      </td>
                      <td style="padding:8px;">
                        <template v-if="abonoEditIndex===index">
                          <input type="number" v-model.number="abonoEdit.monto" class="input-edicion" style="max-width:120px;" />
                        </template>
                        <template v-else>
                          {{ item.monto !== undefined ? `$${Number(item.monto).toLocaleString('es-CO')}` : '—' }}
                        </template>
                      </td>
                      <td style="padding:8px;">
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
                      <td style="padding:8px; color:#6b7280;">{{ item.tipo }}</td>
                      <td style="padding:8px; text-align:right;">
                        <template v-if="item.tipo==='Abono'">
                          <template v-if="abonoEditIndex===index">
                            <button class="btn btn-primary" style="margin-right:6px;" @click="guardarEdicionAbono()">Guardar</button>
                            <button class="btn btn-secondary" @click="abonoEditIndex=null">Cancelar</button>
                          </template>
                          <template v-else>
                            <button class="btn btn-secondary" style="margin-right:6px;" @click="iniciarEdicionAbono(index)">Editar</button>
                            <button class="btn btn-danger" @click="eliminarAbono(index)">Eliminar</button>
                          </template>
                        </template>
                        <template v-else>
                          —
                        </template>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-else class="sin-pagos">
                <p>No hay pagos ni abonos registrados</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <!-- Botones en modo vista -->
        <template v-if="!editando">
          <button @click="toggleEdicion" class="btn btn-edit">
            ✏️ Editar
          </button>
          <button @click="$emit('cerrar')" class="btn btn-secondary">
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
import { ref, onMounted } from 'vue';
import { API_CONFIG } from '@/config/environment';
import mensualidadesService from '@/services/mensualidadesService';

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
  }
});

// Emits
const emit = defineEmits(['cerrar', 'gestionar', 'guardar-cambios']);

// Estado reactivo
const editando = ref(props.modoEdicion);
const activeTab = ref('editar');
const metodosPago = ref([]);
const formEdicion = ref({
  id_metodo_pago: undefined,
  valor: props.mensualidad.valor || '',
  valorSinSimbolo: extraerNumeroDeValor(props.mensualidad.valor),
  fecha_vencimiento: props.mensualidad.vencimiento ? formatearAInputDate(props.mensualidad.vencimiento) : '',
  saldo_pendiente: undefined,
  estado_ui: props.mensualidad.estado || 'Pendiente',
  activo: true,
  fecha_pago: ''
});
const nuevoAbono = ref({ fecha: '', monto: undefined });
const abonos = ref([]);
const abonoEditIndex = ref(null);
const abonoEdit = ref({ fecha: '', monto: undefined, id_metodo_pago: undefined });

onMounted(async () => {
  try {
    const base = API_CONFIG.baseURL || '';
    const resp = await fetch(`${base}/api/catalogos/metodos-pago`, { headers: { 'Accept': 'application/json' } });
    if (resp.ok) {
      const json = await resp.json();
      metodosPago.value = (json.data || []).map(m => ({ id: m.id_metodo_pago || m.id, nombre: m.nombre || m.nombre_metodo }));
    } else {
      metodosPago.value = [];
    }
  } catch {
    metodosPago.value = [];
  }
  // Inicializar campos derivados del objeto mensualidad
  formEdicion.value = {
    id_metodo_pago: undefined,
    valor: props.mensualidad.valor || '',
    valorSinSimbolo: extraerNumeroDeValor(props.mensualidad.valor),
    fecha_vencimiento: props.mensualidad.vencimiento ? formatearAInputDate(props.mensualidad.vencimiento) : '',
    saldo_pendiente: props.mensualidad.saldoPendiente || undefined,
    estado_ui: props.mensualidad.estado || 'Pendiente',
    activo: props.mensualidad.activo !== undefined ? !!props.mensualidad.activo : true,
    fecha_pago: props.mensualidad.fecha && props.mensualidad.fecha !== 'Pendiente' ? formatearAInputDate(props.mensualidad.fecha) : ''
  };

  // Cargar abonos para totales
  try {
    const respAb = await mensualidadesService.listarAbonos(props.mensualidad.id);
    abonos.value = (respAb.data || []).map(a => ({ id_abono: a.id_abono, monto: Number(a.monto) || 0, fecha_abono: a.fecha_abono, id_metodo_pago: a.id_metodo_pago, es_pago_final: !!a.es_pago_final }));
  } catch {
    abonos.value = [];
  }
});

// Computed/Helpers
// eslint-disable-next-line no-unused-vars
function getClaseSaldo() {
  if (props.mensualidad.estado === 'Pagado') return 'saldo-completo';

  const valorTotal = parseFloat(props.mensualidad.valor.replace(/[^0-9.-]+/g, ''));
  const saldoPendiente = props.mensualidad.saldoPendiente || valorTotal;

  if (saldoPendiente === 0) return 'saldo-completo';
  if (saldoPendiente <= valorTotal * 0.3) return 'saldo-bajo';
  if (saldoPendiente <= valorTotal * 0.7) return 'saldo-medio';
  return 'saldo-alto';
}

const calcularSaldoPendiente = () => {
  if (props.mensualidad.estado === 'Pagado') return '$0';

  const valorTotal = parseFloat(props.mensualidad.valor.replace(/[^0-9.-]+/g, ''));
  const saldoPendiente = props.mensualidad.saldoPendiente || valorTotal;

  return `$${saldoPendiente.toLocaleString('es-CO')}`;
};

// Funciones de edición
function extraerNumeroDeValor(valor) {
  if (!valor) return '';
  return valor.replace(/[^0-9.-]+/g, '');
}

function formatearAInputDate(valor) {
  // acepta DD/MM/YYYY o YYYY-MM-DD → devuelve YYYY-MM-DD
  if (!valor) return '';
  if (/^\d{4}-\d{2}-\d{2}$/.test(valor)) return valor;
  if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(valor)) {
    const [d, m, y] = valor.split('/').map(x => parseInt(x));
    const mm = String(m).padStart(2, '0');
    const dd = String(d).padStart(2, '0');
    return `${y}-${mm}-${dd}`;
  }
  return '';
}

function formatCOP(n) {
  const num = Number(n) || 0;
  return `$${num.toLocaleString('es-CO')}`;
}

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
      if (!isNaN(d)) return d.toLocaleDateString('es-CO');
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
    if (!isNaN(n)) return `$${n.toLocaleString('es-CO')}`;
  }
  // Fallback al cálculo local
  return calcularSaldoPendiente();
}

function actualizarValorConSimbolo() {
  if (formEdicion.value.valorSinSimbolo) {
    const numero = parseFloat(formEdicion.value.valorSinSimbolo);
    if (!isNaN(numero)) {
      formEdicion.value.valor = `$${numero.toLocaleString('es-CO')}`;
    }
  } else {
    formEdicion.value.valor = '';
  }
}

function toggleEdicion() {
  editando.value = !editando.value;
  if (!editando.value) {
    // Restaurar
    formEdicion.value = {
      id_metodo_pago: undefined,
      valor: props.mensualidad.valor || '',
      valorSinSimbolo: extraerNumeroDeValor(props.mensualidad.valor),
      fecha_vencimiento: props.mensualidad.vencimiento ? formatearAInputDate(props.mensualidad.vencimiento) : '',
      saldo_pendiente: props.mensualidad.saldoPendiente || undefined,
      estado_ui: props.mensualidad.estado || 'Pendiente',
      activo: props.mensualidad.activo !== undefined ? !!props.mensualidad.activo : true,
      fecha_pago: props.mensualidad.fecha && props.mensualidad.fecha !== 'Pendiente' ? formatearAInputDate(props.mensualidad.fecha) : ''
    };
  }
}

function guardarCambios() {
  if (!formEdicion.value.valorSinSimbolo) {
    alert('Ingresa el valor total');
    return;
  }

  const payloadUpdate = {
    id_metodo_pago: formEdicion.value.id_metodo_pago,
    monto_pago: Number(formEdicion.value.valorSinSimbolo),
    fecha_vencimiento: formEdicion.value.fecha_vencimiento || null,
    activo: formEdicion.value.activo
  };

  if (formEdicion.value.estado_ui === 'Pagado') {
    payloadUpdate.saldo_pendiente = 0;
  } else if (formEdicion.value.saldo_pendiente !== undefined && formEdicion.value.saldo_pendiente !== null && formEdicion.value.saldo_pendiente !== '') {
    payloadUpdate.saldo_pendiente = Number(formEdicion.value.saldo_pendiente);
  }

  const mensualidadActualizada = {
    ...props.mensualidad,
    ...payloadUpdate,
    valor: formEdicion.value.valor
  };

  emit('guardar-cambios', mensualidadActualizada);
  editando.value = false;
}

async function registrarAbono() {
  if (!nuevoAbono.value.monto || nuevoAbono.value.monto <= 0) {
    alert('Ingresa el monto del abono');
    return;
  }
  try {
    await mensualidadesService.abonar(props.mensualidad.id, {
      monto_abonado: Number(nuevoAbono.value.monto),
      fecha_abono: nuevoAbono.value.fecha || undefined,
      id_metodo_pago: nuevoAbono.value.id_metodo_pago
    })
    alert('Abono registrado correctamente');
    // Sugerir al padre refrescar datos
    emit('guardar-cambios', { ...props.mensualidad });
    // Recargar abonos en el modal
    try {
      const respAb = await mensualidadesService.listarAbonos(props.mensualidad.id);
      abonos.value = (respAb.data || []).map(a => ({ id_abono: a.id_abono, monto: Number(a.monto) || 0, fecha_abono: a.fecha_abono, id_metodo_pago: a.id_metodo_pago, es_pago_final: !!a.es_pago_final }));
    } catch {
      // Ignorar error de refresco de abonos en UI
    }
  } catch (e) {
    alert(e?.message || 'Error registrando abono');
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
  try {
    await mensualidadesService.updateAbono(props.mensualidad.id, ed.id_abono, {
      fecha_abono: ed.fecha,
      monto: Number(ed.monto),
      id_metodo_pago: ed.id_metodo_pago
    });
    const respAb = await mensualidadesService.listarAbonos(props.mensualidad.id);
    abonos.value = (respAb.data || []).map(a => ({ monto: Number(a.monto) || 0, fecha: a.fecha_abono, id_metodo_pago: a.id_metodo_pago, es_pago_final: !!a.es_pago_final, id_abono: a.id_abono }));
    abonoEditIndex.value = null;
  } catch (e) {
    alert(e?.message || 'Error guardando abono');
  }
}

async function eliminarAbono(index) {
  const lista = listaPagosYAbonos();
  const item = lista[index];
  const original = (abonos.value || []).find(a => a.id_abono === item.id_abono);
  if (!original || !original.id_abono) return;
  if (!confirm('¿Eliminar este abono?')) return;
  try {
    await mensualidadesService.deleteAbono(props.mensualidad.id, original.id_abono);
    const respAb = await mensualidadesService.listarAbonos(props.mensualidad.id);
    abonos.value = (respAb.data || []).map(a => ({ monto: Number(a.monto) || 0, fecha: a.fecha_abono, id_metodo_pago: a.id_metodo_pago, es_pago_final: !!a.es_pago_final, id_abono: a.id_abono }));
  } catch (e) {
    alert(e?.message || 'Error eliminando abono');
  }
}

function calcularTotalPagado() {
  if (abonos.value && abonos.value.length > 0) {
    return abonos.value.reduce((total, a) => total + (a.monto || 0), 0);
  }
  if (!props.mensualidad.fechasPago || props.mensualidad.fechasPago.length === 0) return 0;
  return props.mensualidad.fechasPago.reduce((total, pago) => total + obtenerMontoPago(pago), 0);
}

function obtenerMontoPago(pago) {
  if (typeof pago === 'object' && pago.monto !== undefined) {
    return parseFloat(pago.monto) || 0;
  }
  return 0;
}

function calcularSaldoPendienteHistorial() {
  const totalMensualidad = Number(props.mensualidad.monto_pago_raw ?? obtenerValorNumericoMensualidad());
  const totalPagado = calcularTotalPagado();
  const saldo = totalMensualidad - totalPagado;
  return Math.max(0, saldo);
}

function obtenerValorNumericoMensualidad() {
  if (!props.mensualidad.valor) return 0;
  return parseFloat(props.mensualidad.valor.replace(/[^0-9.-]+/g, ''));
}

function getEstadoPago() {
  const sp = props.mensualidad.saldo_pendiente_raw;
  if (sp !== undefined && sp !== null) return Number(sp) === 0 ? 'Pagado' : 'Pendiente';
  const totalPagado = calcularTotalPagado();
  const totalMensualidad = obtenerValorNumericoMensualidad();
  if (totalPagado === 0) return 'Sin pagos';
  if (totalPagado === totalMensualidad) return 'Pagado';
  if (totalPagado < totalMensualidad) return 'Pendiente';
  return 'Pagado';
}

function getClaseEstado() {
  const totalPagado = calcularTotalPagado();
  const totalMensualidad = obtenerValorNumericoMensualidad();
  if (totalPagado === 0) return 'sin-pagos';
  if (totalPagado === totalMensualidad) return 'completo';
  if (totalPagado < totalMensualidad) return 'parcial';
  return 'pagado';
}

function formatearFecha(fecha) {
  if (!fecha) return '';
  try {
    if (typeof fecha === 'string' && /^\d{1,2}\/\d{1,2}\/\d{4}$/.test(fecha)) {
      return fecha;
    }
    if (typeof fecha === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
      const [año, mes, dia] = fecha.split('-');
      return `${parseInt(dia)}/${parseInt(mes)}/${año}`;
    }
    let fechaObj;
    if (typeof fecha === 'string') {
      if (fecha.includes('-')) {
        const [año, mes, dia] = fecha.split('-');
        fechaObj = new Date(parseInt(año), parseInt(mes) - 1, parseInt(dia));
      } else {
        fechaObj = new Date(fecha + 'T00:00:00');
      }
    } else {
      fechaObj = new Date(fecha);
    }
    if (isNaN(fechaObj.getTime())) return fecha;
    const dia = fechaObj.getDate();
    const mes = fechaObj.getMonth() + 1;
    const año = fechaObj.getFullYear();
    return `${dia}/${mes}/${año}`;
  } catch {
    return fecha;
  }
}

function listaPagosYAbonos() {
  const items = [];
  // Abonos desde backend
  if (abonos.value && abonos.value.length > 0) {
    abonos.value.forEach(a => {
      const metodo = (() => {
        const id = a.id_metodo_pago;
        if (!id) return undefined;
        const found = (metodosPago.value || []).find(x => x.id === id);
        return found ? found.nombre : `Método ${id}`;
      })();
      const tipo = a.es_pago_final ? 'Pago' : 'Abono';
      items.push({ id_abono: a.id_abono, fecha: a.fecha_abono || a.fecha || a.f, monto: a.monto, metodo, tipo });
    });
  }
  // Fechas de pago heredadas (si existen en la tarjeta)
  if (props.mensualidad.fechasPago && props.mensualidad.fechasPago.length > 0) {
    props.mensualidad.fechasPago.forEach(p => {
      const fecha = (typeof p === 'object' && p.fecha) ? p.fecha : p;
      // Evitar duplicar si ya existe un registro (abono/pago) con la misma fecha
      const yaExiste = items.some(x => String(x.fecha).slice(0, 10) === String(fecha).slice(0, 10));
      if (yaExiste) return;
      const monto = (typeof p === 'object' && p.monto !== undefined) ? p.monto : undefined;
      items.push({ id_abono: undefined, fecha, monto, metodo: undefined, tipo: 'Pago' });
    });
  }
  return items.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));
}
</script>

<style>
.btn-toggle-activo {
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid #d1d5db; /* gray-300 */
  background: #f9fafb;       /* gray-50 */
  color: #374151;            /* gray-700 */
  cursor: pointer;
  transition: all 0.15s ease-in-out;
}
.btn-toggle-activo:hover { filter: brightness(0.98); }
.btn-toggle-activo.on {
  background: #ecfdf5;       /* emerald-50 */
  border-color: #10b981;     /* emerald-500 */
  color: #059669;            /* emerald-600 */
}
.tabs-edicion {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.tab-btn {
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  color: #374151;
  border-radius: 8px;
  cursor: pointer;
}
.tab-btn.active {
  background: #eef2ff; /* indigo-50 */
  border-color: #6366f1; /* indigo-500 */
  color: #3730a3; /* indigo-800 */
}
</style>