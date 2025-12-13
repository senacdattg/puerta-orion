import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import TarjetaAcudientesAcudidos from '@/components/deportistas/tarjeta-acudientes-acudidos.vue'
import Swal from 'sweetalert2'

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn()
  }
}))

describe('TarjetaAcudientesAcudidos', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  const createWrapper = (props = {}) => {
    return mount(TarjetaAcudientesAcudidos, {
      props: {
        rol: props.rol || 'Deportista',
        mostrarAgregar: props.mostrarAgregar !== undefined ? props.mostrarAgregar : true,
        mostrarVer: props.mostrarVer !== undefined ? props.mostrarVer : true
      },
      global: {
        stubs: {
          'img': true
        }
      }
    })
  }

  describe('Renderizado básico', () => {
    it('should render component when rol is valid', () => {
      wrapper = createWrapper({ rol: 'Deportista' })
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.tarjeta-acudiente').exists()).toBe(true)
    })

    it('should not render component when rol is invalid', () => {
      wrapper = createWrapper({ rol: 'InvalidRol' })
      expect(wrapper.find('.tarjeta-acudiente').exists()).toBe(false)
    })

    it('should display "Acudientes" title for Deportista', () => {
      wrapper = createWrapper({ rol: 'Deportista' })
      expect(wrapper.text()).toContain('Acudientes')
    })

    it('should display "Acudidos" title for Acudiente', () => {
      wrapper = createWrapper({ rol: 'Acudiente' })
      expect(wrapper.text()).toContain('Acudidos')
    })
  })

  describe('Lista de personas', () => {
    it('should display personas for Deportista', () => {
      wrapper = createWrapper({ rol: 'Deportista' })
      const inputs = wrapper.findAll('input[type="text"]')
      const nombres = inputs.map(input => input.element.value)
      expect(nombres).toContain('Pedro Ramírez (Acudiente)')
      expect(nombres).toContain('Laura Torres (Acudiente)')
    })

    it('should display personas for Acudiente', () => {
      wrapper = createWrapper({ rol: 'Acudiente' })
      const inputs = wrapper.findAll('input[type="text"]')
      const nombres = inputs.map(input => input.element.value)
      expect(nombres).toContain('Kevin Santiago Prada Castellanos')
      expect(nombres).toContain('María Fernanda Ruiz Pérez')
    })

    it('should render Ver buttons when mostrarVer is true', () => {
      wrapper = createWrapper({ rol: 'Deportista', mostrarVer: true })
      const buttons = wrapper.findAll('.boton-acudiente')
      expect(buttons.length).toBeGreaterThan(0)
    })

    it('should not render Ver buttons when mostrarVer is false', () => {
      wrapper = createWrapper({ rol: 'Deportista', mostrarVer: false })
      const buttons = wrapper.findAll('.boton-acudiente')
      // Solo debería haber el botón Agregar, no los botones Ver
      const verButtons = buttons.filter(btn => btn.text().includes('Ver'))
      expect(verButtons.length).toBe(0)
    })
  })

  describe('Botón Agregar', () => {
    it('should show agregar button when mostrarAgregar is true', () => {
      wrapper = createWrapper({ rol: 'Deportista', mostrarAgregar: true })
      const agregarButton = wrapper.findAll('.boton-acudiente').find(btn => btn.text() === 'Agregar')
      expect(agregarButton).toBeDefined()
    })

    it('should not show agregar button when mostrarAgregar is false', () => {
      wrapper = createWrapper({ rol: 'Deportista', mostrarAgregar: false })
      const agregarButtons = wrapper.findAll('.boton-acudiente').filter(btn => btn.text() === 'Agregar')
      expect(agregarButtons.length).toBe(0)
    })

    it('should show info message when agregar is clicked', async () => {
      wrapper = createWrapper({ rol: 'Deportista' })
      const agregarButton = wrapper.findAll('.boton-acudiente').find(btn => btn.text() === 'Agregar')
      await agregarButton.trigger('click')
      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'info',
        title: 'Función en desarrollo',
        text: 'Aquí podrás agregar un nuevo registro.'
      })
    })
  })

  describe('Ver persona', () => {
    it('should show persona info when Ver is clicked', async () => {
      wrapper = createWrapper({ rol: 'Deportista' })
      const verButtons = wrapper.findAll('.boton-acudiente').filter(btn => btn.text() === 'Ver')
      if (verButtons.length > 0) {
        await verButtons[0].trigger('click')
        expect(Swal.fire).toHaveBeenCalledWith(
          expect.objectContaining({
            icon: 'info',
            title: expect.any(String),
            text: 'Información simulada del registro.'
          })
        )
      }
    })
  })
})

