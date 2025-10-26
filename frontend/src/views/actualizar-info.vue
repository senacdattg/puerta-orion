<template>
  <div class="actualizar-info-page">
    <div class="actualizar-container">
      <div class="actualizar-header">
        <h1 class="actualizar-title">
          <i class="fas fa-edit"></i>
          Actualizar Información
        </h1>
        <p class="actualizar-subtitle">Modifica tus datos personales</p>
      </div>

      <div class="actualizar-content">
        <form @submit.prevent="actualizarInformacion" class="form-actualizar">
          <div class="form-section">
            <h3>Información Personal</h3>

            <div class="form-group">
              <label for="primer_nombre">Primer Nombre *</label>
              <input
                type="text"
                id="primer_nombre"
                v-model="formData.primer_nombre"
                required
                class="form-input"
              >
            </div>

            <div class="form-group">
              <label for="primer_apellido">Primer Apellido *</label>
              <input
                type="text"
                id="primer_apellido"
                v-model="formData.primer_apellido"
                required
                class="form-input"
              >
            </div>

            <div class="form-group">
              <label for="correo_electronico">Correo Electrónico *</label>
              <input
                type="email"
                id="correo_electronico"
                v-model="formData.correo_electronico"
                required
                class="form-input"
              >
            </div>

            <div class="form-group">
              <label for="telefono">Teléfono</label>
              <input
                type="tel"
                id="telefono"
                v-model="formData.telefono"
                class="form-input"
              >
            </div>

            <div class="form-group">
              <label for="direccion">Dirección</label>
              <textarea
                id="direccion"
                v-model="formData.direccion"
                class="form-textarea"
                rows="3"
              ></textarea>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="cancelar" class="btn-cancel">
              <i class="fas fa-times"></i>
              Cancelar
            </button>
            <button type="submit" class="btn-save" :disabled="guardando">
              <i class="fas fa-save"></i>
              {{ guardando ? 'Guardando...' : 'Guardar Cambios' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const guardando = ref(false)

const formData = ref({
  primer_nombre: '',
  primer_apellido: '',
  correo_electronico: '',
  telefono: '',
  direccion: ''
})

onMounted(() => {
  // Cargar datos actuales del usuario
  if (authStore.user?.persona) {
    const persona = authStore.user.persona
    formData.value = {
      primer_nombre: persona.primer_nombre || '',
      primer_apellido: persona.primer_apellido || '',
      correo_electronico: persona.correo_electronico || '',
      telefono: persona.telefono || '',
      direccion: persona.direccion || ''
    }
  }
})

const actualizarInformacion = async () => {
  guardando.value = true

  try {
    // Aquí se implementaría la llamada al backend
    console.log('Actualizando información:', formData.value)

    // Simular llamada API
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Mostrar mensaje de éxito
    alert('Información actualizada correctamente')

    // Redirigir al perfil
    router.push('/perfil')

  } catch (error) {
    console.error('Error actualizando información:', error)
    alert('Error al actualizar la información')
  } finally {
    guardando.value = false
  }
}

const cancelar = () => {
  router.push('/perfil')
}
</script>

<style scoped>
.actualizar-info-page {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 2rem 1rem;
}

.actualizar-container {
  max-width: 600px;
  margin: 0 auto;
}

.actualizar-header {
  text-align: center;
  margin-bottom: 2rem;
}

.actualizar-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.actualizar-subtitle {
  font-size: 1.1rem;
  color: #6c757d;
  margin: 0;
}

.actualizar-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.form-section {
  margin-bottom: 2rem;
}

.form-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #f8f9fa;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #007bff;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.btn-cancel,
.btn-save {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background: #5a6268;
}

.btn-save {
  background: #28a745;
  color: white;
}

.btn-save:hover:not(:disabled) {
  background: #218838;
}

.btn-save:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .actualizar-info-page {
    padding: 1rem 0.5rem;
  }

  .actualizar-title {
    font-size: 2rem;
  }

  .actualizar-content {
    padding: 1.5rem;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn-cancel,
  .btn-save {
    width: 100%;
    justify-content: center;
  }
}
</style>

