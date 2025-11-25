<template>
  <div>
    <div class="fila-texto campo-nombre-centrado">
      <input
        v-model.trim="localForm.nombre"
        type="text"
        placeholder="Nombre"
        required
      />
    </div>
    <hr class="form-divider" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

// Definir nombre del componente para cumplir con la guía de estilo de Vue
defineOptions({
  name: 'SexoFormulario'
})

const props = defineProps({
  modelValue: { type: Object, default: () => ({ nombre: '' }) }
})

const emit = defineEmits(['update:modelValue'])

const LOCALE_COL = 'es-CO'

function normalizarNombre(valor = '') {
  const mayus = valor ? valor.toLocaleUpperCase(LOCALE_COL) : ''
  return mayus.replace(/[^A-ZÁÉÍÓÚÜÑ\s'-]/g, '').replace(/\s{2,}/g, ' ').trimStart() // NOSONAR: S7781 - replaceAll() no acepta regex
}

const localForm = ref({ nombre: normalizarNombre(props.modelValue?.nombre || '') })

// Solo actualizar localForm si el valor realmente cambió desde el padre
watch(() => props.modelValue, (newVal) => {
  const nuevoNombre = normalizarNombre(newVal?.nombre || '')
  if (localForm.value.nombre !== nuevoNombre) {
    localForm.value = { nombre: nuevoNombre }
  }
}, { deep: true })

// Normalizar y emitir cuando cambia el input
watch(() => localForm.value.nombre, (nuevoValor) => {
  const normalizado = normalizarNombre(nuevoValor)
  if (normalizado !== nuevoValor) {
    localForm.value.nombre = normalizado
    return
  }

  const actual = normalizarNombre(props.modelValue?.nombre || '')
  if (normalizado !== actual) {
    emit('update:modelValue', { nombre: normalizado })
  }
})
</script>


