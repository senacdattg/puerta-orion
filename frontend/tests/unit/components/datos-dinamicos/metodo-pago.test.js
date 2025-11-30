import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import MetodoPago from '@/components/datos-dinamicos/metodo-pago.vue'

describe('MetodoPago', () => {
  let pinia
  let wrapper

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    vi.clearAllMocks()
  })

  const createWrapper = (props = {}) => {
    return mount(MetodoPago, {
      props: {
        modelValue: { nombre: '', estado: true },
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

    it('should render estado select', () => {
      wrapper = createWrapper()
      const select = wrapper.find('select')
      expect(select.exists()).toBe(true)
    })
  })

  describe('Data Normalization', () => {
    it('should normalize nombre to uppercase', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('efectivo')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('EFECTIVO')
    })

    it('should handle estado boolean', async () => {
      wrapper = createWrapper({ modelValue: { nombre: '', estado: false } })
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.estado).toBe(false)
    })

    it('should default estado to true', () => {
      wrapper = createWrapper({ modelValue: { nombre: '' } })
      expect(wrapper.vm.localForm.estado).toBe(true)
    })
  })

  describe('v-model', () => {
    it('should emit update:modelValue when fields change', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('Transferencia')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    })
  })
})

