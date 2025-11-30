<template>
  <div class="lista-mensualidades">

    <div class="seccion-contenido grande">
      <div class="bloque-subtitulo">
        <span class="subtitulo-bloque">Categorías de busqueda</span>



        <!-- Filtros y búsqueda -->
        <div class="contenedor-filtros">
          <div class="buscador">
            <input type="search" v-model="busqueda" placeholder="Buscar mensualidades..." class="entrada-busqueda" />
            <span class="icono-busqueda">🔍</span>
          </div>

          <div class="filtros">
            <select v-model="filtroMes" class="filtro-select">
              <option value="">Todos los meses</option>
              <option v-for="mes in meses" :key="mes" :value="mes">{{ mes }}</option>
            </select>
            <select v-model="filtroEstado" class="filtro-select">
              <option value="">Todos los estados</option>
              <option v-for="estado in estados" :key="estado" :value="estado">{{ estado }}</option>
            </select>
          </div>
        </div>
      </div>


      <!-- Estadísticas -->
      <div class="estadisticas ordenadas">
        <div id="statCard-total" class="stat-card stat-total">
          <span class="stat-numero">{{ mensualidadesFiltradas.length }}</span>
          <span class="stat-label">TOTAL</span>
        </div>
        <div id="statCard-pagadas" class="stat-card stat-pagadas">
          <span class="stat-numero">{{ estadisticas.pagadas }}</span>
          <span class="stat-label">PAGADAS</span>
        </div>
        <div id="statCard-pendientes" class="stat-card stat-pendientes">
          <span class="stat-numero">{{ estadisticas.pendientes }}</span>
          <span class="stat-label">PENDIENTES</span>
        </div>
        <div id="statCard-vencidas" class="stat-card stat-vencidas">
          <span class="stat-numero">{{ estadisticas.vencidas }}</span>
          <span class="stat-label">VENCIDAS</span>
        </div>
      </div>

      <div class="linea-abajo"></div>

      <!-- Estado de carga -->
      <div v-if="props.loading" class="loading-state" style="text-align: center; padding: 40px;">
        <div class="spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #004AAD; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto;"></div>
        <p style="margin-top: 15px; color: #64748b;">Cargando mensualidades...</p>
      </div>

      <!-- Estado de error -->
      <div v-else-if="props.error" class="error-state" style="text-align: center; padding: 40px; background: #fee; border-radius: 8px; border: 1px solid #fcc; margin: 20px 0;">
        <div style="color: #dc3545; font-size: 48px; margin-bottom: 15px;">⚠️</div>
        <h4 style="color: #dc3545; margin-bottom: 10px;">Error al cargar mensualidades</h4>
        <p style="color: #856404;">{{ props.error }}</p>
        <button @click="$emit('recargar')" class="btn btn-primary" style="margin-top: 15px;">Intentar de nuevo</button>
      </div>

      <!-- Grid de mensualidades -->
      <div v-else class="grid-mensualidades">
        <TarjetaMensualidad v-for="mensualidad in mensualidadesFiltradas" :key="mensualidad.id"
          :mensualidad="mensualidad" @ver-detalle-completo="verDetalleCompleto"
          @eliminar="eliminarMensualidad" />

        <div v-if="esAdmin" class="boton-agregar" @click="abrirFormulario">
          +
        </div>
      </div>

      <!-- Sin resultados -->
      <div v-if="!props.loading && !props.error && mensualidadesFiltradas.length === 0" class="sin-resultados mejorado">
        <div class="empty-card">
          <div class="empty-icon">🗂️</div>
          <h4 class="empty-title">No se encontraron mensualidades</h4>
          <p class="empty-sub">Prueba limpiar los filtros o crea una nueva mensualidad.</p>
          <div class="empty-actions">
            <button @click="limpiarFiltros" class="btn btn-primary">Limpiar filtros</button>
            <button v-if="esAdmin" @click="abrirFormulario" class="btn btn-secondary">Nueva mensualidad</button>
          </div>
        </div>
      </div>

      <br>



      <!-- Modal de Detalles Completos -->
      <ModalDetalles v-if="modalDetalleCompletoVisible" :mensualidad="mensualidadSeleccionada"
        :modo-edicion="modalDetalleEnEdicion"
        :mostrar="modalDetalleCompletoVisible"
        @cerrar="cerrarModalDetalleCompleto" @gestionar="abrirModalEnModoEdicion"
        @guardar-cambios="guardarCambiosMensualidad" />


      <!-- Modal de formulario para nueva mensualidad -->
      <div v-if="mostrarFormulario && esAdmin" class="modal-overlay">
        <div class="modal-content mensualidades-modal modal-sm" @click.stop>
          <div class="modal-header">
            <h2 class="modal-title">
              <i class="fas fa-plus-circle"></i>
              Agregar Nueva Mensualidad
            </h2>
            <button class="btn-cerrar" title="Cerrar" @click="cerrarFormulario">
              <i class="fas fa-times"></i>
            </button>
          </div>

          <div class="modal-body">
          <form id="form-nueva-mensualidad" @submit.prevent="guardarMensualidad" class="form-modal-panel" :key="formKey" autocomplete="off">
            <!-- Sección: Información básica -->
            <div class="seccion-form">
              <h6>Información básica</h6>
              <p class="descripcion-seccion">Identifica al deportista y configura el método de pago.</p>
              <div class="grid-detalles">
                <div class="campo-formulario">
                  <label for="docPersona">
                    <i class="fas fa-id-card"></i>
                    Documento *
                  </label>
                  <input
                    id="docPersona"
                    v-model="form.numero_documento"
                    type="text"
                    inputmode="numeric"
                    placeholder="Ej: 12345678"
                    autocomplete="off"
                    class="input-edicion"
                    required
                    @input="manejarDocumento"
                    @blur="verificarDocumento"
                  />
                  <small
                    v-if="estadoDocumento.mensaje"
                    :class="['mensaje-documento', estadoDocumento.status]"
                  >
                    {{ estadoDocumento.mensaje }}
                  </small>
                </div>

                <div class="campo-formulario">
                  <label for="idMetodo">
                    <i class="fas fa-money-bill-wave"></i>
                    Método de Pago *
                  </label>
                  <select id="idMetodo" v-model.number="form.id_metodo_pago" class="select-edicion" required>
                    <option disabled value="">Selecciona un método</option>
                    <option v-for="m in metodosPago" :key="m.id" :value="m.id">{{ m.nombre }}</option>
                  </select>
                  <small class="hint">Usa el método por defecto de esta mensualidad.</small>
                </div>
              </div>
            </div>
            <div class="linea-abajo" style="margin:12px 0;"></div>

            <!-- Sección: Montos y estado -->
            <div class="seccion-form">
              <h6>Montos y estado</h6>
              <p class="descripcion-seccion">Configura el método, el estado deseado y los importes.</p>
              <div class="grid-detalles">
                <div class="campo-formulario">
                  <label for="estado-inicial">
                    <i class="fas fa-info-circle"></i>
                    Estado (visual)
                  </label>
                  <select id="estado-inicial" v-model="form.estado_ui" class="select-edicion">
                    <option value="Pendiente">Pendiente</option>
                    <option value="Pagado">Pagado</option>
                  </select>
                  <small class="hint">El estado real lo fija el saldo pendiente (0 = Pagado).</small>
                </div>
              </div>
              <div class="grid-detalles" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;align-items:start;margin-top:16px;">
                <div class="campo-formulario">
                  <label for="monto">
                    <i class="fas fa-dollar-sign"></i>
                    Valor Total *
                  </label>
                  <div class="input-with-symbol">
                    <span class="dollar-symbol">$</span>
                    <input
                      id="monto"
                      v-model="form.valorSinSimbolo"
                      type="text"
                      inputmode="decimal"
                      placeholder="150000"
                      autocomplete="off"
                      class="input-edicion"
                      required
                      @input="manejarMontoCampo('valorSinSimbolo', $event)"
                    />
                  </div>
                  <small class="hint">Es el valor base de cada mensualidad.</small>
                </div>
                <div class="campo-formulario">
                  <label for="saldoPendiente">
                    <i class="fas fa-balance-scale"></i>
                    Saldo Pendiente
                  </label>
                  <input
                    id="saldoPendiente"
                    v-model="form.saldo_pendiente"
                    type="text"
                    inputmode="decimal"
                    placeholder="0"
                    class="input-edicion"
                    @input="manejarMontoCampo('saldo_pendiente', $event)"
                  />
                  <small class="hint">Si eliges "Pagado", se guardará con saldo 0 automáticamente.</small>
                </div>
              </div>
            </div>
            <div class="linea-abajo" style="margin:12px 0;"></div>

            <!-- Sección: Fechas y vigencia -->
            <div class="seccion-form">
              <h6>Fechas y vigencia</h6>
              <p class="descripcion-seccion">Controla vigencia y confirma cuándo quedó pago.</p>
              <div class="grid-detalles">
                <div class="campo-formulario">
                  <label for="vencimiento">
                    <i class="fas fa-clock"></i>
                    Fecha de Vencimiento
                  </label>
                  <input id="vencimiento" v-model="form.vencimiento" type="date" class="input-edicion" required autocomplete="off" />
                </div>

                <div class="campo-formulario">
                  <label for="fecha-pago">
                    <i class="fas fa-calendar-check"></i>
                    Fecha de Pago
                  </label>
                  <input id="fecha-pago" type="date" :value="''" class="input-edicion" disabled />
                  <small class="hint">Se llena sola cuando el saldo llega a 0.</small>
                </div>

                <div class="campo-formulario">
                  <label for="activo-toggle" class="label-text">
                    <i class="fas fa-toggle-on"></i>
                    Activo
                  </label>
                  <button type="button"
                          id="activo-toggle"
                          class="btn-toggle-activo"
                          :class="{ on: form.activo }"
                          :aria-label="form.activo ? 'Desactivar mensualidad' : 'Activar mensualidad'"
                          @click="form.activo = !form.activo">
                    {{ form.activo ? 'Activo' : 'Inactivo' }}
                  </button>
                  <small class="hint">Click para activar/desactivar.</small>
                </div>
              </div>
            </div>

          </form>
          </div>

          <div class="modal-footer">
            <button type="submit" form="form-nueva-mensualidad" class="btn btn-primary">Guardar</button>
            <button type="button" class="btn btn-secondary" @click="cerrarFormulario">Cancelar</button>
          </div>
        </div>
      </div>
    </div>
  </div>


