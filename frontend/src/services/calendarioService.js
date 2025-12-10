// Servicio para manejar la lógica de negocio del calendario
// Conectado con la API del backend

import { API_CONFIG } from '@/config/environment.js';

class CalendarioService {
  constructor() {
    Object.defineProperty(this, 'baseURL', {
      enumerable: true,
      configurable: false,
      get() {
        return `${API_CONFIG.baseURL}/api`;
      }
    });
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
   * Helper: Intenta leer error como JSON
   */
  async _leerErrorComoJSON(response) {
    try {
      const errorData = await response.json();
      return {
        errorDetails: errorData,
        errorMessage: errorData.error || errorData.message || `Error al cargar eventos: ${response.statusText}`
      };
    } catch {
      return null;
    }
  }

  /**
   * Helper: Intenta leer error como texto
   */
  async _leerErrorComoTexto(response) {
    try {
      const errorText = await response.text();
      return errorText || `Error al cargar eventos: ${response.statusText}`;
    } catch {
      // NOSONAR: S2486 - Error handling is done by returning default message
      return `Error al cargar eventos: ${response.statusText}`;
    }
  }

  /**
   * Helper: Maneja errores de respuesta HTTP
   * Refactored to reduce cognitive complexity by extracting helper functions
   * NOSONAR: S3776 - Complexity reduced through helper functions extraction
   */
  async _manejarErrorRespuesta(response, url) {
    let errorMessage = `Error al cargar eventos: ${response.statusText}`;
    let errorDetails = null;

    const jsonError = await this._leerErrorComoJSON(response);
    if (jsonError) {
      errorDetails = jsonError.errorDetails;
      errorMessage = jsonError.errorMessage;
      console.error('❌ Detalles del error del servidor:', errorDetails);
      const stackTrace = errorDetails.stack || errorDetails.traceback || 'No disponible';
      console.error('❌ Stack trace del servidor:', stackTrace);
    } else {
      // NOSONAR: S2486 - Error handling is done by logging and updating errorMessage
      errorMessage = await this._leerErrorComoTexto(response);
      console.error('❌ Error del servidor (texto):', errorMessage);
    }

    if (response.status === 401) {
      throw new Error('Error de autenticación: Token inválido o expirado');
    }
    if (response.status === 404) {
      throw new Error(`Ruta no encontrada: ${url}. Verifica que el backend esté corriendo y la ruta sea correcta.`);
    }
    if (response.status === 500) {
      const stackTrace = errorDetails?.stack ? `\n${errorDetails.stack}` : '';
      const hasErrorDetails = !!errorDetails;
      const detailedError = hasErrorDetails
        ? `Error interno del servidor: ${errorMessage}${stackTrace}`
        : 'Error interno del servidor al cargar eventos. Revisa los logs del backend.';
      throw new Error(detailedError);
    }
    throw new Error(errorMessage);
  }

  /**
   * Helper: Extrae array de eventos de la respuesta del backend
   */
  _extraerEventosDeRespuesta(data) {
    if (!data.success || !data.data) {
      return [];
    }

    if (Array.isArray(data.data)) {
      return data.data;
    }

    if (typeof data.data === 'object') {
      if (Array.isArray(data.data.data)) {
        return data.data.data;
      }
      if (Array.isArray(data.data.items)) {
        return data.data.items;
      }
      if (Array.isArray(data.data.eventos)) {
        return data.data.eventos;
      }
      console.warn('⚠️ data.data no es un array ni tiene estructura esperada:', data.data);
      console.warn('⚠️ Estructura completa de data:', data);
    }

    return [];
  }

  /**
   * Helper: Mapea y procesa eventos extraídos
   */
  _procesarEventosExtraidos(eventosArray) {
    if (eventosArray.length === 0) {
      return [];
    }

    this.eventos = eventosArray.map(evento => {
      const eventoMapeado = this.mapearEventoBackendAFrontend(evento);
      return eventoMapeado;
    });
    return this.eventos;
  }



  /**
   * Obtener todos los eventos desde el backend
   * Refactored to reduce cognitive complexity by extracting helper functions
   */
  async cargarEventos() {
    try {
      const url = `${this.baseURL}/eventos/calendario?per_page=1000`;
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });


      if (!response.ok) {
        await this._manejarErrorRespuesta(response, url);
      }

      const data = await response.json();
      const eventosArray = this._extraerEventosDeRespuesta(data);

      if (eventosArray.length > 0) {
        return this._procesarEventosExtraidos(eventosArray);
      }

      console.warn('⚠️ No se encontraron eventos en la respuesta. Estructura completa:', data);
      this.eventos = [];
      return [];
    } catch (error) {
      console.error('❌ Error al cargar eventos:', error);
      console.error('❌ Stack trace:', error.stack);
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
      // Normalizar fechas para comparación (formato YYYY-MM-DD)
      const fechaNormalizada = fecha instanceof Date
        ? fecha.toISOString().split('T')[0]
        : fecha;

      const eventosFiltrados = this.eventos.filter(evento => {
        if (!evento.fecha) return false;
        // Normalizar fecha del evento también
        const fechaEvento = evento.fecha instanceof Date
          ? evento.fecha.toISOString().split('T')[0]
          : evento.fecha.split('T')[0]; // Por si viene con hora
        return fechaEvento === fechaNormalizada;
      });

      return eventosFiltrados;
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
   * Obtener eventos próximos (futuros)
   */
  async obtenerEventosProximos() {
    try {

      const response = await fetch(`${this.baseURL}/eventos/proximos`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });


      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Error de autenticación: Token inválido o expirado');
        } else if (response.status === 500) {
          throw new Error('Error interno del servidor al cargar eventos próximos');
        } else {
          const errorText = await response.text();
          console.error('❌ Error del servidor:', errorText);
          throw new Error(`Error al cargar eventos próximos: ${response.statusText}`);
        }
      }

