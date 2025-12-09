// Servicio alineado al patrón de la carpeta services (clase + API_CONFIG + logging)
import { API_CONFIG } from '@/config/environment'
import authService from '@/services/authService'

class MensualidadesApi {
  constructor () {
    Object.defineProperty(this, 'baseURL', {
      enumerable: true,
      configurable: false,
      get () {
        return API_CONFIG.baseURL
      }
    })
  }

  // Helpers
  async _request (path, options = {}, logLabel = 'MensualidadesApi') {
    const url = `${this.baseURL}${path}`
    try {
      const token = authService.getToken?.()
      const res = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        ...options
      })
      if (!res.ok) {
        let errorMessage = `${res.status} ${res.statusText}`
        try {
          // Leer el texto de la respuesta primero
          const errorText = await res.text()
          console.error(`❌ ${logLabel}: server error response`, errorText)

          // Intentar parsear como JSON
          try {
            const errorData = JSON.parse(errorText)
            // Intentar extraer el mensaje de error del backend
            if (errorData?.error) {
              errorMessage = errorData.error
            } else if (errorData?.message) {
              errorMessage = errorData.message
            }
          } catch {
            // Si no es JSON válido, usar el texto directamente si no está vacío
            if (errorText?.trim()) {
              errorMessage = errorText
            }
          }
        } catch (readError) {
          console.error(`❌ ${logLabel}: could not read error response`, readError)
        }
        const error = new Error(errorMessage)
        error.status = res.status
        throw error
      }
      const data = await res.json()
      return data
    } catch (err) {
      console.error(`❌ ${logLabel}: request error`, err)
      throw err
    }
  }

  /**
   * Listar mensualidades con filtros
   * @param {{persona_id?:number, estado?:'pagado'|'pendiente', activo?:0|1, page?:number, per_page?:number}} params
   */
  async list (params = {}) {
    const qs = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null) qs.set(k, String(v))
    })
    // Extract nested template literal to improve readability
    const queryString = qs.toString()
    const path = queryString ? `/api/mensualidades?${queryString}` : '/api/mensualidades'
    return this._request(path, {}, 'MensualidadesApi.list')
  }

  /** Obtener una mensualidad */
  async get (id) {
    return this._request(`/api/mensualidades/${id}`, {}, 'MensualidadesApi.get')
  }

  /** Crear mensualidad */
  async create (payload) {
    return this._request('/api/mensualidades', {
      method: 'POST',
      body: JSON.stringify(payload)
    }, 'MensualidadesApi.create')
  }

  /** Actualizar mensualidad */
  async update (id, payload) {
    return this._request(`/api/mensualidades/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    }, 'MensualidadesApi.update')
  }

  /** Desactivar */
  async desactivar (id) {
    return this._request(`/api/mensualidades/${id}/desactivar`, {
      method: 'PATCH'
    }, 'MensualidadesApi.desactivar')
  }

  /** Reactivar */
  async reactivar (id) {
    return this._request(`/api/mensualidades/${id}/reactivar`, {
      method: 'PATCH'
    }, 'MensualidadesApi.reactivar')
  }

  /** Buscar persona por número de documento para crear mensualidad */
  async buscarPersonaPorDocumento (documento) {
    const qs = new URLSearchParams()
    if (documento) qs.set('documento', documento)
    // Extract nested template literal to improve readability
    const queryString = qs.toString()
    const path = queryString ? `/api/mensualidades/buscar-persona?${queryString}` : '/api/mensualidades/buscar-persona'
    return this._request(path, {}, 'MensualidadesApi.buscarPersona')
  }

  /** Registrar abono (con fecha opcional e id_metodo_pago opcional) */
  async abonar (id, { monto_abonado, fecha_abono, id_metodo_pago } = {}) {
    const body = { monto_abonado }
    if (fecha_abono) body.fecha_abono = fecha_abono
    if (id_metodo_pago !== undefined) body.id_metodo_pago = id_metodo_pago
    return this._request(`/api/mensualidades/${id}/abonar`, {
      method: 'POST',
      body: JSON.stringify(body)
    }, 'MensualidadesApi.abonar')
  }

  /** Listar abonos de una mensualidad */
  async listarAbonos (id) {
    return this._request(`/api/mensualidades/${id}/abonos`, {}, 'MensualidadesApi.listarAbonos')
  }

  /** Actualizar abono */
  async updateAbono (mensualidadId, abonoId, payload) {
    return this._request(`/api/mensualidades/${mensualidadId}/abonos/${abonoId}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    }, 'MensualidadesApi.updateAbono')
  }

  /** Eliminar abono */
  async deleteAbono (mensualidadId, abonoId) {
    return this._request(`/api/mensualidades/${mensualidadId}/abonos/${abonoId}`, {
      method: 'DELETE'
    }, 'MensualidadesApi.deleteAbono')
  }

  /** Crear preferencia de pago en MP */
  async crearPreferenciaMensualidad (args) {
    return this._request('/api/mercadopago/crear-preferencia', {
      method: 'POST',
      body: JSON.stringify({ tipo_pago: 'mensualidad', ...args })
    }, 'MensualidadesApi.crearPreferenciaMensualidad')
  }
}

// Exportar instancia única, igual que otros services
export default new MensualidadesApi()
export { MensualidadesApi }
