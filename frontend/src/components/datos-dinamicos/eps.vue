<template>
  <div>
    <div class="fila-texto campo-nombre-centrado">
      <input 
        v-model.trim="localForm.nombre" 
        type="text" 
        placeholder="Nombre *" 
        required 
      />
    </div>
    <div class="fila-texto campo-nombre-centrado">
      <input 
        v-model.trim="localForm.codigo" 
        type="text" 
        placeholder="Código EPS" 
      />
      <select v-model="localForm.estado" required>
        <option value="" disabled>Estado *</option>
        <option :value="true">Activo</option>
        <option :value="false">Inactivo</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { 
    type: Object, 
    default: () => ({ nombre: '', codigo: '', estado: true }) 
  }
})

const emit = defineEmits(['update:modelValue'])

const localForm = ref({
  nombre: props.modelValue?.nombre || '',
  codigo: props.modelValue?.codigo || '',
  estado: props.modelValue?.estado ?? true
})

watch(() => props.modelValue, (newVal) => {
  localForm.value = {
    nombre: newVal?.nombre || '',
    codigo: newVal?.codigo || '',
    estado: newVal?.estado ?? true
  }
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

