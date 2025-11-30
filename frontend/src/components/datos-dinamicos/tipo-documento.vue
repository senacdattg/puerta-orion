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
import { useDynamicDataForm } from '@/composables/useDynamicDataForm'

const props = defineProps({
  modelValue: { type: Object, default: () => ({ nombre: '' }) }
})

const emit = defineEmits(['update:modelValue'])

const { localForm } = useDynamicDataForm(props, emit, 'standard')
</script>


