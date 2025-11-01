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
    <div class="fila-texto">
      <textarea 
        v-model.trim="localForm.descripcion" 
        placeholder="Descripción (opcional)" 
        rows="3" 
        style="grid-column: 1 / -1;"
      ></textarea>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { 
    type: Object, 
    default: () => ({ nombre: '', descripcion: '' }) 
  }
})

const emit = defineEmits(['update:modelValue'])

const localForm = ref({
  nombre: props.modelValue?.nombre || '',
  descripcion: props.modelValue?.descripcion || ''
})

watch(() => props.modelValue, (newVal) => {
  localForm.value = {
    nombre: newVal?.nombre || '',
    descripcion: newVal?.descripcion || ''
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

.fila-texto textarea {
  grid-column: 1 / -1;
  min-height: 80px;
  resize: vertical;
}
</style>

