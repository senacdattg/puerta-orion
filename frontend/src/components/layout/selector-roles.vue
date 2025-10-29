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

  // Retornar el primer rol disponible
  return nombresRoles[0] || 'usuario'
}

const rolesDisponibles = computed(() => {
  if (!authStore.user?.roles) return []
  return authStore.user.roles
})

// Función para inicializar el rol activo
function inicializarRolActivo() {
  const rolGuardado = localStorage.getItem('rolActivo')
  const roles = authStore.user?.roles || []

  // Si hay un rol guardado y está disponible, usarlo
  if (rolGuardado && roles.some(r => getNombreRolSimple(r) === rolGuardado)) {
    return rolGuardado
  }

  // Si no, usar el rol principal (prioridad: Acudiente > Deportista > otros)
  if (roles.length > 0) {
    const rolPrincipal = obtenerRolPrincipal(roles)
    localStorage.setItem('rolActivo', rolPrincipal)
    return rolPrincipal
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

function cambiarRol() {
  localStorage.setItem('rolActivo', rolActivo.value)

  // Redirigir según el rol activo
  const rutasPorRol = {
    'Deportista': '/home',
    'Acudiente': '/home',
    'Entrenador': '/home',
    'Administrador': '/admin-manager',
    'SuperAdmin': '/admin-manager',
    'Usuario': '/home',
    'usuario': '/home'
  }

  const ruta = rutasPorRol[rolActivo.value] || '/home'

  // Solo redirigir si no estamos ya en esa ruta
  if (router.currentRoute.value.path !== ruta) {
    router.push(ruta)
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
      rolActivo.value = nuevoRolPrincipal
      localStorage.setItem('rolActivo', nuevoRolPrincipal)

      // Redirigir solo si es necesario
      cambiarRol()
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
