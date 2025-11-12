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

<style scoped>
.card-deportista {
  background: var(--color-blanco);
  border-radius: var(--radio-borde);
  padding: var(--espaciado-lg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: flex-start;
  gap: var(--espaciado-md);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  border: 1px solid rgba(0, 74, 173, 0.1);
  min-height: 120px;
  overflow: hidden;
}

.card-deportista::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: #FFD600;
  transform: scaleY(0);
  transform-origin: bottom;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-deportista.clickable {
  cursor: pointer;
}

.card-deportista.clickable:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 24px rgba(0, 74, 173, 0.2);
  border-color: #004AAD;
}

.card-deportista.clickable:hover::before {
  transform: scaleY(1);
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: var(--radio-borde);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: var(--tamano-fuente-xxl);
  color: #004AAD;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-deportista.clickable:hover .card-icon {
  transform: scale(1.1) rotate(5deg);
  color: #003d8f;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: var(--tamano-fuente-lg);
  font-weight: var(--peso-fuente-semibold);
  color: var(--color-gris-oscuro);
  margin: 0 0 var(--espaciado-xs) 0;
  font-family: 'Poppins', sans-serif;
}

.card-description {
  font-size: var(--tamano-fuente-sm);
  color: var(--color-gris);
  margin: 0 0 var(--espaciado-sm) 0;
  line-height: 1.5;
}

.card-value {
  font-size: var(--tamano-fuente-xl);
  font-weight: var(--peso-fuente-bold);
  color: #004AAD;
  margin-top: var(--espaciado-xs);
}

.card-arrow {
  position: absolute;
  top: var(--espaciado-md);
  right: var(--espaciado-md);
  color: rgba(108, 117, 125, 0.5);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0.6;
}

.card-deportista.clickable:hover .card-arrow {
  color: #004AAD;
  transform: translateX(6px);
  opacity: 1;
}

/* Responsive */
@media (max-width: 768px) {
  .card-deportista {
    padding: var(--espaciado-md);
    min-height: 100px;
  }

  .card-icon {
    width: 50px;
    height: 50px;
    font-size: var(--tamano-fuente-xl);
  }

  .card-title {
    font-size: var(--tamano-fuente-base);
  }

  .card-description {
    font-size: var(--tamano-fuente-xs);
  }
}
</style>

