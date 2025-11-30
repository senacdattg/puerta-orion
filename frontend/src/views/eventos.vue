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
      // Prefer Number.isNaN over isNaN for robust number validation
      if (Number.isNaN(fecha.getTime())) {
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



