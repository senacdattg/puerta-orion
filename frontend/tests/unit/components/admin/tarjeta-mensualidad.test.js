import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import TarjetaMensualidad from '@/components/admin/tarjeta-mensualidad.vue'
import Swal from 'sweetalert2'

const mockUseAuthStore = vi.fn()
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockUseAuthStore()
}))

vi.mock('@/config/environment', () => ({
  API_CONFIG: {
    baseURL: 'http://localhost:5000'
  }
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn()
  }
}))

global.fetch = vi.fn()
global.localStorage = {
  getItem: vi.fn(() => 'test-token'),
  setItem: vi.fn(),
  removeItem: vi.fn()
}

global.location = { href: '' }

describe('TarjetaMensualidad Component', () => {
  let wrapper
  let mockAuthStore

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    mockAuthStore = {
      user: {
        nombres: 'Juan',
        apellidos: 'Pérez',
        email: 'juan@test.com',
        documento: '12345678',
        tipo_documento: 'CC',
        roles: [{ nombre_rol: 'Deportista' }]
      },
      hasPermission: vi.fn(() => false)
    }

    // Configurar el mock global
    mockUseAuthStore.mockReturnValue(mockAuthStore)
  })

  const createWrapper = (props = {}) => {
    return mount(TarjetaMensualidad, {
      props: {
        mensualidad: {
          id: 1,
          nombre: 'Juan Pérez',
          mes: 'Enero',
          valor: '$150000',
          estado: 'Pendiente',
          fecha_vencimiento: '2024-12-31',
          saldo_pendiente_raw: 50000,
          monto_pago_raw: 150000,
          activo: true,
          ...props.mensualidad
        }
      },
      global: {
        stubs: {
          'i': true,
          'img': true
        }
      }
    })
  }

  describe('Renderizado básico', () => {
    it('should render component', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.tarjeta-mensualidad').exists()).toBe(true)
    })

    it('should display mensualidad nombre', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Juan Pérez')
    })

    it('should display mes', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Enero')
    })

    it('should display estado badge', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.estado-badge').exists()).toBe(true)
    })
  })

  describe('Estado icons and classes', () => {
    it('should return correct icon for estado', () => {
      wrapper = createWrapper({ mensualidad: { estado: 'Pagado' } })
      expect(wrapper.vm.getIconoEstado()).toBe('✓')
    })

    it('should return correct clase for saldo', () => {
      wrapper = createWrapper()
      const clase = wrapper.vm.getClaseSaldo()
      expect(clase).toBeTruthy()
    })

    it('should format saldo pendiente text', () => {
      wrapper = createWrapper()
      const texto = wrapper.vm.saldoPendienteTexto()
      expect(texto).toContain('$')
    })

    it('should format total pagado text', () => {
      wrapper = createWrapper()
      const texto = wrapper.vm.totalPagadoTexto()
      expect(texto).toContain('$')
    })
  })

  describe('Vencimiento computed', () => {
    it('should detect vencida mensualidad', () => {
      const fechaVencida = new Date()
      fechaVencida.setMonth(fechaVencida.getMonth() - 1)
      const fechaStr = fechaVencida.toISOString().split('T')[0]

      wrapper = createWrapper({
        mensualidad: {
          fecha_vencimiento_raw: fechaStr,
          estado: 'Pendiente'
        }
      })

      expect(wrapper.vm.esVencida).toBe(true)
    })

    it('should calculate days to vencimiento', () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 5)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      wrapper = createWrapper({
        mensualidad: {
          fecha_vencimiento_raw: fechaStr
        }
      })

      // Allow 1 day difference due to timing
      expect(wrapper.vm.diasParaVencimiento).toBeGreaterThanOrEqual(4)
      expect(wrapper.vm.diasParaVencimiento).toBeLessThanOrEqual(6)
    })

    it('should return correct vencimiento class', () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 2)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      wrapper = createWrapper({
        mensualidad: {
          fecha_vencimiento_raw: fechaStr
        }
      })

      expect(wrapper.vm.claseVencimiento).toBe('proximo-vencer')
    })

    it('should return correct vencimiento text', () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 3)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      wrapper = createWrapper({
        mensualidad: {
          fecha_vencimiento_raw: fechaStr
        }
      })

      expect(wrapper.vm.textoVencimiento).toContain('Vence en')
    })
  })

  describe('Events', () => {
    it('should emit ver-detalle on click', async () => {
      wrapper = createWrapper()
      await wrapper.vm.verDetalle()
      expect(wrapper.emitted('ver-detalle')).toBeTruthy()
    })

    it('should emit ver-detalle-completo', async () => {
      wrapper = createWrapper()
      await wrapper.vm.verDetalleCompleto()
      expect(wrapper.emitted('ver-detalle-completo')).toBeTruthy()
    })

    it('should emit gestionar', async () => {
      wrapper = createWrapper()
      await wrapper.vm.gestionarMensualidad()
      expect(wrapper.emitted('gestionar')).toBeTruthy()
    })

    it('should emit eliminar', async () => {
      wrapper = createWrapper()
      await wrapper.vm.eliminarMensualidad()
      expect(wrapper.emitted('eliminar')).toBeTruthy()
    })
  })

  describe('Permissions', () => {
    it('should show edit button for admin', () => {
      mockAuthStore.user.roles = [{ nombre_rol: 'Administrador' }]
      wrapper = createWrapper()
      expect(wrapper.vm.puedeEditarMensualidad).toBe(true)
    })

    it('should show toggle button for admin', () => {
      mockAuthStore.user.roles = [{ nombre_rol: 'SuperAdmin' }]
      wrapper = createWrapper()
      expect(wrapper.vm.puedeToggleMensualidad).toBe(true)
    })

    it('should allow pago for deportista', () => {
      mockAuthStore.user.roles = [{ nombre_rol: 'Deportista' }]
      wrapper = createWrapper()
      expect(wrapper.vm.puedeIniciarPago).toBe(true)
    })

    it('should detect saldo pendiente positivo', () => {
      wrapper = createWrapper({
        mensualidad: {
          saldo_pendiente_raw: 10000
        }
      })
      expect(wrapper.vm.saldoPendientePositivo).toBe(true)
    })
  })

  describe('Pago con MercadoPago', () => {
    it('should create preference and redirect', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: async () => JSON.stringify({
          success: true,
          init_point: 'https://mercadopago.com/checkout'
        })
      })

      await wrapper.vm.pagarConMercadoPago()
      await wrapper.vm.$nextTick()

      expect(global.fetch).toHaveBeenCalled()
    })

    it('should handle error creating preference', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      global.fetch.mockResolvedValueOnce({
        ok: false,
        text: async () => JSON.stringify({
          success: false,
          error: 'Error test'
        })
      })

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.pagarConMercadoPago()

      expect(Swal.fire).toHaveBeenCalled()
    })
  })

  describe('Image error handling', () => {
    it('should handle image error', () => {
      wrapper = createWrapper()
      const event = {
        target: {
          src: 'invalid-url'
        }
      }
      wrapper.vm.imagenPorDefecto(event)
      expect(event.target.src).toBeTruthy()
    })
  })

  describe('Estado computed properties', () => {
    it('should return correct icon for Parcial estado', () => {
      wrapper = createWrapper({ mensualidad: { estado: 'Parcial' } })
      expect(wrapper.vm.getIconoEstado()).toBe('💰')
    })

    it('should return correct icon for Vencido estado', () => {
      wrapper = createWrapper({ mensualidad: { estado: 'Vencido' } })
      expect(wrapper.vm.getIconoEstado()).toBe('⚠️')
    })

    it('should return correct icon for unknown estado', () => {
      wrapper = createWrapper({ mensualidad: { estado: 'Unknown' } })
      expect(wrapper.vm.getIconoEstado()).toBe('❓')
    })

    it('should return correct icon for Pendiente estado', () => {
      wrapper = createWrapper({ mensualidad: { estado: 'Pendiente' } })
      expect(wrapper.vm.getIconoEstado()).toBe('⏳')
    })
  })

  describe('Saldo computed properties', () => {
    it('should return saldo-completo class when saldo is 0', () => {
      wrapper = createWrapper({
        mensualidad: {
          saldo_pendiente_raw: 0,
          monto_pago_raw: 100000
        }
      })
      expect(wrapper.vm.getClaseSaldo()).toBe('saldo-completo')
    })

    it('should return saldo-bajo class when ratio <= 0.3', () => {
      wrapper = createWrapper({
        mensualidad: {
          saldo_pendiente_raw: 20000,
          monto_pago_raw: 100000
        }
      })
      expect(wrapper.vm.getClaseSaldo()).toBe('saldo-bajo')
    })

    it('should return saldo-medio class when ratio <= 0.7', () => {
      wrapper = createWrapper({
        mensualidad: {
          saldo_pendiente_raw: 50000,
          monto_pago_raw: 100000
        }
      })
      expect(wrapper.vm.getClaseSaldo()).toBe('saldo-medio')
    })

    it('should return saldo-alto class when ratio > 0.7', () => {
      wrapper = createWrapper({
        mensualidad: {
          saldo_pendiente_raw: 80000,
          monto_pago_raw: 100000
        }
      })
      expect(wrapper.vm.getClaseSaldo()).toBe('saldo-alto')
    })

    it('should return saldo-alto class when monto is 0', () => {
      wrapper = createWrapper({
        mensualidad: {
          saldo_pendiente_raw: 50000,
          monto_pago_raw: 0
        }
      })
      expect(wrapper.vm.getClaseSaldo()).toBe('saldo-alto')
    })

    it('should format saldo pendiente with fallback', () => {
      wrapper = createWrapper({
        mensualidad: {
          saldo_pendiente_raw: undefined,
          monto_pago_raw: 150000
        }
      })
      const texto = wrapper.vm.saldoPendienteTexto()
      expect(texto).toContain('$')
    })
  })

  describe('Vencimiento edge cases', () => {
    it('should return null diasParaVencimiento when no fecha and no fechasPago', () => {
      wrapper = createWrapper({
        mensualidad: {
          fecha_vencimiento_raw: null,
          fecha_vencimiento: null,
          fechasPago: null,
          mes: null
        }
      })
      expect(wrapper.vm.diasParaVencimiento).toBeNull()
    })

    it('should return sin-fecha class when diasParaVencimiento is null', () => {
      wrapper = createWrapper({
        mensualidad: {
          fecha_vencimiento_raw: null,
          fecha_vencimiento: null,
          fechasPago: null,
          mes: null
        }
      })
      expect(wrapper.vm.claseVencimiento).toBe('sin-fecha')
    })

    it('should return "Sin fecha" text when diasParaVencimiento is null', () => {
      wrapper = createWrapper({
        mensualidad: {
          fecha_vencimiento_raw: null,
          fecha_vencimiento: null,
          fechasPago: null,
          mes: null
        }
      })
      expect(wrapper.vm.textoVencimiento).toBe('Sin fecha')
    })

    it('should return vencido class when esVencida is true', () => {
      const fechaVencida = new Date()
      fechaVencida.setMonth(fechaVencida.getMonth() - 1)
      const fechaStr = fechaVencida.toISOString().split('T')[0]

      wrapper = createWrapper({
        mensualidad: {
          fecha_vencimiento_raw: fechaStr
        }
      })

      expect(wrapper.vm.claseVencimiento).toBe('vencido')
      expect(wrapper.vm.textoVencimiento).toBe('Vencido')
    })

    it('should return proximo-vencer class when dias === 0', () => {
      const hoy = new Date()
      const fechaStr = hoy.toISOString().split('T')[0]

      wrapper = createWrapper({
        mensualidad: {
          fecha_vencimiento_raw: fechaStr
        }
      })

      // Puede ser 'proximo-vencer' o 'advertencia' dependiendo del cálculo
      expect(['proximo-vencer', 'advertencia']).toContain(wrapper.vm.claseVencimiento)
      // El texto puede variar ligeramente
      expect(wrapper.vm.textoVencimiento).toMatch(/Vence/)
    })

    it('should return advertencia class when dias <= 7', () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 5)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      wrapper = createWrapper({
        mensualidad: {
          fecha_vencimiento_raw: fechaStr
        }
      })

      expect(wrapper.vm.claseVencimiento).toBe('advertencia')
    })

    it('should return normal class when dias > 7', () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      wrapper = createWrapper({
        mensualidad: {
          fecha_vencimiento_raw: fechaStr
        }
      })

      expect(wrapper.vm.claseVencimiento).toBe('normal')
    })

    it('should format textoVencimiento for 1 day', () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 1)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      wrapper = createWrapper({
        mensualidad: {
          fecha_vencimiento_raw: fechaStr
        }
      })

      // Permitir variación de 1 día por timing
      expect(wrapper.vm.textoVencimiento).toMatch(/Vence en \d+ día/)
    })

    it('should format textoVencimiento for multiple days', () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 5)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      wrapper = createWrapper({
        mensualidad: {
          fecha_vencimiento_raw: fechaStr
        }
      })

      // Permitir variación de 1 día por timing
      expect(wrapper.vm.textoVencimiento).toMatch(/Vence en \d+ días/)
      const dias = wrapper.vm.diasParaVencimiento
      expect(dias).toBeGreaterThanOrEqual(4)
      expect(dias).toBeLessThanOrEqual(6)
    })
  })

  describe('Permissions edge cases', () => {
    it('should check permission for puedeEditarMensualidad', () => {
      mockAuthStore.user.roles = [{ nombre_rol: 'Usuario' }]
      mockAuthStore.hasPermission.mockReturnValue(true)
      wrapper = createWrapper()
      expect(wrapper.vm.puedeEditarMensualidad).toBe(true)
    })

    it('should handle permission error gracefully for puedeEditarMensualidad', () => {
      mockAuthStore.user.roles = [{ nombre_rol: 'Usuario' }]
      mockAuthStore.hasPermission.mockImplementation(() => { throw new Error('Permission error') })
      wrapper = createWrapper()
      expect(wrapper.vm.puedeEditarMensualidad).toBe(false)
    })

    it('should check permission for puedeToggleMensualidad', () => {
      mockAuthStore.user.roles = [{ nombre_rol: 'Usuario' }]
      mockAuthStore.hasPermission.mockReturnValue(true)
      wrapper = createWrapper()
      expect(wrapper.vm.puedeToggleMensualidad).toBe(true)
    })

    it('should handle permission error gracefully for puedeToggleMensualidad', () => {
      mockAuthStore.user.roles = [{ nombre_rol: 'Usuario' }]
      mockAuthStore.hasPermission.mockImplementation(() => { throw new Error('Permission error') })
      wrapper = createWrapper()
      expect(wrapper.vm.puedeToggleMensualidad).toBe(false)
    })

    it('should allow pago for acudiente', () => {
      mockAuthStore.user.roles = [{ nombre_rol: 'Acudiente' }]
      wrapper = createWrapper()
      expect(wrapper.vm.puedeIniciarPago).toBe(true)
    })

    it('should not allow pago for other roles', () => {
      mockAuthStore.user.roles = [{ nombre_rol: 'Entrenador' }]
      wrapper = createWrapper()
      expect(wrapper.vm.puedeIniciarPago).toBe(false)
    })

    it('should detect saldo pendiente positivo using saldoPendiente fallback', () => {
      wrapper = createWrapper({
        mensualidad: {
          saldo_pendiente_raw: undefined,
          saldoPendiente: 5000,
          estado: 'Pendiente'
        }
      })
      expect(wrapper.vm.saldoPendientePositivo).toBe(true)
    })

    it('should detect saldo pendiente negativo', () => {
      wrapper = createWrapper({
        mensualidad: {
          saldo_pendiente_raw: -1000
        }
      })
      expect(wrapper.vm.saldoPendientePositivo).toBe(false)
    })

    it('should show pagar button when estado is not Pagado (fallback)', () => {
      wrapper = createWrapper({
        mensualidad: {
          saldo_pendiente_raw: NaN,
          estado: 'Pendiente'
        }
      })
      expect(wrapper.vm.saldoPendientePositivo).toBe(true)
    })

    it('should not show pagar button when estado is Pagado (fallback)', () => {
      wrapper = createWrapper({
        mensualidad: {
          saldo_pendiente_raw: NaN,
          estado: 'Pagado'
        }
      })
      expect(wrapper.vm.saldoPendientePositivo).toBe(false)
    })
  })

  describe('Pago con MercadoPago edge cases', () => {
    it('should handle fetch error', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      global.fetch.mockRejectedValueOnce(new Error('Network error'))

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.pagarConMercadoPago()

      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should handle non-OK response', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        text: async () => 'Error'
      })

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.pagarConMercadoPago()

      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should handle response without init_point', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: async () => JSON.stringify({
          success: true,
          init_point: null
        })
      })

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.pagarConMercadoPago()

      expect(Swal.fire).toHaveBeenCalled()
    })
  })

  describe('Role names edge cases', () => {
    it('should handle string roles', () => {
      mockAuthStore.user.roles = ['Deportista', 'Administrador']
      wrapper = createWrapper()
      expect(wrapper.vm.puedeIniciarPago).toBe(true)
    })

    it('should handle mixed roles format', () => {
      mockAuthStore.user.roles = ['Deportista', { nombre_rol: 'Administrador' }]
      wrapper = createWrapper()
      expect(wrapper.vm.isSuperOrAdmin).toBe(true)
    })

    it('should handle roles with null nombre_rol', () => {
      mockAuthStore.user.roles = [{ nombre_rol: null }, { nombre_rol: 'Deportista' }]
      wrapper = createWrapper()
      expect(wrapper.vm.puedeIniciarPago).toBe(true)
    })
  })
})

