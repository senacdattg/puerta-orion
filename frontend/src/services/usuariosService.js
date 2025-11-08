/**
 * Servicio para gestión de usuarios
 * Maneja las llamadas a la API de usuarios
 */
import { useAuthStore } from '@/stores/auth'
import { getApiBaseUrl } from '@/config/environment'

const API_BASE_URL = getApiBaseUrl()

class UsuariosService {
  constructor() {
    // No inicializar el store aquí para evitar problemas de orden
  }

  /**
   * Obtiene el token de autenticación
   */
  getAuthHeaders() {
    // Obtener el store dinámicamente cuando se necesite
    const authStore = useAuthStore()
    const token = authStore.token
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    }
  }

  /**
   * Lista todos los usuarios con sus roles
   */
  async listarUsuarios() {
    try {
      const response = await fetch(`${API_BASE_URL}/usuarios/`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error al listar usuarios:', error)
      throw error
    }
  }

  /**
   * Obtiene todos los roles disponibles
   */
  async listarRoles() {
    try {
      const response = await fetch(`${API_BASE_URL}/dynamic-data/roles`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error al listar roles:', error)
      throw error
    }
  }

  /**
   * Cambia los roles de un usuario (acepta múltiples roles)
   */
  async cambiarRolUsuario(idUsuario, idRoles) {
    try {
      // Normalizar: si viene un solo número, convertirlo a array
      const rolesArray = Array.isArray(idRoles) ? idRoles : [idRoles]
      
      const response = await fetch(`${API_BASE_URL}/usuarios/${idUsuario}/rol`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ id_roles: rolesArray })
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error al cambiar roles de usuario:', error)
      throw error
    }
  }
}

// Exportar instancia única del servicio
export default new UsuariosService()

