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
import { ref, computed, watch } from 'vue'
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

  // Si el usuario es deportista:
  // - Si es menor de edad: ocultar "Usuario"
  // - Si es mayor de edad pero ya es acudiente: ocultar "Usuario"
  // - Si es mayor de edad y NO es acudiente: mostrar "Usuario" (para que pueda registrarse como acudiente)
  if (esDeportista.value) {
    // Si es menor de edad, ocultar "Usuario"
    if (!esMayorDeEdad.value) {
      return nombresRoles.filter(rol => rol !== 'Usuario' && rol !== 'usuario')
    }
    // Si es mayor de edad pero ya es acudiente, ocultar "Usuario"
    if (yaEsAcudiente.value) {
      return nombresRoles.filter(rol => rol !== 'Usuario' && rol !== 'usuario')
    }
    // Si es mayor de edad y NO es acudiente, mostrar "Usuario"
    return nombresRoles
  }

  // Si no es deportista, mostrar todos los roles
  return nombresRoles
})

// Lista de roles válidos para validación
const ROLES_VALIDOS = ['Deportista', 'Acudiente', 'Entrenador', 'Administrador', 'SuperAdmin', 'Usuario', 'usuario']

// Función para validar y limpiar el rol guardado
function validarRol(rol) {
  if (!rol || typeof rol !== 'string') return null
  const rolLimpio = rol.trim()
  // Validar que el rol sea uno de los válidos o esté en la lista de roles válidos
  if (ROLES_VALIDOS.includes(rolLimpio)) {
    return rolLimpio
  }
  // Si el rol contiene caracteres corruptos o no es válido, retornar null
  return null
}

// Eliminado: lógica antigua basada en localStorage (sustituida por authStore.activeRole)

// Obtener el rol activo: preferir store.activeRole, si no, elegir por prioridad
const rolActivo = ref(authStore.activeRole || obtenerRolPrincipal(rolesDisponibles.value))

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

  // Actualizar el estado con el rol validado PRIMERO
  rolActivo.value = rolValidado

  try {
    await authStore.setActiveRole?.(rolValidado)
    console.log('✅ Rol establecido en el store:', rolValidado)
  } catch (e) {
    console.warn('⚠️ No se pudo establecer el rol activo en el store:', e)
  }

  // Redirigir siempre al panel de inicio (/home) cuando se cambia de rol
  const ruta = '/home'
  console.log('🗺️ Ruta a navegar:', ruta)
  console.log('📍 Ruta actual:', router.currentRoute.value.path)

  // Redirigir siempre al cambiar de rol al panel de inicio
  if (router.currentRoute.value.path !== ruta) {
    try {
      await router.replace(ruta)
      console.log('✅ Redirección exitosa a:', ruta)
    } catch (err) {
      console.error('❌ Error de navegación:', err)
      // Si hay un error de navegación, forzar navegación
      window.location.href = ruta
    }
  } else {
    console.log('ℹ️ Ya estamos en /home, recargando la página para actualizar el contexto del rol')
    // Si ya estamos en /home, forzar recarga para actualizar el contexto
    window.location.reload()
  }
}

// Observar cambios en los roles del usuario y el detalle del usuario
watch(() => [authStore.user?.roles, authStore.userDetail], () => {
  // Cargar detalle si no está cargado y el usuario es deportista
  if (esDeportista.value && !authStore.userDetail) {
    authStore.loadUserProfileDetail()
  }

  // Si el usuario es deportista menor de edad y tiene el rol "Usuario" activo, cambiarlo automáticamente
  if (esDeportista.value && !esMayorDeEdad.value && (rolActivo.value === 'Usuario' || rolActivo.value === 'usuario')) {
    const roles = authStore.user?.roles || []
    const nombresRoles = roles.map(r => getNombreRolSimple(r) || r).filter(Boolean)
    const rolesDisponibles = nombresRoles.filter(rol => rol !== 'Usuario' && rol !== 'usuario')

    if (rolesDisponibles.length > 0) {
      const nuevoRol = obtenerRolPrincipal(roles)
      if (nuevoRol && nuevoRol !== 'Usuario' && nuevoRol !== 'usuario') {
        rolActivo.value = nuevoRol
        authStore.setActiveRole?.(nuevoRol)
      }
    }
  }
}, { immediate: true })

// Observar cambios en los roles del usuario
watch(() => authStore.user?.roles, (nuevosRoles) => {
  if (nuevosRoles && nuevosRoles.length > 0) {
    // Obtener nombres de roles
    const nombresRoles = nuevosRoles.map(r => getNombreRolSimple(r))

    // Si el rol activo no está en los nuevos roles, usar el rol principal
    if (!nombresRoles.includes(rolActivo.value)) {
      const nuevoRolPrincipal = obtenerRolPrincipal(nuevosRoles)
      if (nuevoRolPrincipal) {
        rolActivo.value = nuevoRolPrincipal
        // No cambiar automáticamente el rol, solo actualizar el valor
        // El usuario debe cambiar manualmente desde el selector
      }
    }
  }
}, { immediate: true })

// Mantener sincronía si el rol activo en el store cambia desde otra parte
watch(() => authStore.activeRole, (nuevo) => {
  if (nuevo && nuevo !== rolActivo.value) {
    rolActivo.value = nuevo
  }
})
</script>

<style scoped>
.selector-roles {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  padding: 12px 16px;
  margin: 10px 0;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.selector-roles-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selector-roles-content label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-weight: 600;
  font-size: 0.95rem;
  white-space: nowrap;
}

.selector-roles-content label i {
  font-size: 1.1rem;
}

.select-rol {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid white;
  border-radius: 6px;
  background: white;
  color: #333;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.select-rol:hover {
  border-color: #f0f8ff;
  background: #f0f8ff;
}

.select-rol:focus {
  outline: none;
  border-color: #ffd700;
  box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.2);
}

.select-rol option {
  padding: 8px;
  font-weight: 600;
}

.select-rol option:disabled {
  color: #999;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Responsive */
@media (max-width: 768px) {
  .selector-roles {
    padding: 10px 12px;
  }

  .selector-roles-content {
    flex-direction: column;
    gap: 8px;
  }

  .selector-roles-content label {
    width: 100%;
    justify-content: center;
  }

  .select-rol {
    width: 100%;
  }
}
</style>
