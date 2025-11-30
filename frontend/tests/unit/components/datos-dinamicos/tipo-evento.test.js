import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import TipoEvento from '@/components/datos-dinamicos/tipo-evento.vue'

describe('TipoEvento', () => {
  let pinia
  let wrapper

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    vi.clearAllMocks()
  })

  const createWrapper = (props = {}) => {
    return mount(TipoEvento, {
      props: {
        modelValue: { nombre: '', descripcion: '' },
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

    it('should render descripcion textarea', () => {
      wrapper = createWrapper()
      const descripcionTextarea = wrapper.find('textarea')
      expect(descripcionTextarea.exists()).toBe(true)
      expect(descripcionTextarea.attributes('placeholder')).toBe('Descripción')
    })
  })

  describe('Data Normalization', () => {
    it('should normalize nombre to uppercase', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('torneo local')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('TORNEO LOCAL')
    })

    it('should normalize descripcion to uppercase', async () => {
      wrapper = createWrapper()
      const descripcionTextarea = wrapper.find('textarea')
      
      await descripcionTextarea.setValue('descripción del evento')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.descripcion).toBe('DESCRIPCIÓN DEL EVENTO')
    })

    it('should limit descripcion length to MAX_DESCRIPCION', async () => {
      wrapper = createWrapper()
      const descripcionTextarea = wrapper.find('textarea')
      
      await descripcionTextarea.setValue('A'.repeat(600))
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.descripcion.length).toBeLessThanOrEqual(500)
    })

    it('should remove multiple spaces from descripcion', async () => {
      wrapper = createWrapper()
      const descripcionTextarea = wrapper.find('textarea')
      
      await descripcionTextarea.setValue('Descripción    con    espacios')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.descripcion).toBe('DESCRIPCIÓN CON ESPACIOS')
    })
  })

  describe('v-model', () => {
    it('should emit update:modelValue when fields change', async () => {
      wrapper = createWrapper()
      const nombreInput = wrapper.find('input[type="text"]')
      
      await nombreInput.setValue('Torneo')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0][0]).toHaveProperty('nombre')
    })

    it('should handle empty modelValue', () => {
      wrapper = createWrapper({ modelValue: {} })
      expect(wrapper.vm.localForm.nombre).toBe('')
      expect(wrapper.vm.localForm.descripcion).toBe('')
    })
  })

  describe('Watch Behavior', () => {
    it('should update when modelValue changes', async () => {
      wrapper = createWrapper({ modelValue: { nombre: 'TORNEO', descripcion: 'DESC' } })
      await wrapper.vm.$nextTick()

      await wrapper.setProps({ modelValue: { nombre: 'CAMPEONATO', descripcion: 'NUEVA DESC' } })
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.localForm.nombre).toBe('CAMPEONATO')
      expect(wrapper.vm.localForm.descripcion).toBe('NUEVA DESC')
    })
  })
})