</template>

<script setup>
import { ref, computed, watch } from 'vue';
import mensualidadesService from '@/services/mensualidadesService';
import { useAuthStore } from '@/stores/auth';
import TarjetaMensualidad from './tarjeta-mensualidad.vue';
import { useModalScrollLock } from '@/composables/useModalScrollLock';
import ModalDetalles from './modal-detalles.vue';
import { API_CONFIG } from '@/config/environment';
import Swal from 'sweetalert2';

// Props
const props = defineProps({
  mensualidades: {
    type: Array,
    required: true,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  }
});

// Emits
const emit = defineEmits(['editar', 'nueva', 'eliminar', 'recargar']);

// Constantes
const meses = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

const authStore = useAuthStore();
// Verificar el rol activo actual, no todos los roles del usuario
const esAdmin = computed(() => {
  const rolActivo = authStore.activeRole;
  return rolActivo === 'SuperAdmin' || rolActivo === 'Administrador';
});

const estados = ['Pagado', 'Pendiente', 'Vencido'];

// Constantes de validación
const MIN_DOCUMENTO = 6;
const MAX_DOCUMENTO = 10;

function normalizarDocumento(valor = '') {
  return (valor || '')
    .toString()
    .replace(/\D/g, '').slice(0, MAX_DOCUMENTO); // NOSONAR: S7781 - replaceAll() no acepta regex
}

