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

  // Validar formato de email básico
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
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

<style scoped>
/* Estilos específicos para el éxito */
.success-container {
  text-align: center;
  padding: 2rem 0;
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.success-icon-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.success-icon {
  width: 80px;
  height: 80px;
  color: var(--color-exito);
  animation: scaleIn 0.5s ease-out;
}

@keyframes scaleIn {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

.success-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primario);
  margin: 0 0 1rem 0;
}

.success-message {
  font-size: 1rem;
  color: var(--color-gris-oscuro);
  line-height: 1.6;
  margin: 0 0 1.5rem 0;
  padding: 0 1rem;
}

.success-countdown {
  font-size: 0.9rem;
  color: var(--color-gris-oscuro);
  padding: 1rem;
  background: var(--color-gris-claro);
  border-radius: var(--radio-md);
}

.success-countdown strong {
  color: var(--color-primario);
  font-size: 1.2rem;
}

/* Estilos para el ícono de enviar */
.send-icon {
  width: 20px;
  height: 20px;
  animation: iconSend 0.5s ease-in-out infinite alternate;
}

@keyframes iconSend {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(3px);
  }
}

/* Contenedor para el enlace de volver */
.back-link-container {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  padding-bottom: 2rem;
  text-align: center;
  border-top: 1px solid var(--color-gris-medio);
}

/* Estilos para el ícono de volver */
.back-icon {
  width: 18px;
  height: 18px;
  margin-right: 0.5rem;
  transition: var(--transicion);
}

.link-text-volleyball {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  color: var(--color-primario);
  text-decoration: none;
  font-weight: 500;
  transition: var(--transicion);
  padding: 0.5rem 1rem;
}

.link-text-volleyball:hover {
  color: #003380;
  text-decoration: underline;
}

.link-text-volleyball:hover .back-icon {
  transform: translateX(-3px);
}

/* Estilos para el botón cuando está enviando */
.submit-button-volleyball.sending {
  animation: sendingPulse 1.5s ease-in-out infinite;
}

@keyframes sendingPulse {
  0%, 100% {
    box-shadow: var(--sombra-md);
  }
  50% {
    box-shadow: 0 0 20px rgba(0, 71, 171, 0.4);
  }
}

/* Responsive */
@media (max-width: 640px) {
  .success-icon {
    width: 60px;
    height: 60px;
  }

  .success-title {
    font-size: 1.25rem;
  }

  .success-message {
    font-size: 0.9rem;
  }
}
</style>
