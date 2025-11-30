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
      console.log(`🔄 Obteniendo ${catalogName} desde:`, url)

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      })

      console.log(`📡 Respuesta ${catalogName}:`, response.status, response.statusText)

      if (!response.ok) {
        const errorText = await response.text()
        console.error(`❌ Error del servidor ${catalogName}:`, errorText)
        throw new Error(`Error al obtener ${catalogName}: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      console.log(`📦 Datos ${catalogName} recibidos:`, data)

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
      console.log('🔄 CatalogosService: Obteniendo catálogos completos desde:', `${this.baseURL}/api/catalogos/catalogos-completos`);

      const response = await fetch(`${this.baseURL}/api/catalogos/catalogos-completos`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      console.log('📡 CatalogosService: Respuesta catálogos completos:', response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ CatalogosService: Error del servidor catálogos completos:', errorText);
        throw new Error(`Error al obtener catálogos: ${response.status} ${response.statusText}`)
      }

      const data = await response.json();
      console.log('📦 CatalogosService: Datos catálogos completos recibidos:', data);

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
      console.log('🔄 CatalogosService: Cargando catálogos completos...');

      const response = await this.getCatalogosCompletos()
      console.log('📦 CatalogosService: Respuesta completa recibida:', response);

      // El backend devuelve { success: true, data: { tipos_documento: [...], sexos: [...] } }
      // Necesitamos acceder a response.data, no directamente a response
      const catalogos = response && typeof response === 'object' && 'data' in response
        ? response.data
        : response;

      console.log('📦 CatalogosService: Catálogos extraídos:', catalogos);

      const resultado = {
        tiposDocumento: (catalogos && catalogos.tipos_documento) ? catalogos.tipos_documento : [],
        sexos: (catalogos && catalogos.sexos) ? catalogos.sexos : []
      };

      console.log('✅ CatalogosService: Resultado procesado:', resultado);
      console.log('✅ CatalogosService: Tipos documento:', resultado.tiposDocumento.length);
      console.log('✅ CatalogosService: Sexos:', resultado.sexos.length);
      return resultado;
    } catch (error) {
      console.error('❌ CatalogosService: Error al cargar catálogos:', error)
      throw error
    }
  }
}

// Exportar instancia única
export default new CatalogosService()
