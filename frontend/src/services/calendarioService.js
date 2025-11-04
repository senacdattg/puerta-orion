// Servicio para manejar la lógica de negocio del calendario
// Conectado con la API del backend

import { API_CONFIG } from '@/config/environment.js';

class CalendarioService {
  constructor() {
    this.baseURL = `${API_CONFIG.baseURL}/api`;
    this.eventos = [];
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
  // MÉTODOS DE API - EVENTOS
  // ============================================================================

  /**
   * Obtener todos los eventos desde el backend
   */
  async cargarEventos() {
    try {
      const response = await fetch(`${this.baseURL}/calendario?per_page=1000`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });

      if (!response.ok) {
        // Manejar diferentes tipos de errores
        if (response.status === 401) {
          throw new Error('Error de autenticación: Token inválido o expirado');
        } else if (response.status === 500) {
          throw new Error('Error interno del servidor al cargar eventos');
        } else {
          throw new Error(`Error al cargar eventos: ${response.statusText}`);
        }
      }

      const data = await response.json();

      if (data.success && data.data) {
        // Mapear eventos del backend al formato del frontend
        this.eventos = data.data.map(evento => this.mapearEventoBackendAFrontend(evento));
        return this.eventos;
      }

      return [];
    } catch (error) {
      console.error('Error al cargar eventos:', error);
      // Retornar array vacío en lugar de lanzar error para evitar crashes
      this.eventos = [];
      return [];
    }
  }

  /**
   * Obtener eventos por fecha específica
   */
  obtenerEventosPorFecha(fecha) {
    try {
      // Filtrar eventos por fecha usando los eventos ya cargados en memoria
      return this.eventos.filter(evento => evento.fecha === fecha);
    } catch (error) {
      console.error('Error al obtener eventos por fecha:', error);
      return [];
    }
  }

  /**
   * Obtener todos los eventos
   */
  async obtenerTodosLosEventos() {
    try {
      if (this.eventos.length === 0) {
        await this.cargarEventos();
      }
      return this.eventos;
    } catch (error) {
      console.error('Error al obtener todos los eventos:', error);
      // Retornar array vacío para evitar crashes en el frontend
      return [];
    }
  }

  /**
   * Crear un nuevo evento
   */
  async crearEvento(evento) {
    try {
      // Mapear evento de frontend a backend
      const eventoBackend = this.mapearEventoFrontendABackend(evento);
      
      // Validar que las horas estén en formato correcto antes de enviar
      if (eventoBackend.hora_inicio && !/^\d{2}:\d{2}(:\d{2})?$/.test(eventoBackend.hora_inicio)) {
        console.error('⚠️ Formato de hora_inicio inválido:', eventoBackend.hora_inicio);
        throw new Error('Formato de hora de inicio inválido. Debe ser HH:MM');
      }
      
      if (eventoBackend.hora_fin && !/^\d{2}:\d{2}(:\d{2})?$/.test(eventoBackend.hora_fin)) {
        console.error('⚠️ Formato de hora_fin inválido:', eventoBackend.hora_fin);
        throw new Error('Formato de hora de fin inválido. Debe ser HH:MM');
      }
      
      console.log('📤 Enviando evento al backend:', {
        nombre: eventoBackend.nombre,
        fecha: eventoBackend.fecha_evento,
        hora_inicio: eventoBackend.hora_inicio,
        hora_fin: eventoBackend.hora_fin,
        categoria: eventoBackend.id_categoria
      });

      const response = await fetch(`${this.baseURL}/calendario`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(eventoBackend)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Error al crear evento');
      }

      if (data.success && data.data) {
        // Agregar el nuevo evento a la cache local
        const nuevoEvento = this.mapearEventoBackendAFrontend(data.data);
        this.eventos.push(nuevoEvento);
        return nuevoEvento;
      }

      throw new Error('Respuesta inválida del servidor');
    } catch (error) {
      console.error('Error al crear evento:', error);
      throw error;
    }
  }

