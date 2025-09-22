<template>
  <div v-if="mostrar" class="modal-overlay" @click="cerrarModal">
    <div class="modal-content" @click.stop>
      <!-- Header del Modal -->
      <div class="modal-header">
        <h2 class="modal-title">
          <i class="fas fa-user-plus"></i>
          Registro de Nuevo Usuario
        </h2>
        <button class="btn-cerrar" @click="cerrarModal">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- Paso 1: Selección de Rol -->
      <div v-if="paso === 1" class="modal-body">
        <div class="seleccion-rol">
          <h3 class="paso-titulo">Paso 1: Selecciona el tipo de usuario</h3>
          <p class="paso-descripcion">Elige el rol que mejor describa al nuevo usuario del sistema</p>

          <div class="roles-grid">
            <div
              v-for="rol in rolesDisponibles"
              :key="rol.id"
              class="rol-option"
              :class="{ seleccionado: rolSeleccionado?.id === rol.id }"
              @click="seleccionarRol(rol)"
            >
              <div class="rol-icono">
                <i :class="rol.icono"></i>
              </div>
              <div class="rol-info">
                <h4 class="rol-nombre">{{ rol.nombre }}</h4>
                <p class="rol-descripcion">{{ rol.descripcion }}</p>
              </div>
              <div class="rol-check">
                <i v-if="rolSeleccionado?.id === rol.id" class="fas fa-check"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Paso 2: Formulario de Registro -->
      <div v-if="paso === 2" class="modal-body">
        <div class="formulario-registro">
          <div class="paso-header">
            <button class="btn-volver" @click="volverPaso1">
              <i class="fas fa-arrow-left"></i>
              Volver
            </button>
            <h3 class="paso-titulo">
              Paso 2: Registro de {{ rolSeleccionado?.nombre }}
            </h3>
          </div>

          <!-- Formulario según el rol -->
          <FormularioGeneral
            v-if="rolSeleccionado?.tipo === 'general'"
            :modo="'registrar'"
            @submit="manejarRegistro"
            @cancel="cancelarRegistro"
          />

          <FormularioDeportista
            v-else-if="rolSeleccionado?.tipo === 'deportista'"
            :modo="'registrar'"
            @submit="manejarRegistro"
            @cancel="cancelarRegistro"
          />

          <FormularioEntrenador
            v-else-if="rolSeleccionado?.tipo === 'entrenador'"
            :modo="'registrar'"
            @submit="manejarRegistro"
            @cancel="cancelarRegistro"
          />

          <FormularioAcudiente
            v-else-if="rolSeleccionado?.tipo === 'acudiente'"
            :modo="'registrar'"
            @submit="manejarRegistro"
            @cancel="cancelarRegistro"
          />
        </div>
      </div>

      <!-- Footer del Modal -->
      <div class="modal-footer">
        <div v-if="paso === 1" class="footer-acciones">
          <button class="btn btn--outline" @click="cerrarModal">
            Cancelar
          </button>
          <button
            class="btn btn--primary"
            :disabled="!rolSeleccionado"
            @click="siguientePaso"
          >
            Continuar
            <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import FormularioGeneral from '../formularios/formulario-general.vue';
import FormularioDeportista from '../formularios/formulario-deportista.vue';
import FormularioEntrenador from '../formularios/formulario-entrenador.vue';
import FormularioAcudiente from '../formularios/formulario-acudiente.vue';

// Props
const props = defineProps({
  mostrar: {
    type: Boolean,
    default: false
  }
});

// Debug: Log cuando cambie la prop mostrar
watch(() => props.mostrar, (nuevoValor) => {
  console.log('Modal mostrar cambió a:', nuevoValor);
});

// Emits
const emit = defineEmits(['cerrar', 'usuario-registrado']);

// Estado reactivo
const paso = ref(1);
const rolSeleccionado = ref(null);

