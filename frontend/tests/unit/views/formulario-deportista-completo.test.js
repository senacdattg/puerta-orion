import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import FormularioDeportistaCompleto from '@/views/formulario-deportista-completo.vue'
import authService from '@/services/authService'
import Swal from 'sweetalert2'

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

vi.mock('@/services/authService', () => ({
  default: {
    getProfile: vi.fn(),
    completarPerfilDeportista: vi.fn()
  }
}))

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
    name: 'Titulo',
    template: '<div class="titulo-club">Título Club</div>'
  }
}))

vi.mock('@/components/layout/pie.vue', () => ({
  default: {
    name: 'Pie',
    template: '<div class="pie">Pie</div>'
  }
}))

vi.mock('@/components/formularios/formulario-deportista.vue', () => ({
  default: {
    name: 'FormularioDeportista',
    template: '<div class="formulario-deportista">Formulario</div>',
    props: ['modo', 'datos'],
    emits: ['submit', 'cancel']
  }
}))

describe('FormularioDeportistaCompleto', () => {
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
    return mount(FormularioDeportistaCompleto, {
      global: {
        plugins: [router],
        stubs: {}
      }
    })
  }

  describe('Renderizado básico', () => {
    it('should render component', async () => {
      authService.getProfile.mockResolvedValue({ data: { roles: [] } })
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('main').exists()).toBe(true)
    })

    it('should render Encabezado component', async () => {
      authService.getProfile.mockResolvedValue({ data: { roles: [] } })
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.findComponent({ name: 'Encabezado' }).exists()).toBe(true)
    })

    it('should render FormularioDeportista component when not loading', async () => {
      authService.getProfile.mockResolvedValue({ data: { roles: [] } })
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.findComponent({ name: 'FormularioDeportista' }).exists()).toBe(true)
    })

    it('should display loading state initially', async () => {
      authService.getProfile.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({ data: {} }), 100)))
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.cargando).toBe(true)
      expect(wrapper.text()).toContain('Cargando datos del usuario')
    })
  })

  describe('Cargar datos del usuario', () => {
    it('should load user profile on mount', async () => {
      authService.getProfile.mockResolvedValue({ data: { roles: [] } })
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(authService.getProfile).toHaveBeenCalled()
      expect(wrapper.vm.cargando).toBe(false)
    })

    it('should redirect to home if user already has Deportista role', async () => {
      authService.getProfile.mockResolvedValue({
        data: {
          roles: [{ nombre_rol: 'Deportista' }]
        }
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockRouter.push).toHaveBeenCalledWith('/home')
    })

    it('should handle error loading profile', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      authService.getProfile.mockRejectedValue(new Error('Network error'))
      Swal.fire.mockResolvedValue({})

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'error',
        title: 'Error',
        text: 'No pudimos cargar tus datos. Intenta nuevamente.'
      })
      expect(wrapper.vm.cargando).toBe(false)
      consoleSpy.mockRestore()
    })
  })

  describe('Manejar registro completo', () => {
    it('should handle successful registro', async () => {
      authService.getProfile.mockResolvedValue({ data: { roles: [] } })
      authService.completarPerfilDeportista.mockResolvedValue({
        success: true,
        message: 'Perfil completado exitosamente'
      })
      Swal.fire.mockResolvedValue({})

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const formulario = wrapper.findComponent({ name: 'FormularioDeportista' })
      await formulario.vm.$emit('submit', { nombre: 'Test' })
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(authService.completarPerfilDeportista).toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'success',
        title: 'Perfil completado',
        text: 'Perfil completado exitosamente',
        confirmButtonText: 'Continuar'
      })
      expect(mockRouter.push).toHaveBeenCalledWith('/home')
    })

    it('should handle registro error from service', async () => {
      authService.getProfile.mockResolvedValue({ data: { roles: [] } })
      authService.completarPerfilDeportista.mockResolvedValue({
        success: false,
        error: 'Error al completar perfil'
      })
      Swal.fire.mockResolvedValue({})

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const formulario = wrapper.findComponent({ name: 'FormularioDeportista' })
      await formulario.vm.$emit('submit', { nombre: 'Test' })
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'error',
        title: 'No se pudo completar',
        text: 'Error al completar perfil'
      })
    })

    it('should handle exception during registro', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      authService.getProfile.mockResolvedValue({ data: { roles: [] } })
      authService.completarPerfilDeportista.mockRejectedValue(new Error('Network error'))
      Swal.fire.mockResolvedValue({})

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const formulario = wrapper.findComponent({ name: 'FormularioDeportista' })
      await formulario.vm.$emit('submit', { nombre: 'Test' })
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'error',
        title: 'Error de conexión',
        text: 'No pudimos completar el perfil. Intenta nuevamente.'
      })
      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })
  })

  describe('Manejar cancelación', () => {
    it('should navigate to completar-perfil when cancelled', async () => {
      authService.getProfile.mockResolvedValue({ data: { roles: [] } })
      Swal.fire.mockResolvedValue({ isConfirmed: true })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const formulario = wrapper.findComponent({ name: 'FormularioDeportista' })
      await formulario.vm.$emit('cancel')
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'question',
        title: '¿Cancelar registro?',
        text: 'Se perderá la información ingresada.',
        showCancelButton: true,
        confirmButtonText: 'Sí, cancelar',
        cancelButtonText: 'Continuar'
      })
      expect(mockRouter.push).toHaveBeenCalledWith('/completar-perfil')
    })

    it('should not navigate when user does not confirm cancellation', async () => {
      authService.getProfile.mockResolvedValue({ data: { roles: [] } })
      Swal.fire.mockResolvedValue({ isConfirmed: false })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const formulario = wrapper.findComponent({ name: 'FormularioDeportista' })
      await formulario.vm.$emit('cancel')
      await wrapper.vm.$nextTick()

      expect(mockRouter.push).not.toHaveBeenCalled()
    })
  })

  describe('Props passed to FormularioDeportista', () => {
    it('should pass modo actualizar to FormularioDeportista', async () => {
      authService.getProfile.mockResolvedValue({ data: { roles: [] } })
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const formulario = wrapper.findComponent({ name: 'FormularioDeportista' })
      expect(formulario.props('modo')).toBe('actualizar')
    })

    it('should pass datosUsuario to FormularioDeportista', async () => {
      const mockData = { id: 1, nombre: 'Test User', roles: [] }
      authService.getProfile.mockResolvedValue({ data: mockData })
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const formulario = wrapper.findComponent({ name: 'FormularioDeportista' })
      expect(formulario.props('datos')).toEqual(mockData)
    })
  })
})