function normalizarMonto(valor = '') {
  if (!valor) return '';
  const saneado = valor
    .toString()
    .replace(/[^0-9.,]/g, '').replaceAll(',', '.'); // NOSONAR: S7781 - replaceAll() no acepta regex para el primer replace

  const partes = saneado.split('.');
  if (partes.length === 1) {
    return partes[0];
  }

  const enteros = partes.shift() || '';
  const decimales = partes.join('');
  return decimales ? `${enteros}.${decimales}` : enteros;
}

function parseMonto(valor = '') {
  if (valor === '' || valor === null || valor === undefined) return Number.NaN;
  const numero = Number(valor);
  return Number.isFinite(numero) ? numero : Number.NaN;
}

function esFechaValida(fecha) {
  return !!fecha && !Number.isNaN(Date.parse(fecha));
}

function actualizarEstadoDocumento(status, mensaje) {
  estadoDocumento.value = { status, mensaje };
}

function resetEstadoDocumento() {
  personaEncontrada.value = null;
  personaRolValido.value = false;
  estadoDocumento.value = { status: 'idle', mensaje: '' };
  documentoConsultando = null;
}

// Estado reactivo
const busqueda = ref('');
const filtroMes = ref('');
const filtroEstado = ref('');
// filtroVencimiento eliminado
const modalDetalleCompletoVisible = ref(false);
const mensualidadSeleccionada = ref({});
const modalDetalleEnEdicion = ref(false);

