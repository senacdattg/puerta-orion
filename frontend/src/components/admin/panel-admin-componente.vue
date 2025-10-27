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
                    </div>
                </div>
            </div>
        </div>

        <!-- Dashboard Stats -->
        <section class="stats-section">
            <div class="container">
                <div class="stats-grid">
                    <div
                        v-for="tarjeta in tarjetasStats"
                        :key="tarjeta.key"
                        class="stat-card"
                    >
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
                                    <input
                                        v-model="terminoBusqueda"
                                        type="text"
                                        placeholder="Nombre..."
                                        class="control-input"
                                    />
                                </div>
                                <div v-if="mostrarFiltros" class="control-item">
                                    <label class="control-label">Filtrar por rol</label>
                                    <select v-model="filtroRol" class="control-input">
                                        <option
                                            v-for="opt in rolesOptions"
                                            :key="opt.value"
                                            :value="opt.value"
                                        >
                                            {{ opt.label }}
                                        </option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <TablaUsuarios
                            :search-term="terminoBusqueda"
                            :role-filter="filtroRol"
                            @usuarios-cargados="setUsuarios"
                            @usuario-actualizado="actualizarUsuario"
                        />
                    </div>

                    <!-- Panel de Actividad Reciente -->
                    <div class="content-panel">
                        <div class="panel-header">
                            <h2 class="panel-title">
                                <i class="fas fa-history"></i>
                                Actividad Reciente
                            </h2>
                        </div>
                        <div class="activity-list">
                            <div class="activity-item">
                                <div class="activity-icon activity-icon--success">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="activity-content">
                                    <p class="activity-text">Rol de usuario "María" actualizado a Moderador</p>
                                    <span class="activity-time">Hace 5 minutos</span>
                                </div>
                            </div>

                            <div class="activity-item">
                                <div class="activity-icon activity-icon--info">
                                    <i class="fas fa-user-plus"></i>
                                </div>
                                <div class="activity-content">
                                    <p class="activity-text">Nuevo usuario "Carlos" registrado</p>
                                    <span class="activity-time">Hace 15 minutos</span>
                                </div>
                            </div>

                            <div class="activity-item">
                                <div class="activity-icon activity-icon--warning">
                                    <i class="fas fa-exclamation-triangle"></i>
                                </div>
                                <div class="activity-content">
                                    <p class="activity-text">Intento de acceso no autorizado bloqueado</p>
                                    <span class="activity-time">Hace 1 hora</span>
                                </div>
                            </div>

                            <div class="activity-item">
                                <div class="activity-icon activity-icon--success">
                                    <i class="fas fa-sync"></i>
                                </div>
                                <div class="activity-content">
                                    <p class="activity-text">Respaldo de base de datos completado</p>
                                    <span class="activity-time">Hace 2 horas</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Modal de Registro de Usuario -->
        <ModalRegistroUsuario :mostrar="mostrarModalRegistro" @cerrar="cerrarModalRegistro"
            @usuario-registrado="manejarUsuarioRegistrado" />
    </main>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue';
import ModalRegistroUsuario from '@/components/admin/modal-registro-usuario.vue';
import TablaUsuarios from '@/components/admin/tabla-usuarios.vue';
import usuariosService from '@/services/usuariosService';

// Estado del modal
const mostrarModalRegistro = ref(false);
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
        // Determinar icono según el rol
        let iconClass = 'fas fa-user'; // Por defecto
        let statClass = 'stat-icon--user'; // Por defecto (azul)

        const rolLower = nombreRol.toLowerCase();

        if (rolLower.includes('admin')) {
            iconClass = 'fas fa-user-shield';
            statClass = 'stat-icon--admin'; // Rojo
        } else if (rolLower.includes('entrenador')) {
            iconClass = 'fas fa-user-tie';
            statClass = 'stat-icon--moderator'; // Amarillo
        } else if (rolLower.includes('deportista')) {
            iconClass = 'fas fa-running';
            statClass = 'stat-icon--user'; // Azul
        } else if (rolLower.includes('acudiente')) {
            iconClass = 'fas fa-user-group';
            statClass = 'stat-icon--user'; // Azul
        } else if (rolLower.includes('usuario')) {
          iconClass = 'fas fa-user';
          statClass = 'stat-icon--moderator'; // Azul
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
    console.log('Abriendo modal de registro...');
    mostrarModalRegistro.value = true;
    console.log('Estado del modal:', mostrarModalRegistro.value);
}

function cerrarModalRegistro() {
    mostrarModalRegistro.value = false;
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
</script>
