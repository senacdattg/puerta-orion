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
            <select v-model="filtroVencimiento" class="filtro-select">
              <option value="">Todos los vencimientos</option>
              <option v-for="(label, value) in filtrosVencimiento" :key="value" :value="value">{{ label }}</option>
            </select>
          </div>
        </div>
      </div>


      <!-- Estadísticas -->
      <div class="estadisticas">
        <div class="stat-card">
          <span class="stat-numero">{{ mensualidadesFiltradas.length }}</span>
          <span class="stat-label">Total</span>
        </div>
        <div class="stat-card">
          <span class="stat-numero">{{ estadisticas.pagadas }}</span>
          <span class="stat-label">Pagadas</span>
        </div>
        <div class="stat-card">
          <span class="stat-numero">{{ estadisticas.pendientes }}</span>
          <span class="stat-label">Pendientes</span>
        </div>
        <div class="stat-card">
          <span class="stat-numero">{{ estadisticas.vencidas }}</span>
          <span class="stat-label">Vencidas</span>
        </div>
      </div>

      <!-- Controles de acción -->
      <div class="controles-accion">
        <button @click="emit('nueva')" class="btn btn-primary btn-lg">
          ➕ Nueva Mensualidad
        </button>
        <button @click="exportarDatos" class="btn btn-secondary btn-lg">
          📊 Exportar
        </button>
        <button @click="enviarRecordatorios" class="btn btn-warning btn-lg">
          📧 Recordatorios
        </button>
      </div>

      <!-- Grid de mensualidades -->
      <div class="grid-mensualidades">
        <TarjetaMensualidad v-for="mensualidad in mensualidadesFiltradas" :key="mensualidad.id"
          :mensualidad="mensualidad" @ver-detalle-completo="verDetalleCompleto" @gestionar="emit('editar', $event)"
          @reporte="generarReporte" />
      </div>

      <!-- Sin resultados -->
      <div v-if="mensualidadesFiltradas.length === 0" class="sin-resultados">
        <p>No se encontraron mensualidades con los filtros aplicados</p>
        <button @click="limpiarFiltros" class="btn btn-primary">
          Limpiar filtros
        </button>
      </div>

      <!-- Modal de Detalles Completos -->
      <ModalDetalles v-if="modalDetalleCompletoVisible" :mensualidad="mensualidadSeleccionada"
        @cerrar="cerrarModalDetalleCompleto" @gestionar="emit('editar', $event)" @reporte="generarReporte" />
    </div>
  </div>

</template>

<script setup>
import { ref, computed } from 'vue';
import TarjetaMensualidad from './tarjeta-mensualidad.vue';
import ModalDetalles from './modal-detalles.vue';

// Props
const props = defineProps({
  mensualidades: {
    type: Array,
    required: true,
    default: () => []
  }
});

// Emits
const emit = defineEmits(['editar', 'nueva']);

// Constantes
const meses = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

const estados = ['Pagado', 'Pendiente', 'Vencido'];

const filtrosVencimiento = {
  proximo: 'Próximo a vencer',
  vencido: 'Vencido',
  normal: 'Normal'
};

// Estado reactivo
const busqueda = ref('');
const filtroMes = ref('');
const filtroEstado = ref('');
const filtroVencimiento = ref('');
const modalDetalleCompletoVisible = ref(false);
const mensualidadSeleccionada = ref({});

// Computed properties
const mensualidadesFiltradas = computed(() => {
  return props.mensualidades.filter(mensualidad => {
    const cumpleBusqueda = !busqueda.value ||
      mensualidad.nombre.toLowerCase().includes(busqueda.value.toLowerCase()) ||
      mensualidad.mes.toLowerCase().includes(busqueda.value.toLowerCase());

    const cumpleMes = !filtroMes.value || mensualidad.mes === filtroMes.value;
    const cumpleEstado = !filtroEstado.value || mensualidad.estado === filtroEstado.value;
    const cumpleVencimiento = !filtroVencimiento.value ||
      getCumpleVencimiento(mensualidad, filtroVencimiento.value);

    return cumpleBusqueda && cumpleMes && cumpleEstado && cumpleVencimiento;
  });
});

const estadisticas = computed(() => ({
  pagadas: props.mensualidades.filter(m => m.estado === 'Pagado').length,
  pendientes: props.mensualidades.filter(m => m.estado === 'Pendiente').length,
  vencidas: props.mensualidades.filter(m => m.estado === 'Vencido').length
}));

// Funciones
function getCumpleVencimiento(mensualidad, filtro) {
  if (!mensualidad.vencimiento) return false;

  const hoy = new Date();
  const vencimiento = new Date(mensualidad.vencimiento);
  const diffDays = Math.ceil((vencimiento - hoy) / (1000 * 60 * 60 * 24));

  switch (filtro) {
    case 'proximo': return diffDays <= 7 && diffDays > 0;
    case 'vencido': return diffDays < 0;
    case 'normal': return diffDays > 7;
    default: return true;
  }
}

function verDetalleCompleto(mensualidad) {
  mensualidadSeleccionada.value = mensualidad;
  modalDetalleCompletoVisible.value = true;
}

function cerrarModalDetalleCompleto() {
  modalDetalleCompletoVisible.value = false;
  mensualidadSeleccionada.value = {};
}

function generarReporte(mensualidad) {
  console.log('Generando reporte para:', mensualidad);
  // Implementar lógica de reportes
}

function exportarDatos() {
  console.log('Exportando datos...');
  // Implementar exportación
}

function enviarRecordatorios() {
  console.log('Enviando recordatorios...');
  // Implementar envío de recordatorios
}

function limpiarFiltros() {
  busqueda.value = '';
  filtroMes.value = '';
  filtroEstado.value = '';
  filtroVencimiento.value = '';
}
</script>
