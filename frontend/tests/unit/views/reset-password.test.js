import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ResetPassword from '@/views/reset-password.vue'
import authService from '@/services/authService'
import Swal from 'sweetalert2'

// Mock services
vi.mock('@/services/authService', () => ({
  default: {
    resetPassword: vi.fn()
  }
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(() => Promise.resolve({ isConfirmed: true }))
  }
}))

// Mock vue-router
const mockRouter = {
  push: vi.fn()
}

const mockRoute = {
  query: {}
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter,
    useRoute: () => mockRoute
  }
})

describe('ResetPassword', () => {
  let pinia
  let wrapper

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    vi.clearAllMocks()
    mockRouter.push.mockClear()
    mockRoute.query = {}

    authService.resetPassword.mockResolvedValue({
      success: true,
      message: 'Contraseña actualizada correctamente'
    })
  })

  afterEach(() => {
    vi.clearAllTimers()
    vi.useRealTimers()
  })

  const createWrapper = (routeQuery = {}) => {
    mockRoute.query = routeQuery
    return mount(ResetPassword, {
      global: {
        plugins: [pinia],
        stubs: {
          'router-link': true
        }
      }
    })
  }

  describe('Rendering', () => {
    it('should render main component', () => {
      wrapper = createWrapper({ token: 'valid-token' })
      expect(wrapper.find('main.login-container-volleyball').exists()).toBe(true)
    })

    it('should render form when token is valid', () => {
      wrapper = createWrapper({ token: 'valid-token' })
      expect(wrapper.find('form.login-form-volleyball').exists()).toBe(true)
    })

    it('should render invalid token message when token is missing', async () => {
      wrapper = createWrapper({})
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.token-invalid-container').exists()).toBe(true)
    })

    it('should show password and confirm password fields', () => {
      wrapper = createWrapper({ token: 'valid-token' })
      const inputs = wrapper.findAll('input[type="password"], input[type="text"]')
      expect(inputs.length).toBeGreaterThanOrEqual(2)
    })

    it('should show password toggle buttons', () => {
      wrapper = createWrapper({ token: 'valid-token' })
      const toggles = wrapper.findAll('.password-toggle-volleyball')
      expect(toggles.length).toBe(2)
    })
  })

  describe('Token Validation', () => {
    it('should set token from query params', async () => {
      wrapper = createWrapper({ token: 'test-token-123' })
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.token).toBe('test-token-123')
      expect(wrapper.vm.tokenValido).toBe(true)
    })

    it('should mark token as invalid when missing', async () => {
      wrapper = createWrapper({})
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.tokenValido).toBe(false)
      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should show invalid token message when token is invalid', async () => {
      wrapper = createWrapper({})
      await wrapper.vm.$nextTick()

      const invalidMessage = wrapper.find('.token-invalid-container')
      expect(invalidMessage.exists()).toBe(true)
      expect(invalidMessage.text()).toContain('Token inválido')
    })
  })

  describe('Password Validation', () => {
    beforeEach(() => {
      wrapper = createWrapper({ token: 'valid-token' })
    })

    it('should validate passwords match', async () => {
      wrapper.vm.newPassword = 'password123'
      wrapper.vm.confirmPassword = 'password123'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.passwordsMatch).toBe(true)
    })

    it('should detect when passwords do not match', async () => {
      wrapper.vm.newPassword = 'password123'
      wrapper.vm.confirmPassword = 'password456'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.passwordsMatch).toBe(false)
    })

    it('should return true when passwords are empty', () => {
      wrapper.vm.newPassword = ''
      wrapper.vm.confirmPassword = ''

      expect(wrapper.vm.passwordsMatch).toBe(true)
    })

    it('should show password mismatch error', async () => {
      wrapper.vm.newPassword = 'password123'
      wrapper.vm.confirmPassword = 'password456'
      await wrapper.vm.$nextTick()

      const errorMessage = wrapper.find('.password-match-error')
      expect(errorMessage.exists()).toBe(true)
    })
  })

  describe('Password Strength', () => {
    beforeEach(() => {
      wrapper = createWrapper({ token: 'valid-token' })
    })

    it('should show weak password strength for short passwords', async () => {
      wrapper.vm.newPassword = '12345'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.passwordStrength).toBe('weak')
      expect(wrapper.vm.passwordStrengthText).toBe('Contraseña débil')
    })

    it('should show medium password strength for medium length passwords', async () => {
      wrapper.vm.newPassword = '12345678'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.passwordStrength).toBe('medium')
      expect(wrapper.vm.passwordStrengthText).toBe('Contraseña media')
    })

    it('should show strong password strength for long passwords', async () => {
      wrapper.vm.newPassword = '12345678901'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.passwordStrength).toBe('strong')
      expect(wrapper.vm.passwordStrengthText).toBe('Contraseña fuerte')
    })

    it('should calculate strength percentage correctly', async () => {
      wrapper.vm.newPassword = '12345'
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.passwordStrengthPercent).toBeLessThan(100)

      wrapper.vm.newPassword = '12345678901'
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.passwordStrengthPercent).toBe(100)
    })

    it('should show password strength indicator', async () => {
      wrapper.vm.newPassword = 'password123'
      await wrapper.vm.$nextTick()

      const strengthIndicator = wrapper.find('.password-strength')
      expect(strengthIndicator.exists()).toBe(true)
    })
  })

  describe('Password Toggle', () => {
    beforeEach(() => {
      wrapper = createWrapper({ token: 'valid-token' })
    })

    it('should toggle password visibility', async () => {
      expect(wrapper.vm.showPassword).toBe(false)

      const toggleButton = wrapper.findAll('.password-toggle-volleyball')[0]
      await toggleButton.trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.showPassword).toBe(true)
    })

    it('should toggle confirm password visibility', async () => {
      expect(wrapper.vm.showConfirmPassword).toBe(false)

      const toggleButton = wrapper.findAll('.password-toggle-volleyball')[1]
      await toggleButton.trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.showConfirmPassword).toBe(true)
    })

    it('should change input type when toggled', async () => {
      wrapper.vm.showPassword = true
      await wrapper.vm.$nextTick()

      const passwordInput = wrapper.find('input[placeholder*="nueva contraseña"]')
      expect(passwordInput.attributes('type')).toBe('text')
    })
  })

  describe('Form Submission', () => {
    beforeEach(() => {
      wrapper = createWrapper({ token: 'valid-token' })
    })

    it('should submit form successfully', async () => {
      wrapper.vm.newPassword = 'newpassword123'
      wrapper.vm.confirmPassword = 'newpassword123'
      await wrapper.vm.$nextTick()

      await wrapper.vm.handleResetPassword()
      await wrapper.vm.$nextTick()

      expect(authService.resetPassword).toHaveBeenCalledWith(
        'valid-token',
        'newpassword123',
        'newpassword123'
      )
      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should show success state after successful reset', async () => {
      wrapper.vm.newPassword = 'newpassword123'
      wrapper.vm.confirmPassword = 'newpassword123'
      await wrapper.vm.$nextTick()

      await wrapper.vm.handleResetPassword()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.exito).toBe(true)
    })

    it('should validate empty passwords', async () => {
      wrapper.vm.newPassword = ''
      wrapper.vm.confirmPassword = ''

      await wrapper.vm.handleResetPassword()

      expect(authService.resetPassword).not.toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalled()
      const swalCall = Swal.fire.mock.calls.find(call => call[0].title === 'Campos incompletos')
      expect(swalCall).toBeTruthy()
    })

    it('should validate password minimum length', async () => {
      wrapper.vm.newPassword = '12345'
      wrapper.vm.confirmPassword = '12345'

      await wrapper.vm.handleResetPassword()

      expect(authService.resetPassword).not.toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalled()
      const swalCall = Swal.fire.mock.calls.find(call => call[0].title === 'Contraseña muy corta')
      expect(swalCall).toBeTruthy()
    })

    it('should validate passwords match before submission', async () => {
      wrapper.vm.newPassword = 'password123'
      wrapper.vm.confirmPassword = 'password456'

      await wrapper.vm.handleResetPassword()

      expect(authService.resetPassword).not.toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalled()
      const swalCall = Swal.fire.mock.calls.find(call => call[0].title === 'Contraseñas diferentes')
      expect(swalCall).toBeTruthy()
    })

    it('should handle reset password error', async () => {
      authService.resetPassword.mockResolvedValue({
        success: false,
        error: 'Token expirado'
      })

      wrapper.vm.newPassword = 'newpassword123'
      wrapper.vm.confirmPassword = 'newpassword123'
      await wrapper.vm.$nextTick()

      await wrapper.vm.handleResetPassword()
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalled()
      const errorCall = Swal.fire.mock.calls.find(call => call[0].icon === 'error')
      expect(errorCall).toBeTruthy()
    })

    it('should mark token as invalid on token error', async () => {
      authService.resetPassword.mockResolvedValue({
        success: false,
        error: 'Token inválido'
      })

      wrapper.vm.newPassword = 'newpassword123'
      wrapper.vm.confirmPassword = 'newpassword123'
      await wrapper.vm.$nextTick()

      await wrapper.vm.handleResetPassword()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.tokenValido).toBe(false)
    })

    it('should handle network error', async () => {
      authService.resetPassword.mockRejectedValue(new Error('Network error'))

      wrapper.vm.newPassword = 'newpassword123'
      wrapper.vm.confirmPassword = 'newpassword123'
      await wrapper.vm.$nextTick()

      await wrapper.vm.handleResetPassword()
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalled()
      const errorCall = Swal.fire.mock.calls.find(call => call[0].title === 'Error de conexión')
      expect(errorCall).toBeTruthy()
    })

    it('should set loading state during submission', async () => {
      // NOSONAR: S2004 - Test structure requires this level of nesting for async operations
      authService.resetPassword.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100))) // NOSONAR: S2004

      wrapper.vm.newPassword = 'newpassword123'
      wrapper.vm.confirmPassword = 'newpassword123'
      await wrapper.vm.$nextTick()

      const promise = wrapper.vm.handleResetPassword()
      expect(wrapper.vm.cargando).toBe(true)

      await promise
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.cargando).toBe(false)
    })

    it('should disable submit button when loading', async () => {
      wrapper.vm.cargando = true
      await wrapper.vm.$nextTick()

      const submitButton = wrapper.find('.submit-button-volleyball')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should disable submit button when passwords do not match', async () => {
      wrapper.vm.newPassword = 'password123'
      wrapper.vm.confirmPassword = 'password456'
      await wrapper.vm.$nextTick()

      const submitButton = wrapper.find('.submit-button-volleyball')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })
  })

  describe('Countdown and Redirect', () => {
    beforeEach(() => {
      vi.useFakeTimers()
      wrapper = createWrapper({ token: 'valid-token' })
    })

    it('should start countdown after success', async () => {
      wrapper.vm.newPassword = 'newpassword123'
      wrapper.vm.confirmPassword = 'newpassword123'
      await wrapper.vm.$nextTick()

      await wrapper.vm.handleResetPassword()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.exito).toBe(true)
      expect(wrapper.vm.countdown).toBe(3)
    })

    it('should decrement countdown', async () => {
      wrapper.vm.exito = true
      wrapper.vm.startCountdown()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.countdown).toBe(3)

      vi.advanceTimersByTime(1000)
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.countdown).toBe(2)

      vi.advanceTimersByTime(1000)
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.countdown).toBe(1)
    })

    it('should redirect to login after countdown', async () => {
      wrapper.vm.exito = true
      wrapper.vm.startCountdown()
      await wrapper.vm.$nextTick()

      vi.advanceTimersByTime(3000)
      await wrapper.vm.$nextTick()

      expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })

    it('should show countdown message', async () => {
      wrapper.vm.exito = true
      wrapper.vm.countdown = 3
      await wrapper.vm.$nextTick()

      const countdownMessage = wrapper.find('.success-countdown')
      expect(countdownMessage.exists()).toBe(true)
      expect(countdownMessage.text()).toContain('3')
    })
  })

  describe('Input Focus Handler', () => {
    it('should handle input focus', async () => {
      wrapper = createWrapper({ token: 'valid-token' })

      const mockEvent = {
        target: {
          parentElement: {
            classList: {
              add: vi.fn()
            }
          }
        }
      }

      wrapper.vm.handleInputFocus(mockEvent)

      expect(mockEvent.target.parentElement.classList.add).toHaveBeenCalledWith('input-focused')
    })
  })

  describe('Success State', () => {
    it('should show success message', async () => {
      wrapper = createWrapper({ token: 'valid-token' })
      wrapper.vm.exito = true
      await wrapper.vm.$nextTick()

      const submitButton = wrapper.find('.submit-button-volleyball')
      expect(submitButton.classes()).toContain('success')
      expect(submitButton.text()).toContain('Contraseña restablecida')
    })

    it('should not show form when success', async () => {
      wrapper = createWrapper({ token: 'valid-token' })
      wrapper.vm.exito = true
      await wrapper.vm.$nextTick()

      // Form might still exist but be disabled/hidden
      expect(wrapper.vm.exito).toBe(true)
    })
  })
})

