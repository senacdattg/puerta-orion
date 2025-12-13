/**
 * Utility functions for MercadoPago payment integration
 * Provides reusable payment functions following DRY principles
 */

import { API_CONFIG } from '@/config/environment'
import Swal from 'sweetalert2'
import { extraerMensajeError } from './error-handling'

/**
 * Creates payment preference with MercadoPago
 * @param {Object} params - Payment parameters
 * @param {number} params.id_mensualidad - Monthly payment ID
 * @param {string} params.nombre_pagador - Payer name
 * @param {string} params.email_pagador - Payer email
 * @param {string} [params.numero_documento] - Payer document number
 * @param {string} [params.tipo_documento] - Document type
 * @param {string} [params.tipo_pago] - Payment type (default: 'mensualidad')
 * @returns {Promise<{success: boolean, url?: string, error?: string}>} Payment result
 */
export async function crearPreferenciaMercadoPago(params) {
  const {
    id_mensualidad,
    nombre_pagador,
    email_pagador,
    numero_documento,
    tipo_documento,
    tipo_pago = 'mensualidad'
  } = params

  try {
    const base = API_CONFIG.baseURL || ''
    const token = localStorage.getItem('token') || ''

    const resp = await fetch(`${base}/api/mercadopago/crear-preferencia`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        tipo_pago,
        id_mensualidad,
        nombre_pagador,
        email_pagador,
        numero_documento,
        tipo_documento
      })
    })

    const text = await resp.text()
    let json
    try {
      json = text ? JSON.parse(text) : {}
    } catch {
      json = {}
    }

    if (!resp.ok || !json.success) {
      const msg = extraerMensajeError(json) || text || 'No se pudo crear la preferencia'
      return { success: false, error: msg }
    }

    const url = json.init_point || json.preference_url || json.initPoint || json.url || json.sandbox_init_point
    if (!url) {
      return { success: false, error: 'Preferencia creada sin URL de inicio' }
    }

    return { success: true, url }
  } catch (error) {
    const errorMsg = extraerMensajeError(error)
    return { success: false, error: errorMsg }
  }
}

/**
 * Initiates payment with MercadoPago and redirects to payment page
 * @param {Object} params - Payment parameters
 * @param {Function} [onError] - Optional error callback
 * @returns {Promise<void>}
 */
export async function iniciarPagoMercadoPago(params, onError) {
  const result = await crearPreferenciaMercadoPago(params)

  if (!result.success) {
    const errorMsg = result.error || 'No se pudo iniciar el pago'
    await Swal.fire({
      icon: 'error',
      title: 'No se pudo iniciar el pago',
      text: errorMsg
    })
    if (onError) {
      onError(errorMsg)
    }
    return
  }

  if (result.url) {
    globalThis.location.href = result.url
  } else {
    await Swal.fire({
      icon: 'error',
      title: 'Sin enlace de pago',
      text: 'No se obtuvo link de pago.'
    })
    if (onError) {
      onError('No se obtuvo link de pago')
    }
  }
}

