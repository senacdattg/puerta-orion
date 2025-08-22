// Servicio para manejar la lógica de negocio del calendario
// Principio SRP: Responsabilidad única de gestionar eventos del calendario

class CalendarioService {
  constructor() {
    this.eventos = this.cargarEventosDesdeStorage();
  }

  // Cargar eventos desde localStorage
  cargarEventosDesdeStorage() {
    const eventosGuardados = localStorage.getItem('eventosCalendario');
    if (eventosGuardados) {
      return JSON.parse(eventosGuardados);
    }

    // Eventos por defecto
    return [
      {
        id: 1,
        titulo: 'Entrenamiento Fútbol',
        tipo: 'Entrenamiento',
        lugar: 'Sede Principal - SENA',
        hora: '15:00',
        descripcion: 'Entrenamiento de técnica y táctica',
        fecha: '2025-07-15'
      },
      {
        id: 2,
        titulo: 'Partido Amistoso',
        tipo: 'Evento',
        lugar: 'Cancha Interna Parque U. Salitre',
        hora: '16:00',
        descripcion: 'Partido amistoso contra equipo local',
        fecha: '2025-07-20'
      },
      {
        id: 3,
        titulo: 'Competencia Regional',
        tipo: 'Competencia',
        lugar: 'Estadio Metropolitano',
        hora: '14:00',
        descripcion: 'Torneo regional de fútbol juvenil',
        fecha: '2025-07-25'
      }
    ];
  }

  // Guardar eventos en localStorage
  guardarEventosEnStorage() {
    localStorage.setItem('eventosCalendario', JSON.stringify(this.eventos));
  }

  // Obtener todos los eventos
  obtenerTodosLosEventos() {
    return this.eventos;
  }

  // Obtener eventos por fecha
  obtenerEventosPorFecha(fecha) {
    return this.eventos.filter(evento => evento.fecha === fecha);
  }

  // Validar datos del evento
  validarEvento(evento) {
    const errores = [];

    if (!evento.titulo || evento.titulo.trim().length < 3) {
      errores.push('El título debe tener al menos 3 caracteres');
    }

    if (!evento.tipo) {
      errores.push('Debe seleccionar un tipo de evento');
    }

    if (!evento.lugar || evento.lugar.trim().length < 3) {
      errores.push('El lugar debe tener al menos 3 caracteres');
    }

    if (!evento.hora) {
      errores.push('Debe especificar una hora');
    }

    if (!evento.fecha) {
      errores.push('Debe especificar una fecha');
    }

    return errores;
  }

  // Crear nuevo evento
  crearEvento(evento) {
    const nuevoEvento = {
      ...evento,
      id: Date.now(),
      fechaCreacion: new Date().toISOString()
    };

    this.eventos.push(nuevoEvento);
    this.guardarEventosEnStorage();
    return nuevoEvento;
  }

  // Actualizar evento existente
  actualizarEvento(id, datosActualizados) {
    const indice = this.eventos.findIndex(evento => evento.id === id);
    if (indice !== -1) {
      this.eventos[indice] = {
        ...this.eventos[indice],
        ...datosActualizados,
        fechaModificacion: new Date().toISOString()
      };
      this.guardarEventosEnStorage();
      return this.eventos[indice];
    }
    return null;
  }

  // Eliminar evento
  eliminarEvento(id) {
    const indice = this.eventos.findIndex(evento => evento.id === id);
    if (indice !== -1) {
      const eventoEliminado = this.eventos.splice(indice, 1)[0];
      this.guardarEventosEnStorage();
      return eventoEliminado;
    }
    return null;
  }



    // Validar datos del evento
  validarEvento(evento) {
    const errores = [];

    if (!evento.titulo || evento.titulo.trim().length < 3) {
      errores.push('El título debe tener al menos 3 caracteres');
    }

    if (!evento.tipo) {
      errores.push('Debe seleccionar un tipo de evento');
    }

    if (!evento.lugar || evento.lugar.trim().length < 3) {
      errores.push('El lugar debe tener al menos 3 caracteres');
    }

    if (!evento.hora) {
      errores.push('Debe especificar una hora');
    }

    if (!evento.fecha) {
      errores.push('Debe especificar una fecha');
    }

    // Validar que la fecha sea válida
    if (evento.fecha) {
      const fecha = new Date(evento.fecha);
      if (isNaN(fecha.getTime())) {
        errores.push('La fecha especificada no es válida');
      }
    }

    return errores;
  }


}

export default new CalendarioService();
