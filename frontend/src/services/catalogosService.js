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
      console.log('🔄 Obteniendo tipos de documento desde:', `${this.baseURL}/api/catalogos/tipos-documento`);

      const response = await fetch(`${this.baseURL}/api/catalogos/tipos-documento`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      console.log('📡 Respuesta tipos documento:', response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Error del servidor tipos documento:', errorText);
        throw new Error(`Error al obtener tipos de documento: ${response.status} ${response.statusText}`)
      }

      const data = await response.json();
      console.log('📦 Datos tipos documento recibidos:', data);

      return data.data || []
    } catch (error) {
      console.error('❌ Error al obtener tipos de documento:', error)
      throw error
    }
  }

  /**
   * Obtener sexos/géneros
   */
  async getSexos() {
    try {
      console.log('🔄 Obteniendo sexos desde:', `${this.baseURL}/api/catalogos/sexos`);

      const response = await fetch(`${this.baseURL}/api/catalogos/sexos`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      console.log('📡 Respuesta sexos:', response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Error del servidor sexos:', errorText);
        throw new Error(`Error al obtener sexos: ${response.status} ${response.statusText}`)
      }

      const data = await response.json();
      console.log('📦 Datos sexos recibidos:', data);

      return data.data || []
    } catch (error) {
      console.error('❌ Error al obtener sexos:', error)
      throw error
    }
  }

  /**
   * Obtener categorías
   */
  async getCategorias() {
    try {
      console.log('🔄 Obteniendo categorías desde:', `${this.baseURL}/api/catalogos/categorias`);

      const response = await fetch(`${this.baseURL}/api/catalogos/categorias`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      console.log('📡 Respuesta categorías:', response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Error del servidor categorías:', errorText);
        throw new Error(`Error al obtener categorías: ${response.status} ${response.statusText}`)
      }

      const data = await response.json();
      console.log('📦 Datos categorías recibidos:', data);

      // El backend puede retornar { success: true, data: [...] } o directamente el array
      if (data.success && Array.isArray(data.data)) {
        return data.data;
      } else if (Array.isArray(data.data)) {
        return data.data;
      } else if (Array.isArray(data)) {
        return data;
      }

      return [];
    } catch (error) {
      console.error('❌ Error al obtener categorías:', error)
      throw error
    }
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

      return data.data || {}
    } catch (error) {
      console.error('❌ CatalogosService: Error al obtener catálogos completos:', error)
      throw error
    }
  }

  /**
   * Obtener parentescos
   */
  async getParentescos() {
    try {
      console.log('🔄 Obteniendo parentescos desde:', `${this.baseURL}/api/catalogos/parentescos`);

      const response = await fetch(`${this.baseURL}/api/catalogos/parentescos`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      console.log('📡 Respuesta parentescos:', response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Error del servidor parentescos:', errorText);
        throw new Error(`Error al obtener parentescos: ${response.status} ${response.statusText}`)
      }

      const data = await response.json();
      console.log('📦 Datos parentescos recibidos:', data);

      return data.data || []
    } catch (error) {
      console.error('❌ Error al obtener parentescos:', error)
      throw error
    }
  }

  /**
   * Cargar todos los catálogos necesarios para el formulario
   */
  async cargarCatalogosFormulario() {
    try {
      console.log('🔄 CatalogosService: Cargando catálogos completos...');

      const catalogos = await this.getCatalogosCompletos()
      console.log('📦 CatalogosService: Catálogos recibidos:', catalogos);

      const resultado = {
        tiposDocumento: catalogos.tipos_documento || [],
        sexos: catalogos.sexos || []
      };

      console.log('✅ CatalogosService: Resultado procesado:', resultado);
      return resultado;
    } catch (error) {
      console.error('❌ CatalogosService: Error al cargar catálogos:', error)
      throw error
    }
  }
}

// Exportar instancia única
export default new CatalogosService()