// Estado del formulario
const mostrarFormulario = ref(false);
const esperandoCierreFormulario = ref(false);

// Bloquear scroll del body cuando el modal de crear está abierto
// El modal de detalles maneja su propio bloqueo de scroll
useModalScrollLock(computed(() => mostrarFormulario.value));

// Watch para cerrar el formulario cuando las mensualidades se actualicen después de crear una nueva
watch(() => props.mensualidades, (nuevasMensualidades) => {
  // Si estamos esperando cerrar el formulario y las mensualidades cambiaron
  if (esperandoCierreFormulario.value && mostrarFormulario.value) {
    // Verificar que realmente hay nuevas mensualidades (no solo un cambio vacío)
    if (nuevasMensualidades && nuevasMensualidades.length > 0) {
      // Esperar un momento para que el mensaje de éxito del padre se muestre primero
      setTimeout(() => {
        cerrarFormularioForzado();
        esperandoCierreFormulario.value = false;
      }, 100);
    }
  }
}, { deep: true });

const formKey = ref(0);
const form = ref({
  numero_documento: '',
  id_metodo_pago: '',
  valorSinSimbolo: '',
  valor: '',
  vencimiento: '',
  activo: true,
  saldo_pendiente: undefined,
  estado_ui: 'Pendiente'
});
// Guardar estado inicial para comparar cambios
const formInicial = ref(null);

const metodosPago = ref([]);
const cargandoMetodosPago = ref(false);
const personaEncontrada = ref(null);
const personaRolValido = ref(false);
const estadoDocumento = ref({ status: 'idle', mensaje: '' });
let documentoConsultando = null;

// Computed properties
const mensualidadesFiltradas = computed(() => {
  return props.mensualidades.filter(mensualidad => {
    const cumpleBusqueda = !busqueda.value ||
      mensualidad.nombre.toLowerCase().includes(busqueda.value.toLowerCase()) ||
      mensualidad.mes.toLowerCase().includes(busqueda.value.toLowerCase());

    const cumpleMes = !filtroMes.value || mensualidad.mes === filtroMes.value;
    const cumpleEstado = !filtroEstado.value || mensualidad.estado === filtroEstado.value;
    return cumpleBusqueda && cumpleMes && cumpleEstado;
  });
});

const estadisticas = computed(() => ({
  pagadas: mensualidadesFiltradas.value.filter(m => m.estado === 'Pagado').length,
  pendientes: mensualidadesFiltradas.value.filter(m => m.estado === 'Pendiente').length,
  vencidas: mensualidadesFiltradas.value.filter(m => m.estado === 'Vencido').length
}));

// Filtro de vencimiento eliminado

function verDetalleCompleto(mensualidad) {
  mensualidadSeleccionada.value = mensualidad;
  modalDetalleCompletoVisible.value = true;
}

function cerrarModalDetalleCompleto() {
  modalDetalleCompletoVisible.value = false;
  mensualidadSeleccionada.value = {};
  modalDetalleEnEdicion.value = false;
}

function abrirModalEnModoEdicion(mensualidad) {
  console.log('Abriendo modal en modo edición para:', mensualidad);
  mensualidadSeleccionada.value = mensualidad;
  modalDetalleEnEdicion.value = true;
  modalDetalleCompletoVisible.value = true;
}

