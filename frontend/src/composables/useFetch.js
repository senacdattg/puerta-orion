import { ref, computed } from 'vue'

/**
 * Composable para manejar peticiones HTTP con estado de carga y error
 * Proporciona una interfaz reactiva para operaciones de API
 */
export function useFetch() {
  const data = ref(null)
  const error = ref(null)
  const isLoading = ref(false)
  const isSuccess = ref(false)

  // Estado computado
  const hasError = computed(() => !!error.value)
  const hasData = computed(() => !!data.value)

  /**
   * Ejecuta una petición HTTP
   * @param {Function} requestFn - Función que retorna una Promise
   * @param {Object} options - Opciones adicionales
   */
  const execute = async (requestFn, options = {}) => {
    const {
      resetData = true,
      showLoading = true,
      onSuccess,
      onError
    } = options

    try {
      // Reset estado
      error.value = null
      isSuccess.value = false

      if (resetData) {
        data.value = null
      }

      if (showLoading) {
        isLoading.value = true
      }

      // Ejecutar petición
      const result = await requestFn()

      data.value = result
      isSuccess.value = true

      if (onSuccess) {
        onSuccess(result)
      }

      return { success: true, data: result }
    } catch (err) {
      error.value = err.message || 'Error desconocido'
      isSuccess.value = false

      if (onError) {
        onError(err)
      }

      return { success: false, error: err }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Ejecuta una petición GET
   * @param {Function} getFn - Función que retorna una Promise
   * @param {Object} options - Opciones adicionales
   */
  const get = async (getFn, options = {}) => {
    return execute(getFn, options)
  }

  /**
   * Ejecuta una petición POST
   * @param {Function} postFn - Función que retorna una Promise
   * @param {Object} options - Opciones adicionales
   */
  const post = async (postFn, options = {}) => {
    return execute(postFn, options)
  }

  /**
   * Ejecuta una petición PUT
   * @param {Function} putFn - Función que retorna una Promise
   * @param {Object} options - Opciones adicionales
   */
  const put = async (putFn, options = {}) => {
    return execute(putFn, options)
  }

  /**
   * Ejecuta una petición DELETE
   * @param {Function} deleteFn - Función que retorna una Promise
   * @param {Object} options - Opciones adicionales
   */
  const remove = async (deleteFn, options = {}) => {
    return execute(deleteFn, options)
  }

  /**
   * Resetea el estado del composable
   */
  const reset = () => {
    data.value = null
    error.value = null
    isLoading.value = false
    isSuccess.value = false
  }

  /**
   * Establece un error manualmente
   * @param {string} message - Mensaje de error
   */
  const setError = (message) => {
    error.value = message
    isSuccess.value = false
  }

  /**
   * Establece datos manualmente
   * @param {any} newData - Nuevos datos
   */
  const setData = (newData) => {
    data.value = newData
    error.value = null
    isSuccess.value = true
  }

  return {
    // Estado
    data,
    error,
    isLoading,
    isSuccess,
    hasError,
    hasData,

    // Métodos
    execute,
    get,
    post,
    put,
    remove,
    reset,
    setError,
    setData
  }
}

/**
 * Hook especializado para peticiones de datos con paginación
 */
export function usePaginatedFetch() {
  const { data, error, isLoading, execute, reset } = useFetch()

  const currentPage = ref(1)
  const totalPages = ref(1)
  const totalItems = ref(0)
  const itemsPerPage = ref(10)

  const paginatedData = computed(() => {
    if (!data.value) return []
    return Array.isArray(data.value) ? data.value : data.value.items || []
  })

  const hasNextPage = computed(() => currentPage.value < totalPages.value)
  const hasPrevPage = computed(() => currentPage.value > 1)

  const fetchPage = async (page, fetchFn) => {
    currentPage.value = page
    return execute(() => fetchFn(page, itemsPerPage.value))
  }

  const nextPage = async (fetchFn) => {
    if (hasNextPage.value) {
      return fetchPage(currentPage.value + 1, fetchFn)
    }
  }

  const prevPage = async (fetchFn) => {
    if (hasPrevPage.value) {
      return fetchPage(currentPage.value - 1, fetchFn)
    }
  }

  const resetPagination = () => {
    reset()
    currentPage.value = 1
    totalPages.value = 1
    totalItems.value = 0
  }

  return {
    ...useFetch(),
    paginatedData,
    currentPage,
    totalPages,
    totalItems,
    itemsPerPage,
    hasNextPage,
    hasPrevPage,
    fetchPage,
    nextPage,
    prevPage,
    resetPagination
  }
}

