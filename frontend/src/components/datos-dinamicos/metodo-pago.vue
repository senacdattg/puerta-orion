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

// Solo actualizar localForm si el valor realmente cambió desde el padre
watch(() => props.modelValue, (newVal) => {
  const nuevoNombre = normalizarNombre(newVal?.nombre || '')
  const nuevoEstado = newVal?.estado ?? true

  if (localForm.value.nombre !== nuevoNombre || localForm.value.estado !== nuevoEstado) {
    localForm.value = {
      nombre: nuevoNombre,
      estado: nuevoEstado
    }
  }
}, { deep: true })

// Normalizar y emitir cambios
watch([() => localForm.value.nombre, () => localForm.value.estado],
  ([nombre, estado]) => {
    const nombreNormalizado = normalizarNombre(nombre)
    if (nombreNormalizado !== nombre) {
      localForm.value.nombre = nombreNormalizado
      return
    }

    const valorActual = props.modelValue
    const nombreActual = normalizarNombre(valorActual?.nombre || '')
    const estadoActual = valorActual?.estado ?? true

    if (nombreNormalizado !== nombreActual || estado !== estadoActual) {
      emit('update:modelValue', { nombre: nombreNormalizado, estado })
    }
  }
)
</script>


