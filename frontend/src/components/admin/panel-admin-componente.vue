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

          <!-- Panel: Pagos recientes (Mercado Pago) -->
          <div class="content-panel">
            <div class="panel-header">
              <h2 class="panel-title">
                <i class="fas fa-credit-card"></i>
                Pagos recientes
              </h2>
              <div class="panel-actions">
                <button class="btn btn--small" @click="cargarPagosRecientes">Actualizar</button>
              </div>
            </div>
            <div class="panel-body">
              <div v-if="cargandoPagos" class="muted">Cargando...</div>
              <div v-else-if="pagosRecientes.length === 0" class="muted">Sin pagos recientes</div>
              <table v-else class="tabla-simple">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Estado</th>
                    <th>Monto</th>
                    <th>Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="p in pagosRecientes" :key="p.id_transaccion || p.id">
                    <td>{{ p.id_pago_mercadopago || p.preference_id || p.id }}</td>
                    <td>{{ p.estado }}</td>
                    <td>${{ Number(p.monto || p.transaction_amount || 0).toLocaleString('es-CO') }}</td>
                    <td>{{ formatearFecha(p.fecha_creacion || p.created_at) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Modal de Registro de Usuario -->
    <ModalRegistroUsuario :mostrar="mostrarModalRegistro" @cerrar="cerrarModalRegistro"
      @usuario-registrado="manejarUsuarioRegistrado" />

    <!-- Modal Añadir Datos -->
    <ModalAnadirDatos :mostrar="mostrarModalDatos" @cerrar="cerrarModalDatos" @guardar-dato="onGuardarDato" />
  </main>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue';
import { API_CONFIG } from '@/config/environment';
import ModalRegistroUsuario from '@/components/admin/modal-registro-usuario.vue';
import ModalAnadirDatos from '@/components/admin/modal-anadir-datos.vue';
import TablaUsuarios from '@/components/admin/tabla-usuarios.vue';
import usuariosService from '@/services/usuariosService';

// Estado del modal
const mostrarModalRegistro = ref(false);
const mostrarModalDatos = ref(false);
const mostrarFiltros = ref(false);
const mostrarBusqueda = ref(false);
const terminoBusqueda = ref('');
const filtroRol = ref('todos');

// Opciones de roles cargadas desde la API
const rolesOptions = ref([{ value: 'todos', label: 'Todos' }]);

// Usuarios para conteos
const usuariosPanel = ref([]);
const pagosRecientes = ref([]);
const cargandoPagos = ref(false);

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
      iconClass = 'fas fa-user';
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
  await cargarPagosRecientes();
});

// Funciones
function abrirModalRegistro() {
  console.log('Abriendo modal de registro...');
  mostrarModalRegistro.value = true;
  console.log('Estado del modal:', mostrarModalRegistro.value);
}

function cerrarModalRegistro() {
  mostrarModalRegistro.value = false;
}

function abrirModalDatos() {
  mostrarModalDatos.value = true;
}

function cerrarModalDatos() {
  mostrarModalDatos.value = false;
}

function onGuardarDato(payload) {
  console.log('Añadir dato recibido:', payload)
  // Aquí luego llamaremos a la API correspondiente según payload.entidad
}

function manejarUsuarioRegistrado(datosUsuario) {
  console.log('Usuario registrado desde admin-manager:', datosUsuario);
  // Aquí puedes agregar lógica adicional como actualizar la lista de usuarios
  // o mostrar notificaciones
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

async function cargarPagosRecientes() {
  try {
    cargandoPagos.value = true;
    const base = API_CONFIG.baseURL || '';
    const resp = await fetch(`${base}/api/mercadopago/transacciones?limit=10`, {
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      }
    });
    if (!resp.ok) throw new Error('No se pudieron cargar');
    const json = await resp.json();
    pagosRecientes.value = json.transacciones || [];
  } catch (e) {
    pagosRecientes.value = [];
  } finally {
    cargandoPagos.value = false;
  }
}

function formatearFecha(fecha) {
  if (!fecha) return '';
  try { return new Date(fecha).toLocaleString('es-CO'); } catch { return String(fecha); }
}
</script>
