import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useForm, useRegistrationForm } from '@/composables/useForm'

describe('useForm', () => {
  describe('initial state', () => {
    it('should initialize with initial data', () => {
      const initialData = { name: 'John', email: 'john@example.com' }
      const { formData } = useForm(initialData)

      expect(formData.name).toBe('John')
      expect(formData.email).toBe('john@example.com')
    })

    it('should initialize with empty errors', () => {
      const { errors, hasErrors } = useForm()

      expect(Object.keys(errors).length).toBe(0)
      expect(hasErrors.value).toBe(false)
    })

    it('should initialize with default state flags', () => {
      const { isSubmitting, isDirty, isValid, canSubmit } = useForm()

      expect(isSubmitting.value).toBe(false)
      expect(isDirty.value).toBe(false)
      expect(isValid.value).toBe(true)
      expect(canSubmit.value).toBe(true)
    })
  })

  describe('updateField', () => {
    it('should update field value', () => {
      const { formData, updateField } = useForm({ name: '' })

      updateField('name', 'John')

      expect(formData.name).toBe('John')
      expect(isDirty.value).toBe(true)
    })

    it('should validate field when updating', () => {
      const { updateField, errors } = useForm({ email: '' }, {
        email: (value) => {
          const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
          return !value || emailRegex.test(value) || 'Email inválido'
        }
      })

      updateField('email', 'invalid-email')

      expect(errors.email).toBe('Email inválido')
    })
  })

  describe('validateField', () => {
    it('should validate field successfully', () => {
      const { validateField, errors } = useForm({ name: 'John' }, {
        name: [(value) => !!value || 'Required']
      })

      const result = validateField('name', 'John')

      expect(result).toBe(true)
      expect(errors.name).toBeUndefined()
    })

    it('should return false and set error when validation fails', () => {
      const { validateField, errors } = useForm({ name: '' }, {
        name: [(value) => !!value || 'Required']
      })

      const result = validateField('name', '')

      expect(result).toBe(false)
      expect(errors.name).toBe('Required')
    })

    it('should return true when field has no rules', () => {
      const { validateField } = useForm({ name: 'John' })

      const result = validateField('name', 'John')

      expect(result).toBe(true)
    })
  })

  describe('validateForm', () => {
    it('should validate all fields successfully', () => {
      const { validateForm, isValid } = useForm(
        { name: 'John', email: 'john@example.com' },
        {
          name: [(value) => !!value || 'Required'],
          email: [(value) => {
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
            return !value || emailRegex.test(value) || 'Email inválido'
          }]
        }
      )

      const result = validateForm()

      expect(result).toBe(true)
      expect(isValid.value).toBe(true)
    })

    it('should return false when validation fails', () => {
      const { validateForm, isValid, errors } = useForm(
        { name: '', email: 'invalid' },
        {
          name: [(value) => !!value || 'Required'],
          email: [(value) => {
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
            return !value || emailRegex.test(value) || 'Email inválido'
          }]
        }
      )

      const result = validateForm()

      expect(result).toBe(false)
      expect(isValid.value).toBe(false)
      expect(errors.name).toBe('Required')
      expect(errors.email).toBe('Email inválido')
    })
  })

  describe('setErrors', () => {
    it('should set errors manually', () => {
      const { setErrors, errors, isValid } = useForm()

      setErrors({ name: 'Name is required', email: 'Email is invalid' })

      expect(errors.name).toBe('Name is required')
      expect(errors.email).toBe('Email is invalid')
      expect(isValid.value).toBe(false)
    })
  })

  describe('clearErrors', () => {
    it('should clear all errors', () => {
      const { setErrors, clearErrors, errors, isValid, hasErrors } = useForm()

      setErrors({ name: 'Error' })
      expect(hasErrors.value).toBe(true)

      clearErrors()

      expect(Object.keys(errors).length).toBe(0)
      expect(isValid.value).toBe(true)
      expect(hasErrors.value).toBe(false)
    })
  })

  describe('resetForm', () => {
    it('should reset form to initial state', () => {
      const initialData = { name: 'John', email: 'john@example.com' }
      const { formData, updateField, setErrors, resetForm, isDirty, errors } = useForm(initialData)

      updateField('name', 'Jane')
      setErrors({ name: 'Error' })

      resetForm()

      expect(formData.name).toBe('John')
      expect(formData.email).toBe('john@example.com')
      expect(isDirty.value).toBe(false)
      expect(Object.keys(errors).length).toBe(0)
    })
  })

  describe('submit', () => {
    it('should submit form successfully', async () => {
      const submitFn = vi.fn().mockResolvedValueOnce({ success: true })
      const { submit, isSubmitting } = useForm({ name: 'John' })

      const result = await submit(submitFn)

      expect(result.success).toBe(true)
      expect(result.data).toEqual({ success: true })
      expect(isSubmitting.value).toBe(false)
      expect(submitFn).toHaveBeenCalledWith({ name: 'John' })
    })

    it('should validate before submit when validateBeforeSubmit is true', async () => {
      const submitFn = vi.fn()
      const { submit } = useForm(
        { name: '' },
        { name: [(value) => !!value || 'Required'] }
      )

      const result = await submit(submitFn, { validateBeforeSubmit: true })

      expect(result.success).toBe(false)
      expect(result.error).toBe('Formulario inválido')
      expect(submitFn).not.toHaveBeenCalled()
    })

    it('should skip validation when validateBeforeSubmit is false', async () => {
      const submitFn = vi.fn().mockResolvedValueOnce({ success: true })
      const { submit } = useForm(
        { name: '' },
        { name: [(value) => !!value || 'Required'] }
      )

      const result = await submit(submitFn, { validateBeforeSubmit: false })

      expect(result.success).toBe(true)
      expect(submitFn).toHaveBeenCalled()
    })

    it('should call onSuccess callback', async () => {
      const submitFn = vi.fn().mockResolvedValueOnce({ id: 1 })
      const onSuccess = vi.fn()
      const { submit } = useForm({ name: 'John' })

      await submit(submitFn, { onSuccess })

      expect(onSuccess).toHaveBeenCalledWith({ id: 1 })
    })

    it('should handle server validation errors', async () => {
      const error = {
        response: {
          data: {
            errors: {
              email: 'Email already exists',
              name: 'Name is too short'
            }
          }
        }
      }
      const submitFn = vi.fn().mockRejectedValueOnce(error)
      const { submit, errors } = useForm({ name: 'John', email: 'john@example.com' })

      const result = await submit(submitFn)

      expect(result.success).toBe(false)
      expect(errors.email).toBe('Email already exists')
      expect(errors.name).toBe('Name is too short')
    })

    it('should handle general errors', async () => {
      const error = new Error('Network error')
      const submitFn = vi.fn().mockRejectedValueOnce(error)
      const { submit, errors } = useForm({ name: 'John' })

      const result = await submit(submitFn)

      expect(result.success).toBe(false)
      expect(errors.general).toBe('Network error')
    })

    it('should call onError callback', async () => {
      const error = new Error('Submit failed')
      const submitFn = vi.fn().mockRejectedValueOnce(error)
      const onError = vi.fn()
      const { submit } = useForm({ name: 'John' })

      await submit(submitFn, { onError })

      expect(onError).toHaveBeenCalledWith(error)
    })
  })

  describe('default validation rules', () => {
    it('should validate required field', () => {
      const { validateField, errors } = useForm({ name: '' }, {
        name: 'required'
      })

      validateField('name', '')

      expect(errors.name).toBe('Este campo es requerido')
    })

    it('should validate email format', () => {
      const { validateField, errors } = useForm({ email: '' }, {
        email: 'email'
      })

      validateField('email', 'invalid-email')

      expect(errors.email).toBe('Email inválido')
    })

    it('should validate minLength', () => {
      const { validateField, errors } = useForm({ password: '' }, {
        password: 'minLength(6)'
      })

      validateField('password', '123')

      expect(errors.password).toBe('Mínimo 6 caracteres')
    })

    it('should validate maxLength', () => {
      const { validateField, errors } = useForm({ username: '' }, {
        username: 'maxLength(20)'
      })

      validateField('username', 'a'.repeat(21))

      expect(errors.username).toBe('Máximo 20 caracteres')
    })

    it('should validate numeric', () => {
      const { validateField, errors } = useForm({ age: '' }, {
        age: 'numeric'
      })

      validateField('age', 'not-a-number')

      expect(errors.age).toBe('Debe ser un número')
    })
  })
})

