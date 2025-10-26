import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { usuariosService } from '@/services/usuariosService'

/**
 * Store para manejar datos de usuarios
 * Incluye gestión de deportistas, acudientes, etc.
 */
export const useUserStore = defineStore('user', () => {
  // Estado
  const users = ref([])
  const deportistas = ref([])
  const acudientes = ref([])
  const entrenadores = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  // Computed
  const totalUsers = computed(() => users.value.length)
  const totalDeportistas = computed(() => deportistas.value.length)
  const totalAcudientes = computed(() => acudientes.value.length)
  const totalEntrenadores = computed(() => entrenadores.value.length)

  // Métodos para usuarios
  const fetchUsers = async () => {
    try {
      isLoading.value = true
      error.value = null

      const response = await usuariosService.obtenerUsuarios()
      users.value = response.data || []

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.message || 'Error al cargar usuarios'
      return { success: false, error: err }
    } finally {
      isLoading.value = false
    }
  }

  const fetchDeportistas = async () => {
    try {
      isLoading.value = true
      error.value = null

      const response = await usuariosService.obtenerDeportistas()
      deportistas.value = response.data || []

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.message || 'Error al cargar deportistas'
      return { success: false, error: err }
    } finally {
      isLoading.value = false
    }
  }

  const fetchAcudientes = async () => {
    try {
      isLoading.value = true
      error.value = null

      const response = await usuariosService.obtenerAcudientes()
      acudientes.value = response.data || []

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.message || 'Error al cargar acudientes'
      return { success: false, error: err }
    } finally {
      isLoading.value = false
    }
  }

  const fetchEntrenadores = async () => {
    try {
      isLoading.value = true
      error.value = null

      const response = await usuariosService.obtenerEntrenadores()
      entrenadores.value = response.data || []

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.message || 'Error al cargar entrenadores'
      return { success: false, error: err }
    } finally {
      isLoading.value = false
    }
  }

  // Métodos para crear usuarios
  const createDeportista = async (deportistaData) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await usuariosService.crearDeportista(deportistaData)

      // Actualizar lista local
      deportistas.value.push(response.data)

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.message || 'Error al crear deportista'
      return { success: false, error: err }
    } finally {
      isLoading.value = false
    }
  }

  const createAcudiente = async (acudienteData) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await usuariosService.crearAcudiente(acudienteData)

      // Actualizar lista local
      acudientes.value.push(response.data)

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.message || 'Error al crear acudiente'
      return { success: false, error: err }
    } finally {
      isLoading.value = false
    }
  }

  const createEntrenador = async (entrenadorData) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await usuariosService.crearEntrenador(entrenadorData)

      // Actualizar lista local
      entrenadores.value.push(response.data)

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.message || 'Error al crear entrenador'
      return { success: false, error: err }
    } finally {
      isLoading.value = false
    }
  }

  // Métodos para actualizar usuarios
  const updateUser = async (userId, userData) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await usuariosService.actualizarUsuario(userId, userData)

      // Actualizar en la lista local
      const index = users.value.findIndex(u => u.id === userId)
      if (index > -1) {
        users.value[index] = response.data
      }

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.message || 'Error al actualizar usuario'
      return { success: false, error: err }
    } finally {
      isLoading.value = false
    }
  }

  // Métodos para eliminar usuarios
  const deleteUser = async (userId) => {
    try {
      isLoading.value = true
      error.value = null

      await usuariosService.eliminarUsuario(userId)

      // Remover de la lista local
      users.value = users.value.filter(u => u.id !== userId)
      deportistas.value = deportistas.value.filter(d => d.id !== userId)
      acudientes.value = acudientes.value.filter(a => a.id !== userId)
      entrenadores.value = entrenadores.value.filter(e => e.id !== userId)

      return { success: true }
    } catch (err) {
      error.value = err.message || 'Error al eliminar usuario'
      return { success: false, error: err }
    } finally {
      isLoading.value = false
    }
  }

  // Métodos de búsqueda
  const searchUsers = (query) => {
    if (!query) return users.value

    const lowercaseQuery = query.toLowerCase()
    return users.value.filter(user =>
      user.persona?.nombre_completo?.toLowerCase().includes(lowercaseQuery) ||
      user.persona?.correo_electronico?.toLowerCase().includes(lowercaseQuery) ||
      user.persona?.documento?.includes(query)
    )
  }

  const searchDeportistas = (query) => {
    if (!query) return deportistas.value

    const lowercaseQuery = query.toLowerCase()
    return deportistas.value.filter(deportista =>
      deportista.persona?.nombre_completo?.toLowerCase().includes(lowercaseQuery) ||
      deportista.persona?.correo_electronico?.toLowerCase().includes(lowercaseQuery) ||
      deportista.persona?.documento?.includes(query)
    )
  }

  // Métodos de utilidad
  const getUserById = (userId) => {
    return users.value.find(u => u.id === userId)
  }

  const getDeportistaById = (deportistaId) => {
    return deportistas.value.find(d => d.id === deportistaId)
  }

  const getAcudienteById = (acudienteId) => {
    return acudientes.value.find(a => a.id === acudienteId)
  }

  const clearError = () => {
    error.value = null
  }

  const reset = () => {
    users.value = []
    deportistas.value = []
    acudientes.value = []
    entrenadores.value = []
    isLoading.value = false
    error.value = null
  }

  return {
    // Estado
    users,
    deportistas,
    acudientes,
    entrenadores,
    isLoading,
    error,

    // Computed
    totalUsers,
    totalDeportistas,
    totalAcudientes,
    totalEntrenadores,

    // Métodos de fetch
    fetchUsers,
    fetchDeportistas,
    fetchAcudientes,
    fetchEntrenadores,

    // Métodos de creación
    createDeportista,
    createAcudiente,
    createEntrenador,

    // Métodos de actualización
    updateUser,

    // Métodos de eliminación
    deleteUser,

    // Métodos de búsqueda
    searchUsers,
    searchDeportistas,

    // Utilidades
    getUserById,
    getDeportistaById,
    getAcudienteById,
    clearError,
    reset
  }
})

