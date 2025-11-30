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

// Solo actualizar localForm si el valor realmente cambió desde el padre
watch(() => props.modelValue, (newVal) => {
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

// Normalizar y emitir cuando cambian los campos
watch([() => localForm.value.nombre, () => localForm.value.descripcion],
  ([nombre, descripcion]) => {
    const nombreNormalizado = normalizarNombre(nombre)
    const descripcionNormalizada = normalizarDescripcion(descripcion)

    if (nombreNormalizado !== nombre) {
      localForm.value.nombre = nombreNormalizado
      return
    }

    if (descripcionNormalizada !== descripcion) {
      localForm.value.descripcion = descripcionNormalizada
      return
    }

    const actualNombre = normalizarNombre(props.modelValue?.nombre || '')
    const actualDescripcion = normalizarDescripcion(props.modelValue?.descripcion || '')

    if (nombreNormalizado !== actualNombre || descripcionNormalizada !== actualDescripcion) {
      emit('update:modelValue', { nombre: nombreNormalizado, descripcion: descripcionNormalizada })
    }
  }
)
</script>

