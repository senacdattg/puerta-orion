<template>
  <div v-if="mostrar" class="modal-overlay modal-registro-overlay" @click="cerrarModal">
    <div class="modal-content modal-registro" @click.stop>
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

      <!-- Formulario de Registro -->
      <div class="modal-body">
        <FormularioGeneral
          :modo="'registrar'"
          :mostrar-boton-login="false"
          texto-boton-registrar="Registrar"
          @submit="manejarRegistro"
          @cancel="cancelarRegistro"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import FormularioGeneral from '../formularios/formulario-general.vue';
import Swal from 'sweetalert2';

// Props
const props = defineProps({
  mostrar: {
    type: Boolean,
    default: false
  }
});

// Emits
const emit = defineEmits(['cerrar', 'usuario-registrado']);

function cerrarModal() {
  emit('cerrar');
}

async function cancelarRegistro() {
  const result = await Swal.fire({
    icon: 'question',
    title: '¿Cancelar registro?',
    text: 'Los datos ingresados se perderán.',
    showCancelButton: true,
    confirmButtonText: 'Sí, cancelar',
    cancelButtonText: 'Seguir registrando'
  });
  if (result.isConfirmed) {
    cerrarModal();
  }
}

async function manejarRegistro(datos) {
  const datosCompletos = {
    ...datos,
    rol: 'usuario',
    tipoUsuario: 'general'
  };

  // Emitir evento con los datos completos
  emit('usuario-registrado', datosCompletos);

  await Swal.fire({
    icon: 'success',
    title: 'Usuario registrado',
    text: 'El nuevo usuario fue registrado correctamente.',
    timer: 1500,
    showConfirmButton: false
  });

  // Cerrar modal y resetear
  cerrarModal();
}
</script>

<style>
.modal-registro-overlay {
  backdrop-filter: blur(4px);
}

.modal-registro {
  max-width: 800px;
  --modal-header-bg: linear-gradient(135deg, #0047ab 0%, #0d47a1 100%);
  --modal-header-color: #ffffff;
}

.modal-registro .modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.modal-registro .btn-cerrar {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-registro .btn-cerrar:hover {
  background: rgba(55, 51, 51, 0.3);
  transform: scale(1.1);
}

.modal-registro .modal-body {
  padding: 30px;
  max-height: 60vh;
  overflow-y: auto;
}

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
  background-color: #0047ab !important;
  transform: none;
  box-shadow: none;
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
