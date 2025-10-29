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

// Función para obtener el rol principal (prioridad: Acudiente > Deportista > otros)
function obtenerRolPrincipal(roles) {
  if (!roles || roles.length === 0) return 'usuario'

  // Convertir roles a nombres simples
  const nombresRoles = roles.map(rol => getNombreRolSimple(rol))

  // Prioridad de roles
  if (nombresRoles.includes('Acudiente')) return 'Acudiente'
  if (nombresRoles.includes('Deportista')) return 'Deportista'
  if (nombresRoles.includes('Administrador')) return 'Administrador'
  if (nombresRoles.includes('Entrenador')) return 'Entrenador'

  // Retornar el primer rol disponible (excluyendo Usuario)
  const rolSinUsuario = nombresRoles.find(r => r !== 'Usuario' && r !== 'usuario')
  return rolSinUsuario || nombresRoles[0] || 'usuario'
}

const rolesDisponibles = computed(() => {
  if (!authStore.user?.roles) return []
  return authStore.user.roles
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

// Función para inicializar el rol activo
function inicializarRolActivo() {
  const rolGuardadoRaw = localStorage.getItem('rolActivo')
  const rolGuardado = validarRol(rolGuardadoRaw)
  const roles = authStore.user?.roles || []

  // Si hay un rol guardado corrupto o inválido, limpiarlo
  if (rolGuardadoRaw && !rolGuardado) {
    console.warn('🧹 Limpiando rol corrupto de localStorage:', rolGuardadoRaw)
    localStorage.removeItem('rolActivo')
  }

  // Si hay un rol guardado válido y está disponible y no es Usuario, usarlo
  if (rolGuardado && roles.some(r => getNombreRolSimple(r) === rolGuardado)) {
    // Si el rol guardado es Usuario, buscar otro rol disponible
    if (rolGuardado === 'Usuario' || rolGuardado === 'usuario') {
      const rolPrincipal = obtenerRolPrincipal(roles)
      if (rolPrincipal && rolPrincipal !== 'Usuario' && rolPrincipal !== 'usuario') {
        localStorage.setItem('rolActivo', rolPrincipal)
        return rolPrincipal
      }
    }
    return rolGuardado
  }

  // Si no, usar el rol principal (prioridad: Acudiente > Deportista > otros)
  if (roles.length > 0) {
    const rolPrincipal = obtenerRolPrincipal(roles)
    if (rolPrincipal && rolPrincipal !== 'Usuario' && rolPrincipal !== 'usuario') {
      localStorage.setItem('rolActivo', rolPrincipal)
      return rolPrincipal
    }
  }

  return 'usuario'
}

// Obtener el rol activo del localStorage o el rol principal
const rolActivo = ref(inicializarRolActivo())

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

function cambiarRol(event) {
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

  // Actualizar el estado con el rol validado
  rolActivo.value = rolValidado
  localStorage.setItem('rolActivo', rolValidado)

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
    router.push(ruta).catch((err) => {
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
        localStorage.setItem('rolActivo', nuevoRolPrincipal)

        // Redirigir solo si es necesario
        cambiarRol({ target: { value: nuevoRolPrincipal } })
      }
    }
  }
}, { immediate: true })
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
