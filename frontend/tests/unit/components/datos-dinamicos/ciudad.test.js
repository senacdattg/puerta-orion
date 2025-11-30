import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Ciudad from '@/components/datos-dinamicos/ciudad.vue'

describe('Ciudad', () => {
  let pinia
  let wrapper

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    vi.clearAllMocks()
  })

  const createWrapper = (props = {}) => {
    return mount(Ciudad, {
      props: {
        modelValue: { nombre: '' },
        ...props
      },
      global: {
        plugins: [pinia]
      }
    })
  }

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
    })

    it('should render nombre input', () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      expect(nombreInput.exists()).toBe(true)
    })
  })

  describe('Data Normalization', () => {
    it('should normalize nombre to uppercase', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('bogotá')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('BOGOTÁ')
    })

    it('should allow numbers in nombre', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('Bogotá D.C.')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('BOGOTÁ D.C.')
    })

    it('should allow dots and hyphens', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('San José de Cúcuta')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('SAN JOSÉ DE CÚCUTA')
    })
  })

  describe('v-model', () => {
    it('should emit update:modelValue when nombre changes', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('Medellín')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    })
  })
})

