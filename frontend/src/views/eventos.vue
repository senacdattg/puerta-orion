<template>
  <main class="eventos-page">
    <Encabezado />
    <div class="eventos-container">
      <div class="eventos-header">
        <h1 class="eventos-title">
          <i class="fas fa-calendar-check"></i>
          Eventos y Actividades
        </h1>
        <p class="eventos-subtitle">Participa en las actividades deportivas del club</p>
      </div>

      <div class="eventos-content">
        <div class="eventos-grid">
          <div
            v-for="evento in eventos"
            :key="evento.id"
            class="evento-card"
            :class="getEventoClass(evento.estado)"
          >
            <div class="card-header">
              <div class="evento-fecha">
                <div class="fecha-dia">{{ evento.dia }}</div>
                <div class="fecha-mes">{{ evento.mes }}</div>
              </div>
              <div class="evento-info">
                <h3>{{ evento.titulo }}</h3>
                <p>{{ evento.categoria }}</p>
              </div>
              <div class="evento-estado">
                <span :class="getEstadoClass(evento.estado)">
                  {{ evento.estado }}
                </span>
              </div>
            </div>

            <div class="card-content">
              <div class="info-item">
                <i class="fas fa-clock"></i>
                <span>{{ evento.hora_inicio }} - {{ evento.hora_fin }}</span>
              </div>
              <div class="info-item">
                <i class="fas fa-map-marker-alt"></i>
                <span>{{ evento.lugar }}</span>
              </div>
              <div class="info-item" v-if="evento.participantes > 0">
                <i class="fas fa-users"></i>
                <span>{{ evento.participantes }} participantes</span>
              </div>
              <div class="info-item" v-if="evento.descripcion">
                <i class="fas fa-info-circle"></i>
                <span>{{ evento.descripcion }}</span>
              </div>
            </div>

          </div>
        </div>

        <div v-if="cargando" class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-spinner fa-spin"></i>
          </div>
          <h3>Cargando eventos...</h3>
          <p>Por favor espera mientras cargamos los eventos</p>
        </div>

        <div v-else-if="eventos.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-calendar-times"></i>
          </div>
          <h3>No hay eventos próximos</h3>
          <p>No se encontraron eventos próximos en el calendario</p>
        </div>
      </div>
    </div>
    <FooterEnhanced />
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Encabezado from '@/components/layout/encabezado.vue'
import FooterEnhanced from '@/components/layout/pie.vue'
import calendarioService from '@/services/calendarioService'

// Definir nombre del componente para evitar error del linter
defineOptions({
  name: 'EventosView'
})

const eventos = ref([])
const cargando = ref(false)

const meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

// Función para formatear hora de HH:MM:SS a HH:MM
const formatearHora = (hora) => {
  if (!hora) return '00:00'
  // Si viene en formato HH:MM:SS, tomar solo HH:MM
  if (hora.includes(':') && hora.split(':').length === 3) {
    const partes = hora.split(':')
    return `${partes[0]}:${partes[1]}`
  }
  return hora
}

onMounted(() => {
  cargarDatos()
})

const cargarDatos = async () => {
  cargando.value = true
  try {
    await cargarEventos()
  } catch (error) {
    console.error('Error cargando datos:', error)
  } finally {
    cargando.value = false
  }
}

const cargarEventos = async () => {
  try {
    // Obtener solo eventos próximos (futuros)
    const eventosCalendario = await calendarioService.obtenerEventosProximos()

    console.log('📅 Eventos próximos recibidos:', eventosCalendario)

    // Mapear eventos del calendario al formato esperado por el componente
    eventos.value = eventosCalendario.map(evento => {
      // El evento ya viene mapeado del servicio, pero necesitamos asegurarnos de que tenga todos los campos
      const fechaStr = evento.fecha || evento.fecha_evento
      const fecha = new Date(fechaStr)

      // Validar que la fecha sea válida
      if (isNaN(fecha.getTime())) {
        console.warn('⚠️ Fecha inválida para evento:', evento)
        return null
      }

      const hoy = new Date()
      hoy.setHours(0, 0, 0, 0)
      const fechaEvento = new Date(fecha)
      fechaEvento.setHours(0, 0, 0, 0)

      // Filtrar eventos pasados: solo incluir eventos de hoy en adelante
      // Si el evento es de ayer o antes, no incluirlo
      if (fechaEvento < hoy) {
        console.log('📅 Evento pasado excluido:', evento.titulo || evento.nombre, fechaStr)
        return null
      }

      // Determinar estado basado en la fecha (solo eventos próximos, pero pueden ser activos si es hoy)
      let estado = 'proximo'
      if (fechaEvento.getTime() === hoy.getTime()) {
        estado = 'activo'
      }

      return {
        id: evento.id,
        titulo: evento.titulo || evento.nombre || 'Evento sin título',
        categoria: evento.categoria?.nombre_categoria || evento.categoria?.nombre || 'Sin categoría',
        id_categoria: evento.idCategoria || evento.id_categoria,
        estado: estado,
        dia: fecha.getDate().toString().padStart(2, '0'),
        mes: meses[fecha.getMonth()],
        hora_inicio: formatearHora(evento.horaInicio || evento.hora_inicio || evento.hora || '00:00'),
        hora_fin: formatearHora(evento.horaFin || evento.hora_fin || '00:00'),
        lugar: evento.lugar || 'No especificado',
        participantes: 0, // Este dato no está disponible en el backend actualmente
        descripcion: evento.descripcion || '',
        fecha_evento: fechaStr
      }
    }).filter(evento => evento !== null) // Filtrar eventos con fechas inválidas o pasadas

    console.log('✅ Eventos procesados (futuros únicamente):', eventos.value.length, eventos.value)

    // Ordenar eventos: activos primero, luego próximos (por fecha)
    eventos.value.sort((a, b) => {
      const ordenEstados = { 'activo': 0, 'proximo': 1 }
      if (ordenEstados[a.estado] !== ordenEstados[b.estado]) {
        return ordenEstados[a.estado] - ordenEstados[b.estado]
      }
      // Si tienen el mismo estado, ordenar por fecha
      return new Date(a.fecha_evento) - new Date(b.fecha_evento)
    })
  } catch (error) {
    console.error('❌ Error cargando eventos próximos:', error)
    eventos.value = []
  }
}

