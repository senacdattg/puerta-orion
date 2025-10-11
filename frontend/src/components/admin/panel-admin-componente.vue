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
                    <div class="stat-card">
                        <div class="stat-icon stat-icon--users">
                            <i class="fas fa-users"></i>
                        </div>
                        <div class="stat-content">
                            <span class="stat-number">156</span>
                            <span class="stat-label">Usuarios Totales</span>
                        </div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon stat-icon--admin">
                            <i class="fas fa-user-shield"></i>
                        </div>
                        <div class="stat-content">
                            <span class="stat-number">8</span>
                            <span class="stat-label">Administradores</span>
                        </div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon stat-icon--moderator">
                            <i class="fas fa-user-tie"></i>
                        </div>
                        <div class="stat-content">
                            <span class="stat-number">12</span>
                            <span class="stat-label">Moderadores</span>
                        </div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon stat-icon--pending">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="stat-content">
                            <span class="stat-number">5</span>
                            <span class="stat-label">Pendientes</span>
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
                                        <option value="todos">Todos</option>
                                        <option value="admin">Administrador</option>
                                        <option value="moderator">Moderador</option>
                                        <option value="user">Usuario</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <TablaUsuarios :search-term="terminoBusqueda" :role-filter="filtroRol" />
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
import { ref } from 'vue';
import ModalRegistroUsuario from '@/components/admin/modal-registro-usuario.vue';
import TablaUsuarios from '@/components/admin/tabla-usuarios.vue';

// Estado del modal
const mostrarModalRegistro = ref(false);
const mostrarFiltros = ref(false);
const mostrarBusqueda = ref(false);
const terminoBusqueda = ref('');
const filtroRol = ref('todos');

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
</script>