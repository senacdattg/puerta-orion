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
        <div id="statCard" class="stat-card stat-total">
          <span class="stat-numero">{{ mensualidadesFiltradas.length }}</span>
          <span class="stat-label">TOTAL</span>
        </div>
        <div id="statCard" class="stat-card stat-pagadas">
          <span class="stat-numero">{{ estadisticas.pagadas }}</span>
          <span class="stat-label">PAGADAS</span>
        </div>
        <div id="statCard" class="stat-card stat-pendientes">
          <span class="stat-numero">{{ estadisticas.pendientes }}</span>
          <span class="stat-label">PENDIENTES</span>
        </div>
        <div id="statCard" class="stat-card stat-vencidas">
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
          :mensualidad="mensualidad" @ver-detalle-completo="verDetalleCompleto" @gestionar="abrirModalEnModoEdicion"
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
        @cerrar="cerrarModalDetalleCompleto" @gestionar="abrirModalEnModoEdicion" 
        @guardar-cambios="guardarCambiosMensualidad" />


      <!-- Modal de formulario para nueva mensualidad -->
      <div v-if="mostrarFormulario && esAdmin" class="modal-overlay">
        <div class="modal-content mensualidades-modal form-modal" @click.stop>
          <div class="modal-header">
            <h3>Agregar Nueva Mensualidad</h3>
            <button class="btn-cerrar" title="Cerrar" @click="cerrarFormulario">
              <i class="fas fa-times"></i>
            </button>
          </div>

          <form @submit.prevent="guardarMensualidad" class="form-modal-panel" :key="formKey" autocomplete="off">
            <div class="campo-formulario">
              <label for="docPersona">
                <i class="fas fa-id-card"></i>
                Número de documento de la persona *
              </label>
              <input
                id="docPersona"
                v-model="form.numero_documento"
                type="text"
                inputmode="numeric"
                placeholder="Ej: 12345678"
                autocomplete="off"
                class="input-mensualidad"
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
              <select id="idMetodo" v-model.number="form.id_metodo_pago" class="select-mensualidad" required>
                <option :value="''">— Sin seleccionar —</option>
                <option v-for="m in metodosPago" :key="m.id" :value="m.id">{{ m.nombre }}</option>
              </select>
              <small class="hint">Selecciona el método con el que se pagará la mensualidad.</small>
            </div>

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
                  class="input-mensualidad"
                  required
                  @input="manejarMontoCampo('valorSinSimbolo', $event)"
                />
              </div>
            </div>

            <div class="campo-formulario">
              <label for="saldoPendiente">
                <i class="fas fa-balance-scale"></i>
                Saldo Pendiente (opcional)
              </label>
              <input
                id="saldoPendiente"
                v-model="form.saldo_pendiente"
                type="text"
                inputmode="decimal"
                placeholder="Ej: 0"
                class="input-mensualidad"
                @input="manejarMontoCampo('saldo_pendiente', $event)"
                required
              />
              <small class="hint">Si lo dejas vacío, será igual al valor total.</small>
            </div>

            <div class="campo-formulario">
              <label for="vencimiento">
                <i class="fas fa-clock"></i>
                Fecha de vencimiento *
              </label>
              <input id="vencimiento" v-model="form.vencimiento" type="date" class="input-mensualidad" required autocomplete="off" />
            </div>

            <div class="campo-formulario">
              <label>
                <i class="fas fa-toggle-on"></i>
                Activo
              </label>
              <button type="button"
                      class="btn-toggle-activo"
                      :class="{ on: form.activo }"
                      @click="form.activo = !form.activo">
                {{ form.activo ? 'Activo' : 'Inactivo' }}
              </button>
            </div>



            <div class="campo-formulario">
              <label>
                <i class="fas fa-info-circle"></i>
                Estado inicial
              </label>
              <div>
                <select v-model="form.estado_ui" class="select-mensualidad">
                  <option value="Pendiente">Pendiente</option>
                  <option value="Pagado">Pagado</option>
                </select>
              </div>
              <small class="hint">El estado real se calculará según el saldo pendiente.</small>
            </div>

            <div class="campo-formulario">
              <label>
                <i class="fas fa-calendar-check"></i>
                Fecha de pago
              </label>
              <input type="date" :value="''" class="input-mensualidad" disabled />
              <small class="hint">Se establecerá automáticamente cuando el saldo llegue a 0.</small>
            </div>

            <div class="acciones centrado">
              <button type="submit" class="btn btn-primary btn-lg">Guardar</button>
              <button type="button" class="btn btn-danger btn-lg" @click="cerrarFormulario">Cancelar</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>