const getEventoClass = (estado) => {
  const classes = {
    'activo': 'evento-activo',
    'proximo': 'evento-proximo',
    'finalizado': 'evento-finalizado'
  }
  return classes[estado] || ''
}

const getEstadoClass = (estado) => {
  const classes = {
    'activo': 'estado-activo',
    'proximo': 'estado-proximo',
    'finalizado': 'estado-finalizado'
  }
  return classes[estado] || ''
}

</script>

<style scoped>
.eventos-page {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 2rem 1rem;
  padding-bottom: 0;
  display: flex;
  flex-direction: column;
}

.eventos-container {
  max-width: 1200px;
  margin: 0 auto;
  margin-bottom: 2rem;
  flex: 1;
}

/* Hacer que el footer se salga del padding del main y se comporte como footer */
.eventos-page :deep(.footer-enhanced) {
  margin-left: -1rem;
  margin-right: -1rem;
  width: calc(100% + 2rem);
  margin-top: auto;
}

.eventos-header {
  text-align: center;
  margin-bottom: 2rem;
}

.eventos-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.eventos-subtitle {
  font-size: 1.1rem;
  color: #6c757d;
  margin: 0;
}

.filters-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 2rem;
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 600;
  color: #495057;
}

.filter-select {
  padding: 0.5rem;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 0.9rem;
  min-width: 200px;
}

.filter-select:focus {
  outline: none;
  border-color: #007bff;
}

.eventos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.evento-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s ease;
}

.evento-card:hover {
  transform: translateY(-4px);
}

.evento-card.evento-activo {
  border-left: 4px solid #28a745;
}

.evento-card.evento-proximo {
  border-left: 4px solid #fd7e14;
}

.evento-card.evento-finalizado {
  border-left: 4px solid #6c757d;
}

.card-header {
  background: #f8f9fa;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.evento-fecha {
  background: #007bff;
  color: white;
  border-radius: 8px;
  padding: 0.75rem;
  text-align: center;
  min-width: 60px;
}

.fecha-dia {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1;
}

.fecha-mes {
  font-size: 0.8rem;
  opacity: 0.9;
}

.evento-info {
  flex: 1;
}

.evento-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
}

.evento-info p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.evento-estado {
  display: flex;
  align-items: center;
}

.estado-activo {
  background: #d4edda;
  color: #155724;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.estado-proximo {
  background: #fff3cd;
  color: #856404;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.estado-finalizado {
  background: #e2e3e5;
  color: #383d41;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.card-content {
  padding: 1.5rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  color: #6c757d;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item i {
  width: 1rem;
  color: #007bff;
}

.card-actions {
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  display: flex;
  justify-content: flex-end;
}

.btn-participate,
.btn-notify,
.btn-view {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  transition: all 0.3s ease;
}

.btn-participate {
  background: #28a745;
  color: white;
}

.btn-participate:hover:not(:disabled) {
  background: #218838;
}

.btn-participate:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.btn-notify {
  background: #fd7e14;
  color: white;
}

.btn-notify:hover {
  background: #e8650e;
}

.btn-view {
  background: #6c757d;
  color: white;
}

.btn-view:hover {
  background: #5a6268;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 4rem;
  color: #6c757d;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: #6c757d;
  margin: 0;
}

@media (max-width: 768px) {
  .eventos-page {
    padding: 1rem 0.5rem;
  }

  .eventos-title {
    font-size: 2rem;
  }

  .filters-section {
    flex-direction: column;
    gap: 1rem;
  }

  .filter-select {
    min-width: auto;
  }

  .eventos-grid {
    grid-template-columns: 1fr;
  }

  .card-header {
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }

  .card-actions {
    justify-content: center;
  }
}
</style>