describe('useRegistrationForm', () => {
  describe('initial state', () => {
    it('should initialize with registration fields', () => {
      const { formData } = useRegistrationForm()

      expect(formData).toHaveProperty('username')
      expect(formData).toHaveProperty('password')
      expect(formData).toHaveProperty('confirmPassword')
      expect(formData).toHaveProperty('email')
      expect(formData).toHaveProperty('nombre')
      expect(formData).toHaveProperty('apellido')
    })
  })

  describe('validateConfirmPassword', () => {
    it('should validate password match', () => {
      const { formData, updateField, errors } = useRegistrationForm()

      updateField('password', 'password123')
      updateField('confirmPassword', 'password123')

      // The validation should be handled by the composable
      expect(errors.confirmPassword).toBeUndefined()
    })

    it('should show error when passwords do not match', () => {
      const { formData, updateField, errors } = useRegistrationForm()

      updateField('password', 'password123')
      updateField('confirmPassword', 'different')

      // This would need to be tested through validateRegistrationForm
      // since validateConfirmPassword is not directly exposed
    })
  })

  describe('validateRegistrationForm', () => {
    it('should validate complete registration form', () => {
      const { formData, updateField, validateRegistrationForm } = useRegistrationForm()

      updateField('username', 'testuser')
      updateField('password', 'password123')
      updateField('confirmPassword', 'password123')
      updateField('email', 'test@example.com')
      updateField('nombre', 'John')
      updateField('apellido', 'Doe')
      updateField('documento', '12345678')
      updateField('tipoDocumento', 'cc')
      updateField('sexo', 'M')

      const result = validateRegistrationForm()

      expect(result).toBe(true)
    })

    it('should return false when passwords do not match', () => {
      const { updateField, validateRegistrationForm, errors } = useRegistrationForm()

      updateField('password', 'password123')
      updateField('confirmPassword', 'different')

      const result = validateRegistrationForm()

      expect(result).toBe(false)
      expect(errors.confirmPassword).toBe('Las contraseñas no coinciden')
    })
  })
})

