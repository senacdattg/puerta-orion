<!-- Componente selector de roles -->
<template>
  <div v-if="rolesDisponibles.length > 1" class="selector-roles">
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
          :disabled="getNombreRolSimple(rol) === 'Usuario' || getNombreRolSimple(rol) === 'usuario'"
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

const rolesDisponibles = computed(() => {
  const roles = authStore.user?.roles || []
  // Normalizar a nombres simples
  return roles.map(r => getNombreRolSimple(r) || r).filter(Boolean)
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
  // Obtener el valor seleccionado
  const nuevoRol = event?.target?.value || rolActivo.value

  // Normalizar el valor del rol
  const rolNormalizado = nuevoRol.trim()

  // Validar el rol antes de procesarlo
  const rolValidado = validarRol(rolNormalizado)
  if (!rolValidado) {
    console.warn('⚠️ Rol inválido detectado, usando rol actual:', rolNormalizado)
    if (event?.target) {
      event.target.value = rolActivo.value
    }
    return
  }

  // Si el rol es "Usuario", no hacer nada y mantener el rol anterior
  if (rolValidado === 'Usuario' || rolValidado === 'usuario') {
    // Restaurar el valor anterior del select
    if (event?.target) {
      event.target.value = rolActivo.value
    }
    return
  }

  // Actualizar el estado con el rol validado y cargar permisos desde el store
  rolActivo.value = rolValidado
  try {
    await authStore.setActiveRole?.(rolValidado)
  } catch (e) {
    console.warn('No se pudo establecer el rol activo en el store:', e)
  }

  // Redirigir según el rol activo a los paneles específicos
  const rutasPorRol = {
    'Deportista': '/deportista/dashboard',
    'Acudiente': '/acudiente/dashboard',
    'Entrenador': '/home',
    'Administrador': '/admin-manager',
    'SuperAdmin': '/admin-manager'
  }

  const ruta = rutasPorRol[rolValidado] || rutasPorRol[rolValidado.toLowerCase()] || '/home'

  // Redirigir siempre al cambiar de rol para asegurar que se muestre el panel correcto
  if (ruta && router.currentRoute.value.path !== ruta) {
    router.replace(ruta).catch((err) => {
      // Si hay un error de navegación, forzar navegación
      console.error('Error de navegación:', err)
      window.location.href = ruta
    })
  }
}

// Observar cambios en los roles del usuario
watch(() => authStore.user?.roles, (nuevosRoles) => {
  if (nuevosRoles && nuevosRoles.length > 0) {
    // Obtener nombres de roles
    const nombresRoles = nuevosRoles.map(r => getNombreRolSimple(r))

    // Si el rol activo no está en los nuevos roles, usar el rol principal
    if (!nombresRoles.includes(rolActivo.value)) {
      const nuevoRolPrincipal = obtenerRolPrincipal(nuevosRoles)
      if (nuevoRolPrincipal && nuevoRolPrincipal !== 'Usuario' && nuevoRolPrincipal !== 'usuario') {
        rolActivo.value = nuevoRolPrincipal
        cambiarRol({ target: { value: nuevoRolPrincipal } })
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
