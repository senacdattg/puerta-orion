/**
 * Servicio de autenticación para el frontend
 * Maneja todas las operaciones relacionadas con autenticación
 */

import { API_CONFIG } from '@/config/environment'

class AuthService {
  constructor() {
    this.baseURL = API_CONFIG.baseURL
  }

  /**
   * Iniciar sesión
   */
  async login(credentials) {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error de autenticación')
      }

      return { success: true, ...data.data }
    } catch (error) {
      console.error('Error en login:', error)
      return { success: false, error: error.message || 'Error de conexión' }
    }
  }

  /**
   * Registrar nuevo usuario
   */
  async register(userData) {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error de registro')
      }

      return { success: true, data: data.data }
    } catch (error) {
      console.error('Error en registro:', error)
      return { success: false, error: error.message || 'Error de conexión' }
    }
  }

  /**
   * Cerrar sesión
   */
  async logout(token) {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error al cerrar sesión')
      }

      return data
    } catch (error) {
      console.error('Error en logout:', error)
      throw error
    }
  }

  /**
   * Obtener perfil del usuario autenticado
   */
  async getProfile() {
    try {
      const token = localStorage.getItem('token')

      if (!token) {
        throw new Error('No hay token de autenticación')
      }

      const response = await fetch(`${this.baseURL}/api/auth/perfil`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error al obtener perfil')
      }

      return data
    } catch (error) {
      console.error('Error al obtener perfil:', error)
      throw error
    }
  }

  /**
   * Verificar si un token es válido
   */
  async verifyToken(token) {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/verify-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Token inválido')
      }

      return data
    } catch (error) {
      console.error('Error al verificar token:', error)
      throw error
    }
  }

  /**
   * Obtener token del localStorage
   */
  getToken() {
    return localStorage.getItem('token')
  }

  /**
   * Verificar si hay un token guardado
   */
  hasToken() {
    return !!this.getToken()
  }

  /**
   * Limpiar datos de autenticación del localStorage
   */
  clearAuthData() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}

// Exportar instancia única
export default new AuthService()
