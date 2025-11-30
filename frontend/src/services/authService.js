/**
 * Servicio de autenticación para el frontend
 * Maneja todas las operaciones relacionadas con autenticación
 */

import { API_CONFIG } from '@/config/environment'

class AuthService {
  constructor() {
    Object.defineProperty(this, 'baseURL', {
      enumerable: true,
      configurable: false,
      get() {
        return API_CONFIG.baseURL
      }
    })
  }

  /**
   * Iniciar sesión
   */
  async login(credentials) {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error de autenticación')
      }

      return { success: true, ...data.data }
    } catch (error) {
      console.error('Error en login:', error)
      return { success: false, error: error.message || 'Error de conexión' }
    }
  }

  /**
   * Registrar nuevo usuario
   */
  async register(userData) {
    try {
      console.log('📤 Enviando registro a:', `${this.baseURL}/api/auth/register`)
      console.log('📦 Datos enviados:', JSON.stringify(userData, null, 2))

      // Crear un AbortController para timeout
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000) // 30 segundos timeout

      const response = await fetch(`${this.baseURL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      console.log('📥 Respuesta recibida - Status:', response.status, response.statusText)

      // Verificar si la respuesta es JSON válido
      let data
      const contentType = response.headers.get('content-type')
      if (contentType?.includes('application/json')) {
        data = await response.json()
        console.log('📦 Datos recibidos:', data)
      } else {
        const text = await response.text()
        console.error('❌ Respuesta no es JSON:', text)
        throw new Error(`Respuesta inválida del servidor: ${text.substring(0, 100)}`)
      }

      if (!response.ok) {
        const errorMsg = data.error || data.message || 'Error de registro'
        console.error('❌ Error en registro:', errorMsg)
        throw new Error(errorMsg)
      }

      console.log('✅ Registro exitoso')
      return { success: true, data: data.data }
    } catch (error) {
      console.error('❌ Error en registro:', error)
      // Si es un error de abort (timeout)
      if (error.name === 'AbortError') {
        return { success: false, error: 'La petición tardó demasiado. El servidor puede estar sobrecargado o hay un problema de conexión.' }
      }
      // Si es un error de red, dar un mensaje más claro
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        return { success: false, error: 'Error de conexión. Verifica que el servidor esté funcionando.' }
      }
      return { success: false, error: error.message || 'Error de conexión' }
    }
  }

  /**
   * Cerrar sesión
   */
  async logout(token) {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      })

      const data = await response.json()

      if (!response.ok) {
        // Silenciar errores 401 (token inválido/expirado)
        if (response.status !== 401) {
          throw new Error(data.error || 'Error al cerrar sesión')
        }
      }

      return data
    } catch (error) {
      // Silenciar errores relacionados con tokens inválidos
      if (!error.message.includes('Token inválido') && !error.message.includes('expirado') && !error.message.includes('401')) {
        console.error('Error en logout:', error)
      }
      throw error
    }
  }

  /**
   * Obtener perfil del usuario autenticado
   */
  async getProfile() {
    try {
      const token = localStorage.getItem('token')

      if (!token) {
        throw new Error('No hay token de autenticación')
      }

      const response = await fetch(`${this.baseURL}/api/auth/perfil`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error al obtener perfil')
      }

      return data
    } catch (error) {
      console.error('Error al obtener perfil:', error)
      throw error
    }
  }

  /**
   * Verificar si un token es válido
   */
  async verifyToken(token) {
    try {
      // Validar que el token no esté vacío o sea inválido
      if (!token || token === 'null' || token === 'undefined' || token.trim() === '') {
        this.clearAuthData()
        return { success: false, message: 'No hay token' }
      }

      const response = await fetch(`${this.baseURL}/api/auth/verify-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token })
      })

      // Verificar si la respuesta es JSON válido
      let data
      try {
        data = await response.json()
      } catch {
        // Silenciar errores de parse cuando es un 401 esperado
        if (response.status === 401) {
          return { success: false, message: 'Token inválido o expirado' }
        }
        this.clearAuthData()
        return { success: false, message: 'Respuesta del servidor inválida' }
      }

      if (!response.ok) {
        // Si el token es inválido o expirado, limpiar datos locales sin hacer throw
        if (response.status === 401) {
          this.clearAuthData()
          return { success: false, message: 'Token inválido o expirado' }
        }
        return { success: false, message: data.error || 'Error al verificar token' }
      }

      return data
    } catch (error) {
      // Silenciar errores de conexión durante verificación de token
      if (!error.message.includes('Failed to fetch')) {
        console.warn('Error al verificar token:', error.message)
      }
      return { success: false, message: 'Error al verificar token' }
    }
  }

  /**
   * Obtener token del localStorage
   */
  getToken() {
    return localStorage.getItem('token')
  }

  /**
   * Verificar si hay un token guardado
   */
  hasToken() {
    return !!this.getToken()
  }

  /**
   * Limpiar datos de autenticación del localStorage
   */
  clearAuthData() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  /**
   * Obtener permisos específicos del usuario autenticado (todos los roles)
   */
  async getUserPermissions() {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('No hay token de autenticación')
      }

      const response = await fetch(`${this.baseURL}/api/auth/user-permissions`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error al obtener permisos')
      }

      return { success: true, ...data.data }
    } catch (error) {
      console.error('Error obteniendo permisos:', error)
      return { success: false, error: error.message || 'Error de conexión' }
    }
  }

  /**
   * Obtener permisos de un rol específico
   */
  async getRolePermissions(roleName) {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('No hay token de autenticación')
      }

      const response = await fetch(`${this.baseURL}/api/auth/role-permissions?role_name=${encodeURIComponent(roleName)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })

      const data = await response.json()

      if (!response.ok) {
        // Si es 401, el token expiró, no lanzar error, solo retornar fallo
        if (response.status === 401) {
          console.warn('⚠️ Token expirado al obtener permisos del rol')
          return { success: false, error: 'Token expirado', expired: true }
        }
        throw new Error(data.error || 'Error al obtener permisos del rol')
      }

      return { success: true, ...data.data }
    } catch (error) {
      // No loguear errores de token expirado como errores críticos
      if (!error.message.includes('expirado') && !error.message.includes('401')) {
        console.error('Error obteniendo permisos del rol:', error)
      }
      return { success: false, error: error.message || 'Error de conexión' }
    }
  }

  /**
   * Verificar estado del perfil del usuario
   */
  async verificarEstadoPerfil() {
    try {
      const token = localStorage.getItem('token')

      if (!token) {
        throw new Error('No hay token de autenticación')
      }

      const response = await fetch(`${this.baseURL}/api/auth/perfil/estado`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error al verificar estado del perfil')
      }

      return data
    } catch (error) {
      console.error('Error al verificar estado del perfil:', error)
      throw error
    }
  }

  /**
   * Obtener el detalle completo del perfil del usuario autenticado
   * Incluye información completa por rol (deportista, acudiente, etc.)
   */
  async getProfileDetail() {
    try {
      const token = localStorage.getItem('token')

      if (!token) {
        throw new Error('No hay token de autenticación')
      }

      const response = await fetch(`${this.baseURL}/api/auth/perfil/detalle`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      })

      const data = await response.json()

      if (!response.ok) {
        // Si es 401, el token expiró, retornar error controlado
        if (response.status === 401) {
          console.warn('⚠️ Token expirado al obtener detalle del perfil')
          return {
            success: false,
            error: 'Sesión inactiva o expirada',
            expired: true
          }
        }

        console.error('❌ Error en getProfileDetail:', {
          status: response.status,
          statusText: response.statusText,
          data
        })
        return {
          success: false,
          error: data.error || `Error al obtener detalle del perfil (${response.status})`
        }
      }

      // Si hay un warning, mostrarlo pero no fallar
      if (data.warning) {
        console.warn('⚠️ Advertencia al obtener detalle:', data.warning)
      }

      console.log('✅ Detalle del perfil obtenido:', data)
      return { success: true, ...data }
    } catch (error) {
      // No loguear errores de token expirado como errores críticos
      if (!error.message.includes('expirado') && !error.message.includes('401')) {
        console.error('Error al obtener detalle del perfil:', error)
      }
      return {
        success: false,
        error: error.message || 'Error al obtener detalle del perfil'
      }
    }
  }

  /**
    * Completar perfil como deportista
    */
   async completarPerfilDeportista(datosDeportista) {
     try {
       const token = localStorage.getItem('token')

       if (!token) {
         throw new Error('No hay token de autenticación')
       }

       // Asegurar que los campos opcionales estén presentes con valores por defecto
       const datosCompletos = {
         id_categoria: datosDeportista.id_categoria || datosDeportista.categoria,
        peso: datosDeportista.peso ? Number.parseFloat(datosDeportista.peso) : null,
        altura: datosDeportista.altura ? Number.parseFloat(datosDeportista.altura) : null,
         fecha_nacimiento: datosDeportista.fecha_nacimiento || datosDeportista.fechaNacimiento,
         id_tipo_sanguineo: datosDeportista.id_tipo_sanguineo || datosDeportista.tipoSangre,
         id_ciudad_recidencia: datosDeportista.id_ciudad_recidencia || datosDeportista.ciudad,
         id_eps: datosDeportista.id_eps || datosDeportista.eps,
         alergias: datosDeportista.alergias || '',
         medicamentos: datosDeportista.medicamentos || '',
         condiciones_medicas: datosDeportista.condiciones_medicas || datosDeportista.condicionesMedicas || '',
         institucion_educativa: datosDeportista.institucion_educativa || datosDeportista.institucionEducativa || '',
         grado: datosDeportista.grado || '',
         jornada: datosDeportista.jornada || ''
       }

       const response = await fetch(`${this.baseURL}/api/auth/perfil/completar-deportista`, {
         method: 'POST',
         headers: {
           'Authorization': `Bearer ${token}`,
           'Content-Type': 'application/json',
         },
         body: JSON.stringify(datosCompletos)
       })

       const data = await response.json()

       if (!response.ok) {
         throw new Error(data.error || 'Error al completar perfil como deportista')
       }

       return { success: true, data: data.data, message: data.message }
     } catch (error) {
       console.error('Error al completar perfil como deportista:', error)
       return { success: false, error: error.message || 'Error de conexión' }
     }
   }

  /**
   * Asociar acudiente existente con un deportista
   */
  async asociarAcudienteDeportista(datosAsociacion) {
    try {
      const token = localStorage.getItem('token')

      if (!token) {
        throw new Error('No hay token de autenticación')
      }

      // Extraer id_deportista de los datos y construir la URL correcta
      const idDeportista = datosAsociacion.id_deportista
      if (!idDeportista) {
        throw new Error('El id_deportista es requerido')
      }

      // Construir el body sin el id_deportista ya que va en la URL
      const body = {
        id_parentesco: datosAsociacion.id_parentesco,
        es_responsable: datosAsociacion.es_responsable
      }

      const response = await fetch(`${this.baseURL}/api/deportistas/${idDeportista}/acudientes`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      })

      // Verificar si la respuesta es JSON antes de parsear
      const contentType = response.headers.get('content-type')
      let data = {}

      if (contentType?.includes('application/json')) {
        data = await response.json()
      } else {
        const text = await response.text()
        throw new Error(`Error ${response.status}: ${response.statusText}. ${text.substring(0, 100)}`)
      }

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Error al asociar acudiente con deportista')
      }

      return { success: true, data: data.data, message: data.message }
    } catch (error) {
      console.error('Error al asociar acudiente con deportista:', error)
      return { success: false, error: error.message || 'Error de conexión' }
    }
  }

  /**
   * Completar perfil como acudiente
   */
  async completarPerfilAcudiente(datosAcudiente = {}) {
     try {
       const token = localStorage.getItem('token')

       if (!token) {
         throw new Error('No hay token de autenticación')
       }

       // Preparar datos del acudiente (ahora solo se requieren: id_deportista, id_parentesco, es_responsable)
       const datosCompletos = {
         id_deportista: datosAcudiente.id_deportista,
         id_parentesco: datosAcudiente.id_parentesco,
         es_responsable: datosAcudiente.es_responsable ?? false
       }

       const response = await fetch(`${this.baseURL}/api/auth/perfil/completar-acudiente`, {
         method: 'POST',
         headers: {
           'Authorization': `Bearer ${token}`,
           'Content-Type': 'application/json',
         },
         body: JSON.stringify(datosCompletos)
       })

       const data = await response.json()

       if (!response.ok) {
         throw new Error(data.error || 'Error al completar perfil como acudiente')
       }

       return { success: true, data: data.data, message: data.message }
     } catch (error) {
       console.error('Error al completar perfil como acudiente:', error)
       return { success: false, error: error.message || 'Error de conexión' }
     }
   }

  /**
   * Solicitar recuperación de contraseña
   */
  async forgotPassword(email) {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || data.error || 'Error al solicitar recuperación')
      }

      return { success: true, message: data.message || 'Se ha enviado un correo con las instrucciones para restablecer tu contraseña' }
    } catch (error) {
      console.error('Error en forgotPassword:', error)
      return { success: false, error: error.message || 'Error de conexión' }
    }
  }

  /**
   * Restablecer contraseña con token
   */
  async resetPassword(token, newPassword, confirmPassword) {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          new_password: newPassword,
          confirm_password: confirmPassword
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || data.error || 'Error al restablecer contraseña')
      }

      return { success: true, message: data.message || 'Contraseña restablecida exitosamente' }
    } catch (error) {
      console.error('Error en resetPassword:', error)
      return { success: false, error: error.message || 'Error de conexión' }
    }
  }

  /**
   * Actualizar datos de usuario
   */
  async updateUser(idUsuario, datosPersona = {}, datosUsuario = {}) {
    try {
      const token = localStorage.getItem('token')

      if (!token) {
        throw new Error('No hay token de autenticación')
      }

      const body = {}
      if (Object.keys(datosPersona).length > 0) {
        body.datos_persona = datosPersona
      }
      if (Object.keys(datosUsuario).length > 0) {
        body.datos_usuario = datosUsuario
      }

      if (Object.keys(body).length === 0) {
        throw new Error('Debe proporcionar al menos datos_persona o datos_usuario')
      }

      const response = await fetch(`${this.baseURL}/api/usuarios/${idUsuario}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error al actualizar usuario')
      }

      return { success: true, data: data.data, message: data.message }
    } catch (error) {
      console.error('Error al actualizar usuario:', error)
      return { success: false, error: error.message || 'Error de conexión' }
    }
  }

  /**
   * Obtener roles disponibles y paneles autorizados para el usuario autenticado
   */
  async getRoleOptions() {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('No hay token de autenticación')
      }

      const response = await fetch(`${this.baseURL}/api/auth/roles/opciones`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      const data = await response.json()

      if (!response.ok) {
        if (response.status === 401) {
          return { success: false, error: 'Sesión expirada', expired: true }
        }
        throw new Error(data.error || 'Error al obtener opciones de roles')
      }

      return { success: true, data: data.data }
    } catch (error) {
      console.error('Error al obtener opciones de roles:', error)
      return { success: false, error: error.message || 'Error de conexión' }
    }
  }

  /**
   * Cambiar el rol activo del usuario autenticado
   */
  async activateRole(roleName) {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('No hay token de autenticación')
      }

      const response = await fetch(`${this.baseURL}/api/auth/roles/activar`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rol: roleName })
      })

      const data = await response.json()

      if (!response.ok) {
        if (response.status === 401) {
          return { success: false, error: 'Sesión expirada', expired: true }
        }
        throw new Error(data.error || 'Error al cambiar rol activo')
      }

      return { success: true, data: data.data }
    } catch (error) {
      console.error('Error al cambiar rol activo:', error)
      return { success: false, error: error.message || 'Error de conexión' }
    }
  }
}

// Exportar instancia única
export default new AuthService()
