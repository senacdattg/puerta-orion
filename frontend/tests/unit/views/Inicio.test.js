import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Inicio from '@/views/Inicio.vue'
import { useAuthStore } from '@/stores/auth'

// Mock components
vi.mock('@/components/layout/encabezado.vue', () => ({
  default: {
    name: 'Encabezado',
    template: '<header class="encabezado">Header</header>',
    props: ['sinMenu']
  }
}))

vi.mock('@/components/ui/titulo-club.vue', () => ({
  default: {
    name: 'TituloClub',
    template: '<div class="titulo-club">Título Club</div>'
  }
}))

vi.mock('@/components/layout/DashboardHome.vue', () => ({
  default: {
    name: 'DashboardHome',
    template: '<div class="dashboard-home">Dashboard</div>'
  }
}))

vi.mock('@/components/layout/pie.vue', () => ({
  default: {
    name: 'FooterEnhanced',
    template: '<footer class="footer">Footer</footer>'
  }
}))

// Mock auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

describe('InicioPage', () => {
  let mockAuthStore

  beforeEach(() => {
    setActivePinia(createPinia())

    mockAuthStore = {
      activeRole: null
    }

    useAuthStore.mockReturnValue(mockAuthStore)
  })

  it('should render the view', () => {
    const wrapper = mount(Inicio)

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.inicio-page').exists()).toBe(true)
  })

  it('should render all main components', () => {
    const wrapper = mount(Inicio)

    expect(wrapper.find('.encabezado').exists()).toBe(true)
    expect(wrapper.find('.titulo-club').exists()).toBe(true)
    expect(wrapper.find('.dashboard-home').exists()).toBe(true)
    expect(wrapper.find('.footer').exists()).toBe(true)
  })

  it('should hide menu for Acudiente role', () => {
    mockAuthStore.activeRole = 'Acudiente'

    const wrapper = mount(Inicio)

    const encabezado = wrapper.findComponent({ name: 'Encabezado' })
    expect(encabezado.props('sinMenu')).toBe(true)
  })

  it('should hide menu for Deportista role', () => {
    mockAuthStore.activeRole = 'Deportista'

    const wrapper = mount(Inicio)

    const encabezado = wrapper.findComponent({ name: 'Encabezado' })
    expect(encabezado.props('sinMenu')).toBe(true)
  })

  it('should show menu for other roles', () => {
    mockAuthStore.activeRole = 'Administrador'

    const wrapper = mount(Inicio)

    const encabezado = wrapper.findComponent({ name: 'Encabezado' })
    expect(encabezado.props('sinMenu')).toBe(false)
  })

  it('should show menu when no active role', () => {
    mockAuthStore.activeRole = null

    const wrapper = mount(Inicio)

    const encabezado = wrapper.findComponent({ name: 'Encabezado' })
    expect(encabezado.props('sinMenu')).toBe(false)
  })
})

