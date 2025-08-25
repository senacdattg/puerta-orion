<script setup>
import Encabezado from '../components/iu/encabezado.vue';
import Admin from '@/components/admin/permisos-admin.vue';
import Pie from '../components/iu/pie.vue';
</script>

<template>
  <main class="admin-page">
    <Encabezado rol="Admin"/>

    <!-- Header del Panel -->
    <div class="admin-header">
      <div class="container">
        <div class="header-content">
          <div class="header-text">
            <h1 class="page-title">Panel de Administración</h1>
            <p class="page-subtitle">Gestiona usuarios, roles y configuraciones del club deportivo</p>
          </div>
          <div class="header-actions">
            <button class="btn btn--primary">
              <i class="fas fa-plus"></i>
              Nuevo Usuario
            </button>
            <button class="btn btn--secondary">
              <i class="fas fa-download"></i>
              Exportar
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
                <button class="btn btn--small btn--outline">
                  <i class="fas fa-filter"></i>
                  Filtros
                </button>
                <button class="btn btn--small btn--outline">
                  <i class="fas fa-search"></i>
                  Buscar
                </button>
              </div>
            </div>
            <Admin />
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

    <Pie />
  </main>
</template>

<style scoped>
/* Estilos del panel de administración */
.admin-page {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Header del Panel */
.admin-header {
  background: linear-gradient(135deg, #0047ab 0%, #0d47a1 100%);
  color: white;
  padding: 40px 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 10px 0;
}

.page-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

/* Botones */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn--primary {
  background-color: #f7d600;
  color: #0047ab;
}

.btn--primary:hover {
  background-color: #ffc107;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(247, 214, 0, 0.4);
}

.btn--secondary {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn--secondary:hover {
  background-color: white;
  color: #0047ab;
  transform: translateY(-2px);
}

.btn--small {
  padding: 8px 16px;
  font-size: 0.9rem;
}

.btn--outline {
  background-color: transparent;
  color: #0047ab;
  border: 2px solid #0047ab;
}

.btn--outline:hover {
  background-color: #0047ab;
  color: white;
}

/* Sección de Estadísticas */
.stats-section {
  padding: 40px 0;
  background-color: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
}

.stat-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.stat-icon--users {
  background-color: #28a745;
}

.stat-icon--admin {
  background-color: #dc3545;
}

.stat-icon--moderator {
  background-color: #ffc107;
}

.stat-icon--pending {
  background-color: #6c757d;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  margin-top: 5px;
}

/* Contenido Principal */
.main-content {
  padding: 40px 0;
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
}

.content-panel {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.panel-header {
  background-color: #f8f9fa;
  padding: 20px 25px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #333;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.panel-actions {
  display: flex;
  gap: 10px;
}

/* Lista de Actividad */
.activity-list {
  padding: 20px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  color: white;
  flex-shrink: 0;
}

.activity-icon--success {
  background-color: #28a745;
}

.activity-icon--info {
  background-color: #17a2b8;
}

.activity-icon--warning {
  background-color: #ffc107;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 0.95rem;
  color: #333;
  margin: 0 0 5px 0;
  line-height: 1.4;
}

.activity-time {
  font-size: 0.8rem;
  color: #666;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .header-content {
    flex-direction: column;
    text-align: center;
  }

  .page-title {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .header-actions {
    justify-content: center;
  }

  .panel-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }

  .panel-actions {
    width: 100%;
    justify-content: center;
  }
}
</style>
