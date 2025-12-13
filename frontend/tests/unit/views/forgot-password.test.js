import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ForgotPassword from '@/views/forgot-password.vue'
import authService from '@/services/authService'
import Swal from 'sweetalert2'

// Mock services
vi.mock('@/services/authService', () => ({
  default: {
    forgotPassword: vi.fn()
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

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter
  }
})

describe('ForgotPassword', () => {
  let pinia
  let wrapper

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    vi.clearAllMocks()
    mockRouter.push.mockClear()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  const createWrapper = () => {
    return mount(ForgotPassword, {
      global: {
        plugins: [pinia]
      }
    })
  }

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.login-container-volleyball').exists()).toBe(true)
    })

    it('should render form when not enviado', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.login-form-volleyball').exists()).toBe(true)
      expect(wrapper.find('.success-container').exists()).toBe(false)
    })

    it('should render success message when enviado', async () => {
      wrapper = createWrapper()
      wrapper.vm.enviado = true
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.success-container').exists()).toBe(true)
      expect(wrapper.find('.login-form-volleyball').exists()).toBe(false)
    })

    it('should render email input', () => {
      wrapper = createWrapper()
      const emailInput = wrapper.find('input[type="email"]')
      expect(emailInput.exists()).toBe(true)
      expect(emailInput.attributes('placeholder')).toBe('Ingresa tu correo electrónico')
    })

    it('should render submit button', () => {
      wrapper = createWrapper()
      const submitButton = wrapper.find('.submit-button-volleyball')
      expect(submitButton.exists()).toBe(true)
    })

    it('should render back to login link', () => {
      wrapper = createWrapper()
      const backLink = wrapper.find('.back-link-container')
      expect(backLink.exists()).toBe(true)
    })
  })

  describe('Form Validation', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should disable submit button when email is empty', () => {
      wrapper.vm.email = ''
      const submitButton = wrapper.find('.submit-button-volleyball')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should enable submit button when email is provided', async () => {
      wrapper.vm.email = 'test@example.com'
      await wrapper.vm.$nextTick()
      const submitButton = wrapper.find('.submit-button-volleyball')
      expect(submitButton.attributes('disabled')).toBeUndefined()
    })

    it('should show warning when submitting empty email', async () => {
      wrapper.vm.email = ''
      await wrapper.vm.handleForgotPassword()

      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'warning',
        title: 'Correo requerido',
        text: 'Por favor ingresa tu correo electrónico para continuar.'
      })
    })

    it('should validate email format', async () => {
      wrapper.vm.email = 'invalid-email'
      await wrapper.vm.handleForgotPassword()

      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'warning',
        title: 'Correo no válido',
        text: 'Revisa el formato del correo electrónico e inténtalo nuevamente.'
      })
      expect(authService.forgotPassword).not.toHaveBeenCalled()
    })

    it('should accept valid email format', async () => {
      wrapper.vm.email = 'test@example.com'
      authService.forgotPassword.mockResolvedValue({ success: true })

      await wrapper.vm.handleForgotPassword()

      expect(authService.forgotPassword).toHaveBeenCalledWith('test@example.com')
    })
  })

  describe('Password Recovery', () => {
    beforeEach(() => {
      wrapper = createWrapper()
      wrapper.vm.email = 'test@example.com'
    })

    it('should send recovery email successfully', async () => {
      authService.forgotPassword.mockResolvedValue({
        success: true,
        message: 'Email sent successfully'
      })

      await wrapper.vm.handleForgotPassword()

      expect(authService.forgotPassword).toHaveBeenCalledWith('test@example.com')
      expect(Swal.fire).toHaveBeenCalled()
      expect(wrapper.vm.enviado).toBe(true)
    })

    it('should show error when email sending fails', async () => {
      authService.forgotPassword.mockResolvedValue({
        success: false,
        error: 'Email not found'
      })

      await wrapper.vm.handleForgotPassword()

      expect(Swal.fire).toHaveBeenCalled()
      const errorCall = Swal.fire.mock.calls.find(call => call[0].icon === 'error')
      expect(errorCall).toBeTruthy()
      expect(wrapper.vm.enviado).toBe(false)
    })

    it('should handle network error', async () => {
      authService.forgotPassword.mockRejectedValue(new Error('Network error'))

      await wrapper.vm.handleForgotPassword()

      expect(Swal.fire).toHaveBeenCalled()
      const errorCall = Swal.fire.mock.calls.find(call => call[0].icon === 'error' && call[0].title === 'Error de conexión')
      expect(errorCall).toBeTruthy()
    })

    it('should set loading state during request', async () => {
      authService.forgotPassword.mockResolvedValue({ success: true })

      const promise = wrapper.vm.handleForgotPassword()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.cargando).toBe(true)

      await promise
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.cargando).toBe(false)
    })

    it('should disable input during loading', async () => {
      wrapper.vm.cargando = true
      await wrapper.vm.$nextTick()

      const emailInput = wrapper.find('input[type="email"]')
      expect(emailInput.attributes('disabled')).toBeDefined()
    })
  })

  describe('Countdown', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should start countdown after successful email send', async () => {
      authService.forgotPassword.mockResolvedValue({ success: true })
      wrapper.vm.email = 'test@example.com'

      await wrapper.vm.handleForgotPassword()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.enviado).toBe(true)
      expect(wrapper.vm.countdown).toBe(5)
    })

    it('should decrement countdown every second', async () => {
      wrapper.vm.enviado = true
      wrapper.vm.startCountdown()

      expect(wrapper.vm.countdown).toBe(5)

      vi.advanceTimersByTime(1000)
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.countdown).toBe(4)

      vi.advanceTimersByTime(1000)
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.countdown).toBe(3)
    })

    it('should redirect to login after countdown', async () => {
      wrapper.vm.enviado = true
      wrapper.vm.startCountdown()

      vi.advanceTimersByTime(5000)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.countdown).toBe(0)
      expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })
  })

  describe('Success Message', () => {
    it('should display countdown in success message', async () => {
      wrapper = createWrapper()
      wrapper.vm.enviado = true
      wrapper.vm.countdown = 3
      await wrapper.vm.$nextTick()

      const countdownText = wrapper.find('.success-countdown')
      expect(countdownText.exists()).toBe(true)
      expect(countdownText.text()).toContain('3')
    })

    it('should show success title and message', async () => {
      wrapper = createWrapper()
      wrapper.vm.enviado = true
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.success-title').text()).toContain('¡Correo enviado!')
      expect(wrapper.find('.success-message').text()).toContain('Se ha enviado un enlace')
    })
  })

  describe('Input Focus', () => {
    it('should handle input focus event', () => {
      wrapper = createWrapper()
      const emailInput = wrapper.find('input[type="email"]')
      const inputGroup = emailInput.element.parentElement

      emailInput.trigger('focus')

      expect(inputGroup.classList.contains('input-focused')).toBe(true)
    })
  })

  describe('Form Submission', () => {
    beforeEach(() => {
      wrapper = createWrapper()
      wrapper.vm.email = 'test@example.com'
    })

    it('should prevent default form submission', async () => {
      const form = wrapper.find('.login-form-volleyball')
      const preventDefault = vi.fn()
      
      await form.trigger('submit', {
        preventDefault
      })

      expect(authService.forgotPassword).toHaveBeenCalled()
    })

    it('should call handleForgotPassword on form submit', async () => {
      authService.forgotPassword.mockResolvedValue({ success: true })

      const form = wrapper.find('.login-form-volleyball')
      await form.trigger('submit')

      expect(authService.forgotPassword).toHaveBeenCalled()
    })
  })

  describe('Loading State', () => {
    beforeEach(() => {
      wrapper = createWrapper()
      wrapper.vm.email = 'test@example.com'
    })

    it('should show loading spinner when cargando', async () => {
      wrapper.vm.cargando = true
      await wrapper.vm.$nextTick()

      const spinner = wrapper.find('.spinner-volleyball')
      expect(spinner.exists()).toBe(true)
    })

    it('should show loading text when cargando', async () => {
      wrapper.vm.cargando = true
      await wrapper.vm.$nextTick()

      const button = wrapper.find('.submit-button-volleyball')
      expect(button.text()).toContain('Enviando...')
    })

    it('should show send icon when not cargando', () => {
      wrapper.vm.cargando = false
      const button = wrapper.find('.submit-button-volleyball')
      expect(button.text()).toContain('Enviar enlace de recuperación')
    })

    it('should apply sending class when cargando', async () => {
      wrapper.vm.cargando = true
      await wrapper.vm.$nextTick()

      const button = wrapper.find('.submit-button-volleyball')
      expect(button.classes()).toContain('sending')
    })
  })
})