async function guardarCambiosMensualidad(mensualidadActualizada) {
  console.log('Guardando cambios de mensualidad:', mensualidadActualizada);

    // El array de mensualidades se actualizará en el componente padre a través del emit 'editar'
    // Por ahora, solo actualizamos mensualidadSeleccionada para el modal

    // Verificar si la mensualidad actualizada corresponde a la seleccionada usando múltiples criterios
    const idActualizada = mensualidadActualizada.id || mensualidadActualizada.id_mensualidad;
    const idSeleccionada = mensualidadSeleccionada.value?.id || mensualidadSeleccionada.value?.id_mensualidad;

    console.log('🔄 [guardarCambiosMensualidad] Comparando IDs:', {
      idActualizada,
      idSeleccionada,
      modalAbierto: modalDetalleCompletoVisible.value,
      saldoPendienteRaw: mensualidadActualizada.saldo_pendiente_raw,
      saldoPendiente: mensualidadActualizada.saldo_pendiente
    });

    // Actualizar la mensualidad seleccionada en el modal si el modal está abierto
    // Comparar IDs de forma más flexible
    const idsCoinciden = (
      idActualizada === idSeleccionada ||
      (idActualizada && idSeleccionada && String(idActualizada) === String(idSeleccionada)) ||
      (!mensualidadSeleccionada.value?.id && !mensualidadSeleccionada.value?.id_mensualidad)
    );

    if (modalDetalleCompletoVisible.value && idsCoinciden) {
      // Create a completely new object with all updated fields from backend
      // This forces Vue reactivity and triggers the watch in the modal
      // Using structuredClone for deep cloning (modern replacement for JSON.parse/stringify)
      let mensualidadActualizadaClon;
      try {
        mensualidadActualizadaClon = structuredClone(mensualidadActualizada);
      } catch {
        // Fallback to JSON method if structuredClone fails (e.g., with circular references)
        mensualidadActualizadaClon = JSON.parse(JSON.stringify(mensualidadActualizada));
      }
      console.log('✅ [guardarCambiosMensualidad] Actualizando mensualidad seleccionada con saldo_pendiente_raw:', mensualidadActualizadaClon.saldo_pendiente_raw);
      mensualidadSeleccionada.value = mensualidadActualizadaClon;
  } else {
    console.warn('⚠️ [guardarCambiosMensualidad] No se actualizó mensualidad seleccionada', {
      idActualizada,
      idSeleccionada,
      modalAbierto: modalDetalleCompletoVisible.value,
      idsCoinciden
    });
  }

  // Emitir al padre para actualizar la lista de mensualidades
  emit('editar', mensualidadActualizada);

  // Si estábamos editando, cerrar el modo edición del modal (el modal ya mostró el mensaje de éxito)
  if (modalDetalleEnEdicion.value) {
    modalDetalleEnEdicion.value = false;
  }
  // El modal se actualizará automáticamente porque mensualidadSeleccionada cambió
}

// función de reporte eliminada

async function eliminarMensualidad(mensualidad) {
  if (!mensualidad || !mensualidad.id) return;

  const estaActiva = mensualidad.activo !== false;
  const accion = estaActiva ? 'desactivar' : 'activar';
  const titulo = estaActiva ? '¿Desactivar mensualidad?' : '¿Activar mensualidad?';
  const texto = estaActiva
    ? 'La mensualidad se desactivará en el sistema.'
    : 'La mensualidad se activará en el sistema.';

  const confirmacion = await Swal.fire({
    icon: 'question',
    title: titulo,
    text: texto,
    showCancelButton: true,
    confirmButtonText: `Sí, ${accion}`,
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#004AAD',
    cancelButtonColor: '#6c757d'
  });

  if (!confirmacion.isConfirmed) return;
  emit('eliminar', mensualidad);
}

function limpiarFiltros() {
  busqueda.value = '';
  filtroMes.value = '';
  filtroEstado.value = '';
}

