<script setup>
import { ref, onMounted } from 'vue';
import Encabezado from '../components/layout/encabezado.vue';
import Titulo from '../components/ui/titulo-club.vue';
import FormularioAcudiente from '../components/formularios/formulario-acudiente.vue';
import Pie from '../components/layout/pie.vue';
import { useRouter } from 'vue-router';
import authService from '@/services/authService';

const router = useRouter();
const datosUsuario = ref({});
const cargando = ref(true);

// Cargar datos del usuario al montar el componente
onMounted(async () => {
  try {
    const perfil = await authService.getProfile();
    datosUsuario.value = perfil.data || {};
    console.log('Datos del usuario cargados:', datosUsuario.value);
  } catch (error) {
    console.error('Error al cargar datos del usuario:', error);
    alert('Error al cargar los datos del usuario');
  } finally {
    cargando.value = false;
  }
});

// Función para manejar el registro completo de acudiente
async function manejarRegistroCompleto(datos) {
  try {
    console.log("Datos completos del acudiente:", datos);

    // Los datos ya están en el formato correcto, el servicio se encarga del mapeo
    const resultado = await authService.completarPerfilAcudiente(datos);

    if (resultado.success) {
      alert(resultado.message || "¡Perfil de acudiente completado exitosamente!");
      router.push('/home');
    } else {
      alert(`Error: ${resultado.error}`);
    }
  } catch (error) {
    console.error("Error al completar perfil de acudiente:", error);
    alert("Error al completar el perfil. Por favor intenta nuevamente.");
  }
}

// Función para manejar la cancelación
function manejarCancelacion() {
  if (confirm("¿Está seguro de que desea cancelar el registro? Se perderá toda la información ingresada.")) {
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
      <FormularioAcudiente
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

<style scoped>
.cargando-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #0047ab;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.cargando-container p {
  color: #666;
  font-size: 1.1rem;
  margin: 0;
}
</style>
