import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import CardDeportista from '@/components/deportistas/CardDeportista.vue'

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

describe('CardDeportista', () => {
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
    return mount(CardDeportista, {
      props: {
        title: props.title || 'Test Title',
        description: props.description,
        icon: props.icon || 'fas fa-user',
        value: props.value,
        to: props.to,
        clickable: props.clickable !== undefined ? props.clickable : true,
        iconBgColor: props.iconBgColor
      },
      global: {
        plugins: [router],
        stubs: {
          'i': true
        }
      }
    })
  }

  describe('Renderizado básico', () => {
    it('should render component', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.card-deportista').exists()).toBe(true)
    })

    it('should display title prop', () => {
      wrapper = createWrapper({ title: 'Mi Perfil' })
      expect(wrapper.text()).toContain('Mi Perfil')
    })

    it('should display description prop', () => {
      wrapper = createWrapper({ description: 'Descripción de prueba' })
      expect(wrapper.text()).toContain('Descripción de prueba')
    })

    it('should display value prop when provided', () => {
      wrapper = createWrapper({ value: '100' })
      expect(wrapper.text()).toContain('100')
    })

    it('should not display value section when value is undefined', () => {
      wrapper = createWrapper({ value: undefined })
      expect(wrapper.find('.card-value').exists()).toBe(false)
    })
  })

  describe('Icono', () => {
    it('should apply default iconBgColor', () => {
      wrapper = createWrapper()
      const iconDiv = wrapper.find('.card-icon')
      expect(iconDiv.attributes('style')).toContain('rgba(255, 214, 0, 0.15)')
    })

    it('should apply custom iconBgColor', () => {
      wrapper = createWrapper({ iconBgColor: 'rgba(255, 0, 0, 0.5)' })
      const iconDiv = wrapper.find('.card-icon')
      expect(iconDiv.attributes('style')).toContain('rgba(255, 0, 0, 0.5)')
    })
  })

  describe('Clickable', () => {
    it('should have clickable class when clickable is true', () => {
      wrapper = createWrapper({ clickable: true })
      expect(wrapper.find('.card-deportista').classes()).toContain('clickable')
    })

    it('should not have clickable class when clickable is false', () => {
      wrapper = createWrapper({ clickable: false })
      expect(wrapper.find('.card-deportista').classes()).not.toContain('clickable')
    })

    it('should show arrow when clickable is true', () => {
      wrapper = createWrapper({ clickable: true })
      expect(wrapper.find('.card-arrow').exists()).toBe(true)
    })

    it('should not show arrow when clickable is false', () => {
      wrapper = createWrapper({ clickable: false })
      expect(wrapper.find('.card-arrow').exists()).toBe(false)
    })
  })

  describe('Navegación y eventos', () => {
    it('should navigate to route when to prop is provided and card is clicked', async () => {
      wrapper = createWrapper({ to: '/perfil' })
      await wrapper.find('.card-deportista').trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/perfil')
    })

    it('should emit click event when card is clicked', async () => {
      wrapper = createWrapper()
      await wrapper.find('.card-deportista').trigger('click')
      expect(wrapper.emitted('click')).toBeTruthy()
    })

    it('should not navigate when to prop is not provided', async () => {
      wrapper = createWrapper({ to: null })
      await wrapper.find('.card-deportista').trigger('click')
      expect(mockRouter.push).not.toHaveBeenCalled()
    })

    it('should not navigate or emit when clickable is false', async () => {
      wrapper = createWrapper({ clickable: false })
      await wrapper.find('.card-deportista').trigger('click')
      expect(mockRouter.push).not.toHaveBeenCalled()
      expect(wrapper.emitted('click')).toBeFalsy()
    })

    it('should navigate and emit click when both are set', async () => {
      wrapper = createWrapper({ to: '/perfil' })
      await wrapper.find('.card-deportista').trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/perfil')
      expect(wrapper.emitted('click')).toBeTruthy()
    })
  })
})

