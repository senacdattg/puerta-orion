// Servicio para manejar la lógica de negocio de la galería
// Conectado con la API del backend

import { API_CONFIG } from '@/config/environment.js';

class GaleriaService {
  constructor() {
    this.baseURL = `${API_CONFIG.baseURL}/api`;
    this.imagenes = [];
    this.tiposEvento = [];
    this.categorias = [];
  }

  /**
   * Obtiene los headers con autenticación
   */
  getAuthHeaders() {
    const token = localStorage.getItem('token')
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    }
  }

  // ============================================================================
  // MÉTODOS DE API - GALERÍA
  // ============================================================================

  /**
   * Obtener todas las imágenes de la galería
   */
  async cargarImagenes(filtros = {}) {
    try {
      const params = new URLSearchParams();

      if (filtros.id_tipo_evento) {
        params.append('id_tipo_evento', filtros.id_tipo_evento);
      }
      if (filtros.id_categoria) {
        params.append('id_categoria', filtros.id_categoria);
      }
      if (filtros.limit) {
        params.append('limit', filtros.limit);
      }
      if (filtros.offset) {
        params.append('offset', filtros.offset);
      }

      const url = `${this.baseURL}/galeria/?${params.toString()}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Error de autenticación: Token inválido o expirado');
        } else if (response.status === 500) {
          throw new Error('Error interno del servidor al cargar galería');
        } else {
          throw new Error(`Error al cargar galería: ${response.statusText}`);
        }
      }

      const data = await response.json();

      if (data.success && data.data) {
        this.imagenes = data.data;
        return this.imagenes;
      }

      return [];
    } catch (error) {
      console.error('Error al cargar imágenes:', error);
      this.imagenes = [];
      return [];
    }
  }

  /**
   * Obtener una imagen específica por ID
   */
  async obtenerImagen(id) {
    try {
      const response = await fetch(`${this.baseURL}/galeria/${id}`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });

      if (!response.ok) {
        throw new Error(`Error al obtener imagen: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success && data.data) {
        return data.data;
      }

      return null;
    } catch (error) {
      console.error('Error al obtener imagen:', error);
      throw error;
    }
  }

  /**
   * Crear una nueva imagen en la galería subiendo un archivo
   */
  async crearImagenConArchivo(formData) {
    try {
      const response = await fetch(`${this.baseURL}/archivos/upload`, {
        method: 'POST',
        headers: {
          'Authorization': this.getAuthHeaders().Authorization
        },
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Error al subir imagen');
      }

      if (data.success && data.data) {
        // Agregar la nueva imagen a la cache local
        this.imagenes.push(data.data);
        return data.data;
      }

      throw new Error('Respuesta inválida del servidor');
    } catch (error) {
      console.error('Error al subir imagen:', error);
      throw error;
    }
  }

  /**
   * Actualizar una imagen existente
   */
  async actualizarImagen(id, datosActualizados) {
    try {
      const response = await fetch(`${this.baseURL}/galeria/${id}`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(datosActualizados)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Error al actualizar imagen');
      }

      if (data.success && data.data) {
        // Actualizar la imagen en la cache local
        const indice = this.imagenes.findIndex(img => img.id_galeria === id);
        if (indice !== -1) {
          this.imagenes[indice] = data.data;
        }
        return data.data;
      }

      throw new Error('Respuesta inválida del servidor');
    } catch (error) {
      console.error('Error al actualizar imagen:', error);
      throw error;
    }
  }

  /**
   * Eliminar una imagen de la galería
   */
  async eliminarImagen(id) {
    try {
      const response = await fetch(`${this.baseURL}/galeria/${id}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders()
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Error al eliminar imagen');
      }

      if (data.success) {
        // Eliminar la imagen de la cache local
        this.imagenes = this.imagenes.filter(img => img.id_galeria !== id);
        return true;
      }

      throw new Error('Respuesta inválida del servidor');
    } catch (error) {
      console.error('Error al eliminar imagen:', error);
      throw error;
    }
  }

  // ============================================================================
  // MÉTODOS DE CATÁLOGOS
  // ============================================================================

  /**
   * Obtener catálogos necesarios para la galería
   */
  async cargarCatalogos() {
    try {
      const response = await fetch(`${this.baseURL}/galeria/catalogos`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });

      if (!response.ok) {
        throw new Error(`Error al cargar catálogos: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success && data.data) {
        this.tiposEvento = data.data.tipos_evento || [];
        this.categorias = data.data.categorias || [];

        return {
          tiposEvento: this.tiposEvento,
          categorias: this.categorias
        };
      }

      return { tiposEvento: [], categorias: [] };
    } catch (error) {
      console.error('Error al cargar catálogos:', error);
      return { tiposEvento: [], categorias: [] };
    }
  }

  // ============================================================================
  // MÉTODOS DE UTILIDAD
  // ============================================================================

  /**
   * Obtener todas las imágenes
   */
  async obtenerTodasLasImagenes() {
    try {
      if (this.imagenes.length === 0) {
        await this.cargarImagenes();
      }
      return this.imagenes;
    } catch (error) {
      console.error('Error al obtener todas las imágenes:', error);
      return [];
    }
  }

  /**
   * Filtrar imágenes por tipo de evento
   */
  filtrarImagenesPorTipoEvento(idTipoEvento) {
    return this.imagenes.filter(img => img.id_tipo_evento === idTipoEvento);
  }

  /**
   * Filtrar imágenes por categoría
   */
  filtrarImagenesPorCategoria(idCategoria) {
    return this.imagenes.filter(img => img.id_categoria === idCategoria);
  }

  /**
   * Obtener tipo de evento por ID
   */
  obtenerTipoEventoPorId(id) {
    return this.tiposEvento.find(tipo => tipo.id_tipo_evento === id);
  }

  /**
   * Obtener categoría por ID
   */
  obtenerCategoriaPorId(id) {
    return this.categorias.find(cat => cat.id_categoria === id);
  }

  /**
   * Limpiar cache local
   */
  limpiarCache() {
    this.imagenes = [];
    this.tiposEvento = [];
    this.categorias = [];
  }
}

export default new GaleriaService();
