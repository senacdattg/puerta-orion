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
import { computed } from 'vue';
import FormularioGeneral from '../formularios/formulario-general.vue';
import Swal from 'sweetalert2';
import { useModalScrollLock } from '@/composables/useModalScrollLock';
import { useAuthStore } from '@/stores/auth';

// Props
const props = defineProps({
  mostrar: {
    type: Boolean,
    default: false
  }
});

// Emits
const emit = defineEmits(['cerrar', 'usuario-registrado']);

// Bloquear scroll del body cuando el modal está abierto
useModalScrollLock(computed(() => props.mostrar));

// Store de autenticación para registrar usuarios
const authStore = useAuthStore();

async function cerrarModal() {
  const result = await Swal.fire({
    icon: 'question',
    title: '¿Cerrar registro?',
    text: '¿Estás seguro de que deseas cerrar el formulario? Los datos ingresados se perderán.',
    showCancelButton: true,
    confirmButtonText: 'Sí, cerrar',
    cancelButtonText: 'Continuar registrando',
    confirmButtonColor: '#dc3545',
    cancelButtonColor: '#6c757d'
  });
  
  if (result.isConfirmed) {
    emit('cerrar');
  }
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

async function manejarRegistro(datosFormulario) {
  // Paso 1: Confirmar antes de registrar
  const confirmacion = await Swal.fire({
    icon: 'question',
    title: '¿Registrar nuevo usuario?',
    text: '¿Estás seguro de que deseas registrar este usuario con los datos ingresados?',
    showCancelButton: true,
    confirmButtonText: 'Sí, registrar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#004AAD',
    cancelButtonColor: '#6c757d'
  });

  if (!confirmacion.isConfirmed) {
    return;
  }

  // Mostrar loading mientras se procesa
  Swal.fire({
    title: 'Registrando usuario...',
    text: 'Por favor espera mientras procesamos tu solicitud.',
    allowOutsideClick: false,
    allowEscapeKey: false,
    didOpen: () => {
      Swal.showLoading();
    }
  });

  try {
    // Preparar datos para el backend (formato esperado por authStore.register)
    const datosPersona = {
      primer_nombre: datosFormulario.nombre1,
      segundo_nombre: datosFormulario.nombre2 || null,
      primer_apellido: datosFormulario.apellido1,
      segundo_apellido: datosFormulario.apellido2 || null,
      documento: datosFormulario.numeroDocumento,
      correo_electronico: datosFormulario.correo,
      direccion: datosFormulario.direccion || null,
      telefono: datosFormulario.telefono || null,
      id_tipo_documento: parseInt(datosFormulario.idTipoDocumento),
      id_sexo: parseInt(datosFormulario.idSexo)
    };

    const datosUsuario = {
      usuario: datosFormulario.usuario,
      password: datosFormulario.contrasena
    };

    const datosRegistro = {
      persona: datosPersona,
      usuario: datosUsuario
    };

    // Registrar usando el store
    const resultado = await authStore.register(datosRegistro);

    // Cerrar el loading
    Swal.close();

    // Paso 2: Verificar resultado y mostrar notificación correspondiente
    if (resultado.success) {
      // Éxito: mostrar notificación de confirmación
      const datosCompletos = {
        ...datosFormulario,
        rol: 'usuario',
        tipoUsuario: 'general'
      };

      // Emitir evento con los datos completos
      emit('usuario-registrado', datosCompletos);

      await Swal.fire({
        icon: 'success',
        title: '¡Usuario registrado exitosamente!',
        text: 'El nuevo usuario ha sido registrado correctamente en el sistema.',
        confirmButtonText: 'Aceptar',
        confirmButtonColor: '#004AAD'
      });

      // Cerrar modal después del éxito
      emit('cerrar');
    } else {
      // Error: mostrar notificación con el error específico
      const mensajeError = extraerMensajeError(resultado.error);
      
      await Swal.fire({
        icon: 'error',
        title: 'Error al registrar usuario',
        html: `<p><strong>No se pudo registrar el usuario.</strong></p><p>${mensajeError}</p>`,
        confirmButtonText: 'Entendido',
        confirmButtonColor: '#dc3545'
      });
    }
  } catch (error) {
    // Cerrar el loading si aún está abierto
    Swal.close();
    
    console.error('Error al registrar usuario:', error);
    
    // Error de conexión o excepción no manejada
    const mensajeError = extraerMensajeError(error);
    
    await Swal.fire({
      icon: 'error',
      title: 'Error al registrar usuario',
      html: `<p><strong>Ocurrió un error inesperado.</strong></p><p>${mensajeError}</p>`,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    });
  }
}

/**
 * Extrae y formatea el mensaje de error de manera más legible
 */
function extraerMensajeError(error) {
  if (!error) {
    return 'No se pudo completar el registro. Por favor, intenta nuevamente.';
  }

  // Si es un string, devolverlo directamente
  if (typeof error === 'string') {
    return error;
  }

  // Si es un objeto con mensaje
  if (error.message) {
    return error.message;
  }

  // Si es un objeto con error
  if (error.error) {
    return typeof error.error === 'string' ? error.error : JSON.stringify(error.error);
  }

  // Si es un objeto con detalles
  if (error.details) {
    return typeof error.details === 'string' ? error.details : JSON.stringify(error.details);
  }

  // Si es un objeto, intentar convertirlo a string legible
  if (typeof error === 'object') {
    try {
      const errorStr = JSON.stringify(error);
      // Si el JSON es muy largo, devolver un mensaje genérico
      if (errorStr.length > 200) {
        return 'Error al procesar la solicitud. Verifica que todos los datos sean correctos.';
      }
      return errorStr;
    } catch {
      return 'Error desconocido. Por favor, intenta nuevamente.';
    }
  }

  return 'Error desconocido. Por favor, intenta nuevamente.';
}
</script>


