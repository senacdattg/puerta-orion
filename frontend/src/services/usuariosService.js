/**
 * Servicio para gestión de usuarios
 * Maneja las llamadas a la API de usuarios
 */

import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

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
      const response = await fetch(`${API_BASE_URL}/usuarios`, {
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
   * Cambia el rol de un usuario
   */
  async cambiarRolUsuario(idUsuario, idRol) {
    try {
      const response = await fetch(`${API_BASE_URL}/usuarios/${idUsuario}/rol`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ id_rol: idRol })
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error al cambiar rol de usuario:', error)
      throw error
    }
  }
}

// Exportar instancia única del servicio
export default new UsuariosService()

