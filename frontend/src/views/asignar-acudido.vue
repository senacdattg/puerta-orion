<template>
  <main class="asignar-acudido-page">
    <Encabezado />
    <TituloClub />
    <div class="asignar-acudido-container">
      <div class="asignar-acudido-header">
        <h1 class="asignar-acudido-title">
          <i class="fas fa-user-plus"></i>
          Asignar Acudido
        </h1>
        <p class="asignar-acudido-subtitle">Vincula un deportista a tu cuenta o crea uno nuevo</p>
      </div>

      <div class="asignar-acudido-content">
        <!-- Botón para crear nuevo deportista -->
        <div class="action-buttons">
          <button class="btn-create" @click="crearNuevoDeportista">
            <i class="fas fa-plus-circle"></i>
            Crear Nuevo Deportista
          </button>
          <button class="btn-search-existing" @click="mostrarBusqueda = !mostrarBusqueda">
            <i class="fas fa-search"></i>
            {{ mostrarBusqueda ? 'Ocultar Búsqueda' : 'Buscar Deportista Existente' }}
          </button>
        </div>

        <div v-if="mostrarBusqueda" class="search-section">
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
    <FooterEnhanced />
  </main>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import Encabezado from '@/components/layout/encabezado.vue'
import TituloClub from '@/components/ui/titulo-club.vue'
import FooterEnhanced from '@/components/layout/pie.vue'
import { useAuthStore } from '@/stores/auth'
import Swal from 'sweetalert2'

const router = useRouter()
const authStore = useAuthStore()
const searchTerm = ref('')
const asignando = ref(false)
const mostrarBusqueda = ref(false)
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

    await Swal.fire({
      icon: 'success',
      title: 'Asignación exitosa',
      text: 'El deportista fue asignado correctamente.',
      timer: 1500,
      showConfirmButton: false
    })

  } catch (error) {
    console.error('Error asignando deportista:', error)
    await Swal.fire({
      icon: 'error',
      title: 'Error al asignar',
      text: 'No pudimos asignar el deportista. Intenta de nuevo.'
    })
  } finally {
    asignando.value = false
  }
}

const desasignarDeportista = async (deportista) => {
  const result = await Swal.fire({
    icon: 'question',
    title: '¿Desasignar deportista?',
    text: 'El deportista dejará de estar asociado a este acudiente.',
    showCancelButton: true,
    confirmButtonText: 'Sí, desasignar',
    cancelButtonText: 'Cancelar'
  })

  if (!result.isConfirmed) return

  try {
    // Aquí se implementaría la llamada al backend
    console.log('Desasignando deportista:', deportista.id)

    // Simular llamada API
    await new Promise(resolve => setTimeout(resolve, 500))

    // Actualizar estado local
    deportista.asignado = false

    await Swal.fire({
      icon: 'success',
      title: 'Desasignación exitosa',
      text: 'El deportista fue desasignado correctamente.',
      timer: 1500,
      showConfirmButton: false
    })

  } catch (error) {
    console.error('Error desasignando deportista:', error)
    await Swal.fire({
      icon: 'error',
      title: 'Error al desasignar',
      text: 'No pudimos completar la desasignación. Intenta nuevamente.'
    })
  }
}

const crearNuevoDeportista = () => {
  // Redirigir al formulario de registro de deportista
  // con un parámetro para indicar que se asignará automáticamente al acudiente
  router.push({
    path: '/registrar-deportista-form',
    query: { asignarAcudiente: 'true', idAcudiente: authStore.user?.id_usuario }
  })
}
</script>

