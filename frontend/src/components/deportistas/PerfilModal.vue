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
                <label>Nombre completo:</label>
                <span>{{ usuario?.persona?.nombre_completo || 'No disponible' }}</span>
              </div>
              <div class="info-row">
                <label>Documento:</label>
                <span>{{ usuario?.persona?.documento || 'No disponible' }}</span>
              </div>
              <div class="info-row">
                <label>Correo electrónico:</label>
                <span>{{ usuario?.persona?.correo_electronico || 'No disponible' }}</span>
              </div>
              <div class="info-row">
                <label>Teléfono:</label>
                <span>{{ usuario?.persona?.telefono || 'No disponible' }}</span>
              </div>
              <div class="info-row">
                <label>Fecha de nacimiento:</label>
                <span>{{ formatearFecha(usuario?.persona?.fecha_nacimiento) || 'No disponible' }}</span>
              </div>
              <div class="info-row">
                <label>Tipo sanguíneo:</label>
                <span>{{ tipoSangre || 'No disponible' }}</span>
              </div>
              <div class="info-row">
                <label>Ciudad:</label>
                <span>{{ ciudad || 'No disponible' }}</span>
              </div>
              <div v-if="diagnostico" class="info-row">
                <label>Diagnóstico:</label>
                <span>{{ diagnostico }}</span>
              </div>
            </div>
          </div>

          <div v-else class="perfil-editar">
            <form @submit.prevent="guardarCambios" class="form-editar">
              <div class="form-group">
                <label>Correo electrónico:</label>
                <input
                  type="email"
                  v-model="formData.correo_electronico"
                  class="form-control"
                  required
                />
              </div>
              <div class="form-group">
                <label>Teléfono:</label>
                <input
                  type="tel"
                  v-model="formData.telefono"
                  class="form-control"
                />
              </div>
              <div class="form-group">
                <label>Dirección:</label>
                <textarea
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

    // Emitir evento de actualización
    emit('update', formData.value)

    editando.value = false
  } catch (error) {
    console.error('Error al guardar cambios:', error)
    alert('Error al guardar los cambios. Por favor, inténtalo de nuevo.')
  } finally {
    guardando.value = false
  }
}

const formatearFecha = (fecha) => {
  if (!fecha) return null
  try {
    const date = new Date(fecha)
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

<style scoped>
.perfil-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: var(--espaciado-md);
}

.perfil-modal {
  background: var(--color-blanco);
  border-radius: var(--radio-borde);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: var(--sombra-fuerte);
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  padding: var(--espaciado-lg);
  border-bottom: 1px solid var(--color-gris-medio);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  margin: 0;
  font-size: var(--tamano-fuente-xl);
  font-weight: var(--peso-fuente-semibold);
  color: var(--color-gris-oscuro);
  display: flex;
  align-items: center;
  gap: var(--espaciado-sm);
  font-family: 'Poppins', sans-serif;
}

.modal-title i {
  color: #004AAD;
}

.modal-close {
  background: none;
  border: none;
  font-size: var(--tamano-fuente-xl);
  color: var(--color-gris);
  cursor: pointer;
  padding: var(--espaciado-xs);
  transition: var(--transicion);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radio-borde-pequeno);
}

.modal-close:hover {
  background: var(--color-gris-claro);
  color: var(--color-gris-oscuro);
}

.modal-content {
  padding: var(--espaciado-lg);
  overflow-y: auto;
  flex: 1;
}

.info-section h4 {
  margin: 0 0 var(--espaciado-md) 0;
  color: #004AAD;
  font-size: var(--tamano-fuente-lg);
  font-weight: var(--peso-fuente-semibold);
  font-family: 'Poppins', sans-serif;
}

.info-row {
  display: flex;
  padding: var(--espaciado-sm) 0;
  border-bottom: 1px solid var(--color-gris-claro);
}

.info-row:last-child {
  border-bottom: none;
}

.info-row label {
  font-weight: var(--peso-fuente-semibold);
  color: var(--color-gris-oscuro);
  min-width: 150px;
  font-family: 'Poppins', sans-serif;
}

.info-row span {
  color: var(--color-gris);
}

.form-group {
  margin-bottom: var(--espaciado-md);
}

.form-group label {
  display: block;
  margin-bottom: var(--espaciado-xs);
  font-weight: var(--peso-fuente-semibold);
  color: var(--color-gris-oscuro);
  font-family: 'Poppins', sans-serif;
}

.form-control {
  width: 100%;
  padding: var(--espaciado-sm);
  border: 1px solid var(--color-gris-medio);
  border-radius: var(--radio-borde-pequeno);
  font-size: var(--tamano-fuente-base);
  font-family: 'Poppins', sans-serif;
  transition: var(--transicion);
}

.form-control:focus {
  outline: none;
  border-color: #004AAD;
  box-shadow: 0 0 0 3px rgba(0, 74, 173, 0.1);
}

.form-actions {
  display: flex;
  gap: var(--espaciado-md);
  justify-content: flex-end;
  margin-top: var(--espaciado-lg);
}

.modal-footer {
  padding: var(--espaciado-lg);
  border-top: 1px solid var(--color-gris-medio);
  display: flex;
  justify-content: flex-end;
}

.btn {
  padding: var(--espaciado-sm) var(--espaciado-lg);
  border: none;
  border-radius: var(--radio-borde-pequeno);
  font-size: var(--tamano-fuente-base);
  font-weight: var(--peso-fuente-semibold);
  cursor: pointer;
  transition: var(--transicion);
  font-family: 'Poppins', sans-serif;
  display: inline-flex;
  align-items: center;
  gap: var(--espaciado-xs);
}

.btn-primary {
  background: #004AAD;
  color: var(--color-blanco);
}

.btn-primary:hover:not(:disabled) {
  background: #003d8f;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--color-gris-medio);
  color: var(--color-gris-oscuro);
}

.btn-secondary:hover {
  background: var(--color-gris);
  color: var(--color-blanco);
}

/* Transiciones */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transicion);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .perfil-modal {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }

  .info-row {
    flex-direction: column;
    gap: var(--espaciado-xs);
  }

  .info-row label {
    min-width: auto;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    flex: 1;
  }
}
</style>

