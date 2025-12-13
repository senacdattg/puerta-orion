/**
 * Servicio para gestión de usuarios
 * Maneja las llamadas a la API de usuarios
 */
import { useAuthStore } from '@/stores/auth'
import { getApiBaseUrl } from '@/config/environment'

const buildUrl = (path = '') => `${getApiBaseUrl()}${path}`

class UsuariosService {
  // NOSONAR: S6647 - Constructor removed as it was empty and unnecessary

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
   * @param {string} estado - 'activo', 'inactivo' o 'todos' (default: 'todos')
   * @param {number} limit - Número de usuarios a retornar (default: 3)
   * @param {number} offset - Número de usuarios a saltar (default: 0)
   */
  async listarUsuarios(estado = 'todos', limit = 3, offset = 0) {
    try {
      const params = new URLSearchParams()
      if (estado !== 'todos') {
        params.append('estado', estado)
      }
      params.append('limit', limit)
      params.append('offset', offset)

      const url = buildUrl(`/usuarios?${params.toString()}`)

      const response = await fetch(url, {
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
      const response = await fetch(buildUrl('/dynamic-data/roles'), {
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

      const response = await fetch(buildUrl(`/usuarios/${idUsuario}/rol`), {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ id_roles: rolesArray })
      })

      const data = await response.json()

      if (!response.ok) {
        // Si hay un mensaje de error en la respuesta, usarlo
        const errorMessage = data.error || data.message || `Error ${response.status}: ${response.statusText}`
        throw new Error(errorMessage)
      }

      return data
    } catch (error) {
      console.error('Error al cambiar roles de usuario:', error)
      throw error
    }
  }

  /**
   * Cambia el estado (activo/inactivo) de un usuario
   */
  async cambiarEstadoUsuario(idUsuario, estado) {
    try {
      const response = await fetch(buildUrl(`/usuarios/${idUsuario}/estado`), {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ estado: estado })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(`Error ${response.status}: ${errorData.error || response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error al cambiar estado de usuario:', error)
      throw error
    }
  }

  /**
   * Obtiene el detalle completo de un usuario
   */
  async obtenerDetalleUsuario(idUsuario) {
    try {
      const response = await fetch(buildUrl(`/usuarios/${idUsuario}/detalle`), {
        method: 'GET',
        headers: this.getAuthHeaders()
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(`Error ${response.status}: ${errorData.error || response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error al obtener detalle de usuario:', error)
      throw error
    }
  }

  /**
   * Actualiza datos del usuario/persona
   * body: { datos_usuario?: { usuario }, datos_persona?: { primer_nombre, ... } }
   */
  async actualizarUsuario(idUsuario, body) {
    try {
      const response = await fetch(buildUrl(`/usuarios/${idUsuario}`), {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(body)
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(`Error ${response.status}: ${errorData.error || response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error al actualizar usuario:', error)
      throw error
    }
  }
}

// Exportar instancia única del servicio
export default new UsuariosService()

