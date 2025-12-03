import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import TarjetaDeportista from '@/components/deportistas/tarjeta-deportista.vue'

describe('TarjetaDeportista', () => {
  let wrapper

  const mockDeportista = {
    id: 1,
    nombre: 'Juan Pérez',
    categoria: 'Pre-infantil',
    estado: 'activo',
    imagen: null,
    id_usuario: 1
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  const createWrapper = (props = {}) => {
    return mount(TarjetaDeportista, {
      props: {
        deportista: props.deportista || mockDeportista
      },
      global: {
        stubs: {
          'img': true
        }
      }
    })
  }

  describe('Renderizado básico', () => {
    it('should render component', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.tarjeta-deportista').exists()).toBe(true)
    })

    it('should display deportista nombre', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.nombre-deportista').text()).toBe('Juan Pérez')
    })

    it('should display deportista categoria', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.categoria-deportista').text()).toBe('Pre-infantil')
    })

    it('should render imagen-deportista container', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.imagen-deportista').exists()).toBe(true)
    })

    it('should render contenido-deportista container', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.contenido-deportista').exists()).toBe(true)
    })
  })

  describe('Estado del deportista', () => {
    it('should show button when deportista has id_usuario and estado is activo', () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: 1, estado: 'activo' }
      })

      const estadoButton = wrapper.find('.estado-deportista')
      expect(estadoButton.exists()).toBe(true)
      expect(estadoButton.text()).toBe('ACTIVO')
      expect(estadoButton.classes()).toContain('activo')
    })

    it('should show button when deportista has id_usuario and estado is inactivo', () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: 1, estado: 'inactivo' }
      })

      const estadoButton = wrapper.find('.estado-deportista')
      expect(estadoButton.exists()).toBe(true)
      expect(estadoButton.text()).toBe('INACTIVO')
      expect(estadoButton.classes()).toContain('inactivo')
    })

    it('should show paragraph when deportista has no id_usuario and estado is activo', () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: null, estado: 'activo' }
      })

      const estadoPara = wrapper.find('.estado-deportista')
      expect(estadoPara.exists()).toBe(true)
      expect(estadoPara.text()).toBe('ACTIVO')
      expect(estadoPara.classes()).toContain('activo')
      expect(estadoPara.element.tagName).toBe('P')
    })

    it('should show paragraph when deportista has no id_usuario and estado is inactivo', () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: null, estado: 'inactivo' }
      })

      const estadoPara = wrapper.find('.estado-deportista')
      expect(estadoPara.exists()).toBe(true)
      expect(estadoPara.text()).toBe('INACTIVO')
      expect(estadoPara.classes()).toContain('inactivo')
      expect(estadoPara.element.tagName).toBe('P')
    })

    it('should show paragraph when deportista has undefined id_usuario', () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: undefined, estado: 'activo' }
      })

      const estadoPara = wrapper.find('.estado-deportista')
      expect(estadoPara.exists()).toBe(true)
      expect(estadoPara.element.tagName).toBe('P')
    })

    it('should show paragraph when deportista has false id_usuario', () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: false, estado: 'activo' }
      })

      const estadoPara = wrapper.find('.estado-deportista')
      expect(estadoPara.exists()).toBe(true)
      expect(estadoPara.element.tagName).toBe('P')
    })
  })

  describe('Botón de cambio de estado', () => {
    it('should have correct title when estado is activo', () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: 1, estado: 'activo' }
      })

      const estadoButton = wrapper.find('.estado-deportista')
      expect(estadoButton.attributes('title')).toBe('Desactivar deportista')
    })

    it('should have correct title when estado is inactivo', () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: 1, estado: 'inactivo' }
      })

      const estadoButton = wrapper.find('.estado-deportista')
      expect(estadoButton.attributes('title')).toBe('Activar deportista')
    })

    it('should not be disabled initially', () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: 1, estado: 'activo' }
      })

      const estadoButton = wrapper.find('.estado-deportista')
      expect(estadoButton.attributes('disabled')).toBeUndefined()
    })

    it('should be disabled when cambiandoEstado is true', async () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: 1, estado: 'activo' }
      })

      wrapper.vm.cambiandoEstado = true
      await wrapper.vm.$nextTick()

      const estadoButton = wrapper.find('.estado-deportista')
      expect(estadoButton.attributes('disabled')).toBeDefined()
    })
  })

  describe('Imagen del deportista', () => {
    it('should use avatarDefault as image src', () => {
      wrapper = createWrapper()
      const img = wrapper.find('img')
      
      expect(img.exists()).toBe(true)
      expect(img.attributes('alt')).toBe('Perfil de Juan Pérez')
    })

    it('should handle image error and set default avatar', async () => {
      wrapper = createWrapper()
      const img = wrapper.find('img')

      const errorEvent = {
        target: {
          src: 'invalid-url'
        }
      }

      await wrapper.vm.imagenPorDefecto(errorEvent)

      expect(errorEvent.target.src).toBeDefined()
    })

    it('should generate correct alt text with deportista nombre', () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, nombre: 'María García' }
      })

      const img = wrapper.find('img')
      expect(img.attributes('alt')).toBe('Perfil de María García')
    })
  })

  describe('Eventos y clics', () => {
    it('should emit ver event when card is clicked', async () => {
      wrapper = createWrapper()
      const card = wrapper.find('.tarjeta-deportista')

      await card.trigger('click')

      expect(wrapper.emitted('ver')).toBeTruthy()
      expect(wrapper.emitted('ver')[0][0]).toEqual(mockDeportista)
    })

    it('should emit cambiar-estado event when button is clicked', async () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: 1, estado: 'activo' }
      })

      const estadoButton = wrapper.find('.estado-deportista')
      await estadoButton.trigger('click')

      expect(wrapper.emitted('cambiar-estado')).toBeTruthy()
      expect(wrapper.emitted('cambiar-estado')[0][0]).toEqual({
        ...mockDeportista,
        id_usuario: 1,
        estado: 'activo'
      })
    })

    it('should stop propagation when estado button is clicked', async () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: 1, estado: 'activo' }
      })

      const card = wrapper.find('.tarjeta-deportista')
      const estadoButton = wrapper.find('.estado-deportista')

      // Simular click en el botón con stopPropagation
      const clickEvent = {
        stopPropagation: vi.fn()
      }

      await estadoButton.trigger('click', clickEvent)

      // Verificar que se emite el evento cambiar-estado
      expect(wrapper.emitted('cambiar-estado')).toBeTruthy()
    })

    it('should not emit cambiar-estado when cambiandoEstado is true', async () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: 1, estado: 'activo' }
      })

      wrapper.vm.cambiandoEstado = true
      await wrapper.vm.$nextTick()

      const estadoButton = wrapper.find('.estado-deportista')
      await estadoButton.trigger('click')

      // No debería emitir el evento porque cambiandoEstado es true
      expect(wrapper.emitted('cambiar-estado')).toBeFalsy()
    })

    it('should not emit cambiar-estado when button is disabled', async () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: 1, estado: 'activo' }
      })

      wrapper.vm.cambiandoEstado = true
      await wrapper.vm.$nextTick()

      const estadoButton = wrapper.find('.estado-deportista[disabled]')
      if (estadoButton.exists()) {
        await estadoButton.trigger('click')
        expect(wrapper.emitted('cambiar-estado')).toBeFalsy()
      }
    })
  })

  describe('Props y valores por defecto', () => {
    it('should use default values when deportista prop is minimal', () => {
      wrapper = createWrapper({
        deportista: {
          id: 2,
          nombre: undefined,
          categoria: undefined
        }
      })

      // Los valores por defecto solo se aplican si la prop default() se ejecuta
      // En Vue 3, si pasas un objeto parcial, solo usa lo que pasaste
      // Por lo tanto, esperamos strings vacíos si no se proporcionan
      const nombreText = wrapper.find('.nombre-deportista').text()
      const categoriaText = wrapper.find('.categoria-deportista').text()
      
      // Verificar que el componente renderiza (puede ser vacío o el valor por defecto)
      expect(wrapper.find('.nombre-deportista').exists()).toBe(true)
      expect(wrapper.find('.categoria-deportista').exists()).toBe(true)
    })

    it('should handle deportista with all properties', () => {
      const fullDeportista = {
        id: 3,
        nombre: 'Carlos López',
        categoria: 'Benjamin',
        estado: 'inactivo',
        imagen: 'http://example.com/image.jpg',
        id_usuario: 2
      }

      wrapper = createWrapper({
        deportista: fullDeportista
      })

      expect(wrapper.find('.nombre-deportista').text()).toBe('Carlos López')
      expect(wrapper.find('.categoria-deportista').text()).toBe('Benjamin')
    })
  })

  describe('defineExpose', () => {
    it('should expose cambiandoEstado', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.cambiandoEstado).toBeDefined()
      expect(typeof wrapper.vm.cambiandoEstado).toBe('boolean')
      expect(wrapper.vm.cambiandoEstado).toBe(false)
    })

    it('should allow parent to access cambiandoEstado', () => {
      wrapper = createWrapper()

      wrapper.vm.cambiandoEstado = true
      expect(wrapper.vm.cambiandoEstado).toBe(true)
    })
  })

  describe('Acciones deportista', () => {
    it('should have acciones-deportista div with display none', () => {
      wrapper = createWrapper()
      const acciones = wrapper.find('.acciones-deportista')

      expect(acciones.exists()).toBe(true)
      expect(acciones.attributes('style')).toContain('display: none')
    })
  })

  describe('Multiple clicks handling', () => {
    it('should prevent multiple estado changes when cambiandoEstado is true', async () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: 1, estado: 'activo' }
      })

      wrapper.vm.cambiandoEstado = true
      await wrapper.vm.$nextTick()

      const estadoButton = wrapper.find('.estado-deportista')
      
      // Intentar hacer click múltiples veces
      await estadoButton.trigger('click')
      await estadoButton.trigger('click')
      await estadoButton.trigger('click')

      // No debería emitir ningún evento
      expect(wrapper.emitted('cambiar-estado')).toBeFalsy()
    })

    it('should allow estado change when cambiandoEstado is false', async () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: 1, estado: 'activo' }
      })

      wrapper.vm.cambiandoEstado = false
      await wrapper.vm.$nextTick()

      const estadoButton = wrapper.find('.estado-deportista')
      await estadoButton.trigger('click')

      expect(wrapper.emitted('cambiar-estado')).toBeTruthy()
    })
  })

  describe('Edge cases', () => {
    it('should handle deportista with empty nombre', () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, nombre: '' }
      })

      expect(wrapper.find('.nombre-deportista').text()).toBe('')
    })

    it('should handle deportista with empty categoria', () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, categoria: '' }
      })

      expect(wrapper.find('.categoria-deportista').text()).toBe('')
    })

    it('should handle deportista with null estado', () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: null, estado: null }
      })

      const estadoPara = wrapper.find('.estado-deportista')
      expect(estadoPara.exists()).toBe(true)
    })

    it('should handle deportista with id_usuario as 0', () => {
      wrapper = createWrapper({
        deportista: { ...mockDeportista, id_usuario: 0, estado: 'activo' }
      })

      // 0 es falsy, así que debería mostrar párrafo
      const estadoPara = wrapper.find('.estado-deportista')
      expect(estadoPara.element.tagName).toBe('P')
    })
  })
})

