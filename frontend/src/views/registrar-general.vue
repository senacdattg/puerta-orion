<script setup>
import FormularioGeneral from '../components/formularios/formulario-general.vue';
import Swal from 'sweetalert2';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

// Función para manejar el registro
async function manejarRegistro(datos) {
  console.log("Datos del nuevo usuario:", datos);

  // Mostrar loading (no await para que no bloquee)
  const loadingSwal = Swal.fire({
    title: 'Registrando usuario...',
    allowOutsideClick: false,
    allowEscapeKey: false,
    didOpen: () => {
      Swal.showLoading();
    }
  });

  try {
    // Preparar datos para el backend
    const datosPersona = {
      primer_nombre: datos.nombre1.trim(),
      segundo_nombre: datos.nombre2 ? datos.nombre2.trim() : null,
      primer_apellido: datos.apellido1.trim(),
      segundo_apellido: datos.apellido2 ? datos.apellido2.trim() : null,
      documento: String(datos.numeroDocumento).trim(),
      correo_electronico: datos.correo.trim().toLowerCase(),
      direccion: datos.direccion ? datos.direccion.trim() : null,
      telefono: datos.telefono ? String(datos.telefono).trim() : null,
      id_tipo_documento: Number.parseInt(datos.idTipoDocumento, 10),
      id_sexo: Number.parseInt(datos.idSexo, 10)
    };

    const datosUsuario = {
      usuario: datos.usuario,
      password: datos.contrasena
    };

    // Registrar usando el store
    const datosRegistro = {
      persona: datosPersona,
      usuario: datosUsuario
    };

    console.log('🔄 Llamando a authStore.register con:', datosRegistro);
    const resultado = await authStore.register(datosRegistro);
    console.log('📋 Resultado del registro:', resultado);

    // Cerrar loading manualmente
    Swal.close();

    if (resultado.success) {
      await Swal.fire({
        icon: 'success',
        title: 'Registro exitoso',
        text: 'El usuario se registró correctamente. Redirigiendo al login...',
        timer: 2000,
        showConfirmButton: false
      });

      // Redirigir al login
      router.push('/login');
    } else {
      await Swal.fire({
        icon: 'error',
        title: 'Error al registrar',
        text: resultado.error || 'No se pudo completar el registro. Por favor, intenta nuevamente.',
        confirmButtonText: 'Aceptar'
      });
    }
  } catch (error) {
    console.error('Error en registro:', error);
    // Cerrar loading si hay error
    Swal.close();
    await Swal.fire({
      icon: 'error',
      title: 'Error al registrar',
      text: error.message || 'Ocurrió un error inesperado. Por favor, intenta nuevamente.',
      confirmButtonText: 'Aceptar'
    });
  }
}

// Función para manejar la cancelación
async function manejarCancelacion() {
  const resultado = await Swal.fire({
    icon: 'question',
    title: '¿Cancelar registro?',
    text: 'Los datos ingresados se perderán.',
    showCancelButton: true,
    confirmButtonText: 'Sí, cancelar',
    cancelButtonText: 'Continuar llenando'
  });
  if (resultado.isConfirmed) {
    console.log("Registro cancelado");
  }
}
</script>

<template>
  <main>
    <div class="contenido-principal-tarjetas">
      <FormularioGeneral
        :modo="'registrar'"
        @submit="manejarRegistro"
        @cancel="manejarCancelacion"
      />
    </div>
  </main>
</template>
