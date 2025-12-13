<template>
  <div>
    <div class="fila-texto">
      <input
        v-model.trim="localForm.nombre"
        type="text"
        placeholder="Nombre"
        required
      />
      <textarea
        v-model.trim="localForm.descripcion"
        placeholder="Descripción"
        rows="3"
        required
      ></textarea>
    </div>
    <hr class="form-divider" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

defineOptions({ name: 'DatosDinamicosTipoEvento' })

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ nombre: '', descripcion: '' })
  }
})

const emit = defineEmits(['update:modelValue'])

const LOCALE_COL = 'es-CO'
const MAX_DESCRIPCION = 500

function normalizarNombre(valor = '') {
  const mayus = valor ? valor.toLocaleUpperCase(LOCALE_COL) : ''
  // NOSONAR: S7781 - replaceAll() no acepta regex, necesitamos replace() para patrones complejos
  return mayus.replace(/[^A-ZÁÉÍÓÚÜÑ\s'-]/g, '').replace(/\s{2,}/g, ' ').trimStart() // NOSONAR: S7781
}

function normalizarDescripcion(valor = '') {
  if (!valor) return ''
  const mayus = valor.toLocaleUpperCase(LOCALE_COL)
  return mayus.replace(/\s{2,}/g, ' ').trim().slice(0, MAX_DESCRIPCION) // NOSONAR: S7781
}

const localForm = ref({
  nombre: normalizarNombre(props.modelValue?.nombre || ''),
  descripcion: normalizarDescripcion(props.modelValue?.descripcion || '')
})

// Flag to prevent update cycle when emitting changes from child
const isUpdatingFromChild = ref(false)

// Only update localForm if the value really changed from parent (not from our own emission)
watch(() => props.modelValue, (newVal) => {
  if (isUpdatingFromChild.value) {
    return
  }

  const nuevoNombre = normalizarNombre(newVal?.nombre || '')
  const nuevaDescripcion = normalizarDescripcion(newVal?.descripcion || '')

  if (localForm.value.nombre !== nuevoNombre ||
      localForm.value.descripcion !== nuevaDescripcion) {
    localForm.value = {
      nombre: nuevoNombre,
      descripcion: nuevaDescripcion
    }
  }
}, { deep: true })

// Normalize and emit when fields change
watch([() => localForm.value.nombre, () => localForm.value.descripcion],
  ([nombre, descripcion]) => {
    const nombreNormalizado = normalizarNombre(nombre)
    const descripcionNormalizada = normalizarDescripcion(descripcion)

    // If normalization changed the value, update localForm and continue to emit
    if (nombreNormalizado !== nombre) {
      localForm.value.nombre = nombreNormalizado
    }

    if (descripcionNormalizada !== descripcion) {
      localForm.value.descripcion = descripcionNormalizada
    }

    const actualNombre = normalizarNombre(props.modelValue?.nombre || '')
    const actualDescripcion = normalizarDescripcion(props.modelValue?.descripcion || '')

    // Emit if there's a real change
    if (nombreNormalizado !== actualNombre || descripcionNormalizada !== actualDescripcion) {
      isUpdatingFromChild.value = true
      emit('update:modelValue', { nombre: nombreNormalizado, descripcion: descripcionNormalizada })
      // Reset flag after emit completes
      setTimeout(() => {
        isUpdatingFromChild.value = false
      }, 0)
    }
  }
)
</script>