  /**
   * Actualizar un evento existente
   */
  async actualizarEvento(id, datosActualizados) {
    try {
      // Mapear datos de frontend a backend
      const datosBackend = this.mapearEventoFrontendABackend(datosActualizados, true);

      const response = await fetch(`${this.baseURL}/calendario/${id}`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(datosBackend)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Error al actualizar evento');
      }

      if (data.success && data.data) {
        // Actualizar el evento en la cache local
        const eventoActualizado = this.mapearEventoBackendAFrontend(data.data);
        const indice = this.eventos.findIndex(e => e.id === id);
        if (indice !== -1) {
          this.eventos[indice] = eventoActualizado;
        }
        return eventoActualizado;
      }

      throw new Error('Respuesta inválida del servidor');
    } catch (error) {
      console.error('Error al actualizar evento:', error);
      throw error;
    }
  }

  /**
   * Eliminar un evento
   */
  async eliminarEvento(id) {
    try {
      const response = await fetch(`${this.baseURL}/calendario/${id}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders()
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Error al eliminar evento');
      }

      if (data.success) {
        // Eliminar el evento de la cache local
        this.eventos = this.eventos.filter(e => e.id !== id);
        return true;
      }

      throw new Error('Respuesta inválida del servidor');
    } catch (error) {
      console.error('Error al eliminar evento:', error);
      throw error;
    }
  }

  // ============================================================================
  // MÉTODOS DE API - CATÁLOGOS (Sesiones, Tipos de Evento, Categorías)
  // ============================================================================


  /**
   * Cargar tipos de evento disponibles
   */
  async cargarTiposEvento() {
    try {
      const response = await fetch(`${this.baseURL}/tipos-evento?per_page=100`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });

      if (!response.ok) {
        throw new Error(`Error al cargar tipos de evento: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success && data.data) {
        this.tiposEvento = data.data;
        return this.tiposEvento;
      }

      console.warn('⚠️ No se encontraron tipos de evento en la respuesta del backend');
      return [];
    } catch (error) {
      console.warn('⚠️ Backend no disponible, usando tipos de ejemplo:', error.message);

      // Fallback: tipos de evento de ejemplo (incluyendo el que tienes en la BD)
      this.tiposEvento = [
        { id_tipo_evento: 1, nombre: 'Entrenamiento', descripcion: 'Sesiones de práctica' },
        { id_tipo_evento: 2, nombre: 'Evento', descripcion: 'Eventos especiales' },
        { id_tipo_evento: 3, nombre: 'Competencia', descripcion: 'Competiciones deportivas' }
      ];

      return this.tiposEvento;
    }
  }