// Funciones del formulario
async function abrirFormulario() {
  if (!esAdmin.value) {
    await Swal.fire({
      icon: 'warning',
      title: 'Acción no permitida',
      text: 'No tienes permiso para crear mensualidades.'
    });
    return;
  }
  limpiarFormulario();
  try {
    cargandoMetodosPago.value = true;
    const base = API_CONFIG.baseURL || '';
    const resp = await fetch(`${base}/api/catalogos/metodos-pago`, { headers: { 'Accept': 'application/json' } });
    if (resp.ok) {
      const json = await resp.json();
      const lista = (json.data || []).map(m => ({ id: m.id_metodo_pago || m.id, nombre: m.nombre || m.nombre_metodo }));
      metodosPago.value = lista.filter(x => x.id && x.nombre);
    } else {
      const alt = await fetch(`${base}/api/metodos-pago`, { headers: { 'Accept': 'application/json' } });
      if (alt.ok) {
        const json = await alt.json();
        const lista = (json.data || json || []).map(m => ({ id: m.id_metodo_pago || m.id, nombre: m.nombre || m.nombre_metodo }));
        metodosPago.value = lista.filter(x => x.id && x.nombre);
      } else {
        metodosPago.value = [];
      }
    }
  } catch (e) {
    console.error('Error cargando métodos de pago', e);
    metodosPago.value = [];
  } finally {
    cargandoMetodosPago.value = false;
  }
  formKey.value++;
  // Seleccionar por defecto 'Ninguno' si existe
  const ninguno = (metodosPago.value || []).find(x => String(x.nombre).toLowerCase() === 'ninguno');
  if (ninguno) {
    form.value.id_metodo_pago = ninguno.id;
  }
  // Guardar estado inicial cuando se abre el formulario
  // Using structuredClone for deep cloning (modern replacement for JSON.parse/stringify)
  try {
    formInicial.value = structuredClone(form.value);
  } catch {
    // Fallback to JSON method if structuredClone fails (e.g., with Vue reactive objects)
    formInicial.value = JSON.parse(JSON.stringify(form.value));
  }
  mostrarFormulario.value = true;
}

// Función para normalizar valores para comparación
function normalizarValorParaComparacion(valor) {
  if (valor === null || valor === undefined) {
    return ''
  }
  if (typeof valor === 'string') {
    return valor.trim()
  }
  if (typeof valor === 'number') {
    return valor
  }
  if (typeof valor === 'boolean') {
    return valor
  }
  return valor
}

// Verificar si hay cambios
function verificarCambios() {
  if (!formInicial.value) {
    return false
  }

  const campos = [
    'numero_documento', 'id_metodo_pago', 'valorSinSimbolo', 'vencimiento',
    'activo', 'saldo_pendiente', 'estado_ui'
  ]

  for (const campo of campos) {
    const valorInicial = normalizarValorParaComparacion(formInicial.value[campo])
    const valorActual = normalizarValorParaComparacion(form.value[campo])
    if (valorInicial !== valorActual) {
      return true
    }
  }

  return false
}

// Extraer mensaje de error de manera legible
function extraerMensajeError(error) {
  if (!error) {
    return 'No se pudo completar la creación. Por favor, intenta nuevamente.'
  }

  if (typeof error === 'string') {
    return error
  }

  if (error.message) {
    return error.message
  }

  if (error.error) {
    return typeof error.error === 'string' ? error.error : JSON.stringify(error.error)
  }

  if (error.details) {
    return typeof error.details === 'string' ? error.details : JSON.stringify(error.details)
  }

  if (typeof error === 'object') {
    try {
      const errorStr = JSON.stringify(error)
      if (errorStr.length > 200) {
        return 'Error al procesar la solicitud. Verifica que todos los datos sean correctos.'
      }
      return errorStr
    } catch {
      return 'Error desconocido. Por favor, intenta nuevamente.'
    }
  }

  return 'Error desconocido. Por favor, intenta nuevamente.'
}

function cerrarFormularioForzado() {
  mostrarFormulario.value = false;
  limpiarFormulario();
  formInicial.value = null;
}

async function cerrarFormulario() {
  // Verificar si hay cambios sin guardar
  const tieneCambios = verificarCambios()

  if (tieneCambios) {
    const result = await Swal.fire({
      icon: 'question',
      title: '¿Descartar cambios?',
      text: '¿Estás seguro de que deseas cerrar? Los datos ingresados se perderán.',
      showCancelButton: true,
      confirmButtonText: 'Sí, cerrar',
      cancelButtonText: 'Continuar',
      confirmButtonColor: '#dc3545',
      cancelButtonColor: '#6c757d'
    })

    if (!result.isConfirmed) {
      return
    }
  }

  mostrarFormulario.value = false;
  limpiarFormulario();
  formInicial.value = null;
}

