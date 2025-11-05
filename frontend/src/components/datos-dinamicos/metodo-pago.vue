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

const localForm = ref({
  nombre: props.modelValue?.nombre || '',
  estado: props.modelValue?.estado ?? true
})

// Solo actualizar localForm si el valor realmente cambió desde el padre
watch(() => props.modelValue, (newVal) => {
  const nuevoNombre = newVal?.nombre || ''
  const nuevoEstado = newVal?.estado ?? true
  
  if (localForm.value.nombre !== nuevoNombre || localForm.value.estado !== nuevoEstado) {
    localForm.value = {
      nombre: nuevoNombre,
      estado: nuevoEstado
    }
  }
}, { deep: true })

// Solo emitir si el valor realmente cambió
watch([() => localForm.value.nombre, () => localForm.value.estado], 
  ([nombre, estado]) => {
    const valorActual = props.modelValue
    if (nombre !== (valorActual?.nombre || '') || 
        estado !== (valorActual?.estado ?? true)) {
      emit('update:modelValue', { nombre, estado })
    }
  }
)
</script>

<style scoped>
</style>

