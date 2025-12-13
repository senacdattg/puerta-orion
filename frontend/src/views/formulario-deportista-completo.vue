<script setup>
import { ref, onMounted } from 'vue';
import Encabezado from '../components/layout/encabezado.vue';
import Titulo from '../components/ui/titulo-club.vue';
import FormularioDeportista from '../components/formularios/formulario-deportista.vue';
import Pie from '../components/layout/pie.vue';
import { useRouter } from 'vue-router';
import authService from '@/services/authService';
import Swal from 'sweetalert2';

const router = useRouter();
const datosUsuario = ref({});
const cargando = ref(true);

// Cargar datos del usuario al montar el componente
onMounted(async () => {
  try {
    const perfil = await authService.getProfile();
    datosUsuario.value = perfil.data || {};
    console.log('Datos del usuario cargados:', datosUsuario.value);
    console.log('Estructura de datos:', Object.keys(datosUsuario.value));

    // Verificar si el usuario ya tiene el rol de deportista
    if (datosUsuario.value.roles && Array.isArray(datosUsuario.value.roles)) {
      const rolesNombre = datosUsuario.value.roles.map(r => r.nombre_rol || r);
      const esDeportista = rolesNombre.some(rol =>
        rol.toLowerCase().includes('deportista') || rol.toLowerCase() === 'deportista'
      );

      if (esDeportista) {
        console.log('Usuario ya tiene rol de deportista, redirigiendo al home...');
        router.push('/home');
        return;
      }
    }
  } catch (error) {
    console.error('Error al cargar datos del usuario:', error);
    await Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'No pudimos cargar tus datos. Intenta nuevamente.'
    });
  } finally {
    cargando.value = false;
  }
});

// Función para manejar el registro completo de deportista
async function manejarRegistroCompleto(datos) {
  try {
    console.log("Datos completos del deportista:", datos);

    // Los datos ya están en el formato correcto, el servicio se encarga del mapeo
    const resultado = await authService.completarPerfilDeportista(datos);

    if (resultado.success) {
      await Swal.fire({
        icon: 'success',
        title: 'Perfil completado',
        text: resultado.message || '¡Perfil de deportista completado exitosamente!',
        confirmButtonText: 'Continuar'
      });
      router.push('/home');
    } else {
      await Swal.fire({
        icon: 'error',
        title: 'No se pudo completar',
        text: resultado.error || 'Ocurrió un error al completar el perfil.'
      });
    }
  } catch (error) {
    console.error("Error al completar perfil de deportista:", error);
    await Swal.fire({
      icon: 'error',
      title: 'Error de conexión',
      text: 'No pudimos completar el perfil. Intenta nuevamente.'
    });
  }
}

// Función para manejar la cancelación
async function manejarCancelacion() {
  const resultado = await Swal.fire({
    icon: 'question',
    title: '¿Cancelar registro?',
    text: 'Se perderá la información ingresada.',
    showCancelButton: true,
    confirmButtonText: 'Sí, cancelar',
    cancelButtonText: 'Continuar'
  });
  if (resultado.isConfirmed) {
    router.push('/completar-perfil');
  }
}
</script>

<template>
  <main>
    <Encabezado :sinMenu="false"/>
    <Titulo />
    <div class="contenido-principal-tarjetas">
      <div v-if="cargando" class="cargando-container">
        <div class="spinner"></div>
        <p>Cargando datos del usuario...</p>
      </div>
      <FormularioDeportista
        v-else
        :modo="'actualizar'"
        :datos="datosUsuario"
        @submit="manejarRegistroCompleto"
        @cancel="manejarCancelacion"
      />
    </div>
    <Pie />
  </main>
</template>


