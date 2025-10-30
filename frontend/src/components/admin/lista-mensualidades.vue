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

      <!-- Grid de mensualidades -->
      <div class="grid-mensualidades">
        <TarjetaMensualidad v-for="mensualidad in mensualidadesFiltradas" :key="mensualidad.id"
          :mensualidad="mensualidad" @ver-detalle-completo="verDetalleCompleto" @gestionar="abrirModalEnModoEdicion"
          @eliminar="eliminarMensualidad" />

        <div v-if="esAdmin" class="boton-agregar" @click="abrirFormulario">
          +
        </div>
      </div>

      <!-- Sin resultados -->
      <div v-if="mensualidadesFiltradas.length === 0" class="sin-resultados mejorado">
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
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Agregar Nueva Mensualidad</h3>
            <button class="btn-cerrar" title="Cerrar" @click="cerrarFormulario">
              <i class="fas fa-times"></i>
            </button>
          </div>

          <form @submit.prevent="guardarMensualidad" class="formulario-mensualidad" :key="formKey" autocomplete="off">
            <div class="campo-formulario">
              <label for="idPersona">
                <i class="fas fa-user"></i>
                ID Persona *
              </label>
              <input id="idPersona" v-model.number="form.id_persona" type="number" placeholder="Ej: 1" autocomplete="off"
                class="input-mensualidad" required />
            </div>

            <div class="campo-formulario">
              <label for="idMetodo">
                <i class="fas fa-money-bill-wave"></i>
                Método de Pago (opcional)
              </label>
              <select id="idMetodo" v-model.number="form.id_metodo_pago" class="select-mensualidad">
                <option :value="''">— Sin seleccionar —</option>
                <option v-for="m in metodosPago" :key="m.id" :value="m.id">{{ m.nombre }}</option>
              </select>
              <small class="hint">Déjalo vacío si no hay pago inicial.</small>
            </div>

            <div class="campo-formulario">
              <label for="monto">
                <i class="fas fa-dollar-sign"></i>
                Valor Total *
              </label>
              <div class="input-with-symbol">
                <span class="dollar-symbol">$</span>
                <input id="monto" v-model="form.valorSinSimbolo" type="number" placeholder="150000" autocomplete="off"
                  class="input-mensualidad" required @input="actualizarValorConSimbolo" />
              </div>
            </div>

            <div class="campo-formulario">
              <label for="saldoPendiente">
                <i class="fas fa-balance-scale"></i>
                Saldo Pendiente (opcional)
              </label>
              <input id="saldoPendiente" v-model.number="form.saldo_pendiente" type="number" placeholder="Ej: 0"
                class="input-mensualidad" />
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
              <button type="submit" class="btn-principal">Guardar</button>
              <button type="button" class="btn-secundario" @click="cerrarFormulario">Cancelar</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>


</template>

<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import TarjetaMensualidad from './tarjeta-mensualidad.vue';
import ModalDetalles from './modal-detalles.vue';
import { API_CONFIG } from '@/config/environment';

// Props
const props = defineProps({
  mensualidades: {
    type: Array,
    required: true,
    default: () => []
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

// Filtro de vencimiento eliminado

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
  id_persona: '',
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

function guardarCambiosMensualidad(mensualidadActualizada) {
  console.log('Guardando cambios de mensualidad:', mensualidadActualizada);

  const index = props.mensualidades.findIndex(m => m.id === mensualidadActualizada.id);
  if (index !== -1) {
    Object.assign(props.mensualidades[index], mensualidadActualizada);
  }
  emit('editar', mensualidadActualizada);
  alert('Cambios guardados exitosamente');
  modalDetalleEnEdicion.value = false;
}

// función de reporte eliminada

function eliminarMensualidad(mensualidad) {
  if (!mensualidad || !mensualidad.id) return;
  if (!confirm('¿Deseas eliminar esta mensualidad? Se desactivará en el sistema.')) return;
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
    alert('No tienes permiso para crear mensualidades');
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
    id_persona: '',
    id_metodo_pago: '',
    valorSinSimbolo: '',
    valor: '',
    vencimiento: '',
    activo: true,
    saldo_pendiente: undefined,
    estado_ui: 'Pendiente'
  };
}

function actualizarValorConSimbolo() {
  if (form.value.valorSinSimbolo) {
    const numero = parseFloat(form.value.valorSinSimbolo);
    if (!isNaN(numero)) {
      form.value.valor = `$${numero.toLocaleString('es-CO')}`;
    }
  } else {
    form.value.valor = '';
  }
}

function guardarMensualidad() {
  if (!form.value.id_persona || !form.value.valorSinSimbolo || !form.value.vencimiento) {
    alert('Completa ID Persona, Valor y Fecha de vencimiento');
    return;
  }

  const payload = {
    id_persona: Number(form.value.id_persona),
    monto_pago: Number(form.value.valorSinSimbolo),
    fecha_vencimiento: form.value.vencimiento,
    activo: !!form.value.activo,
    estado_ui: form.value.estado_ui,
    saldo_pendiente: form.value.saldo_pendiente !== undefined && form.value.saldo_pendiente !== null && form.value.saldo_pendiente !== ''
      ? Number(form.value.saldo_pendiente) : undefined
  };
  // Adjuntar id_metodo_pago solo si fue seleccionado
  if (form.value.id_metodo_pago !== '' && form.value.id_metodo_pago !== undefined && form.value.id_metodo_pago !== null) {
    payload.id_metodo_pago = Number(form.value.id_metodo_pago);
  }
  // Si marcó Pagado en la creación, forzar saldo 0 para coherencia inmediata
  if (form.value.estado_ui === 'Pagado') {
    payload.saldo_pendiente = 0;
  }
  emit('nueva', payload);
  cerrarFormulario();
}
</script>


