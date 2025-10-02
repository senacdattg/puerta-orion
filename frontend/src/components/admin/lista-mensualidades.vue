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

      <div class="linea-abajo"></div>

      <!-- Grid de mensualidades -->
      <div class="grid-mensualidades">
        <TarjetaMensualidad v-for="mensualidad in mensualidadesFiltradas" :key="mensualidad.id"
          :mensualidad="mensualidad" @ver-detalle-completo="verDetalleCompleto" @gestionar="gestionarMensualidad"
          @reporte="generarReporte" />
          
        <div v-if="esAdmin" class="boton-agregar" @click="abrirFormulario">
          +
        </div>
      </div>

      <!-- Sin resultados -->
      <div v-if="mensualidadesFiltradas.length === 0" class="sin-resultados">
        <p>No se encontraron mensualidades con los filtros aplicados</p>
        <button @click="limpiarFiltros" class="btn btn-primary">
          Limpiar filtros
        </button>
      </div>

      <br>



      <!-- Modal de Detalles Completos -->
      <ModalDetalles v-if="modalDetalleCompletoVisible" :mensualidad="mensualidadSeleccionada"
        :modo-edicion="modalDetalleEnEdicion"
        @cerrar="cerrarModalDetalleCompleto" @gestionar="abrirModalEnModoEdicion" 
        @reporte="generarReporte" @guardar-cambios="guardarCambiosMensualidad" />


      <!-- Modal de formulario para nueva mensualidad -->
      <div v-if="mostrarFormulario" class="modal-overlay">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Agregar Nueva Mensualidad</h3>
            <button class="btn-cerrar" title="Cerrar" @click="cerrarFormulario">
              <i class="fas fa-times"></i>
            </button>
          </div>

          <form @submit.prevent="guardarMensualidad" class="formulario-mensualidad">
            <div class="campo-formulario">
              <label for="nombre">
                <i class="fas fa-user"></i>
                Nombre del socio *
              </label>
              <input id="nombre" v-model="form.nombre" type="text" placeholder="Ej: Juan Pérez"
                class="input-mensualidad" required />
            </div>

            <div class="campo-formulario">
              <label for="mes">
                <i class="fas fa-calendar"></i>
                Mes *
              </label>
              <select id="mes" v-model="form.mes" class="select-mensualidad" required>
                <option disabled value="">Selecciona el mes</option>
                <option v-for="mes in meses" :key="mes" :value="mes">{{ mes }}</option>
              </select>
            </div>

            <div class="campo-formulario">
              <label for="año">
                <i class="fas fa-calendar-alt"></i>
                Año *
              </label>
              <input id="año" v-model="form.año" type="number" :min="new Date().getFullYear()"
                :max="new Date().getFullYear() + 1" placeholder="2024" class="input-mensualidad" required />
            </div>

            <div class="campo-formulario">
              <label for="monto">
                <i class="fas fa-dollar-sign"></i>
                Valor Total *
              </label>
              <div class="input-with-symbol">
                <span class="dollar-symbol">$</span>
                <input id="monto" v-model="form.valorSinSimbolo" type="number" placeholder="150000"
                  class="input-mensualidad" required @input="actualizarValorConSimbolo" />
              </div>
            </div>

            <div class="campo-formulario">
              <label for="vencimiento">
                <i class="fas fa-clock"></i>
                Fecha de vencimiento *
              </label>
              <input id="vencimiento" v-model="form.vencimiento" type="date" class="input-mensualidad" required />
            </div>

            <div class="campo-formulario">
              <label for="estado">
                <i class="fas fa-info-circle"></i>
                Estado *
              </label>
              <select id="estado" v-model="form.estado" class="select-mensualidad" required>
                <option disabled value="">Selecciona el estado</option>
                <option v-for="estado in estados" :key="estado" :value="estado">{{ estado }}</option>
              </select>
            </div>

            <div class="campo-formulario">
              <label for="fechas-pago-nuevo">
                <i class="fas fa-calendar"></i>
                Fechas de Pago
              </label>
              <div class="fechas-pago-container">
                <div v-for="(fecha, index) in form.fechasPago" :key="index" class="fecha-pago-item">
                  <input v-model="form.fechasPago[index]" type="date" class="input-fecha" />
                  <button type="button" @click="eliminarFechaPagoNuevo(index)" class="btn-eliminar-fecha">×</button>
                </div>
                <button type="button" @click="agregarFechaPagoNuevo" class="btn-agregar-fecha">
                  + Agregar fecha de pago
                </button>
              </div>
            </div>

            <div class="campo-formulario">
              <label for="observaciones">
                <i class="fas fa-comment"></i>
                Observaciones
              </label>
              <textarea id="observaciones" v-model="form.observaciones" placeholder="Observaciones adicionales..."
                class="input-mensualidad"></textarea>
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
const emit = defineEmits(['editar', 'nueva', 'eliminar']);

// Constantes
const meses = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

const esAdmin = true;

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
const modalDetalleEnEdicion = ref(false);

