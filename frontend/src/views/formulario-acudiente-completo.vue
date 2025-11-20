<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import authService from '@/services/authService';
import { API_CONFIG } from '@/config/environment';
import { useAuthStore } from '@/stores/auth';
import Swal from 'sweetalert2';

const router = useRouter();
const authStore = useAuthStore();
const datosUsuario = ref({});
const cargando = ref(false);

// Datos para asociación con deportista
const cedulaBuscada = ref('');
const isSearchingDeportista = ref(false);
const deportistaEncontrado = ref(null);
const mensajeBusquedaDeportista = ref(null);
const parentescos = ref([]);
const idParentesco = ref('');
const esResponsable = ref(false);
const cargandoParentescos = ref(false);

// Cargar datos del usuario al montar el componente
onMounted(async () => {
  try {
    const perfil = await authService.getProfile();
    datosUsuario.value = perfil.data || {};
    console.log('Datos del usuario cargados:', datosUsuario.value);

    // Verificar si el usuario ya tiene el rol de acudiente
    if (datosUsuario.value.roles && Array.isArray(datosUsuario.value.roles)) {
      const rolesNombre = datosUsuario.value.roles.map(r => r.nombre_rol || r);
      const esAcudiente = rolesNombre.some(rol =>
        rol.toLowerCase().includes('acudiente') || rol.toLowerCase() === 'acudiente'
      );

      if (esAcudiente) {
        console.log('Usuario ya tiene rol de acudiente, redirigiendo al home...');
        router.push('/home');
        return;
      }
    }

    // Cargar parentescos
    await cargarParentescos();
  } catch (error) {
    console.error('Error al cargar datos del usuario:', error);
    await Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No pudimos cargar tus datos. Intenta nuevamente.'
    });
  }
});

// Función para cargar parentescos
async function cargarParentescos() {
  cargandoParentescos.value = true;
  try {
    console.log('🔄 Cargando parentescos desde:', `${API_CONFIG.baseURL}/api/catalogos/parentescos`);
    const response = await fetch(`${API_CONFIG.baseURL}/api/catalogos/parentescos`);

    console.log('📡 Respuesta recibida:', response.status, response.statusText);

    if (!response.ok) {
      console.error('❌ Error en la respuesta:', response.status, response.statusText);
      const errorData = await response.json().catch(() => ({ error: 'Error desconocido' }));
      console.error('❌ Datos del error:', errorData);

      mensajeBusquedaDeportista.value = {
        tipo: 'error',
        titulo: 'Error',
        mensaje: `Error al cargar parentescos: ${errorData.error || response.statusText}`
      };
      return;
    }

    const result = await response.json();
    console.log('✅ Resultado de parentescos:', result);

    if (result.success) {
      parentescos.value = result.data || [];
      console.log(`✅ Parentescos cargados: ${parentescos.value.length}`);

      if (parentescos.value.length === 0) {
        console.warn('⚠️ No se encontraron parentescos en la base de datos');
        mensajeBusquedaDeportista.value = {
          tipo: 'warning',
          titulo: 'Advertencia',
          mensaje: 'No hay parentescos disponibles. Contacte al administrador.'
        };
      }
    } else {
      console.error('❌ Error en resultado:', result);
      mensajeBusquedaDeportista.value = {
        tipo: 'error',
        titulo: 'Error',
        mensaje: result.error || 'Error al cargar parentescos'
      };
    }
  } catch (error) {
    console.error('❌ Error al cargar parentescos:', error);
    mensajeBusquedaDeportista.value = {
      tipo: 'error',
      titulo: 'Error de conexión',
      mensaje: `No se pudo conectar al servidor. Verifique que el backend esté corriendo en ${API_CONFIG.baseURL}`
    };
  } finally {
    cargandoParentescos.value = false;
  }
}

// Función para buscar deportista por cédula
async function buscarDeportistaPorCedula() {
  if (!cedulaBuscada.value || !cedulaBuscada.value.trim()) {
    mensajeBusquedaDeportista.value = {
      tipo: 'error',
      titulo: 'Error',
      mensaje: 'Por favor ingrese un número de cédula'
    };
    return;
  }

  isSearchingDeportista.value = true;
  mensajeBusquedaDeportista.value = null;
  deportistaEncontrado.value = null;

  try {
    const response = await fetch(`${API_CONFIG.baseURL}/api/catalogos/deportistas?cedula=${cedulaBuscada.value}`);
    const result = await response.json();

    if (response.ok && result.success) {
      deportistaEncontrado.value = result.data;
      mensajeBusquedaDeportista.value = {
        tipo: 'success',
        titulo: '✓ Éxito',
        mensaje: 'Deportista encontrado exitosamente'
      };
    } else {
      mensajeBusquedaDeportista.value = {
        tipo: 'warning',
        titulo: '⚠ Deportista no encontrado',
        mensaje: result.message || 'No se encontró un deportista con ese documento',
        sugerencia: result.sugerencia || 'El deportista debe estar registrado en el sistema'
      };
      deportistaEncontrado.value = null;
    }
  } catch (error) {
    console.error('Error al buscar deportista:', error);
    mensajeBusquedaDeportista.value = {
      tipo: 'error',
      titulo: 'Error',
      mensaje: 'Error al buscar deportista. Por favor, intente de nuevo.'
    };
  } finally {
    isSearchingDeportista.value = false;
  }
}

