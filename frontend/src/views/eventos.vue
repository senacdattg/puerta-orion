<template>
  <main class="eventos-page">
    <Encabezado />
    <TituloClub />
    <div class="eventos-container">
      <div class="eventos-header">
        <h1 class="eventos-title">
          <i class="fas fa-calendar-check"></i>
          Eventos y Actividades
        </h1>
        <p class="eventos-subtitle">Participa en las actividades deportivas del club</p>
      </div>

      <div class="eventos-content">
        <div class="filters-section">
          <div class="filter-group">
            <label for="categoria">Categoría:</label>
            <select id="categoria" v-model="filtroCategoria" class="filter-select">
              <option value="">Todas las categorías</option>
              <option value="Fútbol">Fútbol</option>
              <option value="Voleibol">Voleibol</option>
              <option value="Básquetbol">Básquetbol</option>
            </select>
          </div>

          <div class="filter-group">
            <label for="estado">Estado:</label>
            <select id="estado" v-model="filtroEstado" class="filter-select">
              <option value="">Todos los estados</option>
              <option value="activo">Activos</option>
              <option value="finalizado">Finalizados</option>
              <option value="proximo">Próximos</option>
            </select>
          </div>
        </div>

        <div class="eventos-grid">
          <div
            v-for="evento in eventosFiltrados"
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
              <div class="info-item">
                <i class="fas fa-users"></i>
                <span>{{ evento.participantes }} participantes</span>
              </div>
              <div class="info-item" v-if="evento.descripcion">
                <i class="fas fa-info-circle"></i>
                <span>{{ evento.descripcion }}</span>
              </div>
            </div>

            <div class="card-actions">
              <button
                v-if="evento.estado === 'activo'"
                class="btn-participate"
                @click="participarEvento(evento)"
                :disabled="inscribiendo"
              >
                <i class="fas fa-user-plus"></i>
                {{ inscribiendo ? 'Inscribiendo...' : 'Participar' }}
              </button>
              <button
                v-else-if="evento.estado === 'proximo'"
                class="btn-notify"
                @click="notificarEvento(evento)"
              >
                <i class="fas fa-bell"></i>
                Notificar
              </button>
              <button
                v-else
                class="btn-view"
                @click="verDetalle(evento)"
              >
                <i class="fas fa-eye"></i>
                Ver Detalle
              </button>
            </div>
          </div>
        </div>

        <div v-if="eventosFiltrados.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-calendar-times"></i>
          </div>
          <h3>No hay eventos disponibles</h3>
          <p>No se encontraron eventos con los filtros seleccionados</p>
        </div>
      </div>
    </div>
    <FooterEnhanced />
  </main>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import Encabezado from '@/components/layout/encabezado.vue'
import TituloClub from '@/components/ui/titulo-club.vue'
import FooterEnhanced from '@/components/layout/pie.vue'

// Definir nombre del componente para evitar error del linter
defineOptions({
  name: 'EventosView'
})

const router = useRouter()
const filtroCategoria = ref('')
const filtroEstado = ref('')
const inscribiendo = ref(false)
const eventos = ref([])

onMounted(() => {
  cargarEventos()
})

const cargarEventos = async () => {
  try {
    // Aquí se implementaría la llamada al backend
    // Por ahora usamos datos de ejemplo
    eventos.value = [
      {
        id: 1,
        titulo: 'Torneo de Fútbol Sub-15',
        categoria: 'Fútbol',
        estado: 'activo',
        dia: '25',
        mes: 'OCT',
        hora_inicio: '09:00',
        hora_fin: '17:00',
        lugar: 'Cancha Principal',
        participantes: 24,
        descripcion: 'Torneo eliminatorio para categoría Sub-15'
      },
      {
        id: 2,
        titulo: 'Entrenamiento de Voleibol',
        categoria: 'Voleibol',
        estado: 'proximo',
        dia: '28',
        mes: 'OCT',
        hora_inicio: '16:00',
        hora_fin: '18:00',
        lugar: 'Coliseo',
        participantes: 12,
        descripcion: 'Entrenamiento técnico y táctico'
      },
      {
        id: 3,
        titulo: 'Clínica de Básquetbol',
        categoria: 'Básquetbol',
        estado: 'finalizado',
        dia: '20',
        mes: 'OCT',
        hora_inicio: '10:00',
        hora_fin: '12:00',
        lugar: 'Cancha Auxiliar',
        participantes: 18,
        descripcion: 'Clínica de fundamentos básicos'
      }
    ]
  } catch (error) {
    console.error('Error cargando eventos:', error)
  }
}

const eventosFiltrados = computed(() => {
  let filtrados = eventos.value

  if (filtroCategoria.value) {
    filtrados = filtrados.filter(evento => evento.categoria === filtroCategoria.value)
  }

  if (filtroEstado.value) {
    filtrados = filtrados.filter(evento => evento.estado === filtroEstado.value)
  }

  return filtrados
})

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

const participarEvento = async (evento) => {
  inscribiendo.value = true

  try {
    // Aquí se implementaría la llamada al backend
    console.log('Participando en evento:', evento.id)

    // Simular llamada API
    await new Promise(resolve => setTimeout(resolve, 1000))

    alert('Te has inscrito exitosamente en el evento')

  } catch (error) {
    console.error('Error participando en evento:', error)
    alert('Error al inscribirse en el evento')
  } finally {
    inscribiendo.value = false
  }
}

const notificarEvento = (evento) => {
  alert(`Te notificaremos sobre el evento: ${evento.titulo}`)
}

const verDetalle = (evento) => {
  router.push(`/evento/${evento.id}`)
}
</script>

<style scoped>
.eventos-page {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 2rem 1rem;
}

.eventos-container {
  max-width: 1200px;
  margin: 0 auto;
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

