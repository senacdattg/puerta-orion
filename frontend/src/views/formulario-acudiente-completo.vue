<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import authService from '@/services/authService';
import { API_CONFIG } from '@/config/environment';
import { useAuthStore } from '@/stores/auth';

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
    alert('Error al cargar los datos del usuario');
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
    alert('Debe buscar y seleccionar un deportista primero');
    return;
  }

  // Validar que se haya seleccionado un parentesco
  if (!idParentesco.value) {
    alert('Debe seleccionar el parentesco con el deportista');
    return;
  }

  // Validar que el usuario no se esté acudiendo a sí mismo
  // Obtener información del usuario actual
  const usuarioActual = authStore.user;
  const idPersonaUsuario = usuarioActual?.persona?.id_persona || usuarioActual?.id_persona;
  
  // Verificar si el deportista encontrado tiene el mismo id_persona que el usuario actual
  if (deportistaEncontrado.value.id_persona === idPersonaUsuario || 
      deportistaEncontrado.value.persona?.id_persona === idPersonaUsuario) {
    alert('No puedes acudirte a ti mismo. Un deportista no puede ser su propio acudiente.');
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
      alert(resultado.message || "¡Perfil de acudiente completado exitosamente!");

      // Recargar el perfil del usuario para actualizar los roles en el store
      try {
        await authStore.loadUserProfile();
        
        // Establecer automáticamente el rol activo como 'Acudiente' si el usuario tiene ese rol
        const roles = authStore.userRoles || [];
        if (roles.includes('Acudiente')) {
          await authStore.setActiveRole('Acudiente');
          console.log('✅ Rol activo establecido como Acudiente');
          
          // Verificar que el activeRole se estableció correctamente antes de redirigir
          if (authStore.activeRole === 'Acudiente') {
            // Redirigir al dashboard del acudiente
            router.push('/acudiente/dashboard');
          } else {
            // Si no se estableció, esperar un momento y redirigir de todas formas
            setTimeout(() => {
              router.push('/acudiente/dashboard');
            }, 500);
          }
        } else {
          // Si no tiene el rol de Acudiente aún, redirigir de todas formas
          setTimeout(() => {
            router.push('/acudiente/dashboard');
          }, 500);
        }
      } catch (error) {
        console.warn('No se pudo recargar el perfil en el store, pero el registro fue exitoso:', error);
        // Redirigir de todas formas en caso de error
        setTimeout(() => {
          router.push('/acudiente/dashboard');
        }, 500);
      }
    } else {
      alert(`Error: ${resultado.error}`);
    }
  } catch (error) {
    console.error("Error al completar perfil de acudiente:", error);
    alert("Error al completar el perfil. Por favor intenta nuevamente.");
  } finally {
    cargando.value = false;
  }
}

// Función para manejar la cancelación
function manejarCancelacion() {
  if (confirm("¿Está seguro de que desea cancelar el registro? Se perderá toda la información ingresada.")) {
    // Determinar la ruta de redirección según el rol del usuario
    const userRoles = authStore.userRoles || [];
    const roleNames = userRoles.map(role => typeof role === 'string' ? role : role.nombre_rol);
    
    // Si tiene rol activo, usar ese
    if (authStore.activeRole) {
      switch(authStore.activeRole) {
        case 'SuperAdmin':
        case 'Administrador':
          router.push('/admin-manager');
          return;
        case 'Entrenador':
          router.push('/home');
          return;
        case 'Deportista':
          router.push('/deportista/dashboard');
          return;
        case 'Acudiente':
          router.push('/acudiente/dashboard');
          return;
        default:
          router.push('/home');
          return;
      }
    }
    
    // Si no hay rol activo, verificar roles del usuario
    if (roleNames.length === 1) {
      const singleRole = roleNames[0];
      switch(singleRole) {
        case 'SuperAdmin':
        case 'Administrador':
          router.push('/admin-manager');
          return;
        case 'Entrenador':
          router.push('/home');
          return;
        case 'Deportista':
          router.push('/deportista/dashboard');
          return;
        case 'Acudiente':
          router.push('/acudiente/dashboard');
          return;
        default:
          router.push('/home');
          return;
      }
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

<style scoped>
.cargando-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #0047ab;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.cargando-container p {
  color: #666;
  font-size: 1.1rem;
  margin: 0;
}

.card-formulario {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  margin: 0 auto;
}

.titulo-formulario {
  font-size: 1.8rem;
  color: #333;
  margin-bottom: 0.5rem;
  text-align: center;
}

.descripcion-formulario {
  color: #666;
  text-align: center;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.seccion-busqueda,
.seccion-relacion {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.subtitulo-seccion {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 1rem;
}

.campo-busqueda {
  width: 100%;
}

.input-busqueda {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.input-busqueda input {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
}

.input-busqueda input:focus {
  outline: none;
  border-color: #0047ab;
}

.btn-buscar {
  padding: 0.75rem 1.5rem;
  background: #0047ab;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.3s;
}

.btn-buscar:hover:not(:disabled) {
  background: #003d91;
}

.btn-buscar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.mensaje-busqueda {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.mensaje-busqueda.success {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.mensaje-busqueda.error {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

.mensaje-busqueda.warning {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  color: #856404;
}

.mensaje-busqueda strong {
  display: block;
  margin-bottom: 0.5rem;
}

.mensaje-busqueda p {
  margin: 0.25rem 0;
}

.sugerencia {
  font-style: italic;
  margin-top: 0.5rem;
}

.info-deportista-encontrado {
  margin-top: 1rem;
}

.card-deportista {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #28a745;
}

.card-deportista h4 {
  color: #28a745;
  margin-bottom: 1rem;
}

.card-deportista p {
  margin: 0.5rem 0;
  color: #333;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 600;
}

.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
}

.form-group select:focus {
  outline: none;
  border-color: #0047ab;
}

.form-group-checkbox {
  margin-bottom: 1.5rem;
}

.form-group-checkbox label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: normal;
}

.form-group-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.btn-primary {
  padding: 0.75rem 2rem;
  background: #0047ab;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background: #003d91;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 0.75rem 2rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
}

.texto-cargando {
  color: #0047ab;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  font-style: italic;
}

.texto-error {
  color: #dc3545;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
</style>
