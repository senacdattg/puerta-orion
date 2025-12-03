/**
 * Composable for dynamic data forms (tipo-documento, sexo, ciudad, etc.)
 * Provides reusable form logic following DRY principles
 */

import { ref, watch } from 'vue'
import { normalizarNombre, normalizarNombreCiudad } from '@/utils/normalization'

/**
 * Creates a reactive form for dynamic data with name normalization
 * @param {Object} props - Component props
 * @param {Function} emit - Component emit function
 * @param {string} normalizationType - Type of normalization: 'standard' | 'city'
 * @returns {Object} Form state and watchers
 */
export function useDynamicDataForm(props, emit, normalizationType = 'standard') {
  const normalizar = normalizationType === 'city' ? normalizarNombreCiudad : normalizarNombre

  const localForm = ref({
    nombre: normalizar(props.modelValue?.nombre || '')
  })

  // Flag to prevent update cycle when emitting changes from child
  const isUpdatingFromChild = ref(false)

  // Watch for changes from parent (only if not from our own emission)
  watch(() => props.modelValue, (newVal) => {
    if (isUpdatingFromChild.value) {
      return
    }

    const nuevoNombre = normalizar(newVal?.nombre || '')
    if (localForm.value.nombre !== nuevoNombre) {
      localForm.value = { nombre: nuevoNombre }
    }
  }, { deep: true })

  // Normalize and emit when input changes
  watch(() => localForm.value.nombre, (nuevoValor) => {
    const normalizado = normalizar(nuevoValor)
    
    // If normalization changed the value, update localForm and continue to emit
    if (normalizado !== nuevoValor) {
      localForm.value.nombre = normalizado
    }

    const actual = normalizar(props.modelValue?.nombre || '')
    if (normalizado !== actual) {
      isUpdatingFromChild.value = true
      emit('update:modelValue', { nombre: normalizado })
      // Reset flag after emit completes
      setTimeout(() => {
        isUpdatingFromChild.value = false
      }, 0)
    }
  })

  return {
    localForm
  }
}