function limpiarFormulario() {
  form.value = {
    numero_documento: '',
    id_metodo_pago: '',
    valorSinSimbolo: '',
    valor: '',
    vencimiento: '',
    activo: true,
    saldo_pendiente: undefined,
    estado_ui: 'Pendiente'
  };
  resetEstadoDocumento();
}

function manejarDocumento(event) {
  form.value.numero_documento = normalizarDocumento(event?.target?.value ?? form.value.numero_documento ?? '');
  personaEncontrada.value = null;
  personaRolValido.value = false;
  documentoConsultando = null;

  if (!form.value.numero_documento) {
    resetEstadoDocumento();
    return;
  }

  if (form.value.numero_documento.length < MIN_DOCUMENTO) {
    actualizarEstadoDocumento('indicacion', `Ingresa al menos ${MIN_DOCUMENTO} dígitos para buscar.`);
    return;
  }

  actualizarEstadoDocumento('pendiente', 'Documento listo. Sal del campo para verificar.');
}

function manejarMontoCampo(campo, event) {
  const normalizado = normalizarMonto(event?.target?.value ?? form.value[campo] ?? '');
  form.value[campo] = normalizado;
  if (campo === 'valorSinSimbolo') {
    actualizarValorConSimbolo();
  }
}

async function verificarDocumento() {
  const documento = form.value.numero_documento;

  if (!documento) {
    resetEstadoDocumento();
    return;
  }

  if (documento.length < MIN_DOCUMENTO) {
    actualizarEstadoDocumento('indicacion', `Ingresa al menos ${MIN_DOCUMENTO} dígitos para buscar.`);
    return;
  }

  const documentoEnProceso = documento;
  documentoConsultando = documentoEnProceso;
  personaEncontrada.value = null;
  actualizarEstadoDocumento('checking', 'Buscando persona...');

  try {
    const respuesta = await mensualidadesService.buscarPersonaPorDocumento(documentoEnProceso);

    if (documentoConsultando !== documentoEnProceso) {
      return;
    }

    if (!respuesta?.success) {
      const mensaje = respuesta?.error || 'No fue posible verificar el documento.';
      actualizarEstadoDocumento('error', mensaje);
      personaRolValido.value = false;
      return;
    }

    if (respuesta.encontrado) {
      personaEncontrada.value = respuesta.data;
      personaRolValido.value = !!respuesta.data?.rol_deportista;
      const nombre = respuesta.data?.nombre_completo || 'Persona encontrada';
      if (!personaRolValido.value) {
        actualizarEstadoDocumento('error', `${nombre} no tiene el rol de Deportista.`);
      } else if (respuesta.data?.estado === false) {
        actualizarEstadoDocumento('warning', `${nombre} está inactiva. Verifica antes de continuar.`);
      } else {
        actualizarEstadoDocumento('found', `${nombre} registrada en el sistema.`);
      }
    } else {
      const mensaje = respuesta?.message || 'No encontramos una persona con ese documento.';
      personaRolValido.value = false;
      actualizarEstadoDocumento('not-found', mensaje);
    }
  } catch (error) {
    if (documentoConsultando !== documentoEnProceso) {
      return;
    }
    const mensaje = error?.message || 'Error al buscar el documento.';
    personaRolValido.value = false;
    actualizarEstadoDocumento('error', mensaje);
  } finally {
    if (documentoConsultando === documentoEnProceso) {
      documentoConsultando = null;
    }
  }
}

function actualizarValorConSimbolo() {
  const normalizado = normalizarMonto(form.value.valorSinSimbolo);
  form.value.valorSinSimbolo = normalizado;

  const numero = parseMonto(normalizado);
  form.value.valor = Number.isFinite(numero)
    ? `$${numero.toLocaleString('es-CO')}`
    : '';
}