// Estado del formulario
const mostrarFormulario = ref(false);
const form = ref({
  nombre: '',
  mes: '',
  año: new Date().getFullYear(),
  valorSinSimbolo: '',
  valor: '',
  vencimiento: '',
  estado: '',
  fechasPago: [],
  observaciones: ''
});


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
  pagadas: mensualidadesFiltradas.value.filter(m => m.estado === 'Pagado').length,
  pendientes: mensualidadesFiltradas.value.filter(m => m.estado === 'Pendiente').length,
  vencidas: mensualidadesFiltradas.value.filter(m => m.estado === 'Vencido').length
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
  modalDetalleEnEdicion.value = false;
}

function abrirModalEnModoEdicion(mensualidad) {
  console.log('Abriendo modal en modo edición para:', mensualidad);
  modalDetalleEnEdicion.value = true;
}

function guardarCambiosMensualidad(mensualidadActualizada) {
  console.log('Guardando cambios de mensualidad:', mensualidadActualizada);
  
  // Actualizar la mensualidad en el array local para reflejar cambios inmediatamente
  const index = props.mensualidades.findIndex(m => m.id === mensualidadActualizada.id);
  if (index !== -1) {
    // Actualizar el objeto en el array
    Object.assign(props.mensualidades[index], mensualidadActualizada);
  }
  
  // Emitir evento para que el componente padre actualice los datos persistentemente
  emit('editar', mensualidadActualizada);
  
  // Mostrar mensaje de éxito
  alert('Cambios guardados exitosamente');
  
  // Salir del modo edición
  modalDetalleEnEdicion.value = false;
}


function generarReporte(mensualidad) {
  console.log('Generando reporte para:', mensualidad);
  
  // Crear datos del reporte
  const reporteData = {
    deportista: mensualidad.nombre,
    mes: mensualidad.mes,
    valor: mensualidad.valor,
    estado: mensualidad.estado,
    fecha: mensualidad.fecha,
    vencimiento: mensualidad.vencimiento,
    saldoPendiente: mensualidad.saldoPendiente || 0,
    fechaReporte: new Date().toLocaleDateString('es-CO')
  };

  // Generar y descargar reporte en formato JSON
  const dataStr = JSON.stringify(reporteData, null, 2);
  const dataBlob = new Blob([dataStr], {type: 'application/json'});
  const url = URL.createObjectURL(dataBlob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = `reporte-${mensualidad.nombre.replace(/\s+/g, '-')}-${mensualidad.mes}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
  
  // Mostrar confirmación
  alert(`Reporte generado para ${mensualidad.nombre}`);
}

function gestionarMensualidad(mensualidad) {
  console.log('Abriendo modal de detalles en modo edición para:', mensualidad);
  
  // Guardar la mensualidad seleccionada
  mensualidadSeleccionada.value = mensualidad;
  
  // Abrir el modal de detalles en modo edición
  modalDetalleEnEdicion.value = true;
  modalDetalleCompletoVisible.value = true;
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

// Funciones del formulario
function abrirFormulario() {
  limpiarFormulario();
  mostrarFormulario.value = true;
}

function cerrarFormulario() {
  mostrarFormulario.value = false;
  limpiarFormulario();
}

function limpiarFormulario() {
  form.value = {
    nombre: '',
    mes: '',
    año: new Date().getFullYear(),
    valorSinSimbolo: '',
    valor: '',
    vencimiento: '',
    estado: '',
    fechasPago: [],
    observaciones: ''
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

function agregarFechaPagoNuevo() {
  form.value.fechasPago.push('');
}

function eliminarFechaPagoNuevo(index) {
  form.value.fechasPago.splice(index, 1);
}

function guardarMensualidad() {
  // Validar formulario
  if (!form.value.nombre || !form.value.mes || !form.value.año ||
    !form.value.valor || !form.value.vencimiento || !form.value.estado) {
    alert('Por favor, completa todos los campos obligatorios');
    return;
  }

  // Determinar fecha principal basada en fechas de pago
  let fechaPrincipal = 'Pendiente';
  if (form.value.fechasPago && form.value.fechasPago.length > 0) {
    const fechasValidas = form.value.fechasPago.filter(fecha => fecha);
    if (fechasValidas.length > 0) {
      fechaPrincipal = fechasValidas[fechasValidas.length - 1]; // Última fecha de pago
    }
  }

  // Crear objeto de mensualidad con la estructura esperada
  const nuevaMensualidad = {
    id: Date.now(), // ID temporal, en producción debería venir del backend
    nombre: form.value.nombre,
    mes: form.value.mes,
    valor: form.value.valor,
    estado: form.value.estado,
    fecha: fechaPrincipal,
    fechasPago: form.value.fechasPago.filter(fecha => fecha), // Solo fechas válidas
    vencimiento: new Date(form.value.vencimiento).toLocaleDateString('es-CO'),
    avatar: null,
    // Campos adicionales para compatibilidad
    año: form.value.año,
    observaciones: form.value.observaciones || '',
    fechaCreacion: new Date().toISOString().split('T')[0]
  };

  console.log('Emitiendo nueva mensualidad:', nuevaMensualidad);

  // Emitir evento al componente padre
  emit('nueva', nuevaMensualidad);

  // Cerrar formulario
  cerrarFormulario();

  // Mostrar mensaje de éxito
  alert('Mensualidad agregada exitosamente');
}
</script>
