<script setup>
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { computed } from 'vue';
import FormularioDeportista from '../components/formularios/formulario-deportista.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

// Verificar si se debe asignar automáticamente al acudiente
const asignarAcudienteAuto = computed(() => {
  return route.query.asignarAcudiente === 'true'
})

// Función para manejar el registro de deportista
async function manejarRegistroDeportista(datos) {
  console.log("Datos del nuevo deportista:", datos);

  // Recargar el perfil del usuario para obtener los roles actualizados
  try {
    console.log('🔄 Recargando perfil del usuario...');
    const profileUpdated = await authStore.loadUserProfile();

    if (profileUpdated) {
      console.log('✅ Perfil actualizado exitosamente');
      console.log('📋 Roles del usuario:', authStore.userRoles);
      console.log('👤 Usuario completo:', authStore.user);

      // Verificar que tiene el rol de Deportista
      if (authStore.userRoles.includes('Deportista')) {
        // Si se debe asignar automáticamente al acudiente
        if (asignarAcudienteAuto.value) {
          await asignarDeportistaAAcudiente(datos.id_deportista)
        }

        // Mostrar mensaje de éxito
        let mensaje = '¡Registro completado exitosamente! 🎉 Ahora eres un deportista.'
        if (asignarAcudienteAuto.value) {
          mensaje += ' Has sido asignado a tu acudiente.'
        }
        alert(mensaje);

        // Redirigir según el contexto
        setTimeout(() => {
          if (asignarAcudienteAuto.value) {
            console.log('🚀 Redirigiendo a /ver-acudidos');
            router.push('/ver-acudidos');
          } else {
            console.log('🚀 Redirigiendo a /deportista/dashboard con rol Deportista');
            router.push('/deportista/dashboard');
          }
        }, 500);
      } else {
        console.warn('⚠️ El rol Deportista no está presente, redirigiendo de todas formas');
        alert('¡Registro completado! Redirigiendo al dashboard...');
        setTimeout(() => {
          router.push('/deportista/dashboard');
        }, 1000);
      }
    } else {
      console.warn('⚠️ No se pudo actualizar el perfil, pero el registro fue exitoso');
      alert('¡Registro completado! Redirigiendo al dashboard...');
      setTimeout(() => {
        router.push('/deportista/dashboard');
      }, 1500);
    }
  } catch (error) {
    console.error('❌ Error al recargar perfil:', error);
    // Redirigir de todas formas después de un delay
    alert('¡Registro completado! Redirigiendo al dashboard...');
    setTimeout(() => {
      router.push('/deportista/dashboard');
    }, 2000);
  }
}

// Función para asignar el deportista al acudiente actual
async function asignarDeportistaAAcudiente(idDeportista) {
  try {
    // Obtener el ID del acudiente actual
    const usuario = authStore.user
    console.log('👤 Usuario actual:', usuario)

    // Buscar el registro de acudiente del usuario actual
    // El registro de deportista ya debería tener los datos necesarios
    console.log(`🔗 El deportista registrado se asociará automáticamente al acudiente`)

    // La asociación se hace automáticamente en el backend
    // cuando se crea el deportista con el array de acudientes

    return true
  } catch (error) {
    console.error('❌ Error asignando deportista al acudiente:', error)
    return false
  }
}

// Función para manejar la cancelación
function manejarCancelacion() {
  if (confirm("¿Está seguro de que desea cancelar el registro?")) {
    // Si venía desde el panel de gestión de acudidos, volver allí
    if (route.query.asignarAcudiente === 'true') {
      router.push('/ver-acudidos');
    } else {
      router.push('/home');
    }
  }
}
</script>

<template>
  <main>
    <div class="contenido-principal-tarjetas">
      <!-- Mensaje informativo si se asignará automáticamente -->
      <div v-if="asignarAcudienteAuto" class="info-banner">
        <i class="fas fa-info-circle"></i>
        <p>El deportista que registres será asignado automáticamente a tu cuenta de acudiente.</p>
      </div>

      <FormularioDeportista
        :modo="'registrar'"
        @submit="manejarRegistroDeportista"
        @cancel="manejarCancelacion"
      />
    </div>
  </main>
</template>

<style scoped>
.contenido-principal-tarjetas {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.info-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 10px;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 6px rgba(102, 126, 234, 0.2);
}

.info-banner i {
  font-size: 1.5rem;
}

.info-banner p {
  margin: 0;
  font-size: 1rem;
  line-height: 1.5;
}
</style>