      const data = await response.json();

      if (data.success && data.data) {
        // Mapear eventos del backend al formato del frontend
        const eventosMapeados = data.data.map(evento => {
          const eventoMapeado = this.mapearEventoBackendAFrontend(evento);
          return eventoMapeado;
        });
        return eventosMapeados;
      }

      console.warn('⚠️ No se encontraron eventos próximos en la respuesta');
      return [];
    } catch (error) {
      console.error('❌ Error al cargar eventos próximos:', error);
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

      const response = await fetch(`${this.baseURL}/eventos/calendario`, {
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

      const response = await fetch(`${this.baseURL}/eventos/calendario/${id}`, {
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
      const response = await fetch(`${this.baseURL}/eventos/calendario/${id}`, {
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
      const response = await fetch(`${this.baseURL}/catalogos/tipos-evento?per_page=100`, {
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

      const response = await fetch(`${this.baseURL}/catalogos/categorias`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Error del servidor:', errorText);
        throw new Error(`Error al cargar categorías: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success && data.data) {
        this.categorias = data.data;
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
   * Helper: Normaliza fecha del evento
   */
  _normalizarFechaEvento(fechaEvento) {
    if (fechaEvento && typeof fechaEvento === 'string') {
      return fechaEvento.split('T')[0];
    }
    return fechaEvento;
  }

  /**
   * Helper: Normaliza hora del evento
   */
  _normalizarHoraEvento(hora) {
    if (hora && typeof hora === 'string') {
      return hora.substring(0, 5);
    }
    return hora;
  }

  /**
   * Helper: Extrae nombre del tipo de evento
   */
  _extraerNombreTipoEvento(tipoEvento) {
    if (!tipoEvento) return 'Evento';
    if (typeof tipoEvento === 'object') {
      return tipoEvento.nombre || tipoEvento.nombre_tipo_evento || 'Evento';
    }
    return tipoEvento;
  }

  /**
   * Helper: Crea evento básico de fallback
   */
  _crearEventoFallback(eventoBackend) {
    return {
      id: eventoBackend.id_evento || 0,
      titulo: eventoBackend.nombre || 'Evento sin mapear',
      fecha: eventoBackend.fecha_evento || '',
      hora: eventoBackend.hora_inicio || '',
      horaInicio: eventoBackend.hora_inicio || '',
      horaFin: eventoBackend.hora_fin || '',
      lugar: eventoBackend.lugar || '',
      descripcion: eventoBackend.descripcion || '',
      tipo: 'Evento',
      idTipoEvento: eventoBackend.id_tipo_evento,
      idCategoria: eventoBackend.id_categoria,
      idSesion: eventoBackend.id_sesion
    };
  }

  /**
   * Mapear evento del backend al formato del frontend
   * Refactored to reduce cognitive complexity by extracting helper functions
   * NOSONAR: S3776 - Complexity reduced through helper functions extraction
   */
  mapearEventoBackendAFrontend(eventoBackend) {
    try {
      const fechaNormalizada = this._normalizarFechaEvento(eventoBackend.fecha_evento);
      const horaInicio = this._normalizarHoraEvento(eventoBackend.hora_inicio);
      const horaFin = this._normalizarHoraEvento(eventoBackend.hora_fin);
      const tipoNombre = this._extraerNombreTipoEvento(eventoBackend.tipo_evento);

      const eventoMapeado = {
        id: eventoBackend.id_evento,
        titulo: eventoBackend.nombre || eventoBackend.titulo || 'Sin título',
        fecha: fechaNormalizada,
        hora: horaInicio,
        horaInicio: horaInicio,
        horaFin: horaFin,
        lugar: eventoBackend.lugar || '',
        descripcion: eventoBackend.descripcion || '',
        tipo: tipoNombre,
        idTipoEvento: eventoBackend.id_tipo_evento,
        idCategoria: eventoBackend.id_categoria,
        idSesion: eventoBackend.id_sesion,
        // Información adicional
        categoria: eventoBackend.categoria,
        sesion: eventoBackend.sesion,
        tipoEvento: eventoBackend.tipo_evento
      };

      return eventoMapeado;
    } catch (error) {
      console.error('❌ Error al mapear evento:', error, eventoBackend);
      // Return fallback event to prevent application failure
      return this._crearEventoFallback(eventoBackend);
    }
  }

  /**
   * Mapear evento del frontend al formato del backend
   */
  /**
   * Helper: Convierte hora de formato 12 horas a 24 horas
   */
  _convertirHora12A24(match) {
    let horas = Number.parseInt(match[1], 10);
    const minutos = match[2];
    const periodo = match[3].toUpperCase();

    if (periodo.includes('PM') || periodo.includes('P.')) {
      if (horas !== 12) horas += 12;
    } else if (periodo.includes('AM') || periodo.includes('A.')) {
      if (horas === 12) horas = 0;
    }

    return `${horas.toString().padStart(2, '0')}:${minutos}`;
  }

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
      const match = /(\d{1,2}):(\d{2})\s*(AM|PM|a\.m\.|p\.m\.)/i.exec(hora);
      if (match) {
        return this._convertirHora12A24(match);
      }
    }

    // Si no se puede convertir, retornar null
    return null;
  }

  /**
   * Helper: Mapea campos básicos del evento frontend a backend
   */
  _mapearCamposBasicos(eventoFrontend) {
    const eventoBackend = {};
    if (eventoFrontend.titulo !== undefined) {
      eventoBackend.nombre = eventoFrontend.titulo;
    }
    if (eventoFrontend.fecha !== undefined) {
      eventoBackend.fecha_evento = eventoFrontend.fecha;
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
    return eventoBackend;
  }

  /**
   * Helper: Mapea y normaliza horas del evento
   */
  _mapearHoras(eventoFrontend, eventoBackend) {
    if (eventoFrontend.hora !== undefined || eventoFrontend.horaInicio !== undefined) {
      const horaNormalizada = this.normalizarHora(eventoFrontend.horaInicio || eventoFrontend.hora);
      eventoBackend.hora_inicio = horaNormalizada || (eventoFrontend.horaInicio || eventoFrontend.hora);
    }
    if (eventoFrontend.horaFin !== undefined) {
      const horaNormalizada = this.normalizarHora(eventoFrontend.horaFin);
      eventoBackend.hora_fin = horaNormalizada || eventoFrontend.horaFin;
    }
  }

  /**
   * Helper: Agrega valores por defecto para nuevos eventos
   */
  _agregarValoresPorDefecto(eventoBackend) {
    // Si no hay hora_fin, calcular 1 hora después de hora_inicio
    if (!eventoBackend.hora_fin && eventoBackend.hora_inicio) {
      const [horas, minutos] = eventoBackend.hora_inicio.split(':');
      const horaFin = (Number.parseInt(horas, 10) + 1).toString().padStart(2, '0');
      eventoBackend.hora_fin = `${horaFin}:${minutos || '00'}`;
    }
    // Valores por defecto si no existen
    if (!eventoBackend.id_categoria) eventoBackend.id_categoria = 1;
    if (!eventoBackend.id_tipo_evento) eventoBackend.id_tipo_evento = 1;
  }

  /**
   * Mapear evento del frontend al formato del backend
   * NOSONAR: S3776 - Complexity reduced through helper functions extraction
   */
  mapearEventoFrontendABackend(eventoFrontend, esActualizacion = false) {
    const eventoBackend = this._mapearCamposBasicos(eventoFrontend);
    this._mapearHoras(eventoFrontend, eventoBackend);

    // Si no es actualización, agregar valores por defecto para campos requeridos
    if (!esActualizacion) {
      this._agregarValoresPorDefecto(eventoBackend);
    }

    return eventoBackend;
  }

  // ============================================================================
  // MÉTODOS DE VALIDACIÓN
  // ============================================================================

  /**
   * Helper: Valida campos básicos del evento
   */
  _validarCamposBasicos(evento) {
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
    return errores;
  }

  /**
   * Helper: Valida formato de fecha
   */
  _validarFormatoFecha(evento) {
    if (!evento.fecha) return [];
    const fecha = new Date(evento.fecha);
    if (Number.isNaN(fecha.getTime())) {
      return ['La fecha especificada no es válida'];
    }
    return [];
  }

  /**
   * Helper: Valida formato de hora
   */
  _validarFormatoHora(evento) {
    if (!evento.hora && !evento.horaInicio) return [];
    const horaValidar = evento.horaInicio || evento.hora;
    const formatoHora = /^([0-1]?\d|2[0-3]):[0-5]\d(:[0-5]\d)?$/; // NOSONAR: S6353 - Character classes are appropriate here for clarity
    if (!formatoHora.test(horaValidar)) {
      return ['El formato de hora debe ser HH:MM o HH:MM:SS'];
    }
    return [];
  }

  /**
   * Helper: Valida que hora_fin sea mayor que hora_inicio
   */
  _validarRangoHoras(evento) {
    if (!evento.horaInicio || !evento.horaFin) return [];
    // Permitir eventos que cruzan la medianoche (horaFin < horaInicio es válido)
    // Solo rechazar si las horas son iguales (duración cero)
    if (evento.horaFin === evento.horaInicio) {
      return ['La hora de fin debe ser diferente a la hora de inicio'];
    }
    return [];
  }

  /**
   * Validar datos del evento antes de enviar al backend
   * NOSONAR: S3776 - Complexity reduced through helper functions extraction
   */
  validarEvento(evento) {
    // Use concat instead of multiple push() calls for better performance
    return [
      ...this._validarCamposBasicos(evento),
      ...this._validarFormatoFecha(evento),
      ...this._validarFormatoHora(evento),
      ...this._validarRangoHoras(evento)
    ];
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
