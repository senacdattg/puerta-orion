<template>
  <div>
    <div class="fila-texto">
      <input
        v-model.trim="localForm.nombre"
        type="text"
        placeholder="Nombre"
        required
      />
      <input
        v-model.trim="localForm.codigo"
        type="text"
        placeholder="Código EPS"
      />
    </div>
    <hr class="form-divider" />
    <div class="fila-texto campo-nombre-centrado">
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
    default: () => ({ nombre: '', codigo: '', estado: true })
  }
})

const emit = defineEmits(['update:modelValue'])

const LOCALE_COL = 'es-CO'
const MAX_CODIGO = 20

function normalizarNombre(valor = '') {
  const mayus = valor ? valor.toLocaleUpperCase(LOCALE_COL) : ''
  return mayus.replace(/[^A-ZÁÉÍÓÚÜÑ\s'-]/g, '').replace(/\s{2,}/g, ' ').trimStart()
}

function normalizarCodigo(valor = '') {
  if (!valor) return ''
  const mayus = valor.toLocaleUpperCase(LOCALE_COL)
  return mayus.replace(/[^A-Z0-9\-]/g, '').slice(0, MAX_CODIGO)
}

const localForm = ref({
  nombre: normalizarNombre(props.modelValue?.nombre || ''),
  codigo: normalizarCodigo(props.modelValue?.codigo || ''),
  estado: props.modelValue?.estado ?? true
})

// Solo actualizar localForm si el valor realmente cambió desde el padre
watch(() => props.modelValue, (newVal) => {
  const nuevoNombre = normalizarNombre(newVal?.nombre || '')
  const nuevoCodigo = normalizarCodigo(newVal?.codigo || '')
  const nuevoEstado = newVal?.estado ?? true

  if (localForm.value.nombre !== nuevoNombre ||
      localForm.value.codigo !== nuevoCodigo ||
      localForm.value.estado !== nuevoEstado) {
    localForm.value = {
      nombre: nuevoNombre,
      codigo: nuevoCodigo,
      estado: nuevoEstado
    }
  }
}, { deep: true })

// Normalizar y emitir cuando cambian los campos
watch([() => localForm.value.nombre, () => localForm.value.codigo, () => localForm.value.estado],
  ([nombre, codigo, estado]) => {
    const nombreNormalizado = normalizarNombre(nombre)
    const codigoNormalizado = normalizarCodigo(codigo)

    if (nombreNormalizado !== nombre) {
      localForm.value.nombre = nombreNormalizado
      return
    }

    if (codigoNormalizado !== codigo) {
      localForm.value.codigo = codigoNormalizado
      return
    }

    const valorActual = props.modelValue
    const nombreActual = normalizarNombre(valorActual?.nombre || '')
    const codigoActual = normalizarCodigo(valorActual?.codigo || '')
    const estadoActual = valorActual?.estado ?? true

    if (nombreNormalizado !== nombreActual ||
        codigoNormalizado !== codigoActual ||
        estado !== estadoActual) {
      emit('update:modelValue', {
        nombre: nombreNormalizado,
        codigo: codigoNormalizado,
        estado
      })
    }
  }
)
</script>

<style scoped>
.campo-nombre-centrado {
  max-width: 400px;
  margin: 0 auto;
  grid-template-columns: 1fr;
}

.campo-nombre-centrado select {
  text-align: center;
}
</style>

