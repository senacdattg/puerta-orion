/**
 * Servicio dedicado a las operaciones sobre personas.
 * Actualmente se usa para actualizar datos básicos del deportista.
 */

import { useAuthStore } from '@/stores/auth'
import { getApiBaseUrl } from '@/config/environment'

const buildUrl = (path = '') => `${getApiBaseUrl()}${path}`

class PersonasService {
  /**
   * Construye encabezados autenticados para las peticiones.
   * @returns {Record<string, string>}
   */
  getAuthHeaders() {
    const authStore = useAuthStore()
    const token = authStore.token

    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  }

  /**
   * Actualiza parcialmente una persona.
   * @param {number} idPersona
   * @param {Record<string, unknown>} datos
   */
  async actualizarPersona(idPersona, datos) {
    if (!idPersona) {
      throw new Error('Id de persona inválido')
    }

    if (!datos || Object.keys(datos).length === 0) {
      throw new Error('No hay datos para actualizar persona')
    }

    const response = await fetch(buildUrl(`/personas/${idPersona}`), {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(datos)
    })

    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      throw new Error(data.error || data.message || 'Error al actualizar persona')
    }

    return data
  }
}

export default new PersonasService()