// Roles disponibles para registro
const rolesDisponibles = ref([
  {
    id: 'aspirante',
    nombre: 'Aspirante',
    tipo: 'general',
    icono: 'fas fa-user-plus',
    descripcion: 'Usuario nuevo que desea ingresar al club deportivo'
  },
  {
    id: 'deportista',
    nombre: 'Deportista',
    tipo: 'deportista',
    icono: 'fas fa-running',
    descripcion: 'Atleta activo que participa en actividades deportivas'
  },
  {
    id: 'acudiente',
    nombre: 'Acudiente',
    tipo: 'acudiente',
    icono: 'fa-solid fa-user-group',
    descripcion: 'Responsable legal de un deportista menor de edad'
  },
  {
    id: 'entrenador',
    nombre: 'Entrenador',
    tipo: 'entrenador',
    icono: 'fa-solid fa-chalkboard-user',
    descripcion: 'Profesional que dirige y entrena a los deportistas'
  }
]);

// Funciones
function seleccionarRol(rol) {
  rolSeleccionado.value = rol;
}

function siguientePaso() {
  if (rolSeleccionado.value) {
    paso.value = 2;
  }
}

function volverPaso1() {
  paso.value = 1;
  rolSeleccionado.value = null;
}

function cerrarModal() {
  emit('cerrar');
  resetearModal();
}

function cancelarRegistro() {
  if (confirm('¿Estás seguro de que deseas cancelar el registro?')) {
    volverPaso1();
  }
}

function manejarRegistro(datos) {
  // Agregar el rol seleccionado a los datos
  const datosCompletos = {
    ...datos,
    rol: rolSeleccionado.value.id,
    tipoUsuario: rolSeleccionado.value.tipo
  };

  console.log('Nuevo usuario registrado:', datosCompletos);

  // Emitir evento con los datos completos
  emit('usuario-registrado', datosCompletos);

  // Mostrar mensaje de éxito
  alert(`¡${rolSeleccionado.value.nombre} registrado exitosamente!`);

  // Cerrar modal y resetear
  cerrarModal();
}

function resetearModal() {
  paso.value = 1;
  rolSeleccionado.value = null;
}
</script>

<style scoped>
/* Modal Overlay */
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

/* Modal Content */
.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
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

/* Modal Header */
.modal-header {
  background: linear-gradient(135deg, #0047ab 0%, #0d47a1 100%);
  color: white;
  padding: 25px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  background: rgba(55, 51, 51, 0.3);
  transform: scale(1.1);
}

/* Modal Body */
.modal-body {
  padding: 30px;
  max-height: 60vh;
  overflow-y: auto;
}

/* Selección de Rol */
.seleccion-rol {
  text-align: center;
}

.paso-titulo {
  font-size: 1.4rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 10px 0;
}

.paso-descripcion {
  color: #666;
  margin-bottom: 30px;
  font-size: 1rem;
}

.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.rol-option {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  align-items: center;
  gap: 20px;
}

.rol-option:hover {
  border-color: #0047ab;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 71, 171, 0.15);
}

.rol-option.seleccionado {
  border-color: #0047ab;
  background-color: #f8fbff;
  box-shadow: 0 8px 25px rgba(0, 71, 171, 0.2);
}

.rol-icono {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #0047ab 0%, #0d47a1 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.rol-info {
  flex: 1;
  text-align: left;
}

.rol-nombre {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.rol-descripcion {
  color: #666;
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.rol-check {
  width: 30px;
  height: 30px;
  background: #28a745;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.9rem;
  flex-shrink: 0;
}

/* Formulario de Registro */
.formulario-registro {
  width: 100%;
}

.paso-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.btn-volver {
  background: #6c757d;
  border: none;
  color: white;
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-volver:hover {
  background: #5a6268;
}

/* Modal Footer */
.modal-footer {
  background: #f8f9fa;
  padding: 20px 30px;
  border-top: 1px solid #e0e0e0;
}

.footer-acciones {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

/* Botones */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.btn--primary {
  background-color: #0047ab;
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background-color: #003d91;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 71, 171, 0.3);
}

.btn--primary:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn--outline {
  background-color: transparent;
  color: #7d6c6c;
  border: 2px solid #6c757d;
}

.btn--outline:hover {
  background-color: #e30f0f;
  color: white;
}

/* Responsive */
@media (max-width: 768px) {
  .modal-content {
    margin: 10px;
    max-height: 95vh;
  }

  .modal-body {
    padding: 20px;
  }

  .roles-grid {
    grid-template-columns: 1fr;
  }

  .rol-option {
    flex-direction: column;
    text-align: center;
    padding: 20px;
  }

  .footer-acciones {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
