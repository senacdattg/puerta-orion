<template>
  <main class="login-container-volleyball">
    <!-- Fondo animado de cancha de voleibol -->
    <div class="court-background">
      <div class="court-lines"></div>
      <div class="court-net">
        <div class="net-line"></div>
        <div class="net-mesh"></div>
      </div>
    </div>

    <!-- Tarjeta de login -->
    <div class="login-wrapper-volleyball">
      <div class="login-card-volleyball">
        <!-- Header con logo y título -->
        <div class="login-header-volleyball">
          <div class="logo-container-volleyball">
            <img src="@/assets/imgs/icono.png" alt="Logo Puerta de Orión" class="logo-club" />
          </div>
          <h1 class="login-title-volleyball">Recuperar Contraseña</h1>
          <p class="login-subtitle-volleyball">Te enviaremos un enlace para restablecer tu contraseña</p>
        </div>

        <form class="login-form-volleyball" @submit.prevent="handleForgotPassword" v-if="!enviado">
          <!-- Campo de email -->
          <div class="input-group-volleyball">
            <label class="input-label-volleyball">
              <svg class="input-icon-volleyball" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
              </svg>
              Correo electrónico
            </label>
            <input
              type="email"
              v-model="email"
              class="form-input-volleyball"
              placeholder="Ingresa tu correo electrónico"
              required
              :disabled="cargando"
              @focus="handleInputFocus"
            />
          </div>

          <!-- Botón de submit -->
          <button
            class="submit-button-volleyball"
            type="submit"
            :disabled="cargando || !email"
            :class="{ 'sending': cargando }"
          >
            <div class="button-inner">
              <svg v-if="!cargando" class="send-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
              <div v-else class="spinner-volleyball">
                <div class="spinner-ball"></div>
              </div>
              <span v-if="cargando">Enviando...</span>
              <span v-else>Enviar enlace de recuperación</span>
            </div>
          </button>
        </form>

        <!-- Mensaje de éxito con ícono -->
        <div v-if="enviado" class="success-container">
          <div class="success-icon-wrapper">
            <svg class="success-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <h3 class="success-title">¡Correo enviado!</h3>
          <p class="success-message">
            Se ha enviado un enlace de recuperación a tu correo electrónico.
            Por favor revisa tu bandeja de entrada y sigue las instrucciones.
          </p>
          <div class="success-countdown">
            <p>Serás redirigido al inicio de sesión en <strong>{{ countdown }}</strong> segundos</p>
          </div>
        </div>

        <!-- Separador -->
        <div class="divider-volleyball" v-if="!enviado">
          <div class="divider-line"></div>
        </div>

        <!-- Enlace de recuperación -->
        <div class="back-link-container" v-if="!enviado">
          <router-link to="/login" class="link-text-volleyball">
            <svg class="back-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
            </svg>
            Volver al inicio de sesión
          </router-link>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import authService from "@/services/authService"
import "@/assets/css/login.css"
import Swal from "sweetalert2"

const router = useRouter()

// Variables reactivas
const email = ref("")
const cargando = ref(false)
const enviado = ref(false)
const countdown = ref(5)

// Función para manejar el foco de los inputs
function handleInputFocus(event) {
  event.target.parentElement.classList.add('input-focused')
}

// Función para manejar el contador regresivo
function startCountdown() {
  countdown.value = 5
  const interval = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(interval)
      router.push("/login")
    }
  }, 1000)
}

// Función para manejar la solicitud de recuperación
async function handleForgotPassword() {
  if (!email.value) {
    Swal.fire({
      icon: "warning",
      title: "Correo requerido",
      text: "Por favor ingresa tu correo electrónico para continuar."
    })
    return
  }

  // Validar formato de email usando regex seguro (sin backtracking catastrófico)
  // Usamos un regex más simple y seguro que evita ReDoS (Regular Expression Denial of Service)
  // Este regex es más restrictivo pero evita backtracking excesivo
  // nosonar: S5852 - Regex simplificado para evitar ReDoS, validación adicional en backend
  const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  if (!emailRegex.test(email.value)) {
    Swal.fire({
      icon: "warning",
      title: "Correo no válido",
      text: "Revisa el formato del correo electrónico e inténtalo nuevamente."
    })
    return
  }

  cargando.value = true

  try {
    const resultado = await authService.forgotPassword(email.value)

    if (resultado.success) {
      await Swal.fire({
        icon: "success",
        title: "¡Correo enviado!",
        text: resultado.message || "Te enviamos un enlace para restablecer tu contraseña.",
        confirmButtonText: "Entendido"
      })
      enviado.value = true
      startCountdown()
    } else {
      Swal.fire({
        icon: "error",
        title: "No pudimos enviar el correo",
        text: resultado.error || "Inténtalo de nuevo en unos minutos."
      })
    }
  } catch (error) {
    Swal.fire({
      icon: "error",
      title: "Error de conexión",
      text: error.message || "No logramos comunicarnos con el servidor."
    })
  } finally {
    cargando.value = false
  }
}
</script>

