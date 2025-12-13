/**
 * Utility functions for formatting data
 * Provides reusable formatting functions following DRY principles
 */

/**
 * Formats a number as Colombian Peso currency
 * @param {number|string} valor - Value to format
 * @returns {string} Formatted currency string
 */
export function formatoCOP(valor) {
  try {
    return new Intl.NumberFormat('es-CO').format(Number(valor))
  } catch {
    return String(valor)
  }
}

/**
 * Gets month name from ISO date string
 * @param {string} fechaISO - ISO date string
 * @returns {string} Month name in Spanish
 */
export function nombreMes(fechaISO) {
  if (!fechaISO) {
    return ''
  }
  const d = new Date(fechaISO)
  return d.toLocaleDateString('es-CO', { month: 'long' }).replace(/^./, m => m.toUpperCase())
}

/**
 * Gets person name from object with multiple possible name fields
 * @param {Object} persona - Person object
 * @param {number|string} fallbackId - Fallback ID if name not found
 * @returns {string} Person name
 */
export function obtenerNombrePersonaDesdeObjeto(persona, fallbackId) {
  if (!persona) {
    return `Persona #${fallbackId}`
  }

  // Try multiple name conventions
  const posibles = [
    persona.nombre,
    persona.nombres,
    persona.nombre_persona,
    persona.nombre_completo,
    persona.full_name,
    persona.display_name
  ].filter(Boolean)

  if (posibles.length > 0) {
    return String(posibles[0])
  }

  // Combine nombre + apellido if they exist
  const nombre = persona.primer_nombre || persona.nombre1 || persona.nombre
  const apellido = persona.primer_apellido || persona.apellido1 || persona.apellidos || persona.apellido

  if (nombre && apellido) {
    return `${nombre} ${apellido}`
  }
  if (nombre) {
    return String(nombre)
  }

  return `Persona #${fallbackId}`
}

