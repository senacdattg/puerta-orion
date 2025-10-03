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
        <div class="seccion-principal">
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
              <span class="detalle-valor">{{ mensualidad.mes }}</span>
            </div>
            <div class="detalle-item">
              <span class="detalle-label">Valor Total</span>
              <span class="detalle-valor precio">{{ mensualidad.valor }}</span>
            </div>
            <div class="detalle-item">
              <span class="detalle-label">Fecha</span>
              <span class="detalle-valor">{{ mensualidad.fecha }}</span>
            </div>
            <div v-if="mensualidad.vencimiento" class="detalle-item" style="grid-column: 1 / 4;">
              <span class="detalle-label">Vencimiento</span>
              <span class="detalle-valor vencimiento">{{ mensualidad.vencimiento }}</span>
            </div>
          </div>

          <!-- Modo edición -->
          <div v-else class="formulario-edicion">
            <div class="campo-formulario">
              <label for="estado-edicion">
                <i class="fas fa-info-circle"></i>
                Estado *
              </label>
              <select id="estado-edicion" v-model="formEdicion.estado" class="select-edicion" required>
                <option value="Pagado">Pagado</option>
                <option value="Pendiente">Pendiente</option>
                <option value="Vencido">Vencido</option>
              </select>
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
            </div>

            <div class="campo-formulario">
              <label for="fechas-pago">
                <i class="fas fa-calendar"></i>
                Fechas de Pago
              </label>
              <div class="fechas-pago-container">
                <div v-for="(pago, index) in formEdicion.fechasPago" :key="index" class="fecha-pago-item">
                  <input v-model="pago.fecha" type="date" class="input-fecha" placeholder="Fecha" />
                  <div class="input-with-symbol">
                    <span class="dollar-symbol">$</span>
                    <input v-model="pago.monto" type="number" class="input-edicion" placeholder="Monto" />
                  </div>
                  <button type="button" @click="eliminarFechaPago(index)" class="btn-eliminar-fecha">×</button>
                </div>
                <button type="button" @click="agregarFechaPago" class="btn-agregar-fecha">
                  + Agregar fecha de pago
                </button>
              </div>
            </div>

            <div class="campo-formulario">
              <label for="vencimiento-edicion">
                <i class="fas fa-clock"></i>
                Fecha de Vencimiento
              </label>
              <input id="vencimiento-edicion" v-model="formEdicion.vencimiento" type="text" placeholder="DD/MM/AAAA"
                class="input-edicion" />
            </div>

            <div class="campo-formulario">
              <label for="observaciones-edicion">
                <i class="fas fa-comment"></i>
                Observaciones
              </label>
              <textarea id="observaciones-edicion" v-model="formEdicion.observaciones" 
                placeholder="Observaciones adicionales..." class="input-edicion"></textarea>
            </div>

            <!-- Acciones rápidas -->
            <div class="acciones-rapidas">
              <h6>Acciones Rápidas</h6>
              <div class="botones-rapidos">
                <button type="button" @click="marcarComoPagado" class="btn-rapido btn-pagado">
                  ✓ Marcar como Pagado
                </button>
                <button type="button" @click="marcarComoPendiente" class="btn-rapido btn-pendiente">
                  ⏳ Marcar como Pendiente
                </button>
                <button type="button" @click="marcarComoVencido" class="btn-rapido btn-vencido">
                  ⚠️ Marcar como Vencido
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Resumen financiero -->
        <div class="seccion-financiera">
          <h5>💰 Resumen Financiero</h5>
          <div class="resumen-grid">
            <div class="resumen-item">
              <span class="resumen-label">Valor Total</span>
              <span class="resumen-valor">{{ mensualidad.valor }}</span>
            </div>
            <div class="resumen-item">
              <span class="resumen-label">Saldo Pendiente</span>
              <span class="resumen-valor saldo" :class="getClaseSaldo()">
                {{ calcularSaldoPendiente() }}
              </span>
            </div>
          </div>
        </div>

        <!-- Historial de pagos -->
        <div class="seccion-historial">
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
              <h6>Fechas de Pago</h6>
              <div v-if="mensualidad.fechasPago && mensualidad.fechasPago.length > 0" class="pagos-list">
                <div v-for="(pago, index) in mensualidad.fechasPago" :key="index" class="pago-item">
                  <span class="fecha-pago">{{ formatearFecha(pago.fecha || pago) }}</span>
                  <span class="monto-pago">${{ obtenerMontoPago(pago).toLocaleString('es-CO') }}</span>
                </div>
              </div>
              <div v-else class="sin-pagos">
                <p>No hay fechas de pago registradas</p>
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
          <button @click="$emit('reporte', mensualidad)" class="btn btn-reporte">
            📊 Reporte
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
import { computed, ref } from 'vue';
import HistorialPagos from './historial-pagos.vue';

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
const emit = defineEmits(['cerrar', 'gestionar', 'reporte', 'guardar-cambios']);

