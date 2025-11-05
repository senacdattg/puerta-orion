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

const props = defineProps({
  modelValue: { type: Object, default: () => ({ nombre: '' }) }
})

const emit = defineEmits(['update:modelValue'])

const localForm = ref({ nombre: props.modelValue?.nombre || '' })

// Solo actualizar localForm si el valor realmente cambió desde el padre
watch(() => props.modelValue, (newVal) => {
  const nuevoNombre = newVal?.nombre || ''
  if (localForm.value.nombre !== nuevoNombre) {
    localForm.value = { nombre: nuevoNombre }
  }
}, { deep: true })

// Solo emitir si el valor realmente cambió
watch(() => localForm.value.nombre, (newVal) => {
  const valorActual = props.modelValue?.nombre || ''
  if (newVal !== valorActual) {
    emit('update:modelValue', { nombre: newVal })
  }
})
</script>

<style scoped>
.campo-nombre-centrado {
  max-width: 400px;
  margin: 0 auto;
  grid-template-columns: 1fr;
}

.campo-nombre-centrado input {
  text-align: center;
}
</style>

