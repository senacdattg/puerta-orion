import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import MensualidadesView from '@/views/mensualidades.vue'
import mensualidadesService from '@/services/mensualidadesService'
import Swal from 'sweetalert2'
import { getApiUrl } from '@/config/environment'

// Mock services
vi.mock('@/services/mensualidadesService', () => ({
  default: {
    list: vi.fn(),
    update: vi.fn(),
    create: vi.fn(),
    desactivar: vi.fn(),
    reactivar: vi.fn()
  }
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(() => Promise.resolve({ isConfirmed: true }))
  }
}))

vi.mock('@/config/environment', () => ({
  getApiUrl: vi.fn((path) => `http://localhost:5000${path}`),
  CURRENT_CONFIG: {
    API_URL: 'http://localhost:5000'
  }
}))

// Mock global fetch
global.fetch = vi.fn()

// Mock localStorage
global.localStorage = {
  getItem: vi.fn(() => 'mock-token'),
  setItem: vi.fn(),
  removeItem: vi.fn()
}

describe('MensualidadesView', () => {
  let pinia
  let wrapper

  const mockMensualidades = [
    {
      id_mensualidad: 1,
      id_persona: 1,
      persona: {
        primer_nombre: 'Juan',
        primer_apellido: 'Pérez',
        documento: '12345678'
      },
      persona_nombre: 'Juan Pérez',
      numero_documento: '12345678',
      monto_pago: 150000,
      saldo_pendiente: 0,
      fecha_vencimiento: '2024-01-15',
      fecha_pago: '2024-01-10',
      estado: true,
      estado_texto: 'Pagado',
      id_metodo_pago: 1,
      activo: true
    },
    {
      id_mensualidad: 2,
      id_persona: 2,
      persona: {
        primer_nombre: 'María',
        primer_apellido: 'García',
        documento: '87654321'
      },
      persona_nombre: 'María García',
      numero_documento: '87654321',
      monto_pago: 200000,
      saldo_pendiente: 50000,
      fecha_vencimiento: '2024-02-15',
      fecha_pago: null,
      estado: false,
      estado_texto: 'Pendiente',
      id_metodo_pago: 2,
      activo: true
    }
  ]

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    vi.clearAllMocks()
    mensualidadesService.list.mockResolvedValue({
      success: true,
      data: mockMensualidades
    })
  })

  const createWrapper = () => {
    return mount(MensualidadesView, {
      global: {
        plugins: [pinia],
        stubs: {
          'Encabezado': true,
          'ListaMensualidades': true,
          'Pie': true
        }
      }
    })
  }

  describe('Rendering', () => {
    it('should render main component', () => {
      wrapper = createWrapper()
      expect(wrapper.find('main').exists()).toBe(true)
    })

    it('should render child components', () => {
      wrapper = createWrapper()
      expect(wrapper.findComponent({ name: 'Encabezado' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'ListaMensualidades' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'Pie' }).exists()).toBe(true)
    })

    it('should pass props to ListaMensualidades', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const listaComponent = wrapper.findComponent({ name: 'ListaMensualidades' })
      expect(listaComponent.exists()).toBe(true)
      expect(listaComponent.props('loading')).toBeDefined()
      expect(listaComponent.props('error')).toBeDefined()
    })
  })

  describe('Data Loading', () => {
    it('should load mensualidades on mount', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mensualidadesService.list).toHaveBeenCalled()
    })

    it('should map mensualidades correctly', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.mensualidades.length).toBeGreaterThan(0)
      const primera = wrapper.vm.mensualidades[0]
      expect(primera.id).toBe(1)
      expect(primera.nombre).toBeTruthy()
      expect(primera.valor).toContain('$')
    })

    it('should handle loading state', async () => {
      mensualidadesService.list.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 200)))
      wrapper = createWrapper()

      expect(wrapper.vm.loading).toBe(true)
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 250))

      expect(wrapper.vm.loading).toBe(false)
    })

    it('should handle error when loading fails', async () => {
      mensualidadesService.list.mockRejectedValue(new Error('Network error'))
      wrapper = createWrapper()

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.errorMsg).toBeTruthy()
      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should handle 403 error with specific message', async () => {
      const error = new Error('403 Forbidden')
      mensualidadesService.list.mockRejectedValue(error)
      wrapper = createWrapper()

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(Swal.fire).toHaveBeenCalled()
      const swalCall = Swal.fire.mock.calls[0][0]
      expect(swalCall.title).toBe('Sin permisos')
    })

    it('should handle 401 error with specific message', async () => {
      const error = new Error('401 Unauthorized')
      mensualidadesService.list.mockRejectedValue(error)
      wrapper = createWrapper()

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(Swal.fire).toHaveBeenCalled()
      const swalCall = Swal.fire.mock.calls[0][0]
      expect(swalCall.title).toBe('Sesión expirada')
    })
  })

  describe('Helper Functions', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should format COP currency correctly', () => {
      const result = wrapper.vm.formatoCOP(150000)
      expect(result).toContain('150')
    })

    it('should format currency with decimals', () => {
      const result = wrapper.vm.formatoCOP(150000.50)
      expect(typeof result).toBe('string')
    })

    it('should get month name from date', () => {
      const result = wrapper.vm.nombreMes('2024-01-15')
      expect(result).toBeTruthy()
      expect(typeof result).toBe('string')
    })

    it('should return empty string for invalid date', () => {
      const result = wrapper.vm.nombreMes(null)
      expect(result).toBe('')
    })

    it('should get person name from object', () => {
      const persona = {
        primer_nombre: 'Juan',
        primer_apellido: 'Pérez'
      }
      const result = wrapper.vm.obtenerNombrePersonaDesdeObjeto(persona, 1)
      expect(result).toBe('Juan Pérez')
    })

    it('should use fallback when persona is null', () => {
      const result = wrapper.vm.obtenerNombrePersonaDesdeObjeto(null, 123)
      expect(result).toBe('Persona #123')
    })

    it('should map mensualidad to card format', () => {
      const mensualidad = mockMensualidades[0]
      const result = wrapper.vm.mapMensualidadToCard(mensualidad)
      
      expect(result.id).toBe(1)
      expect(result.nombre).toBeTruthy()
      expect(result.valor).toContain('$')
      expect(result.estado).toBe('Pagado')
      expect(result.monto_pago_raw).toBe(150000)
    })
  })

  describe('Payment Flow', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should initiate payment successfully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: async () => JSON.stringify({
          success: true,
          init_point: 'https://mercadopago.com/payment'
        })
      })

      const mensualidad = wrapper.vm.mensualidades[0]
      await wrapper.vm.iniciarPago(mensualidad)

      expect(global.fetch).toHaveBeenCalled()
      const fetchCall = global.fetch.mock.calls[0]
      expect(fetchCall[0]).toContain('/api/mercadopago/crear-preferencia')
      expect(fetchCall[1].method).toBe('POST')
    })

    it('should handle payment error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        text: async () => JSON.stringify({
          success: false,
          error: 'Payment failed'
        })
      })

      const mensualidad = wrapper.vm.mensualidades[0]
      await wrapper.vm.iniciarPago(mensualidad)

      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should handle payment exception', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'))

      const mensualidad = wrapper.vm.mensualidades[0]
      await wrapper.vm.iniciarPago(mensualidad)

      expect(Swal.fire).toHaveBeenCalled()
    })
  })

  describe('Edit Mensualidad', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should edit mensualidad successfully', async () => {
      mensualidadesService.update.mockResolvedValue({ success: true })
      mensualidadesService.list.mockResolvedValue({
        success: true,
        data: mockMensualidades
      })

      const mensualidadActualizada = {
        id: 1,
        id_metodo_pago: 2,
        monto_pago: 200000,
        fecha_vencimiento: '2024-03-15',
        saldo_pendiente: 0,
        activo: true
      }

      await wrapper.vm.editarMensualidad(mensualidadActualizada)

      expect(mensualidadesService.update).toHaveBeenCalledWith(1, expect.objectContaining({
        id_metodo_pago: 2,
        monto_pago: 200000
      }))
      expect(mensualidadesService.list).toHaveBeenCalled()
    })

    it('should handle edit error', async () => {
      mensualidadesService.update.mockRejectedValue(new Error('Update failed'))

      const mensualidadActualizada = {
        id: 1,
        monto_pago: 200000
      }

      await wrapper.vm.editarMensualidad(mensualidadActualizada)

      expect(Swal.fire).toHaveBeenCalled()
      const swalCall = Swal.fire.mock.calls[0][0]
      expect(swalCall.title).toBe('Error al actualizar mensualidad')
    })
  })

  describe('Delete Mensualidad', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should deactivate active mensualidad', async () => {
      mensualidadesService.desactivar.mockResolvedValue({ success: true })
      mensualidadesService.list.mockResolvedValue({
        success: true,
        data: mockMensualidades
      })

      const mensualidad = { id: 1, activo: true }
      wrapper.vm.eliminarMensualidad(mensualidad)

      expect(mensualidadesService.desactivar).toHaveBeenCalledWith(1)
    })

    it('should reactivate inactive mensualidad', async () => {
      mensualidadesService.reactivar.mockResolvedValue({ success: true })
      mensualidadesService.list.mockResolvedValue({
        success: true,
        data: mockMensualidades
      })

      const mensualidad = { id: 1, activo: false }
      wrapper.vm.eliminarMensualidad(mensualidad)

      expect(mensualidadesService.reactivar).toHaveBeenCalledWith(1)
    })

    it('should handle delete error', async () => {
      mensualidadesService.desactivar.mockRejectedValue(new Error('Delete failed'))

      const mensualidad = { id: 1, activo: true }
      await wrapper.vm.eliminarMensualidad(mensualidad)

      expect(Swal.fire).toHaveBeenCalled()
      const swalCall = Swal.fire.mock.calls[0][0]
      expect(swalCall.title).toBe('Error al cambiar estado')
    })
  })

  describe('Create Mensualidad', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should create mensualidad successfully', async () => {
      mensualidadesService.create.mockResolvedValue({ success: true })
      mensualidadesService.list.mockResolvedValue({
        success: true,
        data: mockMensualidades
      })

      const payload = {
        numero_documento: '12345678',
        id_metodo_pago: 1,
        monto_pago: 150000,
        fecha_vencimiento: '2024-04-15',
        activo: true,
        estado_ui: 'Pendiente',
        saldo_pendiente: 150000
      }

      await wrapper.vm.nuevaMensualidad(payload)

      expect(mensualidadesService.create).toHaveBeenCalledWith(expect.objectContaining({
        numero_documento: '12345678',
        id_metodo_pago: 1,
        monto_pago: 150000
      }))
      expect(mensualidadesService.list).toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalled()
      const swalCall = Swal.fire.mock.calls.find(call => call[0].icon === 'success')
      expect(swalCall).toBeTruthy()
    })

    it('should handle create error', async () => {
      mensualidadesService.create.mockRejectedValue(new Error('Create failed'))

      const payload = {
        numero_documento: '12345678',
        id_metodo_pago: 1,
        monto_pago: 150000
      }

      await wrapper.vm.nuevaMensualidad(payload)

      expect(Swal.fire).toHaveBeenCalled()
      const swalCall = Swal.fire.mock.calls.find(call => call[0].icon === 'error')
      expect(swalCall).toBeTruthy()
      expect(swalCall[0].title).toBe('Error al crear mensualidad')
    })
  })

  describe('Event Handlers', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should handle recargar event', async () => {
      mensualidadesService.list.mockClear()
      const listaComponent = wrapper.findComponent({ name: 'ListaMensualidades' })
      
      await listaComponent.vm.$emit('recargar')
      await wrapper.vm.$nextTick()

      expect(mensualidadesService.list).toHaveBeenCalled()
    })

    it('should handle nueva event', async () => {
      mensualidadesService.create.mockResolvedValue({ success: true })
      mensualidadesService.list.mockResolvedValue({
        success: true,
        data: mockMensualidades
      })

      const payload = {
        numero_documento: '99999999',
        id_metodo_pago: 1,
        monto_pago: 100000
      }

      const listaComponent = wrapper.findComponent({ name: 'ListaMensualidades' })
      await listaComponent.vm.$emit('nueva', payload)
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mensualidadesService.create).toHaveBeenCalled()
    })
  })
})

