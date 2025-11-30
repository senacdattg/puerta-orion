<template>
  <transition name="fade">
    <div
      v-if="visible"
      class="perfil-modal-overlay"
      @click.self="cerrarModal"
    >
      <div class="perfil-modal">
        <div class="modal-header">
          <h3 class="modal-title">
            <i class="fas fa-user"></i>
            Mi Perfil
          </h3>
          <button class="modal-close" @click="cerrarModal">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-content">
          <div v-if="!editando" class="perfil-info">
            <div class="info-section">
              <h4>Información Personal</h4>
              <div class="info-row">
                <span class="info-label">Nombre completo:</span>
                <span>{{ usuario?.persona?.nombre_completo || 'No disponible' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Documento:</span>
                <span>{{ usuario?.persona?.documento || 'No disponible' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Correo electrónico:</span>
                <span>{{ usuario?.persona?.correo_electronico || 'No disponible' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Teléfono:</span>
                <span>{{ usuario?.persona?.telefono || 'No disponible' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Fecha de nacimiento:</span>
                <span>{{ formatearFecha(usuario?.persona?.fecha_nacimiento) || 'No disponible' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Tipo sanguíneo:</span>
                <span>{{ tipoSangre || 'No disponible' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Ciudad:</span>
                <span>{{ ciudad || 'No disponible' }}</span>
              </div>
              <div v-if="diagnostico" class="info-row">
                <span class="info-label">Diagnóstico:</span>
                <span>{{ diagnostico }}</span>
              </div>
            </div>
          </div>

          <div v-else class="perfil-editar">
            <form @submit.prevent="guardarCambios" class="form-editar">
              <div class="form-group">
                <label for="correo-electronico-modal">Correo electrónico:</label>
                <input
                  id="correo-electronico-modal"
                  type="email"
                  v-model="formData.correo_electronico"
                  class="form-control"
                  required
                />
              </div>
              <div class="form-group">
                <label for="telefono-modal">Teléfono:</label>
                <input
                  id="telefono-modal"
                  type="tel"
                  v-model="formData.telefono"
                  class="form-control"
                />
              </div>
              <div class="form-group">
                <label for="direccion-modal">Dirección:</label>
                <textarea
                  id="direccion-modal"
                  v-model="formData.direccion"
                  class="form-control"
                  rows="3"
                ></textarea>
              </div>
              <div class="form-actions">
                <button type="button" @click="cancelarEdicion" class="btn btn-secondary">
                  Cancelar
                </button>
                <button type="submit" class="btn btn-primary" :disabled="guardando">
                  <span v-if="guardando">Guardando...</span>
                  <span v-else>Guardar cambios</span>
                </button>
              </div>
            </form>
          </div>
        </div>

        <div class="modal-footer" v-if="!editando">
          <button @click="iniciarEdicion" class="btn btn-primary">
            <i class="fas fa-edit"></i>
            Editar información
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Swal from 'sweetalert2'

defineOptions({
  name: 'PerfilModal'
})

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'update'])

const authStore = useAuthStore()
const editando = ref(false)
const guardando = ref(false)

const usuario = computed(() => authStore.user)

const formData = ref({
  correo_electronico: '',
  telefono: '',
  direccion: ''
})

const tipoSangre = computed(() => {
  return usuario.value?.persona?.tipo_sanguineo?.nombre || null
})

const ciudad = computed(() => {
  return usuario.value?.persona?.ciudad?.nombre || null
})

const diagnostico = computed(() => {
  // Aquí se podría obtener el diagnóstico del deportista si existe
  return null
})

const cerrarModal = () => {
  editando.value = false
  emit('close')
}

const iniciarEdicion = () => {
  formData.value = {
    correo_electronico: usuario.value?.persona?.correo_electronico || '',
    telefono: usuario.value?.persona?.telefono || '',
    direccion: usuario.value?.persona?.direccion || ''
  }
  editando.value = true
}

const cancelarEdicion = () => {
  editando.value = false
}

const guardarCambios = async () => {
  guardando.value = true
  try {
    // Usar el servicio existente para actualizar el perfil
    // Por ahora, actualizamos el store local
    authStore.updateUser({
      persona: {
        ...usuario.value.persona,
        ...formData.value
      }
    })

    emit('update', formData.value)
    editando.value = false
    await Swal.fire({
      icon: 'success',
      title: 'Información actualizada',
      text: 'Perfil guardado correctamente.',
      timer: 1500,
      showConfirmButton: false
    })
  } catch (error) {
    console.error('Error al guardar cambios:', error)
    await Swal.fire({
      icon: 'error',
      title: 'No se pudo guardar',
      text: 'Inténtalo de nuevo.'
    })
  } finally {
    guardando.value = false
  }
}

const formatearFecha = (fecha) => {
  if (!fecha) return null
  try {
    const date = new Date(fecha)
    if (isNaN(date.getTime())) {
      return fecha
    }
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch {
    return fecha
  }
}

watch(() => props.visible, (newValue) => {
  if (!newValue) {
    editando.value = false
  }
})
</script>


