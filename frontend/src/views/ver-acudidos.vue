<template>
  <main>
    <Encabezado />

    <div class="ver-acudidos-page">
      <div class="ver-acudidos-container">
      <div class="ver-acudidos-header">
        <h1 class="ver-acudidos-title">
          <i class="fas fa-users"></i>
          Gestión de Acudidos
        </h1>
        <p class="ver-acudidos-subtitle">Gestiona y asigna deportistas a tu cuenta</p>
      </div>

      <!-- Botón de crear nuevo deportista -->
      <div class="action-header">
        <button class="btn-create-new" @click="crearNuevoDeportista">
          <i class="fas fa-plus-circle"></i>
          Crear Nuevo Deportista
        </button>
      </div>

      <!-- Lista de acudidos o estado vacío -->
      <div v-if="acudidos.length > 0" class="acudidos-grid">
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

      <div v-else class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-user-friends"></i>
        </div>
        <h3>No tienes acudidos registrados</h3>
        <p>Asigna deportistas a tu cuenta para gestionar su información</p>
        <button class="btn-primary" @click="crearNuevoDeportista">
          <i class="fas fa-user-plus"></i>
          Crear Nuevo Deportista
        </button>
      </div>
    </div>
    </div>

    <Pie />
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Encabezado from '@/components/layout/encabezado.vue'
import Pie from '@/components/layout/pie.vue'

const router = useRouter()
const authStore = useAuthStore()

const acudidos = ref([])

onMounted(async () => {
  // Recargar el perfil del usuario para obtener información actualizada
  console.log('🔄 Recargando perfil del usuario...')
  await authStore.loadUserProfile()

  // Esperar un momento para que se actualice el perfil
  setTimeout(() => {
    cargarAcudidos()
  }, 500)
})

const cargarAcudidos = async () => {
  try {
    console.log('🔍 Usuario autenticado:', authStore.user)
    console.log('🔍 Token:', authStore.token ? 'Token existe' : 'No hay token')

    // Obtener el ID del acudiente desde el usuario autenticado
    const acudienteId = authStore.user?.acudiente?.id_acudiente
    console.log('🔍 ID del acudiente:', acudienteId)

    if (!acudienteId) {
      console.error('❌ No se encontró ID del acudiente en el usuario autenticado')
      console.log('💡 Info del usuario:', JSON.stringify(authStore.user, null, 2))
      acudidos.value = []
      return
    }

    console.log(`🌐 Llamando al endpoint: http://localhost:5000/api/deportistas/acudiente/${acudienteId}`)

    // Llamar al backend para obtener los deportistas asociados
    const response = await fetch(`http://localhost:5000/api/deportistas/acudiente/${acudienteId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    console.log('📡 Estado de la respuesta:', response.status)
    const result = await response.json()
    console.log('📦 Datos recibidos:', result)

    if (response.ok && result.success) {
      acudidos.value = result.data || []
      console.log(`✅ ${acudidos.value.length} deportista(s) cargado(s)`)
      console.log('📋 Deportistas:', acudidos.value)
    } else {
      console.error('❌ Error al cargar deportistas:', result.message)
      acudidos.value = []
    }
  } catch (error) {
    console.error('❌ Error cargando acudidos:', error)
    acudidos.value = []
  }
}

const verDetalle = (acudido) => {
  router.push(`/ver-deportista/${acudido.id}`)
}

const editarAcudido = (acudido) => {
  router.push(`/actualizar-deportista/${acudido.id}`)
}

const crearNuevoDeportista = () => {
  router.push({
    path: '/registrar-deportista-form',
    query: { asignarAcudiente: 'true', idAcudiente: authStore.user?.id_usuario }
  })
}
</script>

<style scoped>
.ver-acudidos-page {
  min-height: calc(100vh - 300px);
  background: linear-gradient(to bottom, #f0f8ff 0%, #e3f2fd 100%);
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

/* Action Header */
.action-header {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

.btn-create-new {
  background: #f7d600;
  color: #0047ab;
  border: 2px solid #0047ab;
  padding: 1.2rem 3rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(247, 214, 0, 0.3);
}

.btn-create-new:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(247, 214, 0, 0.4);
  background: #ffc107;
}

.btn-create-new i {
  font-size: 1.3rem;
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
  background: #0047ab;
  color: white;
  border-bottom: 3px solid #f7d600;
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
  color: white;
}

.acudido-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
}

.acudido-info p {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
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
  color: #0047ab;
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
  background: #0047ab;
  color: white;
}

.btn-view:hover {
  background: #003d8f;
}

.btn-edit {
  background: #f7d600;
  color: #0047ab;
  font-weight: 700;
}

.btn-edit:hover {
  background: #ffc107;
  color: #003d8f;
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
  background: #f7d600;
  color: #0047ab;
  border: 2px solid #0047ab;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(247, 214, 0, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(247, 214, 0, 0.4);
  background: #ffc107;
}

@media (max-width: 768px) {
  .ver-acudidos-page {
    padding: 1rem 0.5rem;
  }

  .ver-acudidos-title {
    font-size: 2rem;
  }

  .btn-create-new {
    width: 100%;
    padding: 1rem 2rem;
    font-size: 1rem;
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

