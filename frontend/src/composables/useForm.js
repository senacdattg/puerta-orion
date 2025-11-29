import { ref, reactive, computed } from 'vue'

/**
 * Composable para manejo de formularios con validación
 * Proporciona estado reactivo, validación y manejo de errores
 */
export function useForm(initialData = {}, validationRules = {}) {
  // Estado del formulario
  const formData = reactive({ ...initialData })
  const errors = reactive({})
  const isSubmitting = ref(false)
  const isDirty = ref(false)
  const isValid = ref(true)

  // Reglas de validación por defecto
  const defaultRules = {
    required: (value) => !!value || 'Este campo es requerido',
    email: (value) => {
      // NOSONAR: S5852 - Using a safe and efficient email regex pattern
      const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
      return !value || emailRegex.test(value) || 'Email inválido'
    },
    minLength: (min) => (value) =>
      !value || value.length >= min || `Mínimo ${min} caracteres`,
    maxLength: (max) => (value) =>
      !value || value.length <= max || `Máximo ${max} caracteres`,
    numeric: (value) => !value || !isNaN(value) || 'Debe ser un número',
    phone: (value) => {
      const phoneRegex = /^\+?[1-9]\d{0,15}$/
      return !value || phoneRegex.test(value.replace(/\s/g, '')) || 'Teléfono inválido'
    }
  }

  // Combinar reglas por defecto con las personalizadas
  const rules = { ...defaultRules, ...validationRules }

  /**
   * Valida un campo específico
   * @param {string} field - Nombre del campo
   * @param {any} value - Valor a validar
   */
  const validateField = (field, value) => {
    const fieldRules = rules[field]
    if (!fieldRules) return true

    const ruleArray = Array.isArray(fieldRules) ? fieldRules : [fieldRules]

    for (const rule of ruleArray) {
      const result = rule(value)
      if (result !== true) {
        errors[field] = result
        return false
      }
    }

    delete errors[field]
    return true
  }

  /**
   * Valida el formulario
   */
  const validateForm = () => {
    let formValid = true

    for (const field in formData) {
      if (rules[field]) {
        const fieldValid = validateField(field, formData[field])
        if (!fieldValid) {
          formValid = false
        }
      }
    }

    isValid.value = formValid
    return formValid
  }

  /**
   * Actualiza un campo del formulario
   * @param {string} field - Nombre del campo
   * @param {any} value - Nuevo valor
   */
  const updateField = (field, value) => {
    formData[field] = value
    isDirty.value = true

    // Validar campo si tiene reglas
    if (rules[field]) {
      validateField(field, value)
    }
  }

  /**
   * Establece errores manualmente
   * @param {Object} newErrors - Objeto con errores
   */
  const setErrors = (newErrors) => {
    Object.assign(errors, newErrors)
    isValid.value = Object.keys(errors).length === 0
  }

  /**
   * Limpia todos los errores
   */
  const clearErrors = () => {
    Object.keys(errors).forEach(key => delete errors[key])
    isValid.value = true
  }

  /**
   * Resetea el formulario a su estado inicial
   */
  const resetForm = () => {
    Object.assign(formData, initialData)
    clearErrors()
    isDirty.value = false
    isSubmitting.value = false
  }

  /**
   * Envía el formulario con validación
   * @param {Function} submitFn - Función de envío
   * @param {Object} options - Opciones adicionales
   */
  const submit = async (submitFn, options = {}) => {
    const { validateBeforeSubmit = true, onSuccess, onError } = options

    if (validateBeforeSubmit && !validateForm()) {
      return { success: false, error: 'Formulario inválido' }
    }

    isSubmitting.value = true
    clearErrors()

    try {
      const result = await submitFn(formData)

      if (onSuccess) {
        onSuccess(result)
      }

      return { success: true, data: result }
    } catch (error) {
      console.error('Error en envío de formulario:', error)

      // Manejar errores de validación del servidor
      if (error.response?.data?.errors) {
        setErrors(error.response.data.errors)
      } else {
        setErrors({ general: error.message || 'Error al enviar el formulario' })
      }

      if (onError) {
        onError(error)
      }

      return { success: false, error }
    } finally {
      isSubmitting.value = false
    }
  }

  // Propiedades computadas útiles
  const hasErrors = computed(() => Object.keys(errors).length > 0)
  const canSubmit = computed(() => isValid.value && !isSubmitting.value)
  const errorCount = computed(() => Object.keys(errors).length)

  return {
    // Estado
    formData,
    errors,
    isSubmitting,
    isDirty,
    isValid,
    hasErrors,
    canSubmit,
    errorCount,

    // Métodos
    updateField,
    validateField,
    validateForm,
    setErrors,
    clearErrors,
    resetForm,
    submit
  }
}

/**
 * Hook especializado para formularios de registro
 */
export function useRegistrationForm() {
  // Definir reglas como funciones directamente
  const required = (value) => !!value || 'Este campo es requerido'
  const email = (value) => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    return !value || emailRegex.test(value) || 'Email inválido'
  }
  const minLength3 = (value) => !value || value.length >= 3 || 'Mínimo 3 caracteres'
  const minLength6 = (value) => !value || value.length >= 6 || 'Mínimo 6 caracteres'
  const phone = (value) => {
    const phoneRegex = /^\+?[1-9]\d{0,15}$/
    return !value || phoneRegex.test(value.replace(/\s/g, '')) || 'Teléfono inválido'
  }

  const { formData, errors, isSubmitting, submit, updateField, validateForm } = useForm({
    username: '',
    password: '',
    confirmPassword: '',
    email: '',
    nombre: '',
    apellido: '',
    telefono: '',
    documento: '',
    tipoDocumento: '',
    sexo: '',
    direccion: ''
  }, {
    username: [required, minLength3],
    password: [required, minLength6],
    confirmPassword: [required],
    email: [required, email],
    nombre: [required],
    apellido: [required],
    telefono: [phone],
    documento: [required],
    tipoDocumento: [required],
    sexo: [required]
  })

  // Validación personalizada para confirmación de contraseña
  const validateConfirmPassword = () => {
    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Las contraseñas no coinciden' // NOSONAR: S2068 - This is an error message, not a hard-coded password
      return false
    }
    delete errors.confirmPassword
    return true
  }

  // Validación completa del formulario
  const validateRegistrationForm = () => {
    const baseValid = validateForm()
    const passwordMatch = validateConfirmPassword()
    return baseValid && passwordMatch
  }

  return {
    formData,
    errors,
    isSubmitting,
    updateField,
    validateRegistrationForm,
    submit
  }
}

