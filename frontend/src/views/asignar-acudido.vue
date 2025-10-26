<template>
  <div class="asignar-acudido-page">
    <div class="asignar-acudido-container">
      <div class="asignar-acudido-header">
        <h1 class="asignar-acudido-title">
          <i class="fas fa-user-plus"></i>
          Asignar Acudido
        </h1>
        <p class="asignar-acudido-subtitle">Vincula un deportista a tu cuenta</p>
      </div>

      <div class="asignar-acudido-content">
        <div class="search-section">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input
              type="text"
              v-model="searchTerm"
              placeholder="Buscar deportista por nombre o documento..."
              class="search-input"
              @input="buscarDeportistas"
            >
          </div>
        </div>

        <div class="deportistas-list">
          <div
            v-for="deportista in deportistasFiltrados"
            :key="deportista.id"
            class="deportista-card"
            :class="{ 'asignado': deportista.asignado }"
          >
            <div class="card-header">
              <div class="deportista-avatar">
                <i class="fas fa-user"></i>
              </div>
              <div class="deportista-info">
                <h3>{{ deportista.nombre_completo }}</h3>
                <p>{{ deportista.categoria }}</p>
              </div>
              <div class="card-status">
                <span v-if="deportista.asignado" class="status-asignado">
                  <i class="fas fa-check-circle"></i>
                  Asignado
                </span>
                <span v-else class="status-disponible">
                  <i class="fas fa-user-plus"></i>
                  Disponible
                </span>
              </div>
            </div>

            <div class="card-content">
              <div class="info-item">
                <i class="fas fa-id-card"></i>
                <span>Documento: {{ deportista.documento }}</span>
              </div>
              <div class="info-item">
                <i class="fas fa-calendar"></i>
                <span>Edad: {{ deportista.edad }} años</span>
              </div>
              <div class="info-item">
                <i class="fas fa-envelope"></i>
                <span>{{ deportista.correo_electronico }}</span>
              </div>
            </div>

            <div class="card-actions">
              <button
                v-if="!deportista.asignado"
                class="btn-assign"
                @click="asignarDeportista(deportista)"
                :disabled="asignando"
              >
                <i class="fas fa-link"></i>
                {{ asignando ? 'Asignando...' : 'Asignar' }}
              </button>
              <button
                v-else
                class="btn-unassign"
                @click="desasignarDeportista(deportista)"
              >
                <i class="fas fa-unlink"></i>
                Desasignar
              </button>
            </div>
          </div>
        </div>

        <div v-if="deportistasFiltrados.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-search"></i>
          </div>
          <h3>No se encontraron deportistas</h3>
          <p>Intenta con otros términos de búsqueda</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchTerm = ref('')
const asignando = ref(false)
const deportistas = ref([])

onMounted(() => {
  cargarDeportistas()
})

const cargarDeportistas = async () => {
  try {
    // Aquí se implementaría la llamada al backend
    // Por ahora usamos datos de ejemplo
    deportistas.value = [
      {
        id: 1,
        nombre_completo: 'Juan Pérez',
        categoria: 'Fútbol Sub-15',
        documento: '12345678',
        edad: 14,
        correo_electronico: 'juan.perez@email.com',
        asignado: false
      },
      {
        id: 2,
        nombre_completo: 'María García',
        categoria: 'Voleibol Sub-18',
        documento: '87654321',
        edad: 16,
        correo_electronico: 'maria.garcia@email.com',
        asignado: true
      },
      {
        id: 3,
        nombre_completo: 'Carlos López',
        categoria: 'Básquetbol Sub-16',
        documento: '11223344',
        edad: 15,
        correo_electronico: 'carlos.lopez@email.com',
        asignado: false
      }
    ]
  } catch (error) {
    console.error('Error cargando deportistas:', error)
  }
}

const deportistasFiltrados = computed(() => {
  if (!searchTerm.value) return deportistas.value

  const term = searchTerm.value.toLowerCase()
  return deportistas.value.filter(deportista =>
    deportista.nombre_completo.toLowerCase().includes(term) ||
    deportista.documento.includes(term)
  )
})

const buscarDeportistas = () => {
  // La búsqueda se maneja automáticamente con el computed
}

const asignarDeportista = async (deportista) => {
  asignando.value = true

  try {
    // Aquí se implementaría la llamada al backend
    console.log('Asignando deportista:', deportista.id)

    // Simular llamada API
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Actualizar estado local
    deportista.asignado = true

    alert('Deportista asignado correctamente')

  } catch (error) {
    console.error('Error asignando deportista:', error)
    alert('Error al asignar el deportista')
  } finally {
    asignando.value = false
  }
}

const desasignarDeportista = async (deportista) => {
  if (confirm('¿Estás seguro de que quieres desasignar este deportista?')) {
    try {
      // Aquí se implementaría la llamada al backend
      console.log('Desasignando deportista:', deportista.id)

      // Simular llamada API
      await new Promise(resolve => setTimeout(resolve, 500))

      // Actualizar estado local
      deportista.asignado = false

      alert('Deportista desasignado correctamente')

    } catch (error) {
      console.error('Error desasignando deportista:', error)
      alert('Error al desasignar el deportista')
    }
  }
}
</script>

<style scoped>
.asignar-acudido-page {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 2rem 1rem;
}

.asignar-acudido-container {
  max-width: 1000px;
  margin: 0 auto;
}

.asignar-acudido-header {
  text-align: center;
  margin-bottom: 2rem;
}

.asignar-acudido-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.asignar-acudido-subtitle {
  font-size: 1.1rem;
  color: #6c757d;
  margin: 0;
}

.search-section {
  margin-bottom: 2rem;
}

.search-box {
  position: relative;
  max-width: 500px;
  margin: 0 auto;
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

.deportistas-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.deportista-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.deportista-card.asignado {
  border-left: 4px solid #28a745;
}

.deportista-card:hover {
  transform: translateY(-2px);
}

.card-header {
  background: #f8f9fa;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.deportista-avatar {
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

.deportista-info {
  flex: 1;
}

.deportista-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
}

.deportista-info p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.card-status {
  display: flex;
  align-items: center;
}

.status-asignado {
  color: #28a745;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.status-disponible {
  color: #6c757d;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
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

.btn-assign,
.btn-unassign {
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

.btn-assign {
  background: #20c997;
  color: white;
}

.btn-assign:hover:not(:disabled) {
  background: #1ba085;
}

.btn-assign:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.btn-unassign {
  background: #dc3545;
  color: white;
}

.btn-unassign:hover {
  background: #c82333;
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
  .asignar-acudido-page {
    padding: 1rem 0.5rem;
  }

  .asignar-acudido-title {
    font-size: 2rem;
  }

  .card-header {
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }

  .card-status {
    justify-content: center;
  }
}
</style>

