<script setup>
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { computed } from 'vue';
import FormularioDeportista from '../components/formularios/formulario-deportista.vue';
import Swal from 'sweetalert2';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

// Verificar si se debe asignar automáticamente al acudiente
const asignarAcudienteAuto = computed(() => {
  return route.query.asignarAcudiente === 'true'
})

const recargarPerfilUsuario = async () => {
  console.log('🔄 Recargando perfil del usuario...')
  const profileUpdated = await authStore.loadUserProfile()

  if (profileUpdated) {
    console.log('✅ Perfil actualizado exitosamente')
    console.log('📋 Roles del usuario:', authStore.userRoles)
    console.log('👤 Usuario completo:', authStore.user)
  }

  return profileUpdated
}

const tieneRolDeportista = () => {
  return authStore.userRoles.includes('Deportista')
}

const construirMensajeExito = (datos) => {
  const detalles = datos?.data || {}
  let mensaje = '¡Registro completado exitosamente! Ahora eres un deportista.'

  if (asignarAcudienteAuto.value) {
    mensaje += ' Has sido asignado a tu acudiente.'
  }

  const extra = []
  if (detalles.categoria) {
    extra.push(`Categoría: ${detalles.categoria}`)
  }
  if (detalles.nombre_persona) {
    extra.push(`Nombre: ${detalles.nombre_persona}`)
  }

  const html = [mensaje, ...extra].join('<br>')
  return html
}

const mostrarMensajeExito = async (html) => {
  await Swal.fire({
    icon: 'success',
    title: 'Registro completado',
    html,
    confirmButtonText: 'Continuar'
  })
}

const mostrarMensajeExitoSimple = async () => {
  await Swal.fire({
    icon: 'success',
    title: 'Registro completado',
    text: 'Redirigiendo al dashboard...',
    confirmButtonText: 'Continuar'
  })
}

const redirigirSegunContexto = () => {
  if (asignarAcudienteAuto.value) {
    console.log('🚀 Redirigiendo a /ver-acudidos')
    router.push('/ver-acudidos')
  } else {
    console.log('🚀 Redirigiendo a /deportista/dashboard con rol Deportista')
    router.push('/deportista/dashboard')
  }
}

const procesarRegistroExitoso = async (datos) => {
  if (asignarAcudienteAuto.value) {
    await asignarDeportistaAAcudiente()
  }

  const html = construirMensajeExito(datos)
  await mostrarMensajeExito(html)
  redirigirSegunContexto()
}

const manejarRegistroSinRolDeportista = async () => {
  console.warn('⚠️ El rol Deportista no está presente, redirigiendo de todas formas')
  await mostrarMensajeExitoSimple()
  router.push('/deportista/dashboard')
}

const manejarPerfilNoActualizado = async () => {
  console.warn('⚠️ No se pudo actualizar el perfil, pero el registro fue exitoso')
  await mostrarMensajeExitoSimple()
  router.push('/deportista/dashboard')
}

const manejarErrorRecargaPerfil = async () => {
  console.error('❌ Error al recargar perfil')
  await mostrarMensajeExitoSimple()
  router.push('/deportista/dashboard')
}

// Función para manejar el registro de deportista
async function manejarRegistroDeportista(datos) {
  console.log("Datos del nuevo deportista:", datos)

  try {
    const profileUpdated = await recargarPerfilUsuario()

    if (profileUpdated) {
      if (tieneRolDeportista()) {
        await procesarRegistroExitoso(datos)
      } else {
        await manejarRegistroSinRolDeportista()
      }
    } else {
      await manejarPerfilNoActualizado()
    }
  } catch {
    await manejarErrorRecargaPerfil()
  }
}

// Función para asignar el deportista al acudiente actual
async function asignarDeportistaAAcudiente() {
  try {
    const usuario = authStore.user
    console.log('👤 Usuario actual:', usuario)
    console.log('🔗 El deportista registrado se asociará automáticamente al acudiente')

    // La asociación se hace automáticamente en el backend
    // cuando se crea el deportista con el array de acudientes

    return true
  } catch (error) {
    console.error('❌ Error asignando deportista al acudiente:', error)
    return false
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

