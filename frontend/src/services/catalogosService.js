/**
 * Servicio para obtener catálogos del backend
 * Maneja la obtención de tipos de documento, sexos, etc.
 */

import { API_CONFIG } from '@/config/environment'

class CatalogosService {
  constructor() {
    this.baseURL = API_CONFIG.baseURL
  }

  /**
   * Obtener tipos de documento
   */
  async getTiposDocumento() {
    try {
      const response = await fetch(`${this.baseURL}/api/catalogos/tipos-documento`)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error al obtener tipos de documento')
      }

      return data.data || []
    } catch (error) {
      console.error('Error al obtener tipos de documento:', error)
      throw error
    }
  }

  /**
   * Obtener sexos/géneros
   */
  async getSexos() {
    try {
      const response = await fetch(`${this.baseURL}/api/catalogos/sexos`)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error al obtener sexos')
      }

      return data.data || []
    } catch (error) {
      console.error('Error al obtener sexos:', error)
      throw error
    }
  }

  /**
   * Obtener todos los catálogos en una sola petición
   */
  async getCatalogosCompletos() {
    try {
      const response = await fetch(`${this.baseURL}/api/catalogos/catalogos-completos`)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error al obtener catálogos')
      }

      return data.data || {}
    } catch (error) {
      console.error('Error al obtener catálogos completos:', error)
      throw error
    }
  }

  /**
   * Cargar todos los catálogos necesarios para el formulario
   */
  async cargarCatalogosFormulario() {
    try {
      const catalogos = await this.getCatalogosCompletos()

      return {
        tiposDocumento: catalogos.tipos_documento || [],
        sexos: catalogos.sexos || []
      }
    } catch (error) {
      console.error('Error al cargar catálogos:', error)
      throw error
    }
  }
}

// Exportar instancia única
export default new CatalogosService()