function validarFormularioMensualidad() {
  const errores = [];

  const documento = form.value.numero_documento;
  if (!documento || documento.length < MIN_DOCUMENTO || documento.length > MAX_DOCUMENTO) {
    errores.push(`El número de documento debe tener entre ${MIN_DOCUMENTO} y ${MAX_DOCUMENTO} dígitos`);
  }

  if (!form.value.id_metodo_pago) {
    errores.push('Debes seleccionar un método de pago');
  }

  if (form.value.estado_ui === 'Pagado') {
    form.value.saldo_pendiente = '0';
  }

  const monto = parseMonto(form.value.valorSinSimbolo);
  if (!Number.isFinite(monto) || monto <= 0) {
    errores.push('El valor total debe ser un número mayor a 0');
  }

  let saldo = form.value.saldo_pendiente;
  let saldoNumero;
  if (saldo === undefined || saldo === null || String(saldo).trim() === '') {
    errores.push('Debes especificar el saldo pendiente');
  } else {
    saldo = normalizarMonto(saldo);
    form.value.saldo_pendiente = saldo;
    saldoNumero = parseMonto(saldo);
    if (!Number.isFinite(saldoNumero) || saldoNumero < 0) {
      errores.push('El saldo pendiente debe ser un número mayor o igual a 0');
    } else if (Number.isFinite(monto) && saldoNumero > monto) {
      errores.push('El saldo pendiente no puede ser mayor que el valor total');
    }
  }

  if (!form.value.vencimiento) {
    errores.push('La fecha de vencimiento es obligatoria');
  } else if (!esFechaValida(form.value.vencimiento)) {
    errores.push('La fecha de vencimiento no es válida');
  }

  if (!personaRolValido.value) {
    errores.push('Selecciona un deportista válido para crear la mensualidad');
  }

  return {
    errores,
    monto,
    saldo: saldoNumero
  };
}

async function guardarMensualidad() {
  // Verificar si hay cambios antes de continuar
  const tieneCambios = verificarCambios()

  if (!tieneCambios) {
    await Swal.fire({
      icon: 'info',
      title: 'Sin cambios',
      text: 'No se han ingresado datos en el formulario. No hay nada que guardar.',
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#004AAD'
    })
    return
  }

  const { errores, monto, saldo } = validarFormularioMensualidad();

  if (errores.length > 0) {
    await Swal.fire({
      icon: 'error',
      title: 'Corrige los errores',
      html: `<p><strong>Por favor corrige los siguientes errores:</strong></p><p>${errores.join('<br>')}</p>`,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    });
    return;
  }

  // Confirmación antes de crear
  const confirmacion = await Swal.fire({
    icon: 'question',
    title: '¿Crear mensualidad?',
    text: '¿Estás seguro de que deseas crear esta mensualidad?',
    showCancelButton: true,
    confirmButtonText: 'Sí, crear',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#004AAD',
    cancelButtonColor: '#6c757d'
  });

  if (!confirmacion.isConfirmed) {
    return;
  }

  // Mostrar loading mientras se procesa
  Swal.fire({
    title: 'Creando mensualidad...',
    text: 'Por favor espera mientras procesamos tu solicitud.',
    allowOutsideClick: false,
    allowEscapeKey: false,
    didOpen: () => {
      Swal.showLoading()
    }
  })

  const payload = {
    numero_documento: form.value.numero_documento,
    id_metodo_pago: Number(form.value.id_metodo_pago),
    monto_pago: monto,
    fecha_vencimiento: form.value.vencimiento,
    activo: !!form.value.activo,
    estado_ui: form.value.estado_ui
  };

  const metodo = Number(form.value.id_metodo_pago);
  if (!Number.isNaN(metodo)) {
    payload.id_metodo_pago = metodo;
  }

  if (form.value.estado_ui === 'Pagado') {
    payload.saldo_pendiente = 0;
  } else if (saldo === undefined) {
    // Mantener saldo actual si no se especifica
  } else {
    payload.saldo_pendiente = saldo;
    payload.saldo_pendiente = 0;
  }

  try {
    // Cerrar el loading antes de emitir
    Swal.close();

    // Marcar que estamos esperando el cierre del formulario
    esperandoCierreFormulario.value = true;

    // Emitir evento - el padre manejará el éxito/error
    emit('nueva', payload);

    // El formulario se cerrará cuando el padre recargue las mensualidades
    // El watch detectará el cambio y cerrará el formulario
  } catch (error) {
    esperandoCierreFormulario.value = false;
    // Cerrar el loading si aún está abierto
    Swal.close()

    const mensajeError = extraerMensajeError(error)
    await Swal.fire({
      icon: 'error',
      title: 'Error al crear mensualidad',
      html: `<p><strong>No se pudo crear la mensualidad.</strong></p><p>${mensajeError}</p>`,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    });
  }
}
</script>
