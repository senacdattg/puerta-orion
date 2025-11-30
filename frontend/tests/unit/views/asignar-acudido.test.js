import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import AsignarAcudido from '@/views/asignar-acudido.vue'
import Swal from 'sweetalert2'

const mockRouter = {
  push: vi.fn()
}

const mockUseAuthStore = vi.fn()
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockUseAuthStore()
}))

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter
  }
})

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn()
  }
}))

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

describe('AsignarAcudido', () => {
  let wrapper
  let router
  let mockAuthStore

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()

    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } }
      ]
    })

    mockAuthStore = {
      user: {
        id_usuario: 1
      }
    }

    mockUseAuthStore.mockReturnValue(mockAuthStore)
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  const createWrapper = () => {
    return mount(AsignarAcudido, {
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
      expect(wrapper.find('.asignar-acudido-page').exists()).toBe(true)
    })

    it('should display page title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Asignar Acudido')
    })

    it('should display subtitle', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Vincula un deportista a tu cuenta')
    })

    it('should render action buttons', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.btn-create').exists()).toBe(true)
      expect(wrapper.find('.btn-search-existing').exists()).toBe(true)
    })
  })

  describe('Busqueda', () => {
    it('should toggle search visibility', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarBusqueda).toBe(false)

      const toggleButton = wrapper.find('.btn-search-existing')
      await toggleButton.trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarBusqueda).toBe(true)
    })

    it('should display search section when mostrarBusqueda is true', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarBusqueda = true
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.search-section').exists()).toBe(true)
    })

    it('should filter deportistas by search term', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.searchTerm = 'Juan'
      await wrapper.vm.$nextTick()

      const filtrados = wrapper.vm.deportistasFiltrados
      expect(filtrados.length).toBeGreaterThan(0)
      expect(filtrados[0].nombre_completo).toContain('Juan')
    })

    it('should filter deportistas by documento', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.searchTerm = '12345678'
      await wrapper.vm.$nextTick()

      const filtrados = wrapper.vm.deportistasFiltrados
      expect(filtrados.length).toBeGreaterThan(0)
      expect(filtrados[0].documento).toContain('12345678')
    })

    it('should show all deportistas when search term is empty', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.searchTerm = ''
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.deportistasFiltrados.length).toBe(3)
    })
  })

  describe('Deportistas list', () => {
    it('should load deportistas on mount', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.deportistas.length).toBe(3)
    })

    it('should display deportista cards', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const cards = wrapper.findAll('.deportista-card')
      expect(cards.length).toBe(3)
    })

    it('should display empty state when no deportistas match', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.searchTerm = 'No existe'
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.empty-state').exists()).toBe(true)
      expect(wrapper.text()).toContain('No se encontraron deportistas')
    })
  })

  describe('Asignar deportista', () => {
    it('should assign deportista successfully', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const deportista = wrapper.vm.deportistas[0]
      Swal.fire.mockResolvedValue({})

      const asignarPromise = wrapper.vm.asignarDeportista(deportista)
      vi.advanceTimersByTime(1000)
      await asignarPromise
      await wrapper.vm.$nextTick()

      expect(deportista.asignado).toBe(true)
      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'success',
        title: 'Asignación exitosa',
        text: 'El deportista fue asignado correctamente.',
        timer: 1500,
        showConfirmButton: false
      })
    })

    it('should set asignando to true during assignment', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const deportista = wrapper.vm.deportistas[0]
      Swal.fire.mockResolvedValue({})

      const asignarPromise = wrapper.vm.asignarDeportista(deportista)
      expect(wrapper.vm.asignando).toBe(true)

      vi.advanceTimersByTime(1000)
      await asignarPromise
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.asignando).toBe(false)
    })

    it('should handle error when assigning deportista', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const deportista = wrapper.vm.deportistas[0]
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      // Simular que Swal.fire lanza un error
      Swal.fire.mockRejectedValueOnce(new Error('Network error'))
      Swal.fire.mockResolvedValueOnce({})

      const asignarPromise = wrapper.vm.asignarDeportista(deportista)
      vi.advanceTimersByTime(1000)
      await asignarPromise
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalled()
      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    }, 10000)
  })

  describe('Desasignar deportista', () => {
    it('should desasign deportista when confirmed', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const deportista = { ...wrapper.vm.deportistas[0], asignado: true }
      Swal.fire.mockResolvedValueOnce({ isConfirmed: true })
      Swal.fire.mockResolvedValueOnce({})

      const desasignarPromise = wrapper.vm.desasignarDeportista(deportista)
      await wrapper.vm.$nextTick()
      vi.advanceTimersByTime(500)
      await desasignarPromise
      await wrapper.vm.$nextTick()

      expect(deportista.asignado).toBe(false)
      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should not desasign when user cancels', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const deportista = { ...wrapper.vm.deportistas[0], asignado: true }
      Swal.fire.mockResolvedValue({ isConfirmed: false })

      await wrapper.vm.desasignarDeportista(deportista)

      expect(deportista.asignado).toBe(true)
    })

    it('should handle error when desasigning', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const deportista = { ...wrapper.vm.deportistas[0], asignado: true }
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      Swal.fire.mockResolvedValueOnce({ isConfirmed: true })
      Swal.fire.mockResolvedValueOnce({})

      const desasignarPromise = wrapper.vm.desasignarDeportista(deportista)
      await wrapper.vm.$nextTick()
      vi.advanceTimersByTime(500)
      await desasignarPromise
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })
  })

  describe('Crear nuevo deportista', () => {
    it('should navigate to registrar-deportista-form', () => {
      wrapper = createWrapper()
      wrapper.vm.crearNuevoDeportista()

      expect(mockRouter.push).toHaveBeenCalledWith({
        path: '/registrar-deportista-form',
        query: { asignarAcudiente: 'true', idAcudiente: 1 }
      })
    })

    it('should handle missing user id', () => {
      mockAuthStore.user = null
      wrapper = createWrapper()
      wrapper.vm.crearNuevoDeportista()

      expect(mockRouter.push).toHaveBeenCalledWith({
        path: '/registrar-deportista-form',
        query: { asignarAcudiente: 'true', idAcudiente: undefined }
      })
    })
  })

  describe('Deportista card rendering', () => {
    it('should show asignado status when deportista is assigned', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.deportistas[1].asignado = true
      await wrapper.vm.$nextTick()

      const cards = wrapper.findAll('.deportista-card')
      expect(cards[1].classes()).toContain('asignado')
    })

    it('should show Asignar button for unassigned deportista', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const cards = wrapper.findAll('.deportista-card')
      const firstCard = cards[0]
      expect(firstCard.text()).toContain('Asignar')
    })

    it('should show Desasignar button for assigned deportista', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.deportistas[1].asignado = true
      await wrapper.vm.$nextTick()

      const cards = wrapper.findAll('.deportista-card')
      const secondCard = cards[1]
      expect(secondCard.text()).toContain('Desasignar')
    })
  })
})