// Función para manejar el registro completo de acudiente
async function completarRegistroAcudiente() {
  // Validar que se haya encontrado un deportista
  if (!deportistaEncontrado.value) {
    await Swal.fire({
      icon: 'warning',
      title: 'Falta seleccionar deportista',
      text: 'Busca y selecciona un deportista antes de continuar.'
    });
    return;
  }

  // Validar que se haya seleccionado un parentesco
  if (!idParentesco.value) {
    await Swal.fire({
      icon: 'warning',
      title: 'Parentesco requerido',
      text: 'Selecciona el parentesco con el deportista.'
    });
    return;
  }

  // Validar que el usuario no se esté acudiendo a sí mismo
  // Obtener información del usuario actual
  const usuarioActual = authStore.user;
  const idPersonaUsuario = usuarioActual?.persona?.id_persona || usuarioActual?.id_persona;

  // Verificar si el deportista encontrado tiene el mismo id_persona que el usuario actual
  if (deportistaEncontrado.value.id_persona === idPersonaUsuario ||
      deportistaEncontrado.value.persona?.id_persona === idPersonaUsuario) {
    await Swal.fire({
      icon: 'info',
      title: 'Acción no permitida',
      text: 'No puedes acudirte a ti mismo. Un deportista no puede ser su propio acudiente.'
    });
    return;
  }

  cargando.value = true;

  try {
    const datosAcudiente = {
      id_deportista: deportistaEncontrado.value.id_deportista,
      id_parentesco: parseInt(idParentesco.value),
      es_responsable: esResponsable.value
    };

    console.log("Datos del acudiente a enviar:", datosAcudiente);

    const resultado = await authService.completarPerfilAcudiente(datosAcudiente);

    if (resultado.success) {
      await Swal.fire({
        icon: 'success',
        title: 'Perfil completado',
        text: resultado.message || '¡Perfil de acudiente completado exitosamente!',
        confirmButtonText: 'Continuar'
      });

      // Recargar el perfil del usuario para actualizar los roles en el store
      try {
        await authStore.loadUserProfile();

        // Establecer automáticamente el rol activo como 'Acudiente' si el usuario tiene ese rol
        const roles = authStore.userRoles || [];
        if (roles.includes('Acudiente')) {
          await authStore.setActiveRole('Acudiente');
          console.log('✅ Rol activo establecido como Acudiente');

          router.push('/acudiente/dashboard');
        } else {
          router.push('/acudiente/dashboard');
        }
      } catch (error) {
        console.warn('No se pudo recargar el perfil en el store, pero el registro fue exitoso:', error);
        // Redirigir de todas formas en caso de error
        router.push('/acudiente/dashboard');
      }
    } else {
      await Swal.fire({
        icon: 'error',
        title: 'No se pudo completar',
        text: resultado.error || 'Ocurrió un error al completar el registro.'
      });
    }
  } catch (error) {
    console.error("Error al completar perfil de acudiente:", error);
    await Swal.fire({
      icon: 'error',
      title: 'Error de conexión',
      text: 'No pudimos completar el perfil. Intenta nuevamente.'
    });
  } finally {
    cargando.value = false;
  }
}

// Función para manejar la cancelación
async function manejarCancelacion() {
  const resultado = await Swal.fire({
    icon: 'question',
    title: '¿Cancelar registro?',
    text: 'Se perderá toda la información ingresada.',
    showCancelButton: true,
    confirmButtonText: 'Sí, cancelar',
    cancelButtonText: 'Continuar'
  });
  if (resultado.isConfirmed) {
    // Determinar la ruta de redirección según el rol del usuario
    const userRoles = authStore.userRoles || [];
    const roleNames = userRoles.map(role => typeof role === 'string' ? role : role.nombre_rol);

    const obtenerRutaPorRol = (rol) => {
      switch(rol) {
        case 'SuperAdmin':
        case 'Administrador':
          return '/admin-manager'
        case 'Deportista':
          return '/deportista/dashboard'
        case 'Acudiente':
          return '/acudiente/dashboard'
        case 'Entrenador':
        default:
          return '/home'
      }
    }

    // Si tiene rol activo, usar ese
    if (authStore.activeRole) {
      router.push(obtenerRutaPorRol(authStore.activeRole))
      return
    }

    // Si no hay rol activo, verificar roles del usuario
    if (roleNames.length === 1) {
      router.push(obtenerRutaPorRol(roleNames[0]))
      return
    }

    // Si tiene múltiples roles, redirigir a selección de rol
    if (roleNames.length > 1) {
      router.push('/seleccionar-rol');
      return;
    }

    // Por defecto, ir a home
    router.push('/home');
  }
}
</script>