  /**
   * Cargar categorías disponibles
   */
  async cargarCategorias() {
    try {
      console.log('🔄 Cargando categorías desde:', `${this.baseURL}/catalogos/categorias`);

      const response = await fetch(`${this.baseURL}/catalogos/categorias`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      console.log('📡 Respuesta del servidor:', response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Error del servidor:', errorText);
        throw new Error(`Error al cargar categorías: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('📦 Datos recibidos:', data);

      if (data.success && data.data) {
        this.categorias = data.data;
        console.log('✅ Categorías cargadas exitosamente:', this.categorias.length);
        return this.categorias;
      }

      console.warn('⚠️ Respuesta sin datos válidos');
      return [];
    } catch (error) {
      console.error('❌ Error al cargar categorías:', error.message);
      console.warn('⚠️ Usando categorías de ejemplo como fallback');

      // Fallback: categorías de ejemplo
      this.categorias = [
        { id_categoria: 1, nombre_categoria: 'Fútbol', codigo_categoria: 101, edad_minima: 6, edad_maxima: 18 },
        { id_categoria: 2, nombre_categoria: 'Básquetbol', codigo_categoria: 102, edad_minima: 8, edad_maxima: 18 },
        { id_categoria: 3, nombre_categoria: 'Voleibol', codigo_categoria: 103, edad_minima: 10, edad_maxima: 18 }
      ];

      return this.categorias;
    }
  }

  /**
   * Cargar todos los catálogos necesarios
   */
  async cargarCatalogos() {
    try {
      await Promise.all([
        this.cargarTiposEvento(),
        this.cargarCategorias()
      ]);

      const result = {
        tiposEvento: this.tiposEvento,
        categorias: this.categorias
      };

      return result;
    } catch (error) {
      console.error('Error al cargar catálogos:', error);
      throw error;
    }
  }

  // ============================================================================
  // MÉTODOS DE MAPEO (Frontend <-> Backend)
  // ============================================================================

  /**
   * Mapear evento del backend al formato del frontend
   */
  mapearEventoBackendAFrontend(eventoBackend) {
    return {
      id: eventoBackend.id_evento,
      titulo: eventoBackend.nombre,
      fecha: eventoBackend.fecha_evento,
      hora: eventoBackend.hora_inicio, // Usar hora de inicio como hora principal
      horaInicio: eventoBackend.hora_inicio,
      horaFin: eventoBackend.hora_fin,
      lugar: eventoBackend.lugar,
      descripcion: eventoBackend.descripcion || '',
      // Mapear tipo de evento
      tipo: eventoBackend.tipo_evento ? eventoBackend.tipo_evento.nombre : 'Evento',
      idTipoEvento: eventoBackend.id_tipo_evento,
      idCategoria: eventoBackend.id_categoria,
      idSesion: eventoBackend.id_sesion,
      // Información adicional
      categoria: eventoBackend.categoria,
      sesion: eventoBackend.sesion,
      tipoEvento: eventoBackend.tipo_evento
    };
  }

  /**
   * Mapear evento del frontend al formato del backend
   */
  /**
   * Convierte una hora a formato 24 horas (HH:MM o HH:MM:SS)
   * Asegura que el formato sea correcto para el backend
   */
  normalizarHora(hora) {
    if (!hora) return null;
    
    // Si ya está en formato HH:MM o HH:MM:SS, retornarlo
    if (typeof hora === 'string' && /^\d{2}:\d{2}(:\d{2})?$/.test(hora)) {
      return hora;
    }
    
    // Si viene en formato 12 horas con AM/PM, convertir
    if (typeof hora === 'string' && (hora.includes('AM') || hora.includes('PM') || hora.includes('a.') || hora.includes('p.'))) {
      // Convertir formato 12 horas a 24 horas
      const match = hora.match(/(\d{1,2}):(\d{2})\s*(AM|PM|a\.m\.|p\.m\.)/i);
      if (match) {
        let horas = parseInt(match[1]);
        const minutos = match[2];
        const periodo = match[3].toUpperCase();
        
        if (periodo.includes('PM') || periodo.includes('P.')) {
          if (horas !== 12) horas += 12;
        } else if (periodo.includes('AM') || periodo.includes('A.')) {
          if (horas === 12) horas = 0;
        }
        
        return `${horas.toString().padStart(2, '0')}:${minutos}`;
      }
    }
    
    // Si no se puede convertir, retornar null
    return null;
  }

  mapearEventoFrontendABackend(eventoFrontend, esActualizacion = false) {
    const eventoBackend = {};

    // Solo incluir campos que están presentes
    if (eventoFrontend.titulo !== undefined) {
      eventoBackend.nombre = eventoFrontend.titulo;
    }

    if (eventoFrontend.fecha !== undefined) {
      eventoBackend.fecha_evento = eventoFrontend.fecha;
    }

    if (eventoFrontend.hora !== undefined || eventoFrontend.horaInicio !== undefined) {
      const horaNormalizada = this.normalizarHora(eventoFrontend.horaInicio || eventoFrontend.hora);
      eventoBackend.hora_inicio = horaNormalizada || (eventoFrontend.horaInicio || eventoFrontend.hora);
    }

    if (eventoFrontend.horaFin !== undefined) {
      const horaNormalizada = this.normalizarHora(eventoFrontend.horaFin);
      eventoBackend.hora_fin = horaNormalizada || eventoFrontend.horaFin;
    }

    if (eventoFrontend.lugar !== undefined) {
      eventoBackend.lugar = eventoFrontend.lugar;
    }

    if (eventoFrontend.descripcion !== undefined) {
      eventoBackend.descripcion = eventoFrontend.descripcion;
    }

    if (eventoFrontend.idTipoEvento !== undefined) {
      eventoBackend.id_tipo_evento = eventoFrontend.idTipoEvento;
    }

    if (eventoFrontend.idCategoria !== undefined) {
      eventoBackend.id_categoria = eventoFrontend.idCategoria;
    }


    // Si no es actualización, agregar valores por defecto para campos requeridos
    if (!esActualizacion) {
      // Si no hay hora_fin, calcular 1 hora después de hora_inicio
      if (!eventoBackend.hora_fin && eventoBackend.hora_inicio) {
        const [horas, minutos] = eventoBackend.hora_inicio.split(':');
        const horaFin = (parseInt(horas) + 1).toString().padStart(2, '0');
        eventoBackend.hora_fin = `${horaFin}:${minutos || '00'}`;
      }

      // Valores por defecto si no existen
      if (!eventoBackend.id_categoria) eventoBackend.id_categoria = 1;
      if (!eventoBackend.id_tipo_evento) eventoBackend.id_tipo_evento = 1;
    }

    return eventoBackend;
  }

  // ============================================================================
  // MÉTODOS DE VALIDACIÓN
  // ============================================================================

  /**
   * Validar datos del evento antes de enviar al backend
   */
  validarEvento(evento) {
    const errores = [];

    if (!evento.titulo || evento.titulo.trim().length < 3) {
      errores.push('El título debe tener al menos 3 caracteres');
    }

    if (!evento.fecha) {
      errores.push('Debe especificar una fecha');
    }

    if (!evento.hora && !evento.horaInicio) {
      errores.push('Debe especificar una hora de inicio');
    }

    if (!evento.lugar || evento.lugar.trim().length < 3) {
      errores.push('El lugar debe tener al menos 3 caracteres');
    }

    if (!evento.idTipoEvento) {
      errores.push('Debe seleccionar un tipo de evento');
    }

    if (!evento.idCategoria) {
      errores.push('Debe seleccionar una categoría');
    }

    // Validar formato de fecha
    if (evento.fecha) {
      const fecha = new Date(evento.fecha);
      if (isNaN(fecha.getTime())) {
        errores.push('La fecha especificada no es válida');
      }
    }

    // Validar formato de hora
    if (evento.hora || evento.horaInicio) {
      const horaValidar = evento.horaInicio || evento.hora;
      const formatoHora = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$/;
      if (!formatoHora.test(horaValidar)) {
        errores.push('El formato de hora debe ser HH:MM o HH:MM:SS');
      }
    }

    // Validar que hora_fin sea mayor que hora_inicio
    if (evento.horaInicio && evento.horaFin) {
      if (evento.horaFin <= evento.horaInicio) {
        errores.push('La hora de fin debe ser posterior a la hora de inicio');
      }
    }

    return errores;
  }

  // ============================================================================
  // MÉTODOS AUXILIARES
  // ============================================================================

  /**
   * Obtener tipo de evento por nombre
   */
  obtenerTipoEventoPorNombre(nombreTipo) {
    return this.tiposEvento.find(tipo =>
      tipo.nombre.toLowerCase() === nombreTipo.toLowerCase()
    );
  }


  /**
   * Limpiar cache local
   */
  limpiarCache() {
    this.eventos = [];
    this.tiposEvento = [];
    this.categorias = [];
  }
}

export default new CalendarioService();
