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
          <router-link to="/roles-registro" class="text-primary fw-bold">Regístrate aquí</router-link>
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
    console.log('🔐 Login: Iniciando proceso...')
    console.log('🔐 Login: Credenciales:', { username: username.value, password: '***' })

    // Probar conexión directa primero
    console.log('🔐 Login: Probando conexión directa...')
    const testResponse = await fetch('http://localhost:5000/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      })
    })

    console.log('🔐 Login: Respuesta directa:', testResponse.status)
    const testData = await testResponse.json()
    console.log('🔐 Login: Datos directos:', testData)

    if (!testResponse.ok) {
      mensajeError.value = testData.error || "Error al iniciar sesión"
      return
    }

    // Si la conexión directa funciona, usar el store
    console.log('🔐 Login: Usando store...')
    const resultado = await authStore.login({
      username: username.value,
      password: password.value
    })

    console.log('🔐 Login: Resultado del store:', resultado)
    console.log('🔐 Login: Usuario autenticado:', authStore.estaAutenticado)
    console.log('🔐 Login: Usuario actual:', authStore.usuario)

    if (resultado.success) {
      mensajeExito.value = "¡Login exitoso! Redirigiendo..."

      console.log('🔐 Login: Intentando redirigir a /home...')

      // Redirigir al home después de 1 segundo
      setTimeout(() => {
        console.log('🔐 Login: Ejecutando redirección...')
        router.push("/home")
      }, 1000)
    } else {
      mensajeError.value = resultado.error || "Error al iniciar sesión"
    }
  } catch (error) {
    console.error('🔐 Login: Error completo:', error)
    mensajeError.value = error.message || "Error de conexión"
  } finally {
    cargando.value = false
  }
}
</script>
