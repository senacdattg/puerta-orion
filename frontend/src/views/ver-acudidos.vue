<template>
  <div class="ver-acudidos-page">
    <div class="ver-acudidos-container">
      <div class="ver-acudidos-header">
        <h1 class="ver-acudidos-title">
          <i class="fas fa-users"></i>
          Mis Acudidos
        </h1>
        <p class="ver-acudidos-subtitle">Gestiona la información de tus deportistas</p>
      </div>

      <div class="ver-acudidos-content">
        <div class="acudidos-grid">
          <div
            v-for="acudido in acudidos"
            :key="acudido.id"
            class="acudido-card"
          >
            <div class="card-header">
              <div class="acudido-avatar">
                <i class="fas fa-user"></i>
              </div>
              <div class="acudido-info">
                <h3>{{ acudido.nombre_completo }}</h3>
                <p>{{ acudido.categoria }}</p>
              </div>
            </div>

            <div class="card-content">
              <div class="info-item">
                <i class="fas fa-calendar"></i>
                <span>Edad: {{ acudido.edad }} años</span>
              </div>
              <div class="info-item">
                <i class="fas fa-envelope"></i>
                <span>{{ acudido.correo_electronico }}</span>
              </div>
              <div class="info-item">
                <i class="fas fa-phone"></i>
                <span>{{ acudido.telefono }}</span>
              </div>
            </div>

            <div class="card-actions">
              <button class="btn-action btn-view" @click="verDetalle(acudido)">
                <i class="fas fa-eye"></i>
                Ver Detalle
              </button>
              <button class="btn-action btn-edit" @click="editarAcudido(acudido)">
                <i class="fas fa-edit"></i>
                Editar
              </button>
            </div>
          </div>
        </div>

        <div v-if="acudidos.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-user-friends"></i>
          </div>
          <h3>No tienes acudidos registrados</h3>
          <p>Asigna deportistas a tu cuenta para gestionar su información</p>
          <button class="btn-primary" @click="asignarAcudido">
            <i class="fas fa-user-plus"></i>
            Asignar Acudido
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const acudidos = ref([])

onMounted(() => {
  cargarAcudidos()
})

const cargarAcudidos = async () => {
  try {
    // Aquí se implementaría la llamada al backend
    // Por ahora usamos datos de ejemplo
    acudidos.value = [
      {
        id: 1,
        nombre_completo: 'Juan Pérez',
        categoria: 'Fútbol Sub-15',
        edad: 14,
        correo_electronico: 'juan.perez@email.com',
        telefono: '3001234567'
      },
      {
        id: 2,
        nombre_completo: 'María García',
        categoria: 'Voleibol Sub-18',
        edad: 16,
        correo_electronico: 'maria.garcia@email.com',
        telefono: '3007654321'
      }
    ]
  } catch (error) {
    console.error('Error cargando acudidos:', error)
  }
}

const verDetalle = (acudido) => {
  router.push(`/ver-deportista/${acudido.id}`)
}

const editarAcudido = (acudido) => {
  router.push(`/actualizar-deportista/${acudido.id}`)
}

const asignarAcudido = () => {
  router.push('/asignar-acudido')
}
</script>

<style scoped>
.ver-acudidos-page {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 2rem 1rem;
}

.ver-acudidos-container {
  max-width: 1200px;
  margin: 0 auto;
}

.ver-acudidos-header {
  text-align: center;
  margin-bottom: 2rem;
}

.ver-acudidos-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.ver-acudidos-subtitle {
  font-size: 1.1rem;
  color: #6c757d;
  margin: 0;
}

.acudidos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.acudido-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s ease;
}

.acudido-card:hover {
  transform: translateY(-4px);
}

.card-header {
  background: linear-gradient(135deg, #20c997, #17a2b8);
  color: white;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.acudido-avatar {
  width: 3rem;
  height: 3rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.acudido-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.acudido-info p {
  margin: 0;
  opacity: 0.9;
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
  gap: 0.75rem;
}

.btn-action {
  flex: 1;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  transition: all 0.3s ease;
}

.btn-view {
  background: #007bff;
  color: white;
}

.btn-view:hover {
  background: #0056b3;
}

.btn-edit {
  background: #28a745;
  color: white;
}

.btn-edit:hover {
  background: #218838;
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
  margin: 0 0 2rem 0;
}

.btn-primary {
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

.btn-primary:hover {
  background: #1ba085;
}

@media (max-width: 768px) {
  .ver-acudidos-page {
    padding: 1rem 0.5rem;
  }

  .ver-acudidos-title {
    font-size: 2rem;
  }

  .acudidos-grid {
    grid-template-columns: 1fr;
  }

  .card-header {
    flex-direction: column;
    text-align: center;
  }

  .card-actions {
    flex-direction: column;
  }
}
</style>

