<template>
    <table class="tabla-usuarios">
      <thead>
        <tr class="">
          <th class="">Usuario</th>
          <th class="">Rol</th>
          <th class="">Estado</th>
          <th class="">Acción</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td colspan="4" style="text-align: center; padding: 20px;">
            Cargando usuarios...
          </td>
        </tr>
        <tr v-else-if="error">
          <td colspan="4" style="text-align: center; padding: 20px; color: red;">
            Error: {{ error }}
          </td>
        </tr>
        <tr
          v-else
          v-for="(user, index) in filteredUsers"
          :key="user.id_usuario"
          :data-user-id="user.id_usuario"
          :class="[
            'user-row',
            index % 2 === 0 ? 'user-row--even' : 'user-row--odd'
          ]"
          @click="verDetalleUsuario(user)"
        >
          <td class="user-name">{{ user.usuario }}</td>
          <td class="user-role">
            <div class="roles-badges">
              <span
                v-for="rol in user.roles"
                :key="rol.id_rol"
                :class="['badge', roleColor(rol.nombre_rol)]"
              >
                {{ rol.nombre_rol }}
              </span>
              <span v-if="!user.roles || user.roles.length === 0" class="badge badge-none">Sin rol</span>
            </div>
          </td>
          <td class="user-status" @click.stop>
            <button
              @click="toggleEstadoUsuario(user)"
              :disabled="loading || user.id_usuario === currentUserId"
              :class="['btn-estado', user.estado ? 'btn-activo' : 'btn-inactivo']"
              :title="user.estado ? 'Usuario activo - Click para desactivar' : 'Usuario inactivo - Click para activar'"
            >
              <i :class="user.estado ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
              {{ user.estado ? 'Activo' : 'Inactivo' }}
            </button>
          </td>
          <td class="user-action" @click.stop>
            <div class="roles-checkboxes">
              <label
                v-for="rol in rolesFiltrados"
                :key="rol.value"
                class="role-checkbox-label"
                :class="{ 'role-checkbox-checked': userRolesIds(user).includes(rol.value) }"
                :title="rol.label"
              >
                <input
                  type="checkbox"
                  :value="rol.value"
                  :checked="userRolesIds(user).includes(rol.value)"
                  @change="handleRoleChange(user, rol.value, $event.target.checked)"
                  :disabled="loading"
                  class="role-checkbox"
                />
                <span class="role-checkbox-text">{{ rol.label }}</span>
              </label>
            </div>
          </td>
        </tr>
      </tbody>
      </table>

      <!-- Botón para cargar más usuarios -->
      <div v-if="!loading && !error && hasMore" class="cargar-mas-container">
        <button @click="cargarMasUsuarios" class="btn-cargar-mas">
          <i class="fas fa-chevron-down"></i>
          Cargar más ({{ filteredUsersCompletos.length - usuariosVisibles }} restantes)
        </button>
      </div>

      <!-- Mensaje cuando no hay más usuarios -->
      <div v-if="!loading && !error && !hasMore && filteredUsersCompletos.length > 0" class="sin-mas-usuarios">
        <p>Mostrando todos los {{ filteredUsersCompletos.length }} usuarios</p>
      </div>

  <!-- Modal de Detalle de Usuario -->
  <div v-if="mostrarModalDetalle" class="modal-overlay-detalle" @click.self="cerrarModalDetalle">
    <div class="modal-content-detalle" @click.stop>
      <div class="modal-header-detalle">
        <h2 class="modal-title-detalle">
          <i class="fas fa-user"></i>
          Detalle de Usuario
        </h2>
        <button class="btn-cerrar-modal" @click="cerrarModalDetalle">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="modal-body-detalle">
        <!-- Loading state -->
        <div v-if="cargandoDetalle" class="loading-detalle">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Cargando información del usuario...</p>
        </div>

        <!-- Error state -->
        <div v-else-if="errorDetalle" class="error-detalle">
          <i class="fas fa-exclamation-circle"></i>
          <p>{{ errorDetalle }}</p>
        </div>

        <!-- User details -->
        <div v-else-if="usuarioDetalle" class="detalle-usuario">
          <!-- Información Personal -->
          <div class="seccion-detalle">
            <h3 class="titulo-seccion">
              <i class="fas fa-id-card"></i>
              Información Personal
            </h3>
            <div class="info-grid-detalle">
              <div class="info-item-detalle">
                <label>Nombre Completo:</label>
                <span>{{ usuarioDetalle.persona?.nombre_completo || `${usuarioDetalle.persona?.primer_nombre || ''} ${usuarioDetalle.persona?.primer_apellido || ''}`.trim() || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <label>Primer Nombre:</label>
                <span>{{ usuarioDetalle.persona?.primer_nombre || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <label>Segundo Nombre:</label>
                <span>{{ usuarioDetalle.persona?.segundo_nombre || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <label>Primer Apellido:</label>
                <span>{{ usuarioDetalle.persona?.primer_apellido || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <label>Segundo Apellido:</label>
                <span>{{ usuarioDetalle.persona?.segundo_apellido || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <label>Documento:</label>
                <span>{{ usuarioDetalle.persona?.documento || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <label>Correo Electrónico:</label>
                <span>{{ usuarioDetalle.persona?.correo_electronico || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <label>Teléfono:</label>
                <span>{{ usuarioDetalle.persona?.telefono || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <label>Dirección:</label>
                <span>{{ usuarioDetalle.persona?.direccion || 'N/A' }}</span>
              </div>
            </div>
          </div>

          <!-- Información de Usuario -->
          <div class="seccion-detalle">
            <h3 class="titulo-seccion">
              <i class="fas fa-user-circle"></i>
              Información de Usuario
            </h3>
            <div class="info-grid-detalle info-grid-usuario">
              <div class="info-item-detalle">
                <label>Username:</label>
                <span>{{ usuarioDetalle.usuario?.usuario || usuarioDetalle.usuario || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <label>ID Usuario:</label>
                <span>{{ usuarioDetalle.usuario?.id_usuario || usuarioDetalle.id_usuario || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <label>Estado:</label>
                <span :class="['badge-estado', usuarioDetalle.usuario?.estado !== false ? 'activo' : 'inactivo']">
                  {{ usuarioDetalle.usuario?.estado !== false ? 'Activo' : 'Inactivo' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Roles -->
          <div class="seccion-detalle">
            <h3 class="titulo-seccion">
              <i class="fas fa-user-shield"></i>
              Roles Asignados
            </h3>
            <div class="roles-container-detalle">
              <span
                v-for="rol in usuarioDetalle.roles || []"
                :key="rol.id_rol"
                :class="['badge-detalle', roleColor(rol.nombre_rol)]"
              >
                {{ rol.nombre_rol }}
              </span>
              <span v-if="!usuarioDetalle.roles || usuarioDetalle.roles.length === 0" class="badge-detalle badge-none">
                Sin roles asignados
              </span>
            </div>
          </div>

          <!-- Acciones -->
          <div class="seccion-acciones-detalle">
            <h3 class="titulo-seccion">
              <i class="fas fa-cog"></i>
              Acciones
            </h3>
            <div class="botones-acciones-detalle">
              <button
                @click="toggleEstadoUsuario(usuarioDetalle)"
                :disabled="loading || usuarioDetalle.usuario?.id_usuario === currentUserId || usuarioDetalle.id_usuario === currentUserId"
                :class="['btn-accion-detalle', usuarioDetalle.usuario?.estado !== false ? 'btn-desactivar' : 'btn-activar']"
                style="flex: 0 0 250px !important; width: 250px !important; min-width: 250px !important; max-width: 250px !important; height: 48px !important; min-height: 48px !important; max-height: 48px !important; padding: 14px 24px !important; box-sizing: border-box !important; display: flex !important; align-items: center !important; justify-content: center !important;"
              >
                <i :class="usuarioDetalle.usuario?.estado !== false ? 'fas fa-ban' : 'fas fa-check-circle'"></i>
                {{ usuarioDetalle.usuario?.estado !== false ? 'Desactivar' : 'Activar' }} Usuario
              </button>

              <button
                @click="abrirModalEdicion(usuarioDetalle)"
                :disabled="loading"
                class="btn-accion-detalle btn-editar"
                style="flex: 0 0 250px !important; width: 250px !important; min-width: 250px !important; max-width: 250px !important; height: 48px !important; min-height: 48px !important; max-height: 48px !important; padding: 14px 24px !important; box-sizing: border-box !important; display: flex !important; align-items: center !important; justify-content: center !important;"
              >
                <i class="fas fa-edit"></i>
                Editar Usuario
              </button>

              <button
                @click="abrirGestionRoles(usuarioDetalle)"
                :disabled="loading"
                class="btn-accion-detalle btn-roles"
                style="flex: 0 0 250px !important; width: 250px !important; min-width: 250px !important; max-width: 250px !important; height: 48px !important; min-height: 48px !important; max-height: 48px !important; padding: 14px 24px !important; box-sizing: border-box !important; display: flex !important; align-items: center !important; justify-content: center !important;"
              >
                <i class="fas fa-user-tag"></i>
                Gestionar Roles
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal de Edición -->
  <div v-if="mostrarModalEdicion" class="modal-overlay-detalle" @click.self="cerrarModalEdicion">
    <div class="modal-content-detalle" @click.stop>
      <div class="modal-header-detalle">
        <h2 class="modal-title-detalle">
          <i class="fas fa-edit"></i>
          Editar Usuario
        </h2>
        <button class="btn-cerrar-modal" @click="cerrarModalEdicion">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body-detalle">
        <div v-if="errorEdicion" class="error-detalle" style="color:#ef4444;">
          <i class="fas fa-exclamation-circle"></i>
          <p>{{ errorEdicion }}</p>
        </div>
        <div class="info-grid-detalle">
          <div class="info-item-detalle">
            <label>Username</label>
            <input v-model="formularioEdicion.datos_usuario.usuario" type="text" class="control-input" />
          </div>
          <div class="info-item-detalle">
            <label>Primer Nombre</label>
            <input v-model="formularioEdicion.datos_persona.primer_nombre" type="text" class="control-input" />
          </div>
          <div class="info-item-detalle">
            <label>Segundo Nombre</label>
            <input v-model="formularioEdicion.datos_persona.segundo_nombre" type="text" class="control-input" />
          </div>
          <div class="info-item-detalle">
            <label>Primer Apellido</label>
            <input v-model="formularioEdicion.datos_persona.primer_apellido" type="text" class="control-input" />
          </div>
          <div class="info-item-detalle">
            <label>Segundo Apellido</label>
            <input v-model="formularioEdicion.datos_persona.segundo_apellido" type="text" class="control-input" />
          </div>
          <div class="info-item-detalle">
            <label>Documento</label>
            <input v-model="formularioEdicion.datos_persona.documento" type="text" class="control-input" />
          </div>
          <div class="info-item-detalle">
            <label>Correo</label>
            <input v-model="formularioEdicion.datos_persona.correo_electronico" type="email" class="control-input" />
          </div>
          <div class="info-item-detalle">
            <label>Teléfono</label>
            <input v-model="formularioEdicion.datos_persona.telefono" type="text" class="control-input" />
          </div>
          <div class="info-item-detalle">
            <label>Dirección</label>
            <input v-model="formularioEdicion.datos_persona.direccion" type="text" class="control-input" />
          </div>
        </div>
        <div class="botones-acciones-detalle" style="margin-top:20px;">
          <button class="btn-accion-detalle btn-editar" :disabled="guardandoEdicion" @click="guardarEdicion">
            <i class="fas" :class="guardandoEdicion ? 'fa-spinner fa-spin' : 'fa-save'"></i>
            {{ guardandoEdicion ? 'Guardando...' : 'Guardar Cambios' }}
          </button>
          <button class="btn-accion-detalle btn-desactivar" :disabled="guardandoEdicion" @click="cerrarModalEdicion">
            <i class="fas fa-times"></i>
            Cancelar
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal de Gestión de Roles -->
  <div v-if="mostrarModalRoles" class="modal-overlay-detalle" @click.self="cerrarModalRoles">
    <div class="modal-content-detalle" @click.stop>
      <div class="modal-header-detalle">
        <h2 class="modal-title-detalle">
          <i class="fas fa-user-tag"></i>
          Gestionar Roles
        </h2>
        <button class="btn-cerrar-modal" @click="cerrarModalRoles">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body-detalle">
        <div v-if="errorRoles" class="error-detalle" style="color:#ef4444;">
          <i class="fas fa-exclamation-circle"></i>
          <p>{{ errorRoles }}</p>
        </div>

        <div v-if="usuarioParaRoles" class="info-usuario-roles">
          <div class="usuario-info-roles">
            <h3>Usuario: {{ usuarioParaRoles.usuario?.usuario || usuarioParaRoles.usuario || 'N/A' }}</h3>
            <p class="usuario-nombre-completo">
              {{ usuarioParaRoles.persona?.nombre_completo ||
                 `${usuarioParaRoles.persona?.primer_nombre || ''} ${usuarioParaRoles.persona?.primer_apellido || ''}`.trim() ||
                 'Usuario' }}
            </p>
          </div>
        </div>

        <div class="roles-seleccion-container">
          <h3 class="titulo-seccion-roles">
            <i class="fas fa-user-shield"></i>
            Roles Disponibles
          </h3>
          <p class="descripcion-roles">
            Selecciona los roles que deseas asignar a este usuario. Los roles automáticos (Usuario, Deportista, Acudiente) no se pueden modificar.
          </p>

          <div class="roles-checkbox-list">
            <label
              v-for="rol in rolesFiltrados"
              :key="rol.value"
              class="role-checkbox-item"
              :class="{ 'role-checkbox-selected': rolesSeleccionados.includes(rol.value) }"
            >
              <input
                type="checkbox"
                :value="rol.value"
                :checked="rolesSeleccionados.includes(rol.value)"
                @change="toggleRolSeleccionado(rol.value)"
                :disabled="guardandoRoles"
                class="role-checkbox-input"
              />
              <div class="role-checkbox-content">
                <span class="role-checkbox-name">{{ rol.label }}</span>
                <span class="role-checkbox-badge" :class="roleColor(rol.label)">
                  {{ rol.label }}
                </span>
              </div>
            </label>
          </div>
        </div>

        <div class="botones-acciones-detalle" style="margin-top:20px;">
          <button
            class="btn-accion-detalle btn-roles"
            :disabled="guardandoRoles"
            @click="guardarRoles"
          >
            <i class="fas" :class="guardandoRoles ? 'fa-spinner fa-spin' : 'fa-save'"></i>
            {{ guardandoRoles ? 'Guardando...' : 'Guardar Roles' }}
          </button>
          <button
            class="btn-accion-detalle btn-desactivar"
            :disabled="guardandoRoles"
            @click="cerrarModalRoles"
          >
            <i class="fas fa-times"></i>
            Cancelar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import usuariosService from '@/services/usuariosService';
import { useAuthStore } from '@/stores/auth';

const props = defineProps({
  searchTerm: { type: String, default: '' },
  roleFilter: { type: String, default: 'todos' }
});

const emit = defineEmits(['usuarios-cargados', 'usuario-actualizado']);

const users = ref([]);
const roles = ref([]);
const loading = ref(false);
const error = ref(null);
const authStore = useAuthStore();

// Estado de paginación y visualización
const usuariosPorPagina = 100; // Cargar muchos usuarios del backend
const usuariosVisibles = ref(4); // Mostrar solo 4 usuarios inicialmente en la vista
const offset = ref(0);
const totalUsuarios = ref(0);
const hasMore = ref(false);
const cargandoMas = ref(false);

// Estado del modal de detalle
const mostrarModalDetalle = ref(false);
const usuarioDetalle = ref(null);
const cargandoDetalle = ref(false);
const errorDetalle = ref(null);

// Estado del modal de edición
const mostrarModalEdicion = ref(false);
const guardandoEdicion = ref(false);
const errorEdicion = ref(null);
const formularioEdicion = ref({
  datos_usuario: {
    usuario: ''
  },
  datos_persona: {
    primer_nombre: '',
    segundo_nombre: '',
    primer_apellido: '',
    segundo_apellido: '',
    documento: '',
    correo_electronico: '',
    telefono: '',
    direccion: ''
  }
});

// Estado del modal de gestión de roles
const mostrarModalRoles = ref(false);
const guardandoRoles = ref(false);
const errorRoles = ref(null);
const usuarioParaRoles = ref(null);
const rolesSeleccionados = ref([]);

// Obtener ID del usuario actual para prevenir auto-desactivación
const currentUserId = computed(() => authStore.user?.id_usuario);

// Cargar datos al montar el componente
onMounted(async () => {
  await cargarDatos();
});

// Cargar usuarios y roles
async function cargarDatos() {
  loading.value = true;
  error.value = null;
  offset.value = 0;
  usuariosVisibles.value = 4; // Resetear usuarios visibles a 4

  try {
    // Cargar roles primero
    const rolesResponse = await usuariosService.listarRoles();

    if (rolesResponse.success) {
      // Solo mostrar Entrenador y Administrador (excluir SuperAdmin, Usuario, Deportista, Acudiente)
      const rolesPermitidos = ['entrenador', 'administrador'];
      roles.value = rolesResponse.data
        .filter(rol => {
          const nombreLower = rol.nombre_rol.toLowerCase();
          return rolesPermitidos.includes(nombreLower);
        })
        .map(rol => ({
          value: rol.id_rol,
          label: rol.nombre_rol
        }));
    } else {
      throw new Error(rolesResponse.error || 'Error al cargar roles');
    }

    // Cargar TODOS los usuarios del backend
    let todosUsuarios = [];
    let currentOffset = 0;
    let hayMas = true;
    let total = 0;

    while (hayMas) {
      const usuariosResponse = await usuariosService.listarUsuarios('todos', usuariosPorPagina, currentOffset);

      if (usuariosResponse.success) {
        todosUsuarios = [...todosUsuarios, ...usuariosResponse.data];
        total = usuariosResponse.total || todosUsuarios.length;
        
        // Si la respuesta tiene menos usuarios que el límite, no hay más
        if (usuariosResponse.data.length < usuariosPorPagina) {
          hayMas = false;
        } else {
          // Verificar si hay más según el total
          hayMas = todosUsuarios.length < total;
        }
        
        currentOffset += usuariosResponse.data.length;
    } else {
        throw new Error(usuariosResponse.error || 'Error al cargar usuarios');
      }
    }

    // Guardar todos los usuarios cargados
    users.value = todosUsuarios;
    totalUsuarios.value = total;
    offset.value = currentOffset;
    
    // hasMore se calculará basado en usuariosVisibles vs total
    hasMore.value = usuariosVisibles.value < users.value.length;

    // Resetear selecciones cuando se cargan nuevos usuarios
    userRolesSelections.value = {};
    emit('usuarios-cargados', users.value);
  } catch (err) {
    error.value = err.message;
    console.error('Error al cargar datos:', err);
  } finally {
    loading.value = false;
  }
}

// Mostrar más usuarios (solo incrementa la visualización, no hace petición)
function cargarMasUsuarios() {
  if (!hasMore.value) return;
  
  // Incrementar usuarios visibles en 4
  usuariosVisibles.value += 4;
  
  // hasMore se actualizará automáticamente por el watch
}


// Obtener IDs de roles del usuario (todos)
function userRolesIds(user) {
  return (user.roles || []).map(r => r.id_rol);
}

// Obtener IDs de roles gestionables del usuario (solo Entrenador y Administrador)
function userGestionableRolesIds(user) {
  const rolesPermitidos = ['entrenador', 'administrador'];
  return (user.roles || [])
    .filter(r => rolesPermitidos.includes(r.nombre_rol?.toLowerCase()))
    .map(r => r.id_rol);
}

// Filtrar usuarios localmente
const filteredUsers = computed(() => {
  const text = props.searchTerm.trim().toLowerCase();
  const roleFilter = props.roleFilter;

  // Filtrar todos los usuarios según búsqueda y rol
  const usuariosFiltrados = users.value.filter(user => {
    const matchesText = !text ||
      user.usuario.toLowerCase().includes(text);

    const matchesRole = roleFilter === 'todos' ||
      user.roles.some(rol => rol.nombre_rol.toLowerCase() === roleFilter.toLowerCase());

    return matchesText && matchesRole;
  });

  // Retornar solo los primeros usuariosVisibles para mostrar
  return usuariosFiltrados.slice(0, usuariosVisibles.value);
});

// Usuarios filtrados completos (para calcular hasMore)
const filteredUsersCompletos = computed(() => {
    const text = props.searchTerm.trim().toLowerCase();
    const roleFilter = props.roleFilter;

  return users.value.filter(user => {
      const matchesText = !text ||
        user.usuario.toLowerCase().includes(text);

      const matchesRole = roleFilter === 'todos' ||
        user.roles.some(rol => rol.nombre_rol.toLowerCase() === roleFilter.toLowerCase());

      return matchesText && matchesRole;
    });
});

// Actualizar hasMore reactivamente
watch(
  () => [usuariosVisibles.value, filteredUsersCompletos.value.length],
  () => {
    hasMore.value = usuariosVisibles.value < filteredUsersCompletos.value.length;
  },
  { immediate: true }
);

// Resetear usuarios visibles cuando cambian los filtros de búsqueda
watch(
  () => [props.searchTerm, props.roleFilter],
  () => {
    usuariosVisibles.value = 4; // Resetear a 4 cuando se cambia el filtro
  }
);

// Roles filtrados (sin SuperAdmin)
const rolesFiltrados = computed(() => roles.value);

// Manejar cambio de checkbox de rol
const userRolesSelections = ref({}); // Guardar selecciones temporales por usuario

function handleRoleChange(user, roleId, checked) {
  const userId = user.id_usuario;

  // Si no existe selección previa, inicializar con roles gestionables actuales del usuario
  if (!userRolesSelections.value[userId]) {
    userRolesSelections.value[userId] = [...userGestionableRolesIds(user)];
  }

  // Actualizar selección en el estado
  if (checked) {
    if (!userRolesSelections.value[userId].includes(roleId)) {
      userRolesSelections.value[userId].push(roleId);
    }
  } else {
    userRolesSelections.value[userId] = userRolesSelections.value[userId].filter(id => id !== roleId);
  }

  const newSelection = [...userRolesSelections.value[userId]];

  // Cancelar timeout anterior si existe
  if (userRolesSelections.value[`${userId}_timeout`]) {
    clearTimeout(userRolesSelections.value[`${userId}_timeout`]);
  }

  // Guardar una copia inmutable de los roles para enviar después del delay
  const rolesToSend = [...newSelection];

  // Aplicar cambios después de un pequeño delay para evitar múltiples llamadas
  userRolesSelections.value[`${userId}_timeout`] = setTimeout(() => {
    updateRoles(user, rolesToSend);
  }, 500);
}

// Actualizar múltiples roles de usuario
async function updateRoles(user, selectedRoleIds) {
  try {
    loading.value = true;
    error.value = null;

    const response = await usuariosService.cambiarRolUsuario(user.id_usuario, selectedRoleIds);

    if (response.success) {
      // Actualizar el usuario localmente
      const userIndex = users.value.findIndex(u => u.id_usuario === user.id_usuario);
      if (userIndex !== -1) {
        const updatedUsers = [...users.value];
        updatedUsers[userIndex] = {
          ...updatedUsers[userIndex],
          roles: response.data.roles
        };
        users.value = updatedUsers;

        // Resetear selecciones solo con roles gestionables del estado actual
        userRolesSelections.value[user.id_usuario] = [...userGestionableRolesIds(updatedUsers[userIndex])];

        emit('usuario-actualizado', updatedUsers[userIndex]);
      }

      const rolesNames = response.data.roles.map(r => r.nombre_rol).join(', ');
      console.log(`Roles actualizados: ${user.usuario} ahora tiene: ${rolesNames}`);
    } else {
      throw new Error(response.error || 'Error al actualizar roles');
    }
  } catch (err) {
    error.value = err.message;
    console.error('Error al actualizar roles:', err);
    alert(`❌ Error al actualizar roles: ${err.message}`);
  } finally {
    loading.value = false;
  }
}

// Ver detalle de usuario
async function verDetalleUsuario(user) {
  mostrarModalDetalle.value = true;
  usuarioDetalle.value = null;
  errorDetalle.value = null;
  cargandoDetalle.value = true;

  try {
    const idUsuario = user.id_usuario || user.usuario?.id_usuario;
    const response = await usuariosService.obtenerDetalleUsuario(idUsuario);

    if (response.success) {
      usuarioDetalle.value = response.data;
    } else {
      throw new Error(response.error || 'Error al cargar detalle del usuario');
    }
  } catch (err) {
    errorDetalle.value = err.message;
    console.error('Error al cargar detalle del usuario:', err);
    // Si falla, usar los datos básicos del usuario de la lista
    usuarioDetalle.value = {
      usuario: user,
      persona: user.persona || {},
      roles: user.roles || []
    };
  } finally {
    cargandoDetalle.value = false;
  }
}

// Cerrar modal de detalle
function cerrarModalDetalle() {
  mostrarModalDetalle.value = false;
  usuarioDetalle.value = null;
  errorDetalle.value = null;
}

// Cambiar estado de usuario (activar/desactivar)
async function toggleEstadoUsuario(user) {
  const idUsuario = user.id_usuario || user.usuario?.id_usuario || user.usuario?.id_usuario;

  if (idUsuario === currentUserId.value) {
    alert('⚠️ No puedes desactivar tu propio usuario');
    return;
  }

  const estadoActual = user.estado !== undefined ? user.estado : (user.usuario?.estado !== false);
  const nuevoEstado = !estadoActual;

  const confirmacion = confirm(
    `¿Estás seguro de que deseas ${nuevoEstado ? 'activar' : 'desactivar'} al usuario "${user.usuario || user.usuario?.usuario || 'este usuario'}"?`
  );

  if (!confirmacion) {
    return;
  }

  try {
    loading.value = true;
    error.value = null;

    const response = await usuariosService.cambiarEstadoUsuario(idUsuario, nuevoEstado);

    if (response.success) {
      // Actualizar el usuario localmente
      const userIndex = users.value.findIndex(u => u.id_usuario === idUsuario);
      if (userIndex !== -1) {
        users.value[userIndex].estado = nuevoEstado;
        emit('usuario-actualizado', users.value[userIndex]);
      }

      // Actualizar en el modal si está abierto
      if (usuarioDetalle.value) {
        if (usuarioDetalle.value.usuario) {
          usuarioDetalle.value.usuario.estado = nuevoEstado;
        } else {
          usuarioDetalle.value.estado = nuevoEstado;
        }
      }

      alert(`✅ Usuario ${nuevoEstado ? 'activado' : 'desactivado'} exitosamente`);
    } else {
      throw new Error(response.error || 'Error al cambiar estado del usuario');
    }
  } catch (err) {
    error.value = err.message;
    console.error('Error al cambiar estado del usuario:', err);
    alert(`❌ Error al cambiar estado: ${err.message}`);
  } finally {
    loading.value = false;
  }
}

// Abrir modal de edición con datos actuales
function abrirModalEdicion(user) {
  // El usuario viene del modal de detalle, así que tiene la estructura { usuario: {...}, persona: {...} }
  const usuario = user.usuario || user;
  const persona = user.persona || {};

  formularioEdicion.value = {
    datos_usuario: {
      usuario: usuario.usuario || usuario || ''
    },
    datos_persona: {
      primer_nombre: persona.primer_nombre || '',
      segundo_nombre: persona.segundo_nombre || '',
      primer_apellido: persona.primer_apellido || '',
      segundo_apellido: persona.segundo_apellido || '',
      documento: persona.documento || '',
      correo_electronico: persona.correo_electronico || '',
      telefono: persona.telefono || '',
      direccion: persona.direccion || ''
    }
  };
  mostrarModalEdicion.value = true;
}

function cerrarModalEdicion() {
  mostrarModalEdicion.value = false;
  errorEdicion.value = null;
}

async function guardarEdicion() {
  if (!usuarioDetalle.value) return;
  const idUsuario = usuarioDetalle.value.usuario?.id_usuario || usuarioDetalle.value.id_usuario;
  try {
    guardandoEdicion.value = true;
    errorEdicion.value = null;
    const resp = await usuariosService.actualizarUsuario(idUsuario, formularioEdicion.value);
    if (!resp.success) throw new Error(resp.error || 'Error al actualizar');

    // Actualizar en tabla
    const idx = users.value.findIndex(u => u.id_usuario === idUsuario);
    if (idx !== -1) {
      if (formularioEdicion.value.datos_usuario?.usuario) {
        users.value[idx].usuario = formularioEdicion.value.datos_usuario.usuario;
      }
      if (users.value[idx].persona) {
        Object.assign(users.value[idx].persona, formularioEdicion.value.datos_persona || {});
      }
      emit('usuario-actualizado', users.value[idx]);
    }

    // Refrescar detalle
    const refreshed = await usuariosService.obtenerDetalleUsuario(idUsuario);
    if (refreshed.success) {
      usuarioDetalle.value = refreshed.data;
    }

    cerrarModalEdicion();
    alert('✅ Usuario actualizado');
  } catch (e) {
    console.error(e);
    errorEdicion.value = e.message;
    alert(`❌ ${e.message}`);
  } finally {
    guardandoEdicion.value = false;
  }
}

// Abrir gestión de roles
function abrirGestionRoles(user) {
  usuarioParaRoles.value = user;
  errorRoles.value = null;

  // Obtener los roles actuales del usuario (solo Administrador y Entrenador)
  const rolesActuales = (user.roles || []).filter(rol => {
    const nombreLower = rol.nombre_rol?.toLowerCase() || '';
    return nombreLower === 'administrador' || nombreLower === 'entrenador';
  });

  // Mapear los roles actuales a sus IDs
  rolesSeleccionados.value = rolesActuales.map(rol => rol.id_rol);

  mostrarModalRoles.value = true;
}

// Cerrar modal de gestión de roles
function cerrarModalRoles() {
  mostrarModalRoles.value = false;
  usuarioParaRoles.value = null;
  rolesSeleccionados.value = [];
  errorRoles.value = null;
}

// Toggle de selección de rol
function toggleRolSeleccionado(idRol) {
  const index = rolesSeleccionados.value.indexOf(idRol);
  if (index > -1) {
    rolesSeleccionados.value.splice(index, 1);
  } else {
    rolesSeleccionados.value.push(idRol);
  }
}

// Guardar cambios de roles
async function guardarRoles() {
  if (!usuarioParaRoles.value) return;

  const idUsuario = usuarioParaRoles.value.usuario?.id_usuario || usuarioParaRoles.value.id_usuario;

  try {
    guardandoRoles.value = true;
    errorRoles.value = null;

    // Enviar los roles seleccionados al backend
    const response = await usuariosService.cambiarRolUsuario(idUsuario, rolesSeleccionados.value);

    if (!response.success) {
      throw new Error(response.error || 'Error al actualizar roles');
    }

    // Obtener los roles actualizados desde la respuesta del backend
    const rolesActualizados = response.data?.roles || [];

    // Actualizar en la tabla directamente
    const userIndex = users.value.findIndex(u => u.id_usuario === idUsuario);
    if (userIndex !== -1) {
      // Crear un nuevo array de usuarios para forzar reactividad
      const updatedUsers = [...users.value];

      // Actualizar los roles del usuario
      updatedUsers[userIndex] = {
        ...updatedUsers[userIndex],
        roles: rolesActualizados.map(rol => ({
          id_rol: rol.id_rol,
          nombre_rol: rol.nombre_rol,
          descripcion: rol.descripcion || ''
        }))
      };

      // Asignar el nuevo array para forzar reactividad
      users.value = updatedUsers;

      emit('usuario-actualizado', updatedUsers[userIndex]);
    }

    // También actualizar usuarioParaRoles para mantener consistencia
    if (usuarioParaRoles.value) {
      if (usuarioParaRoles.value.usuario) {
        usuarioParaRoles.value.usuario.roles = rolesActualizados;
      } else {
        usuarioParaRoles.value.roles = rolesActualizados;
      }
    }

    // Refrescar detalle si está abierto
    if (usuarioDetalle.value && (usuarioDetalle.value.usuario?.id_usuario === idUsuario || usuarioDetalle.value.id_usuario === idUsuario)) {
      const refreshed = await usuariosService.obtenerDetalleUsuario(idUsuario);
      if (refreshed.success) {
        usuarioDetalle.value = refreshed.data;
      }
    }

    cerrarModalRoles();
    alert('✅ Roles actualizados exitosamente');
  } catch (err) {
    console.error('Error al guardar roles:', err);
    errorRoles.value = err.message;
    alert(`❌ Error al actualizar roles: ${err.message}`);
  } finally {
    guardandoRoles.value = false;
  }
}

function roleColor(role) {
  switch (role) {
    case "SuperAdmin":
      return "badge-admin";
    case "Administrador":
      return "badge-admin";
    case "Entrenador":
      return "badge-moderator";
    case "Deportista":
      return "badge-user";
    case "Acudiente":
      return "badge-user";
    default:
      return "badge-user";
  }
}
</script>

<style scoped>
.tabla-usuarios {
  width: 100%;
  font-size: 18px;
  border-collapse: collapse;
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  table-layout: fixed;
}

.tabla-usuarios thead tr {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  color: #374151;
  font-weight: 600;
  text-align: left;
}

.tabla-usuarios th {
  padding: 16px 20px;
  font-size: 22px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #d1d5db;
  text-align: center;
}

.tabla-usuarios th:nth-child(1) {
  width: 30%;
}

.tabla-usuarios th:nth-child(2) {
  width: 30%;
}

.tabla-usuarios th:nth-child(3) {
  width: 40%;
}

.tabla-usuarios tbody tr {
  transition: all 0.3s ease;
  border-bottom: 1px solid #f3f4f6;
}

.tabla-usuarios tbody tr:nth-child(even) {
  background-color: #f9fafb;
}

.tabla-usuarios tbody tr:hover {
  background-color: #f0f9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tabla-usuarios td {
  padding: 16px 20px;
  font-size: 14px;
  color: #374151;
  vertical-align: middle;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tabla-usuarios td:first-child {
  font-weight: 600;
  color: #1f2937;
}

/* Estilos para las filas de usuario */
.user-row {
  transition: all 0.3s ease;
  cursor: pointer;
}

.user-row--even {
  background-color: #f9fafb;
}

.user-row--odd {
  background-color: white;
}

.user-row:hover {
  background-color: #f0f9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-name {
  font-weight: 600;
  color: #1f2937;
}

.user-role {
  text-align: center;
  vertical-align: middle;
}

.user-action {
  text-align: center;
  vertical-align: middle;
  display: flex;
  justify-content: center;
  align-items: center;
}

.role-select {
  padding: 8px 12px;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  background-color: white;
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 140px;
}

.role-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.role-select:hover {
  border-color: #9ca3af;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
  letter-spacing: 0.3px;
}

.badge-admin {
  background-color: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.badge-moderator {
  background-color: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.badge-user {
  background-color: #f9fafb;
  color: #6b7280;
  border: 1px solid #e5e7eb;
}

.badge-none {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.roles-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
}

.roles-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 200px;
  max-width: 250px;
  padding: 12px;
  background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin: 0 auto;
}

.role-checkbox-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 10px 14px;
  border-radius: 8px;
  background-color: #ffffff;
  border: 2px solid #e5e7eb;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.role-checkbox-label::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background-color: #3b82f6;
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.role-checkbox-label:hover {
  background-color: #f0f9ff;
  border-color: #93c5fd;
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
}

.role-checkbox-label:hover::before {
  transform: scaleY(1);
}

.role-checkbox-label.role-checkbox-checked,
.role-checkbox-label:has(.role-checkbox:checked) {
  background-color: #eff6ff;
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
}

.role-checkbox-label.role-checkbox-checked::before,
.role-checkbox-label:has(.role-checkbox:checked)::before {
  transform: scaleY(1);
}

.role-checkbox-label.role-checkbox-checked .role-checkbox-text,
.role-checkbox-label:has(.role-checkbox:checked) .role-checkbox-text {
  color: #1e40af;
  font-weight: 600;
}

.role-checkbox {
  width: 20px;
  height: 20px;
  min-width: 20px;
  cursor: pointer;
  accent-color: #3b82f6;
  border-radius: 4px;
  border: 2px solid #d1d5db;
  transition: all 0.3s ease;
  position: relative;
}

.role-checkbox:hover {
  border-color: #3b82f6;
  transform: scale(1.1);
}

.role-checkbox:checked {
  background-color: #3b82f6;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.role-checkbox:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

.role-checkbox:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.role-checkbox-text {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  user-select: none;
  transition: color 0.3s ease;
  flex: 1;
}

.role-checkbox-label:hover .role-checkbox-text {
  color: #1e40af;
}

select {
  padding: 8px 12px;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  background-color: white;
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 140px;
}

select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

select:hover {
  border-color: #9ca3af;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Estilos para botón de estado */
.user-status {
  text-align: center;
  padding: 12px;
}

.btn-estado {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  min-width: 110px;
  justify-content: center;
}

.btn-estado:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.btn-estado:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-activo {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
}

.btn-activo:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4);
}

.btn-inactivo {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
}

.btn-inactivo:hover:not(:disabled) {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  box-shadow: 0 4px 8px rgba(239, 68, 68, 0.4);
}

.btn-estado i {
  font-size: 16px;
}

/* Responsive */
@media (max-width: 768px) {
  .tabla-usuarios {
    font-size: 12px;
  }

  .tabla-usuarios th,
  .tabla-usuarios td {
    padding: 12px 16px;
  }

  .roles-checkboxes {
    min-width: 160px;
    max-width: 200px;
    padding: 8px;
    gap: 8px;
  }

  .role-checkbox-label {
    padding: 8px 10px;
    gap: 10px;
  }

  .role-checkbox {
    width: 18px;
    height: 18px;
    min-width: 18px;
  }

  .role-checkbox-text {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .roles-checkboxes {
    min-width: 140px;
    max-width: 180px;
    padding: 6px;
    gap: 6px;
  }

  .role-checkbox-label {
    padding: 6px 8px;
    gap: 8px;
  }

  .role-checkbox {
    width: 16px;
    height: 16px;
    min-width: 16px;
  }

  .role-checkbox-text {
    font-size: 11px;
  }

  select {
    min-width: 120px;
    font-size: 12px;
    padding: 6px 10px;
  }
}

@media (max-width: 768px) {
  select {
    min-width: 120px;
    font-size: 12px;
    padding: 6px 10px;
  }
}

/* Estilos para el modal de detalle */
.modal-overlay-detalle {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
  padding: 20px;
  overflow-y: auto;
}

.modal-content-detalle {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-header-detalle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 2px solid #e5e7eb;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px 16px 0 0;
}

.modal-title-detalle {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-cerrar-modal {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: all 0.2s ease;
}

.btn-cerrar-modal:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.modal-body-detalle {
  padding: 28px;
  overflow-y: auto;
  flex: 1;
}

.loading-detalle,
.error-detalle {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.loading-detalle i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #667eea;
}

.error-detalle i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #ef4444;
}

.detalle-usuario {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.seccion-detalle {
  background: #f9fafb;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e5e7eb;
}

.titulo-seccion {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e5e7eb;
}

.titulo-seccion i {
  color: #667eea;
}

.info-grid-detalle {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.info-grid-usuario {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.info-item-detalle {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item-detalle label {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item-detalle span {
  font-size: 15px;
  color: #1f2937;
  font-weight: 500;
}

.badge-estado {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-estado.activo {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.badge-estado.inactivo {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.roles-container-detalle {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.badge-detalle {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  text-transform: capitalize;
  letter-spacing: 0.3px;
}

.seccion-acciones-detalle {
  background: #f9fafb;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e5e7eb;
}

.botones-acciones-detalle {
  display: flex !important;
  flex-wrap: nowrap !important;
  gap: 12px !important;
  margin-top: 16px;
  justify-content: center !important;
  align-items: stretch !important;
  width: 100% !important;
}

/* Forzar que todos los botones tengan exactamente el mismo tamaño - MÁXIMA ESPECIFICIDAD */
.botones-acciones-detalle button,
.botones-acciones-detalle > button,
.botones-acciones-detalle button.btn-accion-detalle,
.botones-acciones-detalle .btn-accion-detalle,
.seccion-acciones-detalle .botones-acciones-detalle button,
.seccion-acciones-detalle .botones-acciones-detalle > button,
.seccion-acciones-detalle button.btn-accion-detalle,
.seccion-acciones-detalle button.btn-editar,
.seccion-acciones-detalle button.btn-roles,
.seccion-acciones-detalle button.btn-activar,
.seccion-acciones-detalle button.btn-desactivar,
.seccion-acciones-detalle .botones-acciones-detalle button.btn-editar {
  flex: 0 0 250px !important;
  width: 250px !important;
  min-width: 250px !important;
  max-width: 250px !important;
  height: 48px !important;
  min-height: 48px !important;
  max-height: 48px !important;
  box-sizing: border-box !important;
  padding: 14px 24px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.btn-accion-detalle,
button.btn-accion-detalle,
button.btn-editar,
button.btn-roles,
button.btn-activar,
button.btn-desactivar,
.seccion-acciones-detalle button,
.seccion-acciones-detalle .btn-accion-detalle {
  flex: 0 0 250px !important;
  width: 250px !important;
  min-width: 250px !important;
  max-width: 250px !important;
  height: 48px !important;
  min-height: 48px !important;
  max-height: 48px !important;
  padding: 14px 24px !important;
  border: none !important;
  border-radius: 10px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  cursor: pointer !important;
  transition: all 0.3s ease !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 10px !important;
  color: white !important;
  white-space: nowrap !important;
  box-sizing: border-box !important;
  line-height: 1.5 !important;
}

.btn-accion-detalle:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-accion-detalle:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.btn-desactivar {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.btn-activar {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.btn-editar,
button.btn-editar,
.btn-accion-detalle.btn-editar,
.seccion-acciones-detalle button.btn-editar,
.botones-acciones-detalle button.btn-editar {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
  flex: 0 0 250px !important;
  width: 250px !important;
  min-width: 250px !important;
  max-width: 250px !important;
  height: 48px !important;
  min-height: 48px !important;
  max-height: 48px !important;
  padding: 14px 24px !important;
  box-sizing: border-box !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.btn-roles {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

/* Responsive para modal */
@media (max-width: 768px) {
  .modal-content-detalle {
    max-width: 95%;
    max-height: 95vh;
  }

  .modal-header-detalle {
    padding: 20px;
  }

  .modal-title-detalle {
    font-size: 20px;
  }

  .modal-body-detalle {
    padding: 20px;
  }

  .info-grid-detalle {
    grid-template-columns: 1fr;
  }

  .info-grid-usuario {
    grid-template-columns: 1fr;
  }

  .botones-acciones-detalle {
    flex-direction: column;
  }

  .botones-acciones-detalle button,
  .botones-acciones-detalle .btn-accion-detalle,
  .seccion-acciones-detalle .botones-acciones-detalle button {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
    flex: 0 0 100% !important;
  }

  .btn-accion-detalle {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
    flex: 0 0 100% !important;
  }
}

/* Estilos adicionales para inputs en modal de edición */
.control-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.2s ease;
  background-color: white;
  color: #1f2937;
}

.control-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.control-input:hover {
  border-color: #d1d5db;
}

/* Estilos para modal de gestión de roles */
.info-usuario-roles {
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid #e5e7eb;
}

.usuario-info-roles h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
}

.usuario-nombre-completo {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
}

.roles-seleccion-container {
  background: #f9fafb;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e5e7eb;
}

.titulo-seccion-roles {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.titulo-seccion-roles i {
  color: #8b5cf6;
}

.descripcion-roles {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
}

.roles-checkbox-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.role-checkbox-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.role-checkbox-item:hover {
  border-color: #8b5cf6;
  background: #faf5ff;
  transform: translateX(4px);
}

.role-checkbox-item.role-checkbox-selected {
  border-color: #8b5cf6;
  background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.15);
}

.role-checkbox-input {
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: #8b5cf6;
}

.role-checkbox-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.role-checkbox-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  text-transform: capitalize;
}

.role-checkbox-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

/* Estilos para cargar más usuarios */
.cargar-mas-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding: 20px 0;
}

.btn-cargar-mas {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-cargar-mas:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-cargar-mas:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.sin-mas-usuarios {
  text-align: center;
  padding: 20px 0;
  color: #6b7280;
  font-size: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.sin-mas-usuarios p {
  margin: 0;
  font-style: italic;
}
</style>