</template>

<script setup>
import { ref, computed, nextTick } from 'vue';
import { useAuthStore } from '@/stores/auth';
import TarjetaMensualidad from './tarjeta-mensualidad.vue';
import ModalDetalles from './modal-detalles.vue';
import { API_CONFIG } from '@/config/environment';
import mensualidadesService from '@/services/mensualidadesService';
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
const emit = defineEmits(['editar', 'nueva', 'eliminar']);

// Constantes
const meses = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

const authStore = useAuthStore();
const roleNames = computed(() => (authStore.user?.roles || []).map(r => typeof r === 'string' ? r : r?.nombre_rol));
const esAdmin = computed(() => roleNames.value.includes('SuperAdmin') || roleNames.value.includes('Administrador'));

const estados = ['Pagado', 'Pendiente', 'Vencido'];

// Constantes de validación
const LOCALE_COL = 'es-CO';
const MIN_DOCUMENTO = 6;
const MAX_DOCUMENTO = 10;

function normalizarDocumento(valor = '') {
  return (valor || '')
    .toString()
    .replace(/\D/g, '')
    .slice(0, MAX_DOCUMENTO);
}

function normalizarMonto(valor = '') {
  if (!valor) return '';
  const saneado = valor
    .toString()
    .replace(/[^0-9.,]/g, '')
    .replace(/,/g, '.');

  const partes = saneado.split('.');
  if (partes.length === 1) {
    return partes[0];
  }

  const enteros = partes.shift() || '';
  const decimales = partes.join('');
  return decimales ? `${enteros}.${decimales}` : enteros;
}

function parseMonto(valor = '') {
  if (valor === '' || valor === null || valor === undefined) return NaN;
  const numero = Number(valor);
  return Number.isFinite(numero) ? numero : NaN;
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
  
  const index = props.mensualidades.findIndex(m => m.id === mensualidadActualizada.id);
  if (index !== -1) {
    Object.assign(props.mensualidades[index], mensualidadActualizada);
  }
  emit('editar', mensualidadActualizada);
  const estabaVisible = modalDetalleCompletoVisible.value;
  if (estabaVisible) {
    modalDetalleCompletoVisible.value = false;
    await nextTick();
  }
  await Swal.fire({
    icon: 'success',
    title: 'Cambios guardados',
    text: 'La mensualidad se actualizó correctamente.',
    timer: 1500,
    showConfirmButton: false
  });
  if (estabaVisible) {
    mensualidadSeleccionada.value = { ...mensualidadActualizada };
    modalDetalleCompletoVisible.value = true;
  }
  modalDetalleEnEdicion.value = false;
}

// función de reporte eliminada

async function eliminarMensualidad(mensualidad) {
  if (!mensualidad || !mensualidad.id) return;
  const confirmacion = await Swal.fire({
    icon: 'question',
    title: '¿Eliminar mensualidad?',
    text: 'Se desactivará en el sistema.',
    showCancelButton: true,
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar'
  });
  if (!confirmacion.isConfirmed) return;
  emit('eliminar', mensualidad);
}

function limpiarFiltros() {
  busqueda.value = '';
  filtroMes.value = '';
  filtroEstado.value = '';
  filtroVencimiento.value = '';
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
  mostrarFormulario.value = true;
}

function cerrarFormulario() {
  mostrarFormulario.value = false;
  limpiarFormulario();
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
  let saldoNumero = undefined;
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
  const { errores, monto, saldo } = validarFormularioMensualidad();

  if (errores.length > 0) {
    await Swal.fire({
      icon: 'error',
      title: 'Corrige los errores',
      html: errores.join('<br>')
    });
    return;
  }

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
  } else if (saldo !== undefined) {
    payload.saldo_pendiente = saldo;
  } else {
    payload.saldo_pendiente = 0;
  }

  emit('nueva', payload);
  cerrarFormulario();
}
</script>

<style scoped>
.mensaje-documento {
  display: block;
  margin-top: 6px;
  font-size: 0.85rem;
  line-height: 1.3;
}

.mensaje-documento.indicacion,
.mensaje-documento.pendiente {
  color: #6c757d;
}

.mensaje-documento.checking {
  color: #0d6efd;
}

.mensaje-documento.found {
  color: #198754;
  font-weight: 600;
}

.mensaje-documento.warning {
  color: #ffc107;
  font-weight: 600;
}

.mensaje-documento.not-found,
.mensaje-documento.invalid,
.mensaje-documento.error {
  color: #dc3545;
}
</style>
