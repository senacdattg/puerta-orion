/**
 * Utility functions for error handling and message extraction
 * Provides reusable error message extraction following DRY principles
 */

/**
 * Extracts and formats error messages in a readable way
 * @param {any} error - Error object, string, or response
 * @returns {string} Formatted error message
 */
export function extraerMensajeError(error) {
  if (!error) {
    return 'No se pudo completar la operación. Por favor, intenta nuevamente.'
  }

  // If it's a string, return it directly
  if (typeof error === 'string') {
    return error
  }

  // If it's an object with message
  if (error.message) {
    return error.message
  }

  // If it's an object with error property
  if (error.error) {
    return typeof error.error === 'string' ? error.error : JSON.stringify(error.error)
  }

  // If it's an object with details
  if (error.details) {
    return typeof error.details === 'string' ? error.details : JSON.stringify(error.details)
  }

  // If it's an object, try to convert it to readable string
  if (typeof error === 'object') {
    try {
      const errorStr = JSON.stringify(error)
      // If JSON is too long, return generic message
      if (errorStr.length > 200) {
        return 'Error al procesar la solicitud. Verifica que todos los datos sean correctos.'
      }
      return errorStr
    } catch {
      return 'Error desconocido. Por favor, intenta nuevamente.'
    }
  }

  return 'Error desconocido. Por favor, intenta nuevamente.'
}

