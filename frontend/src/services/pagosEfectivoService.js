/**
 * Servicio para manejo de pagos en efectivo
 * Implementa sistema de verificación y auditoría
 */

class PagosEfectivoService {
  // Prefer class field declaration over 'this' assignment in constructor
  baseURL = '/api/pagos-efectivo';

  constructor() {
    this.pagos = this.cargarPagosLocales();
  }

  /**
   * Registrar un nuevo pago en efectivo
   */
  async registrarPago(datosPago) {
    try {
      // Validaciones de seguridad
      this.validarDatosPago(datosPago);

      // Generar datos adicionales de seguridad
      const pagoCompleto = {
        ...datosPago,
        timestamp: Date.now(),
        hash: this.generarHash(datosPago),
        ubicacion: await this.obtenerUbicacion(),
        dispositivo: this.obtenerInfoDispositivo(),
        administrador: this.obtenerInfoAdministrador()
      };

      // Guardar localmente como respaldo
      this.guardarPagoLocal(pagoCompleto);

      // Enviar al servidor
      const response = await fetch(this.baseURL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(pagoCompleto)
      });

      if (!response.ok) {
        throw new Error('Error al registrar pago en servidor');
      }

      const resultado = await response.json();

      // Generar comprobante
      this.generarComprobante(pagoCompleto);

      return {
        success: true,
        pago: pagoCompleto,
        comprobante: resultado.comprobante
      };

    } catch (error) {
      console.error('Error al registrar pago:', error);

      // Guardar en cola de reintentos
      this.guardarEnColaReintentos(datosPago);

      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Verificar un pago por código de recibo
   */
  async verificarPago(codigoRecibo) {
    try {
      // Buscar localmente primero
      const pagoLocal = this.buscarPagoLocal(codigoRecibo);

      if (pagoLocal) {
        return {
          success: true,
          pago: pagoLocal,
          fuente: 'local'
        };
      }

      // Buscar en servidor
      const response = await fetch(`${this.baseURL}/verificar/${codigoRecibo}`);

      if (!response.ok) {
        throw new Error('Pago no encontrado');
      }

      const resultado = await response.json();

      // Guardar localmente para futuras consultas
      this.guardarPagoLocal(resultado.pago);

      return {
        success: true,
        pago: resultado.pago,
        fuente: 'servidor'
      };

    } catch (error) {
      console.error('Error al verificar pago:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Obtener historial de pagos en efectivo
   */
  async obtenerHistorial(filtros = {}) {
    try {
      // Filtrar pagos locales
      let pagosFiltrados = this.filtrarPagosLocales(filtros);

      // Si hay filtros específicos, buscar en servidor
      if (Object.keys(filtros).length > 0) {
        const response = await fetch(`${this.baseURL}/historial?${new URLSearchParams(filtros)}`);

        if (response.ok) {
          const resultado = await response.json();
          pagosFiltrados = [...pagosFiltrados, ...resultado.pagos];
        }
      }

      return {
        success: true,
        pagos: pagosFiltrados,
        total: pagosFiltrados.length
      };

    } catch (error) {
      console.error('Error al obtener historial:', error);
      return {
        success: false,
        error: error.message,
        pagos: this.pagos // Retornar solo pagos locales
      };
    }
  }

  /**
   * Generar reporte de auditoría
   */
  async generarReporteAuditoria(fechaInicio, fechaFin) {
    try {
      const response = await fetch(`${this.baseURL}/auditoria`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fechaInicio, fechaFin })
      });

      if (!response.ok) {
        throw new Error('Error al generar reporte');
      }

      const resultado = await response.json();

      return {
        success: true,
        reporte: resultado.reporte
      };

    } catch (error) {
      console.error('Error al generar reporte:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Validaciones de seguridad
   */
  validarDatosPago(datosPago) {
    const camposRequeridos = [
      'mensualidadId', 'tipoPago', 'monto', 'recibidoDe',
      'documentoPagador', 'telefonoPagador'
    ];

    camposRequeridos.forEach(campo => {
      if (!datosPago[campo]) {
        throw new Error(`Campo requerido: ${campo}`);
      }
    });

    if (datosPago.monto <= 0) {
      throw new Error('Monto debe ser mayor a 0');
    }

    if (datosPago.monto > 10000000) { // 10 millones
      throw new Error('Monto excede el límite permitido');
    }
  }

  /**
   * Generar hash de seguridad
   */
  generarHash(datos) {
    const datosString = JSON.stringify(datos) + Date.now();
    let hash = 0;

    for (let i = 0; i < datosString.length; i++) {
      // Prefer String#codePointAt() over String#charCodeAt() for better Unicode support
      const char = datosString.codePointAt(i) || 0;
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convertir a entero de 32 bits
    }

    return Math.abs(hash).toString(16);
  }

  /**
   * Obtener ubicación del dispositivo
   * Geolocation es necesario para auditoría y trazabilidad de pagos en efectivo.
   * Requisito de seguridad para registrar la ubicación donde se realizó el pago.
   */
  async obtenerUbicacion() {
    if (!navigator.geolocation) {
      return null
    }

    return new Promise((resolve) => {
      // NOSONAR: S5604 - Geolocation is required for audit and traceability of cash payments
      // This is a security requirement to register the location where the payment was made
      navigator.geolocation.getCurrentPosition( // NOSONAR: S5604
        position => {
          resolve({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            precision: position.coords.accuracy
          });
        },
        () => {
          resolve(null);
        },
        { timeout: 10000, enableHighAccuracy: false }
      );
    });
  }

  /**
   * Obtener información del dispositivo
   */
  obtenerInfoDispositivo() {
    // Extraer plataforma del userAgent sin usar APIs deprecadas
    const userAgent = navigator.userAgent
    let plataforma = 'unknown'

    if (userAgent.includes('Win')) {
      plataforma = 'Windows'
    } else if (userAgent.includes('Mac')) {
      plataforma = 'Mac'
    } else if (userAgent.includes('Linux')) {
      plataforma = 'Linux'
    } else if (userAgent.includes('Android')) {
      plataforma = 'Android'
    } else if (userAgent.includes('iPhone') || userAgent.includes('iPad')) {
      plataforma = 'iOS'
    }

    return {
      userAgent: userAgent,
      plataforma: plataforma,
      idioma: navigator.language,
      cookies: navigator.cookieEnabled,
      timestamp: Date.now()
    };
  }

  /**
   * Obtener información del administrador
   */
  obtenerInfoAdministrador() {
    // En una implementación real, esto vendría del sistema de autenticación
    return {
      id: 'admin_001',
      nombre: 'Administrador',
      rol: 'admin',
      sesion: Date.now()
    };
  }

  /**
   * Guardar pago localmente
   */
  guardarPagoLocal(pago) {
    this.pagos.push(pago);
    localStorage.setItem('pagosEfectivo', JSON.stringify(this.pagos));
  }

  /**
   * Cargar pagos locales
   */
  cargarPagosLocales() {
    try {
      const pagos = localStorage.getItem('pagosEfectivo');
      return pagos ? JSON.parse(pagos) : [];
    } catch (error) {
      console.error('Error al cargar pagos locales:', error);
      return [];
    }
  }

  /**
   * Buscar pago local por código
   */
  buscarPagoLocal(codigo) {
    return this.pagos.find(pago => pago.codigoRecibo === codigo);
  }

  /**
   * Filtrar pagos locales
   */
  filtrarPagosLocales(filtros) {
    return this.pagos.filter(pago => {
      if (filtros.fechaInicio && new Date(pago.fecha) < new Date(filtros.fechaInicio)) {
        return false;
      }
      if (filtros.fechaFin && new Date(pago.fecha) > new Date(filtros.fechaFin)) {
        return false;
      }
      if (filtros.administrador && pago.administrador.id !== filtros.administrador) {
        return false;
      }
      return true;
    });
  }

  /**
   * Guardar en cola de reintentos
   */
  guardarEnColaReintentos(pago) {
    try {
      const cola = JSON.parse(localStorage.getItem('colaReintentos') || '[]');
      cola.push({
        ...pago,
        intentos: 0,
        timestamp: Date.now()
      });
      localStorage.setItem('colaReintentos', JSON.stringify(cola));
    } catch (error) {
      console.error('Error al guardar en cola de reintentos:', error);
    }
  }

  /**
   * Generar comprobante
   */
  generarComprobante(pago) {
    // Aquí se implementaría la generación del comprobante físico
    console.log('Generando comprobante para:', pago.codigoRecibo);
  }

  /**
   * Sincronizar pagos pendientes
   */
  async sincronizarPagosPendientes() {
    try {
      const cola = JSON.parse(localStorage.getItem('colaReintentos') || '[]');
      const pagosExitosos = [];

      for (const pago of cola) {
        if (pago.intentos < 3) {
          try {
            const resultado = await this.registrarPago(pago);
            if (resultado.success) {
              pagosExitosos.push(pago);
            } else {
              pago.intentos++;
            }
          } catch {
            pago.intentos++;
          }
        }
      }

      // Remover pagos exitosos de la cola
      const nuevaCola = cola.filter(pago => !pagosExitosos.includes(pago));
      localStorage.setItem('colaReintentos', JSON.stringify(nuevaCola));

      return {
        success: true,
        sincronizados: pagosExitosos.length,
        pendientes: nuevaCola.length
      };

    } catch (error) {
      console.error('Error al sincronizar pagos pendientes:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
}

// Exportar instancia única
export default new PagosEfectivoService();


