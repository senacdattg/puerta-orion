<template>
  <div>
    <div class="fila-texto">
      <input
        v-model.trim="localForm.nombre"
        type="text"
        placeholder="Nombre"
        required
      />
      <select v-model="localForm.estado" required>
        <option value="" disabled>Estado *</option>
        <option :value="true">Activo</option>
        <option :value="false">Inactivo</option>
      </select>
    </div>
    <hr class="form-divider" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ nombre: '', estado: true })
  }
})

const emit = defineEmits(['update:modelValue'])

const LOCALE_COL = 'es-CO'

function normalizarNombre(valor = '') {
  const mayus = valor ? valor.toLocaleUpperCase(LOCALE_COL) : ''
  return mayus.replace(/[^A-ZÁÉÍÓÚÜÑ\s'-]/g, '').replace(/\s{2,}/g, ' ').trimStart() // NOSONAR: S7781 - replaceAll() no acepta regex
}

const localForm = ref({
  nombre: normalizarNombre(props.modelValue?.nombre || ''),
  estado: props.modelValue?.estado ?? true
})

// Flag to prevent update cycle when emitting changes from child
const isUpdatingFromChild = ref(false)

// Only update localForm if the value really changed from parent (not from our own emission)
watch(() => props.modelValue, (newVal) => {
  if (isUpdatingFromChild.value) {
    return
  }

  const nuevoNombre = normalizarNombre(newVal?.nombre || '')
  const nuevoEstado = newVal?.estado ?? true

  if (localForm.value.nombre !== nuevoNombre || localForm.value.estado !== nuevoEstado) {
    localForm.value = {
      nombre: nuevoNombre,
      estado: nuevoEstado
    }
  }
}, { deep: true })

// Normalize and emit changes
watch([() => localForm.value.nombre, () => localForm.value.estado],
  ([nombre, estado]) => {
    const nombreNormalizado = normalizarNombre(nombre)
    
    // If normalization changed the value, update localForm and continue to emit
    if (nombreNormalizado !== nombre) {
      localForm.value.nombre = nombreNormalizado
    }

    const valorActual = props.modelValue
    const nombreActual = normalizarNombre(valorActual?.nombre || '')
    const estadoActual = valorActual?.estado ?? true

    // Emit if there's a real change
    if (nombreNormalizado !== nombreActual || estado !== estadoActual) {
      isUpdatingFromChild.value = true
      emit('update:modelValue', { nombre: nombreNormalizado, estado })
      // Reset flag after emit completes
      setTimeout(() => {
        isUpdatingFromChild.value = false
      }, 0)
    }
  }
)
</script>


