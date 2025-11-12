<template>
  <main class="admin-page">

        <!-- Header del Panel -->
        <div class="admin-header">
            <div class="container">
                <div class="header-content">
                    <div class="header-text">
                        <h1 class="page-title">Panel de Administración</h1>
                        <p class="page-subtitle">Gestiona usuarios, roles y configuraciones del club deportivo</p>
                    </div>
                    <div class="header-actions">
                        <button class="btn btn-nuevo" @click="abrirModalRegistro">
                            <i class="fas fa-plus"></i>
                            Nuevo Usuario
                        </button>
                        <button class="btn btn-datos" @click="abrirModalDatos">
                            <i class="fas fa-database"></i>
                            Añadir Datos
                        </button>
                    </div>
                </div>
            </div>
        </div>

    <!-- Dashboard Stats -->
    <section class="stats-section">
      <div class="container">
        <div class="stats-grid">
          <div v-for="tarjeta in tarjetasStats" :key="tarjeta.key" class="stat-card" :data-role="tarjeta.key">
            <div :class="['stat-icon', tarjeta.class]">
              <i :class="tarjeta.icon"></i>
            </div>
            <div class="stat-content">
              <span class="stat-number">{{ tarjeta.count }}</span>
              <span class="stat-label">{{ tarjeta.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <section class="main-content">
      <div class="container">
        <div class="content-grid">
          <!-- Panel de Usuarios -->
          <div class="content-panel">
            <div class="panel-header">
              <h2 class="panel-title">
                <i class="fas fa-users"></i>
                Gestión de Usuarios
              </h2>
              <div class="panel-actions">
                <button class="btn btn--small btn-filtros" @click="mostrarFiltros = !mostrarFiltros">
                  <i class="fas fa-filter"></i>
                  Filtros
                </button>
                <button class="btn btn--small btn-filtros" @click="mostrarBusqueda = !mostrarBusqueda">
                  <i class="fas fa-search"></i>
                  Buscar
                </button>
              </div>
            </div>
            <div class="panel-controls" v-if="mostrarFiltros || mostrarBusqueda">
              <div class="controls-grid">
                <div v-if="mostrarBusqueda" class="control-item">
                  <label class="control-label">Buscar usuario</label>
                  <input v-model="terminoBusqueda" type="text" placeholder="Nombre..." class="control-input" />
                </div>
                <div v-if="mostrarFiltros" class="control-item">
                  <label class="control-label">Filtrar por rol</label>
                  <select v-model="filtroRol" class="control-input">
                    <option v-for="opt in rolesOptions" :key="opt.value" :value="opt.value">
                      {{ opt.label }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
            <TablaUsuarios :search-term="terminoBusqueda" :role-filter="filtroRol" @usuarios-cargados="setUsuarios"
              @usuario-actualizado="actualizarUsuario" />
          </div>

        </div>
      </div>
    </section>

    <!-- Sección de Gestión de Datos Dinámicos -->
    <section class="main-content">
      <div class="container">
        <div class="content-panel">
          <div class="panel-header">
            <h2 class="panel-title">
              <i class="fas fa-database"></i>
              Gestión de Datos Base
            </h2>
            <div class="panel-actions">
              <button class="btn btn--small btn-primary" @click="abrirModalDatos">
                <i class="fas fa-plus"></i>
                Añadir Dato
              </button>
            </div>
          </div>
          <div class="panel-body">
            <TablaDatosDinamicos
              :recargar="recargarTablaDatos"
              @editar-dato="abrirModalEdicion"
              @crear-nuevo="abrirModalDatosConTema"
              @dato-eliminado="onDatoEliminado"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- Modal de Registro de Usuario -->
    <ModalRegistroUsuario :mostrar="mostrarModalRegistro" @cerrar="cerrarModalRegistro"
      @usuario-registrado="manejarUsuarioRegistrado" />

    <!-- Modal Añadir Datos -->
    <ModalAnadirDatos
      :mostrar="mostrarModalDatos"
      :tema-inicial="temaParaCrear"
      @cerrar="cerrarModalDatos"
      @guardar-dato="onGuardarDato"
    />

    <!-- Modal Editar Dato -->
    <ModalEditarDato
      :mostrar="mostrarModalEdicion"
      :tema="temaEdicion"
      :dato="datoEdicion"
      @cerrar="cerrarModalEdicion"
      @guardado="onDatoGuardado"
    />
  </main>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue';
import { API_CONFIG } from '@/config/environment';
import ModalRegistroUsuario from '@/components/admin/modal-registro-usuario.vue';
import ModalAnadirDatos from '@/components/admin/modal-anadir-datos.vue';
import ModalEditarDato from '@/components/admin/modal-editar-dato.vue';
import TablaUsuarios from '@/components/admin/tabla-usuarios.vue';
import TablaDatosDinamicos from '@/components/admin/tabla-datos-dinamicos.vue';
import usuariosService from '@/services/usuariosService';
import Swal from 'sweetalert2';

// Estado del modal
const mostrarModalRegistro = ref(false);
const mostrarModalDatos = ref(false);
const mostrarModalEdicion = ref(false);
const temaParaCrear = ref('');
const temaEdicion = ref('');
const datoEdicion = ref({});
const recargarTablaDatos = ref(false);
const mostrarFiltros = ref(false);
const mostrarBusqueda = ref(false);
const terminoBusqueda = ref('');
const filtroRol = ref('todos');

// Opciones de roles cargadas desde la API
const rolesOptions = ref([{ value: 'todos', label: 'Todos' }]);

// Usuarios para conteos
const usuariosPanel = ref([]);

// Conteos computados
const totalUsuarios = computed(() => usuariosPanel.value.length);

// Contar usuarios por cada rol dinámicamente
const conteosPorRol = computed(() => {
  const conteos = {};
  usuariosPanel.value.forEach(usuario => {
    usuario.roles?.forEach(rol => {
      if (!conteos[rol.nombre_rol]) {
        conteos[rol.nombre_rol] = 0;
      }
      conteos[rol.nombre_rol]++;
    });
  });
  return conteos;
});

// Generar tarjetas de estadísticas dinámicamente según los roles existentes
const tarjetasStats = computed(() => {
  const tarjetas = [
    {
      key: 'total',
      label: 'Usuarios Totales',
      count: totalUsuarios.value,
      icon: 'fas fa-users',
      class: 'stat-icon--users'
    },
    // Puedes agregar más tarjetas fijas aquí:
    // {
    //     key: 'ejemplo',
    //     label: 'Mi Nueva Tarjeta',
    //     count: 42, // El valor que quieras mostrar
    //     icon: 'fas fa-star',
    //     class: 'stat-icon--admin' // Clase CSS para el color
    // }
  ];

  // Agregar una tarjeta por cada rol encontrado
  Object.entries(conteosPorRol.value).forEach(([nombreRol, count]) => {
    // Determinar icono y clase según el rol específico
    let iconClass = 'fas fa-user'; // Por defecto
    let statClass = 'stat-icon--user'; // Por defecto

    const rolLower = nombreRol.toLowerCase();

    if (rolLower.includes('superadmin')) {
      iconClass = 'fas fa-crown';
      statClass = 'stat-icon--superadmin';
    } else if (rolLower.includes('administrador')) {
      iconClass = 'fas fa-user-shield';
      statClass = 'stat-icon--administrador';
    } else if (rolLower.includes('entrenador')) {
      iconClass = 'fa-solid fa-chalkboard-user';
      statClass = 'stat-icon--entrenador';
    } else if (rolLower.includes('deportista')) {
      iconClass = 'fas fa-running';
      statClass = 'stat-icon--deportista';
    } else if (rolLower.includes('acudiente')) {
      iconClass = 'fas fa-user-friends';
      statClass = 'stat-icon--acudiente';
    } else if (rolLower.includes('usuario')) {
      statClass = 'stat-icon--usuario';
    }

    tarjetas.push({
      key: nombreRol.toLowerCase(),
      label: nombreRol,
      count: count,
      icon: iconClass,
      class: statClass
    });
  });

  // Agregar pendientes (usuarios sin rol)
  const sinRol = usuariosPanel.value.filter(u => !u.roles || u.roles.length === 0).length;
  if (sinRol > 0) {
    tarjetas.push({
      key: 'pendientes',
      label: 'Pendientes',
      count: sinRol,
      icon: 'fas fa-clock',
      class: 'stat-icon--pending'
    });
  }

  return tarjetas;
});

// Cargar roles desde la API al montar el componente
onMounted(async () => {
  try {
    const res = await usuariosService.listarRoles();
    if (res?.success && Array.isArray(res.data)) {
      rolesOptions.value = [
        { value: 'todos', label: 'Todos' },
        ...res.data.map(rol => ({ value: rol.nombre_rol, label: rol.nombre_rol }))
      ];
    }
  } catch (e) {
    console.error('Error cargando roles:', e);
  }
});

// Funciones
function abrirModalRegistro() {
  mostrarModalRegistro.value = true;
}

function cerrarModalRegistro() {
  mostrarModalRegistro.value = false;
}

function abrirModalDatos() {
  mostrarModalDatos.value = true;
}

function cerrarModalDatos() {
  mostrarModalDatos.value = false;
  temaParaCrear.value = '';
}

function abrirModalDatosConTema(tema) {
  temaParaCrear.value = tema;
  mostrarModalDatos.value = true;
}

function abrirModalEdicion({ tema, dato }) {
  temaEdicion.value = tema;
  datoEdicion.value = dato;
  mostrarModalEdicion.value = true;
}

function cerrarModalEdicion() {
  mostrarModalEdicion.value = false;
  temaEdicion.value = '';
  datoEdicion.value = {};
}

function onDatoGuardado() {
  // Recargar la tabla después de guardar
  recargarTablaDatos.value = !recargarTablaDatos.value
  cerrarModalEdicion();
}

function onDatoEliminado() {
  // La tabla ya se recarga automáticamente en el componente
}

function obtenerTemaBackend(entidad) {
  const temaMap = {
    'tipo_documento': 'tipo-documento',
    'sexo': 'sexo',
    'ciudad': 'ciudad-residencia',
    'eps': 'eps',
    'tipo-evento': 'tipo-evento',
    'metodo_pago': 'metodo-pago'
  }
  return temaMap[entidad]
}

async function mostrarErrorEntidadNoDisponible(entidad) {
  await Swal.fire({
    icon: 'warning',
    title: 'Función no disponible',
    text: `La creación de "${entidad}" aún no está disponible desde esta interfaz.`
  })
}

function prepararDatosMetodoPago(nombre, payload) {
  const datos = { nombre_metodo: nombre.trim() }
  datos.estado = payload.estado !== undefined ? payload.estado : true
  return datos
}

function prepararDatosEPS(nombre, codigo, payload) {
  const datos = { nombre_eps: nombre.trim() }
  if (codigo) {
    datos.codigo_eps = codigo.trim()
  }
  datos.estado = payload.estado !== undefined ? payload.estado : true
  return datos
}

function prepararDatosTipoEvento(nombre, payload) {
  const datos = { nombre: nombre.trim() }
  if (payload.descripcion) {
    datos.descripcion = payload.descripcion.trim()
  }
  return datos
}

function prepararDatosPorEntidad(entidad, nombre, codigo, payload) {
  const mapeoCampos = {
    'tipo_documento': { nombre_documento: nombre.trim() },
    'sexo': { nombre: nombre.trim() },
    'ciudad': { nombre_ciudad: nombre.trim() }
  }

  if (mapeoCampos[entidad]) {
    return mapeoCampos[entidad]
  }

  if (entidad === 'metodo_pago') {
    return prepararDatosMetodoPago(nombre, payload)
  }

  if (entidad === 'eps') {
    return prepararDatosEPS(nombre, codigo, payload)
  }

  if (entidad === 'tipo-evento') {
    return prepararDatosTipoEvento(nombre, payload)
  }

  return { nombre: nombre.trim() }
}

async function onGuardarDato(payload) {
  try {
    const { entidad, nombre, codigo } = payload

    const tema = obtenerTemaBackend(entidad)

    if (!tema) {
      await mostrarErrorEntidadNoDisponible(payload.entidad)
      return
    }

    const datos = prepararDatosPorEntidad(entidad, nombre, codigo, payload)

    const base = API_CONFIG.baseURL || ''
    const response = await fetch(`${base}/api/dynamic-data/${tema}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(datos)
    })

    const result = await response.json()

    if (result.success) {
      await Swal.fire({
        icon: 'success',
        title: 'Dato creado',
        text: `${payload.entidad} creado exitosamente.`,
        timer: 1500,
        showConfirmButton: false
      })
      // Recargar la tabla de datos
      recargarTablaDatos.value = !recargarTablaDatos.value
      cerrarModalDatos()
    } else {
      await Swal.fire({
        icon: 'error',
        title: 'No se pudo crear',
        text: result.error || 'No se pudo crear el registro.'
      })
    }
  } catch (error) {
    console.error('Error al guardar dato:', error)
    await Swal.fire({
      icon: 'error',
      title: 'Error de conexión',
      text: error.message || 'No pudimos comunicarnos con el servidor.'
    })
  }
}

async function manejarUsuarioRegistrado(datosUsuario) {
  console.log('Usuario registrado desde admin-manager:', datosUsuario);
  // Cerrar el modal después del registro exitoso
  cerrarModalRegistro();
  // Aquí puedes agregar lógica adicional como actualizar la lista de usuarios
  // o mostrar notificaciones
  await Swal.fire({
    icon: 'success',
    title: 'Usuario registrado',
    text: 'El nuevo usuario fue registrado correctamente.',
    timer: 1500,
    showConfirmButton: false
  });
}

// Handlers para eventos del hijo
function setUsuarios(lista) {
  usuariosPanel.value = Array.isArray(lista) ? lista : [];
}

function actualizarUsuario(usuarioActualizado) {
  const idx = usuariosPanel.value.findIndex(u => u.id_usuario === usuarioActualizado?.id_usuario);
  if (idx !== -1) {
    const nuevaLista = [...usuariosPanel.value];
    nuevaLista[idx] = { ...nuevaLista[idx], ...usuarioActualizado };
    usuariosPanel.value = nuevaLista;
  }
}

</script>

<style scoped>
/* Estilos para el modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  background: linear-gradient(135deg, #0047ab 0%, #0d47a1 100%);
  color: white;
  padding: 25px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-cerrar {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cerrar:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.modal-body-form {
  padding: 30px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 400px;
}

.modal-body-form ::v-deep .formulario-datos {
  width: 100% !important;
  max-width: 700px;
  margin: 0 auto;
  box-sizing: border-box;
}

.modal-body-form ::v-deep .seccion-formulario {
  margin: 0 auto;
  width: 100%;
}

.modal-body-form ::v-deep .seccion-formulario h3 {
  text-align: center;
}

.modal-body-form ::v-deep .fila-texto {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 15px;
  width: 100%;
}

.modal-body-form ::v-deep .fila-texto input,
.modal-body-form ::v-deep .fila-texto select {
  width: 100%;
  box-sizing: border-box;
}

/* Campos que ocupan todo el ancho - aplicado directamente a los inputs */
.modal-body-form ::v-deep .fila-texto input[placeholder*="Número de documento"],
.modal-body-form ::v-deep .fila-texto input[placeholder*="Dirección"],
.modal-body-form ::v-deep .fila-texto input[placeholder*="Nombre de usuario"] {
  grid-column: 1 / -1;
}

/* Botones centrados */
.modal-body-form ::v-deep .botones-formulario {
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
}

/* Ocultar el botón "Volver al login" en el modal del admin */
.modal-body-form ::v-deep .boton-secundario {
  display: none;
}
</style>
