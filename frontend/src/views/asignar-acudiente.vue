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

<style scoped>
.asignar-acudiente-page {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 2rem 1rem;
}

.asignar-acudiente-container {
  max-width: 1000px;
  margin: 0 auto;
}

.asignar-acudiente-header {
  text-align: center;
  margin-bottom: 2rem;
}

.asignar-acudiente-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.asignar-acudiente-subtitle {
  font-size: 1.1rem;
  color: #6c757d;
  margin: 0;
}

.current-acudiente {
  margin-bottom: 2rem;
}

.current-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border-left: 4px solid #28a745;
}

.no-acudiente {
  margin-bottom: 2rem;
}

.no-acudiente-content {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.no-acudiente-icon {
  font-size: 4rem;
  color: #6c757d;
  margin-bottom: 1rem;
}

.no-acudiente-content h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.no-acudiente-content p {
  color: #6c757d;
  margin: 0 0 2rem 0;
}

.btn-assign {
  background: #20c997;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.3s ease;
}

.btn-assign:hover {
  background: #1ba085;
}

.search-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.search-box {
  position: relative;
  max-width: 500px;
  margin: 0 auto 2rem auto;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #20c997;
}

.acudientes-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.acudiente-card {
  background: #f8f9fa;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.acudiente-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
  background: #e9ecef;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.acudiente-avatar {
  width: 3rem;
  height: 3rem;
  background: #20c997;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.acudiente-info {
  flex: 1;
}

.acudiente-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
}

.acudiente-info p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
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
  color: #20c997;
}

.card-actions {
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  display: flex;
  justify-content: flex-end;
}

.btn-change,
.btn-select {
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

.btn-change {
  background: #fd7e14;
  color: white;
}

.btn-change:hover {
  background: #e8650e;
}

.btn-select {
  background: #20c997;
  color: white;
}

.btn-select:hover:not(:disabled) {
  background: #1ba085;
}

.btn-select:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 2rem;
}

.empty-icon {
  font-size: 3rem;
  color: #6c757d;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.25rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: #6c757d;
  margin: 0;
}

@media (max-width: 768px) {
  .asignar-acudiente-page {
    padding: 1rem 0.5rem;
  }

  .asignar-acudiente-title {
    font-size: 2rem;
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

