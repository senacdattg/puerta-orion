import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Eps from '@/components/datos-dinamicos/eps.vue'

describe('Eps', () => {
  let pinia
  let wrapper

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    vi.clearAllMocks()
  })

  const createWrapper = (props = {}) => {
    return mount(Eps, {
      props: {
        modelValue: { nombre: '', codigo: '', estado: true },
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
      const inputs = wrapper.findAll('input[type="text"]')
      expect(inputs.length).toBeGreaterThan(0)
      expect(inputs[0].attributes('placeholder')).toBe('Nombre')
    })

    it('should render codigo input', () => {
      wrapper = createWrapper()
      const inputs = wrapper.findAll('input[type="text"]')
      expect(inputs.length).toBe(2)
      expect(inputs[1].attributes('placeholder')).toBe('Código EPS')
    })

    it('should render estado select', () => {
      wrapper = createWrapper()
      const select = wrapper.find('select')
      expect(select.exists()).toBe(true)
      const options = wrapper.findAll('option')
      expect(options.length).toBe(3) // disabled placeholder + Activo + Inactivo
    })
  })

  describe('Data Normalization', () => {
    it('should normalize nombre to uppercase', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.findAll('input[type="text"]')[0]
      
      await nombreInput.setValue('sura')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('SURA')
    })

    it('should normalize codigo to uppercase', async () => {
      wrapper = createWrapper()
      const codigoInput = wrapper.findAll('input[type="text"]')[1]
      
      await codigoInput.setValue('sura123')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.codigo).toBe('SURA123')
    })

    it('should limit codigo length to MAX_CODIGO', async () => {
      wrapper = createWrapper()
      const codigoInput = wrapper.findAll('input[type="text"]')[1]
      
      await codigoInput.setValue('A'.repeat(30))
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.codigo.length).toBeLessThanOrEqual(20)
    })

    it('should remove invalid characters from codigo', async () => {
      wrapper = createWrapper()
      const codigoInput = wrapper.findAll('input[type="text"]')[1]
      
      await codigoInput.setValue('sura@#$%')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.codigo).toBe('SURA')
    })

    it('should handle estado boolean', async () => {
      wrapper = createWrapper({ modelValue: { nombre: '', codigo: '', estado: false } })
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.estado).toBe(false)
    })
  })

  describe('v-model', () => {
    it('should emit update:modelValue when fields change', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.findAll('input[type="text"]')[0]
      
      await nombreInput.setValue('SURA')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0][0]).toHaveProperty('nombre')
    })

    it('should handle codigo_eps as fallback', async () => {
      wrapper = createWrapper({ modelValue: { nombre: '', codigo_eps: 'SURA123', estado: true } })
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.codigo).toBe('SURA123')
    })

    it('should default estado to true', () => {
      wrapper = createWrapper({ modelValue: { nombre: '', codigo: '' } })
      expect(wrapper.vm.localForm.estado).toBe(true)
    })
  })

  describe('Watch Behavior', () => {
    it('should update when modelValue changes', async () => {
      wrapper = createWrapper({ modelValue: { nombre: 'SURA', codigo: '123', estado: true } })
      await wrapper.vm.$nextTick()

      await wrapper.setProps({ modelValue: { nombre: 'NUEVA EPS', codigo: '456', estado: false } })
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('NUEVA EPS')
      expect(wrapper.vm.localForm.codigo).toBe('456')
      expect(wrapper.vm.localForm.estado).toBe(false)
    })
  })
})

