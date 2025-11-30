import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import DeportistaDashboard from '@/views/DeportistaDashboard.vue'

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

vi.mock('@/components/layout/encabezado.vue', () => ({
  default: {
    name: 'Encabezado',
    template: '<div class="encabezado">Encabezado</div>'
  }
}))

vi.mock('@/components/ui/titulo-club.vue', () => ({
  default: {
    name: 'TituloClub',
    template: '<div class="titulo-club">Título Club</div>'
  }
}))

vi.mock('@/components/layout/pie.vue', () => ({
  default: {
    name: 'FooterEnhanced',
    template: '<div class="pie">Footer</div>'
  }
}))

vi.mock('@/components/deportistas/PerfilModal.vue', () => ({
  default: {
    name: 'PerfilModal',
    template: '<div class="perfil-modal" v-if="visible">Perfil Modal</div>',
    props: ['visible'],
    emits: ['close', 'update']
  }
}))

describe('DeportistaDashboard', () => {
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

  const createWrapper = () => {
    return mount(DeportistaDashboard, {
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
      expect(wrapper.find('.deportista-dashboard-page').exists()).toBe(true)
    })

    it('should render Encabezado component', () => {
      wrapper = createWrapper()
      expect(wrapper.findComponent({ name: 'Encabezado' }).exists()).toBe(true)
    })

    it('should render TituloClub component', () => {
      wrapper = createWrapper()
      expect(wrapper.findComponent({ name: 'TituloClub' }).exists()).toBe(true)
    })

    it('should render FooterEnhanced component', () => {
      wrapper = createWrapper()
      expect(wrapper.findComponent({ name: 'FooterEnhanced' }).exists()).toBe(true)
    })

    it('should render PerfilModal component', () => {
      wrapper = createWrapper()
      expect(wrapper.findComponent({ name: 'PerfilModal' }).exists()).toBe(true)
    })

    it('should display dashboard title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Panel del Deportista')
    })

    it('should display dashboard subtitle', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Gestiona tu información deportiva')
    })
  })

  describe('Dashboard cards', () => {
    it('should render all dashboard cards', () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      expect(cards.length).toBe(5)
    })

    it('should render Mi Perfil card', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Mi Perfil')
      expect(wrapper.text()).toContain('Gestiona tu información personal')
    })

    it('should render Mis Mensualidades card', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Mis Mensualidades')
      expect(wrapper.text()).toContain('Consulta el estado de tus pagos')
    })

    it('should render Eventos Próximos card', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Eventos Próximos')
      expect(wrapper.text()).toContain('Participa en los próximos eventos')
    })

    it('should render Calendario card', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Calendario')
      expect(wrapper.text()).toContain('Consulta el calendario completo')
    })

    it('should render Galería card', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Galería')
      expect(wrapper.text()).toContain('Explora las últimas imágenes')
    })
  })

  describe('Navegación', () => {
    it('should navigate to perfil when Mi Perfil card is clicked', async () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      await cards[0].trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/perfil')
    })

    it('should navigate to mensualidades when Mis Mensualidades card is clicked', async () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      await cards[1].trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/mensualidades')
    })

    it('should navigate to eventos when Eventos Próximos card is clicked', async () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      await cards[2].trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/eventos')
    })

    it('should navigate to calendario when Calendario card is clicked', async () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      await cards[3].trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/calendario')
    })

    it('should navigate to galeria when Galería card is clicked', async () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      await cards[4].trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/galeria')
    })
  })

  describe('PerfilModal', () => {
    it('should hide PerfilModal initially', () => {
      wrapper = createWrapper()
      const modal = wrapper.findComponent({ name: 'PerfilModal' })
      expect(modal.props('visible')).toBe(false)
    })

    it('should close modal when close event is emitted', async () => {
      wrapper = createWrapper()
      const modal = wrapper.findComponent({ name: 'PerfilModal' })
      await modal.vm.$emit('close')
      await wrapper.vm.$nextTick()
      expect(modal.props('visible')).toBe(false)
    })

    it('should handle perfil update', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      wrapper = createWrapper()
      const modal = wrapper.findComponent({ name: 'PerfilModal' })
      await modal.vm.$emit('update')
      await wrapper.vm.$nextTick()
      expect(consoleSpy).toHaveBeenCalledWith('Perfil actualizado')
      consoleSpy.mockRestore()
    })
  })
})

