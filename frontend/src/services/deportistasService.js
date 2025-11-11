/**
 * Servicio para gestión de deportistas
 * Maneja las llamadas a la API de deportistas
 */
import { useAuthStore } from '@/stores/auth'
import { getApiBaseUrl } from '@/config/environment'

const getBaseUrl = () => getApiBaseUrl()

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
      const baseURL = getBaseUrl()
      const response = await fetch(`${baseURL}/deportistas?page=${page}&per_page=${perPage}`, {
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
      const baseURL = getBaseUrl()
      const response = await fetch(`${baseURL}/deportistas/${idDeportista}`, {
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
   * @param {Object} datos - Datos a actualizar en formato { datos_deportista: {}, datos_informacion_deportiva: {} }
   * @returns {Promise<Object>} Respuesta de la actualización
   */
  async actualizarDeportista(idDeportista, datos) {
    try {
      // Si los datos ya vienen en el formato correcto (con datos_deportista y datos_informacion_deportiva)
      // los usamos directamente, si no, los enviamos tal cual (compatibilidad con método antiguo)
      const datosEnvio = datos.datos_deportista || datos.datos_informacion_deportiva
        ? datos
        : {
            datos_deportista: datos.datos_deportista || {},
            datos_informacion_deportiva: datos.datos_informacion_deportiva || {}
          }

      const baseURL = getBaseUrl()
      const response = await fetch(`${baseURL}/deportistas/${idDeportista}`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(datosEnvio)
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || `Error ${response.status}: ${response.statusText}`)
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
      const baseURL = getBaseUrl()
      const response = await fetch(`${baseURL}/deportistas`, {
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
      const baseURL = getBaseUrl()
      const response = await fetch(`${baseURL}/deportistas/${idDeportista}`, {
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

