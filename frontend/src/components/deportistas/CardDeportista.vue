<template>
  <div
    class="card-deportista"
    @click="handleClick"
    :class="{ clickable: clickable }"
  >
    <div class="card-icon" :style="{ backgroundColor: iconBgColor }">
      <i :class="icon"></i>
    </div>
    <div class="card-content">
      <h3 class="card-title">{{ title }}</h3>
      <p class="card-description">{{ description }}</p>
      <div v-if="value !== undefined" class="card-value">
        {{ value }}
      </div>
    </div>
    <div v-if="clickable" class="card-arrow">
      <i class="fas fa-chevron-right"></i>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

defineOptions({
  name: 'CardDeportista'
})

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    default: undefined
  },
  to: {
    type: String,
    default: null
  },
  clickable: {
    type: Boolean,
    default: true
  },
  iconBgColor: {
    type: String,
    default: 'rgba(255, 214, 0, 0.15)'
  }
})

const emit = defineEmits(['click'])

const router = useRouter()

const handleClick = () => {
  if (props.clickable) {
    if (props.to) {
      router.push(props.to)
    }
    emit('click')
  }
}
</script>


