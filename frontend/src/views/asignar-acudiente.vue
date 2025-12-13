<template>
  <main class="asignar-acudiente-page">
    <Encabezado />
    <TituloClub />
    <div class="asignar-acudiente-container">
      <div class="asignar-acudiente-header">
        <h1 class="asignar-acudiente-title">
          <i class="fas fa-user-friends"></i>
          Asignar Acudiente
        </h1>
        <p class="asignar-acudiente-subtitle">Vincula un acudiente a tu cuenta</p>
      </div>

      <div class="asignar-acudiente-content">
        <div class="current-acudiente" v-if="acudienteActual">
          <div class="current-card">
            <div class="card-header">
              <div class="acudiente-avatar">
                <i class="fas fa-user-friends"></i>
              </div>
              <div class="acudiente-info">
                <h3>Acudiente Actual</h3>
                <p>{{ acudienteActual.nombre_completo }}</p>
              </div>
            </div>

            <div class="card-content">
              <div class="info-item">
                <i class="fas fa-id-card"></i>
                <span>Documento: {{ acudienteActual.documento }}</span>
              </div>
              <div class="info-item">
                <i class="fas fa-envelope"></i>
                <span>{{ acudienteActual.correo_electronico }}</span>
              </div>
              <div class="info-item">
                <i class="fas fa-phone"></i>
                <span>{{ acudienteActual.telefono }}</span>
              </div>
            </div>

            <div class="card-actions">
              <button class="btn-change" @click="cambiarAcudiente">
                <i class="fas fa-exchange-alt"></i>
                Cambiar Acudiente
              </button>
            </div>
          </div>
        </div>

        <div v-else class="no-acudiente">
          <div class="no-acudiente-content">
            <div class="no-acudiente-icon">
              <i class="fas fa-user-friends"></i>
            </div>
            <h3>No tienes acudiente asignado</h3>
            <p>Asigna un acudiente para que pueda gestionar tu información</p>
            <button class="btn-assign" @click="mostrarBusqueda = true">
              <i class="fas fa-user-plus"></i>
              Asignar Acudiente
            </button>
          </div>
        </div>

        <div v-if="mostrarBusqueda" class="search-section">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input
              type="text"
              v-model="searchTerm"
              placeholder="Buscar acudiente por nombre o documento..."
              class="search-input"
              @input="buscarAcudientes"
            >
          </div>

          <div class="acudientes-list">
            <div
              v-for="acudiente in acudientesFiltrados"
              :key="acudiente.id"
              class="acudiente-card"
            >
              <div class="card-header">
                <div class="acudiente-avatar">
                  <i class="fas fa-user-friends"></i>
                </div>
                <div class="acudiente-info">
                  <h3>{{ acudiente.nombre_completo }}</h3>
                  <p>{{ acudiente.profesion || 'Acudiente' }}</p>
                </div>
              </div>

              <div class="card-content">
                <div class="info-item">
                  <i class="fas fa-id-card"></i>
                  <span>Documento: {{ acudiente.documento }}</span>
                </div>
                <div class="info-item">
                  <i class="fas fa-envelope"></i>
                  <span>{{ acudiente.correo_electronico }}</span>
                </div>
                <div class="info-item">
                  <i class="fas fa-phone"></i>
                  <span>{{ acudiente.telefono }}</span>
                </div>
              </div>

              <div class="card-actions">
                <button
                  class="btn-select"
                  @click="seleccionarAcudiente(acudiente)"
                  :disabled="asignando"
                >
                  <i class="fas fa-check"></i>
                  {{ asignando ? 'Asignando...' : 'Seleccionar' }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="acudientesFiltrados.length === 0" class="empty-state">
            <div class="empty-icon">
              <i class="fas fa-search"></i>
            </div>
            <h3>No se encontraron acudientes</h3>
            <p>Intenta con otros términos de búsqueda</p>
          </div>
        </div>
      </div>
    </div>
    <FooterEnhanced />
  </main>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import Encabezado from '@/components/layout/encabezado.vue'
import TituloClub from '@/components/ui/titulo-club.vue'
import FooterEnhanced from '@/components/layout/pie.vue'
import Swal from 'sweetalert2'
const searchTerm = ref('')
const asignando = ref(false)
const mostrarBusqueda = ref(false)
const acudienteActual = ref(null)
const acudientes = ref([])

onMounted(() => {
  cargarAcudienteActual()
  cargarAcudientes()
})

const cargarAcudienteActual = async () => {
  try {
    // Aquí se implementaría la llamada al backend
    // Por ahora usamos datos de ejemplo
    acudienteActual.value = {
      id: 1,
      nombre_completo: 'Ana García',
      documento: '12345678',
      correo_electronico: 'ana.garcia@email.com',
      telefono: '3001234567'
    }
  } catch (error) {
    console.error('Error cargando acudiente actual:', error)
  }
}

const cargarAcudientes = async () => {
  try {
    // Aquí se implementaría la llamada al backend
    // Por ahora usamos datos de ejemplo
    acudientes.value = [
      {
        id: 2,
        nombre_completo: 'Carlos López',
        documento: '87654321',
        correo_electronico: 'carlos.lopez@email.com',
        telefono: '3007654321',
        profesion: 'Ingeniero'
      },
      {
        id: 3,
        nombre_completo: 'María Rodríguez',
        documento: '11223344',
        correo_electronico: 'maria.rodriguez@email.com',
        telefono: '3009876543',
        profesion: 'Médica'
      }
    ]
  } catch (error) {
    console.error('Error cargando acudientes:', error)
  }
}

const acudientesFiltrados = computed(() => {
  if (!searchTerm.value) return acudientes.value

  const term = searchTerm.value.toLowerCase()
  return acudientes.value.filter(acudiente =>
    acudiente.nombre_completo.toLowerCase().includes(term) ||
    acudiente.documento.includes(term)
  )
})

const buscarAcudientes = () => {
  // La búsqueda se maneja automáticamente con el computed
}

const seleccionarAcudiente = async (acudiente) => {
  asignando.value = true

  try {
    // Aquí se implementaría la llamada al backend
    console.log('Asignando acudiente:', acudiente.id)

    // Simular llamada API
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Actualizar estado local
    acudienteActual.value = acudiente
    mostrarBusqueda.value = false
    searchTerm.value = ''

    await Swal.fire({
      icon: 'success',
      title: 'Acudiente asignado',
      text: 'El acudiente se asignó correctamente.',
      timer: 1500,
      showConfirmButton: false
    })

  } catch (error) {
    console.error('Error asignando acudiente:', error)
    await Swal.fire({
      icon: 'error',
      title: 'Error al asignar',
      text: 'No pudimos asignar el acudiente.'
    })
  } finally {
    asignando.value = false
  }
}

const cambiarAcudiente = () => {
  mostrarBusqueda.value = true
}
</script>