<template>
  <main>
    <div class="contenido-principal-tarjetas">
      <div class="card-formulario">
        <h2 class="titulo-formulario">Registro como Acudiente</h2>
        <p class="descripcion-formulario">
          Para completar tu registro como acudiente, debes asociarte con un deportista.
          Busca el deportista por su número de documento y completa la información solicitada.
        </p>

        <!-- Búsqueda de deportista -->
        <div class="seccion-busqueda">
          <h3 class="subtitulo-seccion">1. Buscar Deportista</h3>
          <div class="campo-busqueda">
            <div class="input-busqueda">
              <input
                type="text"
                v-model="cedulaBuscada"
                placeholder="Ingrese el número de documento del deportista"
                :disabled="isSearchingDeportista"
                @keyup.enter="buscarDeportistaPorCedula"
              />
              <button
                type="button"
                class="btn-buscar"
                @click="buscarDeportistaPorCedula"
                :disabled="isSearchingDeportista || !cedulaBuscada.trim()"
              >
                <span v-if="isSearchingDeportista">Buscando...</span>
                <span v-else>🔍 Buscar</span>
              </button>
            </div>

            <!-- Mensaje de búsqueda -->
            <div v-if="mensajeBusquedaDeportista" :class="['mensaje-busqueda', mensajeBusquedaDeportista.tipo]">
              <strong>{{ mensajeBusquedaDeportista.titulo }}</strong>
              <p>{{ mensajeBusquedaDeportista.mensaje }}</p>
              <p v-if="mensajeBusquedaDeportista.sugerencia" class="sugerencia">
                {{ mensajeBusquedaDeportista.sugerencia }}
              </p>
            </div>

            <!-- Información del deportista encontrado -->
            <div v-if="deportistaEncontrado" class="info-deportista-encontrado">
              <div class="card-deportista">
                <h4>✓ Deportista Encontrado</h4>
                <p><strong>Nombre:</strong> {{ deportistaEncontrado.persona?.nombre_completo }}</p>
                <p><strong>Documento:</strong> {{ deportistaEncontrado.persona?.documento }}</p>
                <p><strong>Correo:</strong> {{ deportistaEncontrado.persona?.correo_electronico }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Información de relación -->
        <div v-if="deportistaEncontrado" class="seccion-relacion">
          <h3 class="subtitulo-seccion">2. Información de Relación</h3>

          <div class="form-group">
            <label for="parentesco">Parentesco con el deportista *</label>
            <select
              id="parentesco"
              v-model="idParentesco"
              required
              :disabled="cargando || cargandoParentescos"
            >
              <option value="">{{ cargandoParentescos ? 'Cargando parentescos...' : parentescos.length === 0 ? 'No hay parentescos disponibles' : 'Seleccione el parentesco' }}</option>
              <option v-for="parentesco in parentescos" :key="parentesco.id_parentesco" :value="parentesco.id_parentesco">
                {{ parentesco.nombre }}
              </option>
            </select>
            <p v-if="cargandoParentescos" class="texto-cargando">⏳ Cargando parentescos...</p>
            <p v-else-if="parentescos.length === 0" class="texto-error">⚠️ No hay parentescos disponibles. Contacte al administrador o verifique que el backend esté corriendo.</p>
          </div>

          <div class="form-group-checkbox">
            <label>
              <input
                type="checkbox"
                v-model="esResponsable"
                :disabled="cargando"
              />
              ¿Es responsable legal del deportista?
            </label>
          </div>
        </div>

        <!-- Botones de acción -->
        <div class="form-actions">
          <button
            type="button"
            class="btn-secondary"
            @click="manejarCancelacion"
            :disabled="cargando"
          >
            Cancelar
          </button>
          <button
            type="button"
            class="btn-primary"
            @click="completarRegistroAcudiente"
            :disabled="cargando || !deportistaEncontrado || !idParentesco"
          >
            <span v-if="cargando">Guardando...</span>
            <span v-else>Completar Registro</span>
          </button>
        </div>
      </div>
    </div>
  </main>
</template>


