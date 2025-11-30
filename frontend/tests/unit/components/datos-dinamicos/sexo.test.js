import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Sexo from '@/components/datos-dinamicos/sexo.vue'

describe('Sexo', () => {
  let pinia
  let wrapper

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    vi.clearAllMocks()
  })

  const createWrapper = (props = {}) => {
    return mount(Sexo, {
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
      expect(nombreInput.attributes('placeholder')).toBe('Nombre')
    })
  })

  describe('Data Normalization', () => {
    it('should normalize nombre to uppercase', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('masculino')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('MASCULINO')
    })

    it('should remove invalid characters', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('masculino123@#$')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('MASCULINO')
    })
  })

  describe('v-model', () => {
    it('should emit update:modelValue when nombre changes', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('Femenino')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0][0]).toEqual({ nombre: 'FEMENINO' })
    })
  })
})

