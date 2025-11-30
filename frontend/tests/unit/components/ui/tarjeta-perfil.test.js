import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import TarjetaPerfil from '@/components/ui/tarjeta-perfil.vue'

const mockRouter = {
  push: vi.fn()
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter
  }
})

describe('TarjetaPerfil', () => {
  let wrapper
  let router

  beforeEach(() => {
    vi.clearAllMocks()
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } }
      ]
    })
  })

  const createWrapper = (props = {}) => {
    return mount(TarjetaPerfil, {
      props: {
        rol: props.rol || 'Deportista',
        textoBoton: props.textoBoton,
        mostrarBoton: props.mostrarBoton !== undefined ? props.mostrarBoton : true
      },
      global: {
        plugins: [router],
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
      expect(wrapper.find('.tarjeta-perfil').exists()).toBe(true)
    })

    it('should display rol prop', () => {
      wrapper = createWrapper({ rol: 'Administrador' })
      expect(wrapper.text()).toContain('Administrador')
    })

    it('should display default textoBoton when not provided', () => {
      wrapper = createWrapper({ rol: 'Deportista' })
      expect(wrapper.text()).toContain('Roles')
    })

    it('should display custom textoBoton when provided', () => {
      wrapper = createWrapper({ rol: 'Deportista', textoBoton: 'Ver Perfil' })
      expect(wrapper.text()).toContain('Ver Perfil')
    })
  })

  describe('Botón', () => {
    it('should show button by default', () => {
      wrapper = createWrapper({ rol: 'Deportista' })
      expect(wrapper.find('.boton-perfil').exists()).toBe(true)
    })

    it('should hide button when mostrarBoton is false', () => {
      wrapper = createWrapper({ rol: 'Deportista', mostrarBoton: false })
      expect(wrapper.find('.boton-perfil').exists()).toBe(false)
    })

    it('should navigate to ver-roles when button is clicked', async () => {
      wrapper = createWrapper({ rol: 'Deportista' })
      const button = wrapper.find('.boton-perfil')
      await button.trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/ver-roles')
    })
  })
})

