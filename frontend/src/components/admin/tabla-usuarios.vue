<template>
    <table class="tabla-usuarios">
      <caption class="sr-only">Tabla de usuarios del sistema con información de roles, estado y acciones</caption>
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
                :class="['badge', roleColor(rol.nombre_rol), `badge-${rol.nombre_rol.toLowerCase()}`]"
              >
                {{ rol.nombre_rol === 'SuperAdmin' ? 'Administrador' : rol.nombre_rol }}
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

      <!-- Mensaje cuando no hay resultados de búsqueda/filtro -->
      <div v-if="!loading && !error && filteredUsersCompletos.length === 0" class="sin-resultados">
        <div class="sin-resultados-content">
          <i class="fas fa-search"></i>
          <h3>No se encontraron usuarios</h3>
          <p>No hay usuarios que coincidan con tu búsqueda o filtro seleccionado.</p>
          <p class="sin-resultados-sugerencia">Intenta con otros términos de búsqueda o cambia el filtro de rol.</p>
        </div>
      </div>

      <!-- Mensaje cuando no hay más usuarios -->
      <div v-if="!loading && !error && !hasMore && filteredUsersCompletos.length > 0" class="sin-mas-usuarios">
        <p>Mostrando todos los {{ filteredUsersCompletos.length }} usuarios</p>
      </div>

  <!-- Modal de Detalle de Usuario -->
  <div v-if="mostrarModalDetalle" class="modal-overlay modal-detalle-overlay" @click.self="cerrarModalDetalle">
    <div class="modal-content modal-detalle" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">
          <i class="fas fa-user"></i>
          Detalle de Usuario
        </h2>
        <button class="btn-cerrar" @click="cerrarModalDetalle">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
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
                <span class="info-label">Nombre Completo:</span>
                <span>{{ usuarioDetalle.persona?.nombre_completo || `${usuarioDetalle.persona?.primer_nombre || ''} ${usuarioDetalle.persona?.primer_apellido || ''}`.trim() || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <span class="info-label">Primer Nombre:</span>
                <span>{{ usuarioDetalle.persona?.primer_nombre || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <span class="info-label">Segundo Nombre:</span>
                <span>{{ usuarioDetalle.persona?.segundo_nombre || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <span class="info-label">Primer Apellido:</span>
                <span>{{ usuarioDetalle.persona?.primer_apellido || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <span class="info-label">Segundo Apellido:</span>
                <span>{{ usuarioDetalle.persona?.segundo_apellido || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <span class="info-label">Documento:</span>
                <span>{{ usuarioDetalle.persona?.documento || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <span class="info-label">Correo Electrónico:</span>
                <span>{{ usuarioDetalle.persona?.correo_electronico || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <span class="info-label">Teléfono:</span>
                <span>{{ usuarioDetalle.persona?.telefono || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle info-item-direccion-detalle">
                <span class="info-label">Dirección:</span>
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
                <span class="info-label">Username:</span>
                <span>{{ usuarioDetalle.usuario?.usuario || usuarioDetalle.usuario || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <span class="info-label">ID Usuario:</span>
                <span>{{ usuarioDetalle.usuario?.id_usuario || usuarioDetalle.id_usuario || 'N/A' }}</span>
              </div>
              <div class="info-item-detalle">
                <span class="info-label">Estado:</span>
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
                :class="['badge', 'badge-detalle', roleColor(rol.nombre_rol), `badge-${rol.nombre_rol.toLowerCase()}`]"
              >
                {{ rol.nombre_rol === 'SuperAdmin' ? 'Administrador' : rol.nombre_rol }}
              </span>
              <span v-if="!usuarioDetalle.roles || usuarioDetalle.roles.length === 0" class="badge badge-detalle badge-none">
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
            <div class="botones-acciones-detalle" @click.stop>
              <button
                @click.stop="toggleEstadoUsuario(usuarioDetalle)"
                :disabled="loading || usuarioDetalle.usuario?.id_usuario === currentUserId || usuarioDetalle.id_usuario === currentUserId"
                :class="['btn-accion-detalle', usuarioDetalle.usuario?.estado !== false ? 'btn-desactivar' : 'btn-activar']"
                style="flex: 0 0 250px !important; width: 250px !important; min-width: 250px !important; max-width: 250px !important; height: 48px !important; min-height: 48px !important; max-height: 48px !important; padding: 14px 24px !important; box-sizing: border-box !important; display: flex !important; align-items: center !important; justify-content: center !important;"
              >
                <i :class="usuarioDetalle.usuario?.estado !== false ? 'fas fa-ban' : 'fas fa-check-circle'"></i>
                {{ usuarioDetalle.usuario?.estado !== false ? 'Desactivar' : 'Activar' }} Usuario
              </button>

              <button
                @click.stop="abrirModalEdicion(usuarioDetalle)"
                :disabled="loading"
                class="btn-accion-detalle btn-editar"
                style="flex: 0 0 250px !important; width: 250px !important; min-width: 250px !important; max-width: 250px !important; height: 48px !important; min-height: 48px !important; max-height: 48px !important; padding: 14px 24px !important; box-sizing: border-box !important; display: flex !important; align-items: center !important; justify-content: center !important;"
              >
                <i class="fas fa-edit"></i>
                Editar Usuario
              </button>

              <button
                @click.stop="abrirGestionRoles(usuarioDetalle)"
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
  <div v-if="mostrarModalEdicion" class="modal-overlay modal-edicion-overlay" @click.self="cerrarModalEdicion">
    <div class="modal-content modal-edicion modal-sm" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">
          <i class="fas fa-edit"></i>
          Editar Usuario
        </h2>
        <button class="btn-cerrar" @click="cerrarModalEdicion">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body">
        <div v-if="errorEdicion" class="error-detalle" style="color:#ef4444; margin-bottom: 24px;">
          <i class="fas fa-exclamation-circle"></i>
          <p>{{ errorEdicion }}</p>
        </div>

        <!-- Sección: Información de Usuario -->
        <div class="seccion-formulario-edicion">
          <h3 class="titulo-seccion-edicion">
            <i class="fas fa-user-circle"></i>
            Información de Usuario
          </h3>
          <div class="info-grid-detalle info-grid-usuario-solo">
            <div class="info-item-detalle">
              <label for="edicion-username">Username *</label>
              <input
                id="edicion-username"
                v-model="formularioEdicion.datos_usuario.usuario"
                type="text"
                class="control-input"
                placeholder="Ingrese el nombre de usuario"
                @input="onUsuarioInput"
                @blur="onUsuarioInput"
              />
              <small v-if="erroresCamposEdicion.username" class="input-error">{{ erroresCamposEdicion.username }}</small>
            </div>
          </div>
        </div>

        <!-- Sección: Información Personal -->
        <div class="seccion-formulario-edicion">
          <h3 class="titulo-seccion-edicion">
            <i class="fas fa-id-card"></i>
            Información Personal
          </h3>
          <div class="info-grid-detalle">
            <div class="info-item-detalle">
              <label for="edicion-primer-nombre">Primer Nombre *</label>
              <input
                id="edicion-primer-nombre"
                v-model="formularioEdicion.datos_persona.primer_nombre"
                type="text"
                class="control-input"
                placeholder="Ingrese el primer nombre"
                @input="onNombreInput('primer_nombre')"
                @blur="onNombreInput('primer_nombre')"
              />
              <small v-if="erroresCamposEdicion.primer_nombre" class="input-error">{{ erroresCamposEdicion.primer_nombre }}</small>
            </div>
            <div class="info-item-detalle">
              <label for="edicion-segundo-nombre">Segundo Nombre</label>
              <input
                id="edicion-segundo-nombre"
                v-model="formularioEdicion.datos_persona.segundo_nombre"
                type="text"
                class="control-input"
                placeholder="Ingrese el segundo nombre (opcional)"
                @input="onNombreInput('segundo_nombre')"
                @blur="onNombreInput('segundo_nombre')"
              />
              <small v-if="erroresCamposEdicion.segundo_nombre" class="input-error">{{ erroresCamposEdicion.segundo_nombre }}</small>
            </div>
            <div class="info-item-detalle">
              <label for="edicion-primer-apellido">Primer Apellido *</label>
              <input
                id="edicion-primer-apellido"
                v-model="formularioEdicion.datos_persona.primer_apellido"
                type="text"
                class="control-input"
                placeholder="Ingrese el primer apellido"
                @input="onNombreInput('primer_apellido')"
                @blur="onNombreInput('primer_apellido')"
              />
              <small v-if="erroresCamposEdicion.primer_apellido" class="input-error">{{ erroresCamposEdicion.primer_apellido }}</small>
            </div>
            <div class="info-item-detalle">
              <label for="edicion-segundo-apellido">Segundo Apellido</label>
              <input
                id="edicion-segundo-apellido"
                v-model="formularioEdicion.datos_persona.segundo_apellido"
                type="text"
                class="control-input"
                placeholder="Ingrese el segundo apellido (opcional)"
                @input="onNombreInput('segundo_apellido')"
                @blur="onNombreInput('segundo_apellido')"
              />
              <small v-if="erroresCamposEdicion.segundo_apellido" class="input-error">{{ erroresCamposEdicion.segundo_apellido }}</small>
            </div>
            <div class="info-item-detalle info-item-documento">
              <label for="edicion-documento">Documento *</label>
              <input
                id="edicion-documento"
                v-model="formularioEdicion.datos_persona.documento"
                type="text"
                class="control-input"
                placeholder="Ingrese el número de documento"
                @input="onDocumentoInput"
                @blur="onDocumentoInput"
              />
              <small v-if="erroresCamposEdicion.documento" class="input-error">{{ erroresCamposEdicion.documento }}</small>
            </div>
          </div>
        </div>

        <!-- Sección: Información de Contacto -->
        <div class="seccion-formulario-edicion">
          <h3 class="titulo-seccion-edicion">
            <i class="fas fa-envelope"></i>
            Información de Contacto
          </h3>
          <div class="info-grid-detalle">
            <div class="info-item-detalle">
              <label for="edicion-correo">Correo Electrónico *</label>
              <input
                id="edicion-correo"
                v-model="formularioEdicion.datos_persona.correo_electronico"
                type="email"
                class="control-input"
                placeholder="correo@ejemplo.com"
                @input="onEmailInput"
                @blur="onEmailInput"
              />
              <small v-if="erroresCamposEdicion.correo_electronico" class="input-error">{{ erroresCamposEdicion.correo_electronico }}</small>
            </div>
            <div class="info-item-detalle">
              <label for="edicion-telefono">Teléfono</label>
              <input
                id="edicion-telefono"
                v-model="formularioEdicion.datos_persona.telefono"
                type="text"
                class="control-input"
                placeholder="Ingrese el número telefónico (opcional)"
                @input="onTelefonoInput"
                @blur="onTelefonoInput"
              />
              <small v-if="erroresCamposEdicion.telefono" class="input-error">{{ erroresCamposEdicion.telefono }}</small>
            </div>
            <div class="info-item-detalle info-item-direccion">
              <label for="edicion-direccion">Dirección</label>
              <input
                id="edicion-direccion"
                v-model="formularioEdicion.datos_persona.direccion"
                type="text"
                class="control-input"
                placeholder="Ingrese la dirección (opcional)"
                @input="onDireccionInput"
                @blur="onDireccionInput"
              />
              <small v-if="erroresCamposEdicion.direccion" class="input-error">{{ erroresCamposEdicion.direccion }}</small>
            </div>
          </div>
        </div>

        <!-- Botones de acción -->
        <div class="botones-acciones-detalle">
          <button class="btn-accion-detalle btn-desactivar" :disabled="guardandoEdicion" @click="cerrarModalEdicion">
            <i class="fas fa-times"></i>
            Cancelar
          </button>
          <button class="btn-accion-detalle btn-editar" :disabled="guardandoEdicion" @click="guardarEdicion">
            <i class="fas" :class="guardandoEdicion ? 'fa-spinner fa-spin' : 'fa-save'"></i>
            {{ guardandoEdicion ? 'Guardando...' : 'Guardar Cambios' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal de Gestión de Roles -->
  <div v-if="mostrarModalRoles" class="modal-overlay modal-roles-overlay" @click.self="cerrarModalRoles">
    <div class="modal-content modal-roles" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">
          <i class="fas fa-user-tag"></i>
          Gestionar Roles
        </h2>
        <button class="btn-cerrar" @click="cerrarModalRoles">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body">
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
import Swal from 'sweetalert2';
import { useModalScrollLock } from '@/composables/useModalScrollLock';
import { extraerMensajeError } from '@/utils/error-handling';

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
const rolesIniciales = ref([]); // Guardar roles iniciales para comparar cambios

// Obtener ID del usuario actual para prevenir auto-desactivación
const currentUserId = computed(() => authStore.user?.id_usuario);

// Bloquear scroll del body cuando cualquier modal está abierto
const hayModalAbierto = computed(() => mostrarModalDetalle.value || mostrarModalEdicion.value || mostrarModalRoles.value);
useModalScrollLock(hayModalAbierto);

const DOC_MIN = 6;
const DOC_MAX = 20;
const PHONE_MIN = 7;
const PHONE_MAX = 15;
// Expresión regular optimizada para evitar ReDoS (Regular Expression Denial of Service)
// Usa clases de caracteres específicas en lugar de negaciones para mejor rendimiento
const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
const erroresCamposEdicion = ref({
  username: '',
  primer_nombre: '',
  segundo_nombre: '',
  primer_apellido: '',
  segundo_apellido: '',
  documento: '',
  correo_electronico: '',
  telefono: '',
  direccion: ''
});

function limpiarEspacios(valor = '') {
  return valor.replace(/\s+/g, ' ').trim(); // NOSONAR: S7781 - replaceAll() no acepta regex
}

function normalizarNombre(valor = '') {
  const limpio = limpiarEspacios(valor)
    .replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]/g, ''); // NOSONAR: S7781 - replaceAll() no acepta regex
  return limpio.toUpperCase();
}

function normalizarUsername(valor = '') {
  return limpiarEspacios(valor).replace(/\s/g, '').toLowerCase(); // NOSONAR: S7781 - replaceAll() no acepta regex
}

function normalizarDocumentoValor(valor = '') {
  return valor.replace(/\D/g, '').slice(0, DOC_MAX); // NOSONAR: S7781 - replaceAll() no acepta regex
}

function normalizarTelefonoValor(valor = '') {
  return valor.replace(/\D/g, '').slice(0, PHONE_MAX); // NOSONAR: S7781 - replaceAll() no acepta regex
}

function normalizarDireccionValor(valor = '') {
  const permitido = limpiarEspacios(valor).replace(/[^A-Za-z0-9#.\-\s]/g, ''); // NOSONAR: S7781 - replaceAll() no acepta regex
  return permitido.toUpperCase();
}

function normalizarEmailValor(valor = '') {
  return limpiarEspacios(valor).toLowerCase();
}

function obtenerUsername(user) {
  if (typeof user?.usuario === 'string') {
    return user.usuario;
  }
  if (typeof user?.usuario?.usuario === 'string') {
    return user.usuario.usuario;
  }
  return '';
}

function obtenerNombreUsuarioLegible(user) {
  const username = obtenerUsername(user);
  if (username) return username;

  const personaBase = user?.persona || user?.usuario?.persona || {};
  const nombreCompleto = [
    personaBase.primer_nombre || '',
    personaBase.segundo_nombre || '',
    personaBase.primer_apellido || '',
    personaBase.segundo_apellido || ''
  ].map(parte => (typeof parte === 'string' ? parte.trim() : '')).filter(Boolean).join(' ');

  if (nombreCompleto) return nombreCompleto;

  return 'este usuario';
}

function onNombreInput(campo) {
  if (!formularioEdicion.value?.datos_persona) return;
  formularioEdicion.value.datos_persona[campo] = normalizarNombre(formularioEdicion.value.datos_persona[campo] || '');
}

function onUsuarioInput() {
  if (!formularioEdicion.value?.datos_usuario) return;
  formularioEdicion.value.datos_usuario.usuario = normalizarUsername(formularioEdicion.value.datos_usuario.usuario || '');
}

function onDocumentoInput() {
  if (!formularioEdicion.value?.datos_persona) return;
  formularioEdicion.value.datos_persona.documento = normalizarDocumentoValor(formularioEdicion.value.datos_persona.documento || '');
}

function onTelefonoInput() {
  if (!formularioEdicion.value?.datos_persona) return;
  formularioEdicion.value.datos_persona.telefono = normalizarTelefonoValor(formularioEdicion.value.datos_persona.telefono || '');
}

function onDireccionInput() {
  if (!formularioEdicion.value?.datos_persona) return;
  formularioEdicion.value.datos_persona.direccion = normalizarDireccionValor(formularioEdicion.value.datos_persona.direccion || '');
}

function onEmailInput() {
  if (!formularioEdicion.value?.datos_persona) return;
  formularioEdicion.value.datos_persona.correo_electronico = normalizarEmailValor(formularioEdicion.value.datos_persona.correo_electronico || '');
}

function normalizarFormularioEdicion() {
  onUsuarioInput();
  onNombreInput('primer_nombre');
  onNombreInput('segundo_nombre');
  onNombreInput('primer_apellido');
  onNombreInput('segundo_apellido');
  onDocumentoInput();
  onEmailInput();
  onTelefonoInput();
  onDireccionInput();
}

function resetErroresCampos() {
  erroresCamposEdicion.value = {
    username: '',
    primer_nombre: '',
    segundo_nombre: '',
    primer_apellido: '',
    segundo_apellido: '',
    documento: '',
    correo_electronico: '',
    telefono: '',
    direccion: ''
  };
}

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
      const rolesPermitidos = new Set(['entrenador', 'administrador']);
      roles.value = rolesResponse.data
        .filter(rol => {
          const nombreLower = rol.nombre_rol.toLowerCase();
          return rolesPermitidos.has(nombreLower);
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

// Expose method for parent component to reload data
defineExpose({
  cargarDatos
});

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
  const rolesPermitidos = new Set(['entrenador', 'administrador']);
  return (user.roles || [])
    .filter(r => rolesPermitidos.has(r.nombre_rol?.toLowerCase()))
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
    await Swal.fire({
      icon: 'error',
      title: 'Error al actualizar roles',
      text: err.message || 'No pudimos actualizar los roles. Intenta nuevamente.'
    });
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

function obtenerIdUsuario(user) {
  return user.id_usuario || user.usuario?.id_usuario || user.usuario?.id_usuario;
}

function obtenerEstadoActual(user) {
  if (user.estado !== undefined) {
    return user.estado;
  }
  return user.usuario?.estado !== false;
}

async function validarCambioEstadoPropio(idUsuario) {
  if (idUsuario === currentUserId.value) {
    await Swal.fire({
      icon: 'warning',
      title: 'Acción no permitida',
      text: 'No puedes desactivar tu propio usuario.'
    });
    return false;
  }
  return true;
}

async function confirmarCambioEstado(nuevoEstado, nombreUsuario) {
  const confirmacion = await Swal.fire({
    icon: 'question',
    title: nuevoEstado ? '¿Activar usuario?' : '¿Desactivar usuario?',
    text: nuevoEstado
      ? `Se activará el usuario "${nombreUsuario}".`
      : `Se desactivará el usuario "${nombreUsuario}".`,
    showCancelButton: true,
    confirmButtonText: nuevoEstado ? 'Sí, activar' : 'Sí, desactivar',
    cancelButtonText: 'Cancelar'
  });
  return confirmacion.isConfirmed;
}

function actualizarUsuarioEnLista(idUsuario, nuevoEstado) {
  const userIndex = users.value.findIndex(u => u.id_usuario === idUsuario);
  if (userIndex !== -1) {
    users.value[userIndex].estado = nuevoEstado;
    emit('usuario-actualizado', users.value[userIndex]);
  }
}

function actualizarUsuarioEnModal(nuevoEstado) {
  if (!usuarioDetalle.value) return;

  if (usuarioDetalle.value.usuario) {
    usuarioDetalle.value.usuario.estado = nuevoEstado;
  } else {
    usuarioDetalle.value.estado = nuevoEstado;
  }
}

async function mostrarExitoCambioEstado(nuevoEstado, nombreUsuario) {
  await Swal.fire({
    icon: 'success',
    title: nuevoEstado ? 'Usuario activado' : 'Usuario desactivado',
    text: nuevoEstado
      ? `El usuario "${nombreUsuario}" se activó correctamente.`
      : `El usuario "${nombreUsuario}" se desactivó correctamente.`,
    timer: 1500,
    showConfirmButton: false
  });
}

async function cambiarEstadoUsuario(idUsuario, nuevoEstado) {
  const response = await usuariosService.cambiarEstadoUsuario(idUsuario, nuevoEstado);
  if (!response.success) {
    throw new Error(response.error || 'Error al cambiar estado del usuario');
  }
  return response;
}

// Cambiar estado de usuario (activar/desactivar)
async function toggleEstadoUsuario(user) {
  const idUsuario = obtenerIdUsuario(user);

  if (!(await validarCambioEstadoPropio(idUsuario))) {
    return;
  }

  const estadoActual = obtenerEstadoActual(user);
  const nuevoEstado = !estadoActual;
  const nombreUsuario = obtenerNombreUsuarioLegible(user);

  if (!(await confirmarCambioEstado(nuevoEstado, nombreUsuario))) {
    return;
  }

  try {
    loading.value = true;
    error.value = null;

    await cambiarEstadoUsuario(idUsuario, nuevoEstado);

    actualizarUsuarioEnLista(idUsuario, nuevoEstado);
    actualizarUsuarioEnModal(nuevoEstado);
    await mostrarExitoCambioEstado(nuevoEstado, nombreUsuario);
  } catch (err) {
    error.value = err.message;
    console.error('Error al cambiar estado del usuario:', err);
    await Swal.fire({
      icon: 'error',
      title: 'No se pudo cambiar el estado',
      text: err.message || 'Intenta nuevamente en unos minutos.'
    });
  } finally {
    loading.value = false;
  }
}

// Abrir modal de edición con datos actuales
function abrirModalEdicion(user) {
  console.log('abrirModalEdicion llamada con:', user);
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
  normalizarFormularioEdicion();
  resetErroresCampos();
  errorEdicion.value = null;
  mostrarModalEdicion.value = true;
  console.log('mostrarModalEdicion.value =', mostrarModalEdicion.value);
}

function construirHtmlErrores(errores) {
  const itemsErrores = errores.map(err => `<li>${err}</li>`).join('');
  return `<ul style="text-align:left;margin:0;padding-left:18px;">${itemsErrores}</ul>`;
}

async function cerrarModalEdicion() {
  // Verificar si hay cambios sin guardar
  const tieneCambios = verificarCambiosSinGuardar();

  if (tieneCambios) {
    const result = await Swal.fire({
      icon: 'question',
      title: '¿Cerrar edición?',
      text: '¿Estás seguro de que deseas cerrar el formulario? Los cambios no guardados se perderán.',
      showCancelButton: true,
      confirmButtonText: 'Sí, cerrar',
      cancelButtonText: 'Continuar editando',
      confirmButtonColor: '#dc3545',
      cancelButtonColor: '#6c757d'
    });

    if (!result.isConfirmed) {
      return;
    }
  }

  mostrarModalEdicion.value = false;
  errorEdicion.value = null;
  resetErroresCampos();
}

function verificarCambiosSinGuardar() {
  if (!usuarioDetalle.value) return false;

  const usuarioForm = formularioEdicion.value.datos_usuario || {};
  const personaForm = formularioEdicion.value.datos_persona || {};
  const usuarioOriginal = usuarioDetalle.value.usuario || {};
  const personaOriginal = usuarioDetalle.value.persona || {};

  // Comparar username
  if (usuarioForm.usuario !== (usuarioOriginal.usuario || '')) {
    return true;
  }

  // Comparar campos de persona
  const camposPersona = ['primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'documento', 'correo_electronico', 'telefono', 'direccion'];
  for (const campo of camposPersona) {
    const valorForm = personaForm[campo] || '';
    const valorOriginal = personaOriginal[campo] || '';
    if (valorForm.trim() !== valorOriginal.trim()) {
      return true;
    }
  }

  return false;
}

function validarUsername(username, nuevosErrores, errores) {
  if (!username || username.length < 4 || !/^[a-z0-9._-]+$/i.test(username)) {
    nuevosErrores.username = 'Mínimo 4 caracteres, solo letras, números, punto, guion o guion bajo.';
    errores.push('El username debe tener al menos 4 caracteres y solo puede incluir letras, números, puntos, guiones o guiones bajos.');
  }
}

function validarNombre(nombre, campo, etiqueta, nuevosErrores, errores) {
  if (!nombre || nombre.length < 2) {
    nuevosErrores[campo] = 'Debes ingresar al menos 2 letras.';
    errores.push(`El ${etiqueta} es obligatorio y debe tener al menos 2 caracteres.`);
  }
}

function validarDocumento(documento, nuevosErrores, errores) {
  if (!documento || documento.length < DOC_MIN || documento.length > DOC_MAX) {
    nuevosErrores.documento = `Debe tener entre ${DOC_MIN} y ${DOC_MAX} dígitos.`;
    errores.push(`El documento debe tener entre ${DOC_MIN} y ${DOC_MAX} dígitos.`);
  }
}

function validarCorreo(correo, nuevosErrores, errores) {
  if (!correo || !emailRegex.test(correo)) {
    nuevosErrores.correo_electronico = 'Correo inválido.';
    errores.push('Debes ingresar un correo electrónico válido.');
  }
}

function validarTelefono(telefono, nuevosErrores, errores) {
  if (telefono && (telefono.length < PHONE_MIN || telefono.length > PHONE_MAX)) {
    nuevosErrores.telefono = `Debe tener entre ${PHONE_MIN} y ${PHONE_MAX} dígitos.`;
    errores.push(`El teléfono debe tener entre ${PHONE_MIN} y ${PHONE_MAX} dígitos si lo proporcionas.`);
  }
}

function validarDireccion(direccion, nuevosErrores, errores) {
  if (direccion && direccion.length < 5) {
    nuevosErrores.direccion = 'Debe tener al menos 5 caracteres.';
    errores.push('La dirección debe tener al menos 5 caracteres.');
  }
}

function validarFormularioEdicion(datos) {
  const errores = [];
  const nuevosErrores = {
    username: '',
    primer_nombre: '',
    segundo_nombre: '',
    primer_apellido: '',
    segundo_apellido: '',
    documento: '',
    correo_electronico: '',
    telefono: '',
    direccion: ''
  };

  validarUsername(datos.username, nuevosErrores, errores);
  validarNombre(datos.primerNombre, 'primer_nombre', 'primer nombre', nuevosErrores, errores);
  validarNombre(datos.primerApellido, 'primer_apellido', 'primer apellido', nuevosErrores, errores);
  validarDocumento(datos.documento, nuevosErrores, errores);
  validarCorreo(datos.correo, nuevosErrores, errores);
  validarTelefono(datos.telefono, nuevosErrores, errores);
  validarDireccion(datos.direccion, nuevosErrores, errores);

  return { errores, nuevosErrores };
}

async function mostrarErroresValidacion(errores) {
  await Swal.fire({
    icon: 'error',
    title: 'Corrige los campos',
    html: construirHtmlErrores(errores)
  });
}

async function guardarEdicion() {
  if (!usuarioDetalle.value) return;
  normalizarFormularioEdicion();

  const idUsuario = usuarioDetalle.value.usuario?.id_usuario || usuarioDetalle.value.id_usuario;
  const usuarioForm = formularioEdicion.value.datos_usuario || {};
  const personaForm = formularioEdicion.value.datos_persona || {};

  const datos = {
    username: usuarioForm.usuario || '',
    primerNombre: personaForm.primer_nombre || '',
    segundoNombre: personaForm.segundo_nombre || '',
    primerApellido: personaForm.primer_apellido || '',
    segundoApellido: personaForm.segundo_apellido || '',
    documento: personaForm.documento || '',
    correo: personaForm.correo_electronico || '',
    telefono: personaForm.telefono || '',
    direccion: personaForm.direccion || ''
  };

  const { errores, nuevosErrores } = validarFormularioEdicion(datos);

  if (errores.length > 0) {
    erroresCamposEdicion.value = nuevosErrores;
    errorEdicion.value = errores[0];
    await mostrarErroresValidacion(errores);
    return;
  }

  // Verificar si hay cambios antes de continuar
  const tieneCambios = verificarCambiosSinGuardar();

  if (!tieneCambios) {
    await Swal.fire({
      icon: 'info',
      title: 'Sin cambios',
      text: 'No se han realizado modificaciones en los datos del usuario. No hay nada que guardar.',
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#004AAD'
    });
    return;
  }

  // Confirmar antes de guardar
  const nombreUsuario = datos.username || usuarioDetalle.value.usuario?.usuario || 'usuario';
  const confirmacion = await Swal.fire({
    icon: 'question',
    title: '¿Guardar cambios?',
    text: `¿Estás seguro de que deseas guardar los cambios en el usuario "${nombreUsuario}"?`,
    showCancelButton: true,
    confirmButtonText: 'Sí, guardar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#004AAD',
    cancelButtonColor: '#6c757d'
  });

  if (!confirmacion.isConfirmed) {
    return;
  }

  erroresCamposEdicion.value = nuevosErrores;

  const payload = {
    datos_usuario: {
      usuario: datos.username
    },
    datos_persona: {
      primer_nombre: datos.primerNombre,
      segundo_nombre: datos.segundoNombre,
      primer_apellido: datos.primerApellido,
      segundo_apellido: datos.segundoApellido,
      documento: datos.documento,
      correo_electronico: datos.correo,
      telefono: datos.telefono,
      direccion: datos.direccion
    }
  };

  // Mostrar loading mientras se procesa
  Swal.fire({
    title: 'Guardando cambios...',
    text: 'Por favor espera mientras procesamos tu solicitud.',
    allowOutsideClick: false,
    allowEscapeKey: false,
    didOpen: () => {
      Swal.showLoading();
    }
  });

  try {
    guardandoEdicion.value = true;
    errorEdicion.value = null;
    const resp = await usuariosService.actualizarUsuario(idUsuario, payload);

    // Cerrar el loading
    Swal.close();

    if (!resp.success) {
      const mensajeError = extraerMensajeErrorUsuario(resp.error);
      await Swal.fire({
        icon: 'error',
        title: 'Error al actualizar usuario',
        html: `<p><strong>No se pudieron guardar los cambios.</strong></p><p>${mensajeError}</p>`,
        confirmButtonText: 'Entendido',
        confirmButtonColor: '#dc3545'
      });
      errorEdicion.value = mensajeError;
      return;
    }

    // Actualizar en tabla
    const idx = users.value.findIndex(u => u.id_usuario === idUsuario);
    if (idx !== -1) {
      if (payload.datos_usuario?.usuario) {
        users.value[idx].usuario = payload.datos_usuario.usuario;
      }
      if (users.value[idx].persona) {
        Object.assign(users.value[idx].persona, payload.datos_persona || {});
      }
      emit('usuario-actualizado', users.value[idx]);
    }

    // Refrescar detalle
    const refreshed = await usuariosService.obtenerDetalleUsuario(idUsuario);
    if (refreshed.success) {
      usuarioDetalle.value = refreshed.data;
    }

    formularioEdicion.value = structuredClone(payload);

    // Éxito: mostrar notificación de confirmación
    await Swal.fire({
      icon: 'success',
      title: '¡Usuario actualizado exitosamente!',
      text: `Los cambios en el usuario "${nombreUsuario}" se han guardado correctamente.`,
      confirmButtonText: 'Aceptar',
      confirmButtonColor: '#004AAD'
    });

    cerrarModalEdicion();
  } catch (e) {
    // Cerrar el loading si aún está abierto
    Swal.close();

    console.error(e);
    const mensajeError = extraerMensajeErrorUsuario(e);
    errorEdicion.value = mensajeError;

    await Swal.fire({
      icon: 'error',
      title: 'Error al actualizar usuario',
      html: `<p><strong>Ocurrió un error inesperado.</strong></p><p>${mensajeError}</p>`,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    });
  } finally {
    guardandoEdicion.value = false;
  }
}

// Aliases for consistency with component naming
const extraerMensajeErrorUsuario = extraerMensajeError

// Abrir gestión de roles
function abrirGestionRoles(user) {
  console.log('abrirGestionRoles llamada con:', user);
  usuarioParaRoles.value = user;
  errorRoles.value = null;

  // Obtener los roles actuales del usuario (solo Administrador y Entrenador)
  const rolesActuales = (user.roles || []).filter(rol => {
    const nombreLower = rol.nombre_rol?.toLowerCase() || '';
    return nombreLower === 'administrador' || nombreLower === 'entrenador';
  });

  // Mapear los roles actuales a sus IDs
  const rolesIds = rolesActuales.map(rol => rol.id_rol);
  rolesSeleccionados.value = [...rolesIds];
  rolesIniciales.value = [...rolesIds]; // Guardar una copia para comparar cambios

  console.log('Roles iniciales:', rolesIniciales.value);
  console.log('Roles seleccionados:', rolesSeleccionados.value);

  mostrarModalRoles.value = true;
  console.log('mostrarModalRoles.value =', mostrarModalRoles.value);
}

// Cerrar modal de gestión de roles
async function cerrarModalRoles() {
  // Verificar si hay cambios sin guardar
  const tieneCambios = verificarCambiosRoles();

  console.log('Verificando cambios al cerrar:', {
    tieneCambios,
    rolesIniciales: rolesIniciales.value,
    rolesSeleccionados: rolesSeleccionados.value
  });

  if (tieneCambios) {
    const result = await Swal.fire({
      icon: 'question',
      title: '¿Cerrar gestión de roles?',
      text: '¿Estás seguro de que deseas cerrar? Los cambios en los roles no guardados se perderán.',
      showCancelButton: true,
      confirmButtonText: 'Sí, cerrar',
      cancelButtonText: 'Continuar',
      confirmButtonColor: '#dc3545',
      cancelButtonColor: '#6c757d'
    });

    if (!result.isConfirmed) {
      return;
    }
  }

  mostrarModalRoles.value = false;
  usuarioParaRoles.value = null;
  rolesSeleccionados.value = [];
  rolesIniciales.value = [];
  errorRoles.value = null;
}

function verificarCambiosRoles() {
  if (!usuarioParaRoles.value) {
    return false;
  }

  // Si rolesIniciales no está inicializado (array vacío o undefined), considerar que no hay cambios iniciales
  // pero si rolesSeleccionados tiene elementos, entonces hay cambios
  if (rolesIniciales.value.length === 0) {
    return rolesSeleccionados.value.length > 0;
  }

  // Si rolesSeleccionados está vacío pero rolesIniciales tiene elementos, hay cambios
  if (rolesSeleccionados.value.length === 0 && rolesIniciales.value.length > 0) {
    return true;
  }

  // Comparar arrays de roles (orden no importa)
  const rolesInicialesSorted = [...rolesIniciales.value].sort((a, b) => a - b);
  const rolesSeleccionadosSorted = [...rolesSeleccionados.value].sort((a, b) => a - b);

  // Si las longitudes son diferentes, hay cambios
  if (rolesInicialesSorted.length !== rolesSeleccionadosSorted.length) {
    return true;
  }

  // Comparar elemento por elemento
  return rolesInicialesSorted.some((rol, index) => rol !== rolesSeleccionadosSorted[index]);
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

  // Verificar si hay cambios antes de continuar
  const tieneCambios = verificarCambiosRoles();

  if (!tieneCambios) {
    await Swal.fire({
      icon: 'info',
      title: 'Sin cambios',
      text: 'No se han realizado modificaciones en los roles del usuario. No hay nada que guardar.',
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#004AAD'
    });
    return;
  }

  const idUsuario = usuarioParaRoles.value.usuario?.id_usuario || usuarioParaRoles.value.id_usuario;
  const nombreUsuario = usuarioParaRoles.value.usuario?.usuario || usuarioParaRoles.value.usuario || 'usuario';

  // Confirmar antes de guardar
  const confirmacion = await Swal.fire({
    icon: 'question',
    title: '¿Guardar cambios de roles?',
    text: `¿Estás seguro de que deseas guardar los cambios en los roles del usuario "${nombreUsuario}"?`,
    showCancelButton: true,
    confirmButtonText: 'Sí, guardar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#004AAD',
    cancelButtonColor: '#6c757d'
  });

  if (!confirmacion.isConfirmed) {
    return;
  }

  // Mostrar loading mientras se procesa
  Swal.fire({
    title: 'Guardando roles...',
    text: 'Por favor espera mientras procesamos tu solicitud.',
    allowOutsideClick: false,
    allowEscapeKey: false,
    didOpen: () => {
      Swal.showLoading();
    }
  });

  try {
    guardandoRoles.value = true;
    errorRoles.value = null;

    // Enviar los roles seleccionados al backend
    const response = await usuariosService.cambiarRolUsuario(idUsuario, rolesSeleccionados.value);

    // Cerrar el loading
    Swal.close();

    if (!response.success) {
      const mensajeError = extraerMensajeErrorRoles(response.error);
      await Swal.fire({
        icon: 'error',
        title: 'Error al actualizar roles',
        html: `<p><strong>No se pudieron guardar los cambios.</strong></p><p>${mensajeError}</p>`,
        confirmButtonText: 'Entendido',
        confirmButtonColor: '#dc3545'
      });
      errorRoles.value = mensajeError;
      return;
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

    // Actualizar roles iniciales con los nuevos roles guardados
    const rolesActualizadosIds = rolesActualizados
      .filter(rol => {
        const nombreLower = rol.nombre_rol?.toLowerCase() || '';
        return nombreLower === 'administrador' || nombreLower === 'entrenador';
      })
      .map(rol => rol.id_rol);
    rolesIniciales.value = [...rolesActualizadosIds];

    // Éxito: mostrar notificación de confirmación
    await Swal.fire({
      icon: 'success',
      title: '¡Roles actualizados exitosamente!',
      text: `Los roles del usuario "${nombreUsuario}" se han guardado correctamente.`,
      confirmButtonText: 'Aceptar',
      confirmButtonColor: '#004AAD'
    });

    cerrarModalRoles();
  } catch (err) {
    // Cerrar el loading si aún está abierto
    Swal.close();

    console.error('Error al guardar roles:', err);
    const mensajeError = extraerMensajeErrorRoles(err);
    errorRoles.value = mensajeError;

    await Swal.fire({
      icon: 'error',
      title: 'Error al actualizar roles',
      html: `<p><strong>Ocurrió un error inesperado.</strong></p><p>${mensajeError}</p>`,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    });
  } finally {
    guardandoRoles.value = false;
  }
}

// Alias for roles error extraction
const extraerMensajeErrorRoles = extraerMensajeError

function roleColor(role) {
  switch (role) {
    case "SuperAdmin":
      // SuperAdmin usa el mismo color que Administrador (rojo)
      return "badge-admin badge-administrador";
    case "Administrador":
      return "badge-admin badge-administrador";
    case "Entrenador":
      return "badge-moderator badge-entrenador";
    case "Deportista":
      return "badge-user badge-deportista";
    case "Acudiente":
      return "badge-user badge-acudiente";
    default:
      return "badge-user badge-usuario";
  }
}
</script>