// Estado reactivo
const editando = ref(props.modoEdicion);
const formEdicion = ref({
  estado: props.mensualidad.estado || '',
  valor: props.mensualidad.valor || '',
  valorSinSimbolo: extraerNumeroDeValor(props.mensualidad.valor),
  fechasPago: convertirFechasPagoAObjetos(props.mensualidad.fechasPago || (props.mensualidad.fecha && props.mensualidad.fecha !== 'Pendiente' ? [props.mensualidad.fecha] : [])),
  vencimiento: props.mensualidad.vencimiento || '',
  observaciones: props.mensualidad.observaciones || ''
});

// Computed properties
const getClaseSaldo = () => {
  if (props.mensualidad.estado === 'Pagado') return 'saldo-completo';

  const valorTotal = parseFloat(props.mensualidad.valor.replace(/[^0-9.-]+/g, ''));
  const saldoPendiente = props.mensualidad.saldoPendiente || valorTotal;

  if (saldoPendiente === 0) return 'saldo-completo';
  if (saldoPendiente <= valorTotal * 0.3) return 'saldo-bajo';
  if (saldoPendiente <= valorTotal * 0.7) return 'saldo-medio';
  return 'saldo-alto';
};

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

function convertirFechasPagoAObjetos(fechasPago) {
  if (!fechasPago || !Array.isArray(fechasPago)) return [];
  
  return fechasPago.map(fecha => {
    // Si ya es un objeto con fecha y monto, devolverlo tal como está
    if (typeof fecha === 'object' && fecha.fecha !== undefined) {
      return {
        fecha: fecha.fecha,
        monto: fecha.monto || ''
      };
    }
    // Si es solo una fecha string, convertir a objeto con monto vacío
    return {
      fecha: fecha,
      monto: ''
    };
  });
}

function convertirObjetosAFechasPago(objetosPago) {
  if (!objetosPago || !Array.isArray(objetosPago)) return [];
  
  return objetosPago.map(pago => {
    if (typeof pago === 'object' && pago.fecha) {
      return {
        fecha: pago.fecha,
        monto: parseFloat(pago.monto) || 0
      };
    }
    return pago;
  });
}

