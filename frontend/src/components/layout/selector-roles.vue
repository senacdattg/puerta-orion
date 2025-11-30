<!-- Componente selector de roles -->
<template>
  <div v-if="rolesDisponibles.length > 0" class="selector-roles">
    <div class="selector-roles-content">
      <label for="select-rol-activo">
        <i class="fas fa-user-shield"></i>
        Vista actual:
      </label>
      <select
        id="select-rol-activo"
        v-model="rolActivo"
        @change="cambiarRol"
        class="select-rol"
      >
        <option
          v-for="rol in rolesDisponibles"
          :key="getNombreRolSimple(rol)"
          :value="getNombreRolSimple(rol)"
        >
          {{ getNombreRol(rol) }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

// Función para obtener el nombre real del rol (sin emoji) para comparaciones
function getNombreRolSimple(rol) {
  if (typeof rol === 'string') return rol
  if (typeof rol === 'object' && rol !== null && rol.nombre_rol) {
    return rol.nombre_rol
  }
  return ''
}

// Función para obtener el rol principal (prioridad: Admin > Entrenador > Acudiente > Deportista)
function obtenerRolPrincipal(roles) {
  if (!roles || roles.length === 0) return 'usuario'

  // Aceptar tanto objetos como strings
  const nombresRoles = roles.map(rol => getNombreRolSimple(rol) || rol)

  if (nombresRoles.includes('SuperAdmin')) return 'Administrador'
  if (nombresRoles.includes('Administrador')) return 'Administrador'
  if (nombresRoles.includes('Entrenador')) return 'Entrenador'
  if (nombresRoles.includes('Acudiente')) return 'Acudiente'
  if (nombresRoles.includes('Deportista')) return 'Deportista'

  const primero = nombresRoles.find(r => r && r !== 'Usuario' && r !== 'usuario')
  return primero || 'usuario'
}

// Calcular edad del deportista basándose en fecha_nacimiento
const edadDeportista = computed(() => {
  try {
    // Buscar fecha_nacimiento en diferentes lugares del store
    const userDetail = authStore.userDetail
    const deportista = userDetail?.deportista || authStore.user?.deportista

    if (!deportista) return null

    const fechaNacimiento = deportista.fecha_nacimiento

    if (!fechaNacimiento) return null

    // Si fecha_nacimiento es solo el año (número)
    const añoActual = new Date().getFullYear()
    const añoNacimiento = typeof fechaNacimiento === 'number' ? fechaNacimiento : new Date(fechaNacimiento).getFullYear()
    const edad = añoActual - añoNacimiento

    return edad
  } catch (error) {
    console.error('Error al calcular edad:', error)
    return null
  }
})

// Verificar si el deportista es mayor de edad (>= 18 años)
const esMayorDeEdad = computed(() => {
  const edad = edadDeportista.value
  if (edad === null) return false // Si no se puede calcular la edad, por defecto no mostrar
  return edad >= 18
})

// Verificar si el usuario es deportista
const esDeportista = computed(() => {
  const roles = authStore.user?.roles || []
  const nombresRoles = roles.map(r => getNombreRolSimple(r) || r).filter(Boolean)
  return nombresRoles.includes('Deportista')
})

// Verificar si el usuario ya tiene el rol Acudiente
const yaEsAcudiente = computed(() => {
  const roles = authStore.user?.roles || []
  const nombresRoles = roles.map(r => getNombreRolSimple(r) || r).filter(Boolean)
  return nombresRoles.includes('Acudiente')
})

const rolesDisponibles = computed(() => {
  const roles = authStore.user?.roles || []
  // Normalizar a nombres simples
  const nombresRoles = roles.map(r => getNombreRolSimple(r) || r).filter(Boolean)

  // Priorizar rolesSelector del backend si existe, pero asegurar que "Usuario" siempre aparezca si el usuario lo tiene
  const selectorEntries = Object.entries(authStore.rolesSelector || {}).filter(([, visible]) => visible)
  if (selectorEntries.length > 0) {
    const rolesDelSelector = selectorEntries.map(([role]) => role)
    // Asegurar que "Usuario" esté incluido si el usuario lo tiene
    const tieneUsuario = nombresRoles.some(r => r === 'Usuario' || r === 'usuario')
    if (tieneUsuario && !rolesDelSelector.some(r => r === 'Usuario' || r === 'usuario')) {
      rolesDelSelector.push('Usuario')
    }
    return rolesDelSelector
  }

  // Si no hay rolesSelector del backend, usar los roles del usuario directamente
  // El backend ya maneja la lógica de visibilidad, así que mostramos todos los roles que tiene
  return nombresRoles
})

// Lista de roles válidos para validación
const ROLES_VALIDOS = new Set(['Deportista', 'Acudiente', 'Entrenador', 'Administrador', 'SuperAdmin', 'Usuario', 'usuario'])

// Función para validar y limpiar el rol guardado
function validarRol(rol) {
  if (!rol || typeof rol !== 'string') return null
  const rolLimpio = rol.trim()
  // Validar que el rol sea uno de los válidos o esté en la lista de roles válidos
  if (ROLES_VALIDOS.has(rolLimpio)) {
    return rolLimpio
  }
  // Si el rol contiene caracteres corruptos o no es válido, retornar null
  return null
}

// Eliminado: lógica antigua basada en localStorage (sustituida por authStore.activeRole)

// Obtener el rol activo: preferir store.activeRole o localStorage, si no, elegir por prioridad
// IMPORTANTE: Si hay un rol guardado en localStorage, usarlo (fue seleccionado explícitamente por el usuario)
const rolActivoInicial = authStore.activeRole || localStorage.getItem('activeRole') || obtenerRolPrincipal(rolesDisponibles.value)
const rolActivo = ref(rolActivoInicial)

// Función para obtener el nombre del rol (maneja tanto strings como objetos)
function getNombreRol(rol) {
  // Si el rol es un string, usarlo directamente
  if (typeof rol === 'string') {
    const nombres = {
      'Deportista': '🏃 Deportista',
      'Acudiente': '👨‍👩‍👧 Acudiente',
      'Entrenador': '⚽ Entrenador',
      'Administrador': '👤 Administrador',
      'SuperAdmin': '👑 Super Admin',
      'Usuario': '👤 Usuario',
      'usuario': '👤 Usuario'
    }
    return nombres[rol] || rol
  }

  // Si el rol es un objeto, extraer el nombre_rol
  if (typeof rol === 'object' && rol !== null && rol.nombre_rol) {
    const nombre = rol.nombre_rol
    const nombres = {
      'Deportista': '🏃 Deportista',
      'Acudiente': '👨‍👩‍👧 Acudiente',
      'Entrenador': '⚽ Entrenador',
      'Administrador': '👤 Administrador',
      'SuperAdmin': '👑 Super Admin',
      'Usuario': '👤 Usuario',
      'usuario': '👤 Usuario'
    }
    return nombres[nombre] || nombre
  }

  return JSON.stringify(rol)
}

async function cambiarRol(event) {
  console.log('🔄 Cambiando rol, evento:', event)

  // Obtener el valor seleccionado
  const nuevoRol = event?.target?.value || rolActivo.value
  console.log('📝 Nuevo rol seleccionado:', nuevoRol)

  // Normalizar el valor del rol
  const rolNormalizado = nuevoRol?.trim() || nuevoRol

  // Validar el rol antes de procesarlo
  const rolValidado = validarRol(rolNormalizado)
  if (!rolValidado) {
    console.warn('⚠️ Rol inválido detectado, usando rol actual:', rolNormalizado)
    if (event?.target) {
      event.target.value = rolActivo.value
    }
    return
  }

  console.log('✅ Rol validado:', rolValidado)

  const previousRole = authStore.activeRole || rolActivo.value

  // Actualizar el estado con el rol validado PRIMERO
  rolActivo.value = rolValidado

  try {
    // Pasar true como segundo parámetro para forzar el cambio cuando el usuario selecciona explícitamente
    const result = await authStore.setActiveRole?.(rolValidado, true)
    if (result?.success === false) {
      throw new Error(result.error || 'No se pudo actualizar el rol activo')
    }
    console.log('✅ Rol establecido en el store:', rolValidado)
  } catch (e) {
    console.warn('⚠️ No se pudo establecer el rol activo en el store:', e)
    rolActivo.value = previousRole
    if (event?.target) {
      event.target.value = previousRole
    }
    return
  }

  // Redirigir siempre al panel de inicio (/home) cuando se cambia de rol
  const ruta = '/home'
  console.log('🗺️ Ruta a navegar:', ruta)
  console.log('📍 Ruta actual:', router.currentRoute.value.path)

  // Redirigir siempre al cambiar de rol al panel de inicio
  if (router.currentRoute.value.path === ruta) {
    console.log('ℹ️ Ya estamos en /home, recargando la página para actualizar el contexto del rol')
    // Si ya estamos en /home, forzar recarga para actualizar el contexto
    globalThis.location.reload()
    return;
  }
  try {
    await router.replace(ruta)
    console.log('✅ Redirección exitosa a:', ruta)
  } catch (err) {
    console.error('❌ Error de navegación:', err)
    // Si hay un error de navegación, forzar navegación
    globalThis.location.href = ruta
  }
}

// Helper functions to reduce cognitive complexity in watch
function _cargarDetalleDeportista() {
  if (esDeportista.value && !authStore.userDetail) {
    authStore.loadUserProfileDetail()
  }
}

function _obtenerNombresRoles(roles) {
  return roles.map(r => {
    if (typeof r === 'string') return r
    if (r.nombre_rol) return r.nombre_rol
    return String(r)
  })
}

function _verificarRolGuardadoValido(rolActivoGuardado, rolesUsuario) {
  const nombresRoles = _obtenerNombresRoles(rolesUsuario);
  return nombresRoles.some(r => 
    r === rolActivoGuardado || r.toLowerCase() === rolActivoGuardado.toLowerCase()
  );
}

function _restaurarRolGuardado(rolActivoGuardado, rolActivoActual) {
  const rolesSonIguales = rolActivoActual === rolActivoGuardado;
  if (rolesSonIguales) {
    console.log(`✅ [selector-roles] Rol activo "${rolActivoGuardado}" fue seleccionado explícitamente, NO cambiando automáticamente`)
  } else {
    console.log(`✅ [selector-roles] Restaurando rol activo guardado: ${rolActivoGuardado} (fue seleccionado explícitamente, NO cambiando)`)
    rolActivo.value = rolActivoGuardado
    const rolStoreEsDiferente = authStore.activeRole !== rolActivoGuardado;
    if (rolStoreEsDiferente) {
      // Pasar true para forzar el cambio cuando se restaura un rol guardado explícitamente
      authStore.setActiveRole?.(rolActivoGuardado, true)
    }
  }
}

function _manejarRolGuardado(rolActivoGuardado) {
  const rolActivoActual = rolActivo.value || authStore.activeRole
  const rolesUsuario = authStore.user?.roles || []
  const rolGuardadoEsValido = _verificarRolGuardadoValido(rolActivoGuardado, rolesUsuario)
  
  console.log(`🔍 [selector-roles] Verificando rol guardado: ${rolActivoGuardado}, válido: ${rolGuardadoEsValido}, actual: ${rolActivoActual}`)
  
  if (rolGuardadoEsValido) {
    _restaurarRolGuardado(rolActivoGuardado, rolActivoActual)
    return true // Indica que se manejó el rol guardado
  }
  return false
}

function _debeCambiarRolAutomaticamente(rolActivoGuardado) {
  return !rolActivoGuardado && 
         esDeportista.value && 
         !esMayorDeEdad.value && 
         (rolActivo.value === 'Usuario' || rolActivo.value === 'usuario')
}

function _cambiarRolAutomatico() {
  const roles = authStore.user?.roles || []
  const nombresRoles = roles.map(r => getNombreRolSimple(r) || r).filter(Boolean)
  const rolesDisponibles = nombresRoles.filter(rol => rol !== 'Usuario' && rol !== 'usuario')

  if (rolesDisponibles.length > 0) {
    const nuevoRol = obtenerRolPrincipal(roles)
    if (nuevoRol && nuevoRol !== 'Usuario' && nuevoRol !== 'usuario') {
      console.log(`🔄 [selector-roles] Cambiando rol de "Usuario" a "${nuevoRol}" (usuario menor de edad, NO hay rol guardado)`)
      rolActivo.value = nuevoRol
      authStore.setActiveRole?.(nuevoRol)
    }
  }
}

// Observar cambios en los roles del usuario y el detalle del usuario
// Refactored to reduce cognitive complexity by extracting helper functions
watch(() => [rolesDisponibles.value, authStore.userDetail], () => {
  _cargarDetalleDeportista()

  // PROTECCIÓN CRÍTICA: NUNCA cambiar automáticamente el rol activo si el usuario lo seleccionó explícitamente
  // Verificar PRIMERO si hay un rol activo guardado en localStorage (indica selección explícita del usuario)
  const rolActivoGuardado = localStorage.getItem('activeRole')
  
  // Si hay un rol guardado en localStorage, significa que el usuario lo seleccionó explícitamente
  // NO cambiar el rol en NINGÚN caso, independientemente de la edad, roles disponibles, etc.
  if (rolActivoGuardado) {
    const rolManejado = _manejarRolGuardado(rolActivoGuardado)
    if (rolManejado) {
      return // NO cambiar el rol si fue seleccionado explícitamente
    }
  }
  
  // Solo cambiar automáticamente si NO hay rol guardado (no fue seleccionado explícitamente)
  // Y el usuario es deportista menor de edad con rol "Usuario"
  if (_debeCambiarRolAutomaticamente(rolActivoGuardado)) {
    _cambiarRolAutomatico()
  }
}, { immediate: true })

// Observar cambios en los roles disponibles
watch(() => rolesDisponibles.value, (nuevosRoles) => {
  if (nuevosRoles && nuevosRoles.length > 0) {
    const nombresRoles = nuevosRoles.map(r => getNombreRolSimple(r) || r)

    // Solo cambiar el rol activo si no está en los roles disponibles Y no hay uno guardado válido
    const rolActivoGuardado = authStore.activeRole || localStorage.getItem('activeRole')
    const todosLosRolesUsuario = authStore.user?.roles || []
    const nombresTodosRoles = todosLosRolesUsuario.map(r => {
      if (typeof r === 'string') return r
      if (r.nombre_rol) return r.nombre_rol
      return String(r)
    })

    // Verificar si el rol activo guardado está en todos los roles del usuario (no solo en rolesDisponibles)
    const rolGuardadoEsValido = rolActivoGuardado && nombresTodosRoles.some(r => 
      r === rolActivoGuardado || r.toLowerCase() === rolActivoGuardado.toLowerCase()
    )

    if (!nombresRoles.includes(rolActivo.value)) {
      // Si el rol activo guardado es válido (está en los roles del usuario), mantenerlo
      if (rolGuardadoEsValido && rolActivoGuardado === rolActivo.value) {
        console.log(`✅ Manteniendo rol activo guardado en selector-roles: ${rolActivoGuardado} (no está en rolesDisponibles pero es válido)`)
        return // No cambiar el rol
      }

      // Verificar si el rol fue seleccionado explícitamente por el usuario (está en localStorage)
      const rolEnLocalStorage = localStorage.getItem('activeRole')
      if (rolEnLocalStorage && rolEnLocalStorage === rolActivo.value) {
        console.log(`✅ [selector-roles] Rol activo "${rolEnLocalStorage}" fue seleccionado explícitamente, NO cambiando aunque no esté en rolesDisponibles`)
        return // NO cambiar el rol si fue seleccionado explícitamente
      }

      // Si no hay rol guardado válido y no fue seleccionado explícitamente, cambiar al rol principal
      const nuevoRolPrincipal = obtenerRolPrincipal(nuevosRoles)
      if (nuevoRolPrincipal) {
        console.log(`🔄 [selector-roles] Cambiando rol activo a rol principal: ${nuevoRolPrincipal} (rol actual ${rolActivo.value} no está disponible y no fue seleccionado explícitamente)`)
        rolActivo.value = nuevoRolPrincipal
        // NO llamar a setActiveRole aquí para evitar cambios automáticos no deseados
        // Solo actualizar la referencia local
      }
    }
  }
}, { immediate: true })

// Mantener sincronía si el rol activo en el store cambia desde otra parte
// PERO solo si el cambio no fue causado por una selección explícita del usuario
watch(() => authStore.activeRole, (nuevo) => {
  if (nuevo && nuevo !== rolActivo.value) {
    // Verificar si hay un rol guardado en localStorage que fue seleccionado explícitamente
    const rolGuardado = localStorage.getItem('activeRole')
    if (rolGuardado && rolGuardado === rolActivo.value) {
      // El rol actual fue seleccionado explícitamente, NO cambiarlo aunque el store sugiera otro
      console.log(`✅ [selector-roles] Rol activo "${rolGuardado}" fue seleccionado explícitamente, NO sincronizando con store (store sugiere: ${nuevo})`)
      return
    }
    // Si no hay rol guardado o es diferente, sincronizar con el store
    console.log(`🔄 [selector-roles] Sincronizando rol activo con store: ${nuevo}`)
    rolActivo.value = nuevo
  }
})

onMounted(async () => {
  // Solo refrescar opciones de rol si no hay rolesSelector Y no hay rol activo guardado
  // Esto evita sobrescribir el rol activo que el usuario seleccionó explícitamente
  const tieneRolActivo = authStore.activeRole || localStorage.getItem('activeRole')
  if (!Object.keys(authStore.rolesSelector || {}).length && !tieneRolActivo) {
    await authStore.refreshRoleOptions?.()
  } else if (!Object.keys(authStore.rolesSelector || {}).length && tieneRolActivo) {
    // Hay rol activo guardado pero no hay rolesSelector, refrescar solo el selector sin cambiar el rol
    console.log(`🔄 Refrescando rolesSelector sin cambiar rol activo: ${tieneRolActivo}`)
    await authStore.refreshRoleOptions?.()
    // Restaurar el rol activo si se cambió
    if (authStore.activeRole !== tieneRolActivo) {
      const rolesUsuario = authStore.user?.roles || []
      const nombresRoles = rolesUsuario.map(r => {
        if (typeof r === 'string') return r
        if (r.nombre_rol) return r.nombre_rol
        return String(r)
      })
      if (nombresRoles.some(r => r === tieneRolActivo || r.toLowerCase() === tieneRolActivo.toLowerCase())) {
        console.log(`🔄 Restaurando rol activo después de refresh: ${tieneRolActivo}`)
        await authStore.setActiveRole?.(tieneRolActivo)
      }
    }
  }
})
</script>

