import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import Pie from '@/components/layout/pie.vue'

const mockUseAuthStore = vi.fn()
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockUseAuthStore()
}))

vi.mock('@/config/constants', () => ({
  APP_CONFIG: {
    name: 'Puerta Orion',
    fullName: 'Club Deportivo Puerta de Orión',
    description: 'Club deportivo comprometido con el desarrollo integral',
    founded: '2020',
    contact: {
      address: 'Carrera 12 # 34-56, Colombia',
      phone: '+57 300 123 4567',
      email: 'contacto@puertaorion.com'
    }
  },
  SOCIAL_LINKS: [
    { name: 'Facebook', url: 'https://facebook.com/puertaorion', icon: 'fab fa-facebook' },
    { name: 'Instagram', url: 'https://instagram.com/puertaorion', icon: 'fab fa-instagram' },
    { name: 'Twitter', url: 'https://twitter.com/puertaorion', icon: 'fab fa-twitter' }
  ]
}))

describe('Pie Component', () => {
  let wrapper
  let router
  let mockAuthStore

  beforeEach(() => {
    vi.clearAllMocks()
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } }
      ]
    })

    mockAuthStore = {
      user: null,
      activeRole: null
    }

    mockUseAuthStore.mockReturnValue(mockAuthStore)
  })

  const createWrapper = () => {
    return mount(Pie, {
      global: {
        plugins: [router],
        stubs: {
          'i': true,
          'router-link': {
            template: '<a><slot></slot></a>',
            props: ['to']
          }
        }
      }
    })
  }

  describe('Renderizado básico', () => {
    it('should render component', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.footer-enhanced').exists()).toBe(true)
    })

    it('should display app full name', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Club Deportivo Puerta de Orión')
    })

    it('should display app description', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Club deportivo comprometido con el desarrollo integral')
    })

    it('should display founded year', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('desde 2020')
    })

    it('should display contact information', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Carrera 12 # 34-56, Colombia')
      expect(wrapper.text()).toContain('+57 300 123 4567')
      expect(wrapper.text()).toContain('contacto@puertaorion.com')
    })

    it('should display copyright', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('2024 Club Deportivo Puerta de Orión')
    })
  })

  describe('Social links', () => {
    it('should render social links', () => {
      wrapper = createWrapper()
      const socialLinks = wrapper.findAll('.social-link')
      expect(socialLinks.length).toBe(3)
    })

    it('should validate URLs safely', () => {
      wrapper = createWrapper()
      const socialLinks = wrapper.vm.socialLinks
      expect(socialLinks.length).toBeGreaterThan(0)
      socialLinks.forEach(link => {
        expect(link.url).toMatch(/^https?:\/\//)
      })
    })

    it('should handle invalid URLs', () => {
      wrapper = createWrapper()
      const invalidUrl = wrapper.vm.validarUrlSeguraEnComponente('javascript:alert(1)')
      expect(invalidUrl).toBe('#')
    })

    it('should handle null URL', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.validarUrlSeguraEnComponente(null)
      expect(result).toBe('#')
    })

    it('should handle non-string URL', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.validarUrlSeguraEnComponente(123)
      expect(result).toBe('#')
    })

    it('should warn for unsafe URLs', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      wrapper = createWrapper()
      wrapper.vm.validarUrlSeguraEnComponente('ftp://unsafe.com')
      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })
  })

  describe('User role computed', () => {
    it('should return activeRole when SuperAdmin', () => {
      mockAuthStore.activeRole = 'SuperAdmin'
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Admin')
    })

    it('should return activeRole when Administrador', () => {
      mockAuthStore.activeRole = 'Administrador'
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Admin')
    })

    it('should return activeRole when Deportista', () => {
      mockAuthStore.activeRole = 'Deportista'
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Deportista')
    })

    it('should return activeRole when Acudiente', () => {
      mockAuthStore.activeRole = 'Acudiente'
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Acudiente')
    })

    it('should return activeRole when Entrenador', () => {
      mockAuthStore.activeRole = 'Entrenador'
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Entrenador')
    })

    it('should return Usuario when no user and no activeRole', () => {
      mockAuthStore.user = null
      mockAuthStore.activeRole = null
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Usuario')
    })

    it('should return Usuario when user has no roles', () => {
      mockAuthStore.user = { roles: [] }
      mockAuthStore.activeRole = null
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Usuario')
    })

    it('should return Admin when user has SuperAdmin role', () => {
      mockAuthStore.user = { roles: [{ nombre_rol: 'SuperAdmin' }] }
      mockAuthStore.activeRole = null
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Admin')
    })

    it('should return Admin when user has Administrador role', () => {
      mockAuthStore.user = { roles: [{ nombre_rol: 'Administrador' }] }
      mockAuthStore.activeRole = null
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Admin')
    })

    it('should return Entrenador when user has Entrenador role', () => {
      mockAuthStore.user = { roles: [{ nombre_rol: 'Entrenador' }] }
      mockAuthStore.activeRole = null
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Entrenador')
    })

    it('should return Deportista when user has Deportista role', () => {
      mockAuthStore.user = { roles: [{ nombre_rol: 'Deportista' }] }
      mockAuthStore.activeRole = null
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Deportista')
    })

    it('should return Acudiente when user has Acudiente role', () => {
      mockAuthStore.user = { roles: [{ nombre_rol: 'Acudiente' }] }
      mockAuthStore.activeRole = null
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Acudiente')
    })

    it('should return Usuario when user has usuario role', () => {
      mockAuthStore.user = { roles: [{ nombre_rol: 'usuario' }] }
      mockAuthStore.activeRole = null
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Usuario')
    })

    it('should return UsuarioSinAuth when user has unknown role', () => {
      mockAuthStore.user = { roles: [{ nombre_rol: 'UnknownRole' }] }
      mockAuthStore.activeRole = null
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('UsuarioSinAuth')
    })

    it('should handle string roles', () => {
      mockAuthStore.user = { roles: ['Deportista'] }
      mockAuthStore.activeRole = null
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Deportista')
    })

    it('should handle mixed role formats', () => {
      mockAuthStore.user = { roles: ['Deportista', { nombre_rol: 'Acudiente' }] }
      mockAuthStore.activeRole = null
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Deportista') // First matching
    })

    it('should prioritize activeRole over user roles', () => {
      mockAuthStore.activeRole = 'Deportista'
      mockAuthStore.user = { roles: [{ nombre_rol: 'Administrador' }] }
      wrapper = createWrapper()
      expect(wrapper.vm.userRole).toBe('Deportista')
    })
  })

  describe('Acciones rápidas computed', () => {
    it('should return acciones for Usuario role', () => {
      mockAuthStore.activeRole = null
      mockAuthStore.user = { roles: [{ nombre_rol: 'usuario' }] }
      wrapper = createWrapper()
      const acciones = wrapper.vm.accionesRapidas
      expect(acciones.length).toBe(3)
      expect(acciones[0].texto).toBe('Calendario')
      expect(acciones[1].texto).toBe('Galería')
      expect(acciones[2].texto).toBe('Mi Perfil')
    })

    it('should return acciones for Entrenador role', () => {
      mockAuthStore.activeRole = 'Entrenador'
      wrapper = createWrapper()
      const acciones = wrapper.vm.accionesRapidas
      expect(acciones.length).toBe(4)
      expect(acciones.some(a => a.texto === 'Deportistas')).toBe(true)
    })

    it('should return acciones for Acudiente role', () => {
      mockAuthStore.activeRole = 'Acudiente'
      wrapper = createWrapper()
      const acciones = wrapper.vm.accionesRapidas
      expect(acciones.length).toBe(4)
      expect(acciones.some(a => a.texto === 'Mis Deportistas')).toBe(true)
      expect(acciones.some(a => a.texto === 'Mensualidades')).toBe(true)
    })

    it('should return acciones for Deportista role', () => {
      mockAuthStore.activeRole = 'Deportista'
      wrapper = createWrapper()
      const acciones = wrapper.vm.accionesRapidas
      expect(acciones.length).toBe(4)
      expect(acciones.some(a => a.texto === 'Mi Perfil')).toBe(true)
      expect(acciones.some(a => a.texto === 'Mensualidades')).toBe(true)
      expect(acciones.some(a => a.texto === 'Eventos')).toBe(true)
    })

    it('should return acciones for Admin role', () => {
      mockAuthStore.activeRole = 'SuperAdmin'
      wrapper = createWrapper()
      const acciones = wrapper.vm.accionesRapidas
      expect(acciones.length).toBe(4)
      expect(acciones.some(a => a.texto === 'Panel Admin')).toBe(true)
      expect(acciones.some(a => a.texto === 'Deportistas')).toBe(true)
      expect(acciones.some(a => a.texto === 'Mensualidades')).toBe(true)
    })

    it('should return acciones for UsuarioSinAuth role', () => {
      mockAuthStore.activeRole = null
      mockAuthStore.user = { roles: [{ nombre_rol: 'UnknownRole' }] }
      wrapper = createWrapper()
      const acciones = wrapper.vm.accionesRapidas
      expect(acciones.length).toBe(2)
      expect(acciones[0].texto).toBe('Calendario')
      expect(acciones[1].texto).toBe('Galería')
    })

    it('should fallback to UsuarioSinAuth for unknown role', () => {
      mockAuthStore.activeRole = null
      mockAuthStore.user = { roles: [{ nombre_rol: 'UnknownRole' }] }
      wrapper = createWrapper()
      const acciones = wrapper.vm.accionesRapidas
      expect(acciones.length).toBe(2) // UsuarioSinAuth acciones
    })
  })

  describe('URL validation edge cases', () => {
    it('should handle URL with whitespace', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.validarUrlSeguraEnComponente('  https://example.com  ')
      expect(result).toBe('https://example.com')
    })

    it('should handle URL with dangerous characters', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      wrapper = createWrapper()
      const result = wrapper.vm.validarUrlSeguraEnComponente('https://example.com<script>')
      expect(result).toBe('#')
      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })

    it('should handle empty string URL', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.validarUrlSeguraEnComponente('')
      expect(result).toBe('#')
    })

    it('should handle URL without protocol', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      wrapper = createWrapper()
      const result = wrapper.vm.validarUrlSeguraEnComponente('example.com')
      expect(result).toBe('#')
      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })

    it('should allow valid https URL', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.validarUrlSeguraEnComponente('https://example.com')
      expect(result).toBe('https://example.com')
    })

    it('should allow valid http URL', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.validarUrlSeguraEnComponente('http://example.com')
      expect(result).toBe('http://example.com')
    })
  })
})

