<template>
  <main class="contenedor-formulario">
    <form class="formulario" @submit.prevent="handleLogin">
      <img src="@/assets/imgs/icono.png" alt="text" class="icono-formulario" />
      <label class="etiqueta-formulario">Inicio de Sesión</label>

      <!-- Mensajes de error y éxito -->
      <div v-if="mensajeError" class="mensaje-error">
        {{ mensajeError }}
      </div>
      <div v-if="mensajeExito" class="mensaje-exito">
        {{ mensajeExito }}
      </div>

      <div class="fila-texto">
        <input
          type="text"
          v-model="username"
          placeholder="Usuario o correo electrónico"
          required
          :disabled="cargando"
          @input="limpiarMensajes"
        />
      </div>

      <div class="fila-texto">
        <input
          type="password"
          v-model="password"
          placeholder="Contraseña"
          required
          :disabled="cargando"
          @input="limpiarMensajes"
        />
      </div>

      <button
        class="boton-formulario"
        type="submit"
        :disabled="cargando"
      >
        <span v-if="cargando">Iniciando sesión...</span>
        <span v-else>Iniciar sesión</span>
      </button>

      <div class="text-center mt-3">
        <p>
          ¿No tienes una cuenta?
          <router-link to="/registrar-general" class="text-primary fw-bold">Regístrate aquí</router-link>
        </p>
      </div>
    </form>
  </main>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const router = useRouter()
const authStore = useAuthStore()

// Variables reactivas
const username = ref("")
const password = ref("")
const cargando = ref(false)
const mensajeError = ref("")
const mensajeExito = ref("")

// Función para limpiar mensajes
function limpiarMensajes() {
  mensajeError.value = ""
  mensajeExito.value = ""
}

// Función para manejar el login
async function handleLogin() {
  if (!username.value || !password.value) {
    mensajeError.value = "Por favor completa todos los campos"
    return
  }

  cargando.value = true
  mensajeError.value = ""
  mensajeExito.value = ""

  try {
    const resultado = await authStore.login({
      username: username.value,
      password: password.value
    })

    if (resultado.success) {
      mensajeExito.value = "¡Login exitoso! Redirigiendo..."

      // Verificar roles del usuario para decidir la redirección
      const userRoles = resultado.user?.roles || []
      const roleNames = userRoles.map(role => role.nombre_rol)

      // Determinar ruta de redirección según el rol
      let rutaDestino = "/home"

      if (roleNames.includes('SuperAdmin') || roleNames.includes('Administrador')) {
        rutaDestino = "/admin-manager"
      }

      // Redirigir después de 1 segundo
      setTimeout(() => {
        router.push(rutaDestino)
      }, 1000)
    } else {
      mensajeError.value = resultado.error || "Error al iniciar sesión"
    }
  } catch (error) {
    mensajeError.value = error.message || "Error de conexión"
  } finally {
    cargando.value = false
  }
}
</script>
