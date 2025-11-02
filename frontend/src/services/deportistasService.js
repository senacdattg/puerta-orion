/**
 * Servicio para gestión de deportistas
 * Maneja las llamadas a la API de deportistas
 */

import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

class DeportistasService {
  constructor() {
    // No inicializar el store aquí para evitar problemas de orden
  }

  /**
   * Obtiene el token de autenticación
   */
  getAuthHeaders() {
    const authStore = useAuthStore()
    const token = authStore.token
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    }
  }

  /**
   * Lista todos los deportistas con paginación
   * @param {number} page - Número de página
   * @param {number} perPage - Elementos por página
   * @returns {Promise<Object>} Respuesta con lista de deportistas
   */
  async listarDeportistas(page = 1, perPage = 100) {
    try {
      const response = await fetch(`${API_BASE_URL}/deportistas?page=${page}&per_page=${perPage}`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error al listar deportistas:', error)
      throw error
    }
  }

  /**
   * Obtiene un deportista por su ID
   * @param {number} idDeportista - ID del deportista
   * @returns {Promise<Object>} Información completa del deportista
   */
  async obtenerDeportistaPorId(idDeportista) {
    try {
      const response = await fetch(`${API_BASE_URL}/deportistas/${idDeportista}`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('Respuesta del backend:', data)
      // Normalizar la respuesta para que tenga 'success' además de 'status'
      if (data.status === 'success') {
        data.success = true
      }
      return data
    } catch (error) {
      console.error('Error al obtener deportista:', error)
      throw error
    }
  }

  /**
   * Actualiza un deportista existente
   * @param {number} idDeportista - ID del deportista
   * @param {Object} datos - Datos a actualizar
   * @returns {Promise<Object>} Respuesta de la actualización
   */
  async actualizarDeportista(idDeportista, datos) {
    try {
      const response = await fetch(`${API_BASE_URL}/deportistas/${idDeportista}`, {
        method: 'PATCH',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(datos)
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error al actualizar deportista:', error)
      throw error
    }
  }

  /**
   * Crea un nuevo deportista
   * @param {Object} datos - Datos del deportista
   * @returns {Promise<Object>} Respuesta de la creación
   */
  async crearDeportista(datos) {
    try {
      const response = await fetch(`${API_BASE_URL}/deportistas`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(datos)
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error al crear deportista:', error)
      throw error
    }
  }

  /**
   * Elimina un deportista (si está implementado en el backend)
   * @param {number} idDeportista - ID del deportista
   * @returns {Promise<Object>} Respuesta de la eliminación
   */
  async eliminarDeportista(idDeportista) {
    try {
      const response = await fetch(`${API_BASE_URL}/deportistas/${idDeportista}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error al eliminar deportista:', error)
      throw error
    }
  }
}

// Exportar instancia única del servicio
export default new DeportistasService()

