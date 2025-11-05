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
        placeholder="Descripción (opcional)" 
        rows="3" 
      ></textarea>
    </div>
    <hr class="form-divider" />
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

// Solo actualizar localForm si el valor realmente cambió desde el padre
watch(() => props.modelValue, (newVal) => {
  const nuevoNombre = newVal?.nombre || ''
  const nuevaDescripcion = newVal?.descripcion || ''
  
  if (localForm.value.nombre !== nuevoNombre || 
      localForm.value.descripcion !== nuevaDescripcion) {
    localForm.value = {
      nombre: nuevoNombre,
      descripcion: nuevaDescripcion
    }
  }
}, { deep: true })

// Solo emitir si el valor realmente cambió
watch([() => localForm.value.nombre, () => localForm.value.descripcion], 
  ([nombre, descripcion]) => {
    const valorActual = props.modelValue
    if (nombre !== (valorActual?.nombre || '') || 
        descripcion !== (valorActual?.descripcion || '')) {
      emit('update:modelValue', { nombre, descripcion })
    }
  }
)
</script>

<style scoped>
.fila-texto {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 20px;
  align-items: start;
}

.fila-texto input {
  width: 100%;
  box-sizing: border-box;
}

.fila-texto textarea {
  width: 100%;
  min-height: 80px;
  resize: vertical;
  box-sizing: border-box;
}
</style>

