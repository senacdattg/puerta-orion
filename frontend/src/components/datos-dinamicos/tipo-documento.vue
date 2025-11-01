<template>
  <div class="fila-texto campo-nombre-centrado">
    <input 
      v-model.trim="localForm.nombre" 
      type="text" 
      placeholder="Nombre *" 
      required 
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Object, default: () => ({ nombre: '' }) }
})

const emit = defineEmits(['update:modelValue'])

const localForm = ref({ nombre: props.modelValue?.nombre || '' })

watch(() => props.modelValue, (newVal) => {
  localForm.value = { nombre: newVal?.nombre || '' }
}, { deep: true })

watch(localForm, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })
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

