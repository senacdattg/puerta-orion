import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import TipoDocumento from '@/components/datos-dinamicos/tipo-documento.vue'

describe('TipoDocumento', () => {
  let pinia
  let wrapper

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    vi.clearAllMocks()
  })

  const createWrapper = (props = {}) => {
    return mount(TipoDocumento, {
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
      
      await nombreInput.setValue('cedula de ciudadania')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('CEDULA DE CIUDADANIA')
    })

    it('should remove invalid characters from nombre', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('Cédula123@#$')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('CÉDULA')
    })

    it('should remove multiple spaces', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('Cédula    de    ciudadanía')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('CÉDULA DE CIUDADANÍA')
    })

    it('should trim start spaces', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('   Cédula')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('CÉDULA')
    })
  })

  describe('v-model', () => {
    it('should emit update:modelValue when nombre changes', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('Cédula')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0][0]).toEqual({ nombre: 'CÉDULA' })
    })

    it('should update from modelValue prop', async () => {
      wrapper = createWrapper({ modelValue: { nombre: 'TARJETA DE IDENTIDAD' } })
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('TARJETA DE IDENTIDAD')
    })

    it('should handle empty modelValue', () => {
      wrapper = createWrapper({ modelValue: {} })
      expect(wrapper.vm.localForm.nombre).toBe('')
    })

    it('should handle null modelValue', () => {
      wrapper = createWrapper({ modelValue: null })
      expect(wrapper.vm.localForm.nombre).toBe('')
    })
  })

  describe('Watch Behavior', () => {
    it('should update localForm when modelValue prop changes', async () => {
      wrapper = createWrapper({ modelValue: { nombre: 'CEDULA' } })
      await wrapper.vm.$nextTick()

      await wrapper.setProps({ modelValue: { nombre: 'TARJETA' } })
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('TARJETA')
    })

    it('should not update if value has not changed', async () => {
      wrapper = createWrapper({ modelValue: { nombre: 'CEDULA' } })
      await wrapper.vm.$nextTick()

      const initialForm = { ...wrapper.vm.localForm }
      
      await wrapper.setProps({ modelValue: { nombre: 'CEDULA' } })
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe(initialForm.nombre)
    })
  })
})