function obtenerMontoPago(pago) {
  if (typeof pago === 'object' && pago.monto !== undefined) {
    return parseFloat(pago.monto) || 0;
  }
  // Si es solo una fecha string, no hay monto especificado
  return 0;
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

function agregarFechaPago() {
  formEdicion.value.fechasPago.push({
    fecha: '',
    monto: ''
  });
}

function eliminarFechaPago(index) {
  formEdicion.value.fechasPago.splice(index, 1);
}

function toggleEdicion() {
  editando.value = !editando.value;
  if (!editando.value) {
    // Si se cancela la edición, restaurar valores originales
    formEdicion.value = {
      estado: props.mensualidad.estado || '',
      valor: props.mensualidad.valor || '',
      valorSinSimbolo: extraerNumeroDeValor(props.mensualidad.valor),
      fechasPago: convertirFechasPagoAObjetos(props.mensualidad.fechasPago || (props.mensualidad.fecha && props.mensualidad.fecha !== 'Pendiente' ? [props.mensualidad.fecha] : [])),
      vencimiento: props.mensualidad.vencimiento || '',
      observaciones: props.mensualidad.observaciones || ''
    };
  }
}

function guardarCambios() {
  // Validar formulario
  if (!formEdicion.value.estado || !formEdicion.value.valor) {
    alert('Por favor, completa todos los campos obligatorios');
    return;
  }

  // Determinar fecha principal basada en fechas de pago
  let fechaPrincipal = 'Pendiente';
  if (formEdicion.value.fechasPago && formEdicion.value.fechasPago.length > 0) {
    const fechasValidas = formEdicion.value.fechasPago.filter(pago => pago.fecha);
    if (fechasValidas.length > 0) {
      fechaPrincipal = fechasValidas[fechasValidas.length - 1].fecha; // Última fecha de pago
    }
  }

  // Crear objeto con los cambios
  const mensualidadActualizada = {
    ...props.mensualidad,
    estado: formEdicion.value.estado,
    valor: formEdicion.value.valor,
    fecha: fechaPrincipal,
    fechasPago: convertirObjetosAFechasPago(formEdicion.value.fechasPago.filter(pago => pago.fecha)), // Solo fechas válidas
    vencimiento: formEdicion.value.vencimiento,
    observaciones: formEdicion.value.observaciones
  };

  // Emitir evento con los cambios
  emit('guardar-cambios', mensualidadActualizada);
  
  // Salir del modo edición
  editando.value = false;
}

function marcarComoPagado() {
  formEdicion.value.estado = 'Pagado';
  // Si marca como pagado y no hay fechas, agregar fecha actual
  if (!formEdicion.value.fechasPago || formEdicion.value.fechasPago.length === 0) {
    formEdicion.value.fechasPago = [{
      fecha: new Date().toISOString().split('T')[0],
      monto: ''
    }];
  }
}

function marcarComoPendiente() {
  formEdicion.value.estado = 'Pendiente';
  // Si marca como pendiente, limpiar fechas de pago
  formEdicion.value.fechasPago = [];
}

function marcarComoVencido() {
  formEdicion.value.estado = 'Vencido';
  // Mantener fechas existentes si las hay
}

// Funciones para el historial de pagos
function obtenerValorNumericoMensualidad() {
  if (!props.mensualidad.valor) return 0;
  return parseFloat(props.mensualidad.valor.replace(/[^0-9.-]+/g, ''));
}

function calcularTotalPagado() {
  if (!props.mensualidad.fechasPago || props.mensualidad.fechasPago.length === 0) return 0;
  
  return props.mensualidad.fechasPago.reduce((total, pago) => {
    return total + obtenerMontoPago(pago);
  }, 0);
}


function calcularSaldoPendienteHistorial() {
  const totalMensualidad = obtenerValorNumericoMensualidad();
  const totalPagado = calcularTotalPagado();
  const saldo = totalMensualidad - totalPagado;
  return Math.max(0, saldo); // Nunca negativo
}

function getEstadoPago() {
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
    // Si la fecha ya está en formato DD/MM/YYYY, devolverla tal como está
    if (typeof fecha === 'string' && /^\d{1,2}\/\d{1,2}\/\d{4}$/.test(fecha)) {
      return fecha;
    }
    
    // Si es un string en formato YYYY-MM-DD (formato de input date)
    if (typeof fecha === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
      const [año, mes, dia] = fecha.split('-');
      return `${parseInt(dia)}/${parseInt(mes)}/${año}`;
    }
    
    // Para otros casos, crear la fecha evitando problemas de zona horaria
    let fechaObj;
    if (typeof fecha === 'string') {
      // Si es un string con formato YYYY-MM-DD, crear fecha localmente
      if (fecha.includes('-')) {
        const [año, mes, dia] = fecha.split('-');
        fechaObj = new Date(parseInt(año), parseInt(mes) - 1, parseInt(dia));
      } else {
        fechaObj = new Date(fecha + 'T00:00:00'); // Agregar tiempo para evitar problemas de UTC
      }
    } else {
      fechaObj = new Date(fecha);
    }
    
    if (isNaN(fechaObj.getTime())) return fecha;
    
    const dia = fechaObj.getDate();
    const mes = fechaObj.getMonth() + 1;
    const año = fechaObj.getFullYear();
    
    return `${dia}/${mes}/${año}`;
  } catch (error) {
    return fecha;
  }
}
</script>
