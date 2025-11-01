<template>
  <div>
    <div class="fila-texto">
      <input 
        v-model.trim="localForm.nombre_categoria" 
        type="text" 
        placeholder="Nombre de Categoría *" 
        required 
      />
      <input 
        v-model.number="localForm.edad_minima" 
        type="number" 
        placeholder="Edad Mínima *" 
        required 
        min="0" 
      />
    </div>
    <div class="fila-texto">
      <input 
        v-model.number="localForm.edad_maxima" 
        type="number" 
        placeholder="Edad Máxima *" 
        required 
        min="0" 
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
    default: () => ({ 
      nombre_categoria: '', 
      edad_minima: null, 
      edad_maxima: null, 
      estado: true 
    }) 
  }
})

const emit = defineEmits(['update:modelValue'])

const localForm = ref({
  nombre_categoria: props.modelValue?.nombre_categoria || '',
  edad_minima: props.modelValue?.edad_minima || null,
  edad_maxima: props.modelValue?.edad_maxima || null,
  estado: props.modelValue?.estado ?? true
})

watch(() => props.modelValue, (newVal) => {
  localForm.value = {
    nombre_categoria: newVal?.nombre_categoria || '',
    edad_minima: newVal?.edad_minima || null,
    edad_maxima: newVal?.edad_maxima || null,
    estado: newVal?.estado ?? true
  }
}, { deep: true })

watch(localForm, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })
</script>

<style scoped>
/* Los estilos de .fila-texto vienen de los CSS globales */
</style>

