/**
 * Servicio para obtener catálogos del backend
 * Maneja la obtención de tipos de documento, sexos, etc.
 */

import { API_CONFIG } from '@/config/environment'

class CatalogosService {
  constructor() {
    Object.defineProperty(this, 'baseURL', {
      enumerable: true,
      configurable: false,
      get() {
        return API_CONFIG.baseURL
      }
    })
  }

  /**
   * Generic method to fetch catalog data from an endpoint
   * @param {string} endpoint - API endpoint path
   * @param {string} catalogName - Name of the catalog for logging
   * @returns {Promise<Array>} Catalog data array
   */
  async _fetchCatalog(endpoint, catalogName) {
    try {
      const url = `${this.baseURL}${endpoint}`

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error(`❌ Error del servidor ${catalogName}:`, errorText)
        throw new Error(`Error al obtener ${catalogName}: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()

      // Handle different response formats
      if (data.success && Array.isArray(data.data)) {
        return data.data
      }
      if (Array.isArray(data.data)) {
        return data.data
      }
      if (Array.isArray(data)) {
        return data
      }

      return data.data || []
    } catch (error) {
      console.error(`❌ Error al obtener ${catalogName}:`, error)
      throw error
    }
  }

  /**
   * Obtener tipos de documento
   */
  async getTiposDocumento() {
    return this._fetchCatalog('/api/catalogos/tipos-documento', 'tipos de documento')
  }

  /**
   * Obtener sexos/géneros
   */
  async getSexos() {
    return this._fetchCatalog('/api/catalogos/sexos', 'sexos')
  }

  /**
   * Obtener categorías
   */
  async getCategorias() {
    return this._fetchCatalog('/api/catalogos/categorias', 'categorías')
  }

  /**
   * Obtener todos los catálogos en una sola petición
   */
  async getCatalogosCompletos() {
    try {
      const response = await fetch(`${this.baseURL}/api/catalogos/catalogos-completos`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ CatalogosService: Error del servidor catálogos completos:', errorText);
        throw new Error(`Error al obtener catálogos: ${response.status} ${response.statusText}`)
      }

      const data = await response.json();

      // El backend devuelve { success: true, data: { tipos_documento: [...], sexos: [...] } }
      // Retornamos el objeto completo para que cargarCatalogosFormulario pueda acceder correctamente
      return data
    } catch (error) {
      console.error('❌ CatalogosService: Error al obtener catálogos completos:', error)
      throw error
    }
  }

  /**
   * Obtener parentescos
   */
  async getParentescos() {
    return this._fetchCatalog('/api/catalogos/parentescos', 'parentescos')
  }

  /**
   * Cargar todos los catálogos necesarios para el formulario
   */
  async cargarCatalogosFormulario() {
    try {
      const response = await this.getCatalogosCompletos()

      // El backend devuelve { success: true, data: { tipos_documento: [...], sexos: [...] } }
      // Necesitamos acceder a response.data, no directamente a response
      const catalogos = (typeof response === 'object' && response !== null && 'data' in response)
        ? response.data
        : response;

      const resultado = {
        tiposDocumento: catalogos?.tipos_documento ?? [], // NOSONAR: S6582
        sexos: catalogos?.sexos ?? [] // NOSONAR: S6582
      };

      return resultado;
    } catch (error) {
      console.error('❌ CatalogosService: Error al cargar catálogos:', error)
      throw error
    }
  }
}

// Exportar instancia única
export default new CatalogosService()
