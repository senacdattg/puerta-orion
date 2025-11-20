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
          <h1 class="login-title-volleyball">Restablecer Contraseña</h1>
          <p class="login-subtitle-volleyball">Ingresa tu nueva contraseña</p>
        </div>

        <div v-if="!tokenValido" class="token-invalid-container">
          <div class="invalid-icon-wrapper">
            <svg class="invalid-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
          </div>
          <h3 class="invalid-title">Token inválido o expirado</h3>
          <p class="invalid-message">
            El enlace de recuperación no es válido o ha expirado. Por favor solicita un nuevo enlace.
          </p>
          <div class="invalid-actions">
            <router-link to="/forgot-password" class="link-button">
              Solicitar nuevo enlace
            </router-link>
            <router-link to="/login" class="link-button-secondary">
              Volver al inicio de sesión
            </router-link>
          </div>
        </div>

        <form v-else class="login-form-volleyball" @submit.prevent="handleResetPassword">
          <!-- Campo de nueva contraseña -->
          <div class="input-group-volleyball">
            <label class="input-label-volleyball">
              <svg class="input-icon-volleyball" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
              </svg>
              Nueva contraseña
            </label>
            <div class="password-wrapper">
              <input
                :type="showPassword ? 'text' : 'password'"
                v-model="newPassword"
                class="form-input-volleyball"
                placeholder="Ingresa tu nueva contraseña"
                required
                :disabled="cargando || exito"
                @focus="handleInputFocus"
              />
              <button
                type="button"
                class="password-toggle-volleyball"
                @click="showPassword = !showPassword"
                :disabled="cargando || exito"
                tabindex="-1"
              >
                <svg v-if="showPassword" class="toggle-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                  <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
                </svg>
                <svg v-else class="toggle-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.906 1.255L3.707 2.293zM14.95 6.05a3 3 0 114.242 4.242L9.243 9.243a4.012 4.012 0 01-1.581-1.581L5.05 7.05A3 3 0 0114.95 6.05zm-4.242 4.242a4 4 0 01-1.581 1.581L4.18 16.18A9.958 9.958 0 0010 17c4.478 0 8.268-2.943 9.542-7a10.025 10.025 0 00-4.367-5.657l-1.507 1.507z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Campo de confirmación -->
          <div class="input-group-volleyball">
            <label class="input-label-volleyball">
              <svg class="input-icon-volleyball" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
              </svg>
              Confirmar contraseña
            </label>
            <div class="password-wrapper">
              <input
                :type="showConfirmPassword ? 'text' : 'password'"
                v-model="confirmPassword"
                class="form-input-volleyball"
                :class="{ 'input-error': !passwordsMatch && confirmPassword }"
                placeholder="Confirma tu nueva contraseña"
                required
                :disabled="cargando || exito"
                @focus="handleInputFocus"
              />
              <button
                type="button"
                class="password-toggle-volleyball"
                @click="showConfirmPassword = !showConfirmPassword"
                :disabled="cargando || exito"
                tabindex="-1"
              >
                <svg v-if="showConfirmPassword" class="toggle-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                  <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
                </svg>
                <svg v-else class="toggle-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.906 1.255L3.707 2.293zM14.95 6.05a3 3 0 114.242 4.242L9.243 9.243a4.012 4.012 0 01-1.581-1.581L5.05 7.05A3 3 0 0114.95 6.05zm-4.242 4.242a4 4 0 01-1.581 1.581L4.18 16.18A9.958 9.958 0 0010 17c4.478 0 8.268-2.943 9.542-7a10.025 10.025 0 00-4.367-5.657l-1.507 1.507z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Validación de contraseñas -->
          <div v-if="!passwordsMatch && confirmPassword" class="password-match-error">
            <svg class="error-icon-small" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            Las contraseñas no coinciden
          </div>

          <!-- Indicador de fortaleza de contraseña -->
          <div v-if="newPassword && !exito" class="password-strength">
            <div class="strength-bar">
              <div
                class="strength-fill"
                :class="passwordStrength"
                :style="{ width: passwordStrengthPercent + '%' }"
              ></div>
            </div>
            <p class="strength-text" :class="passwordStrength">
              {{ passwordStrengthText }}
            </p>
          </div>

          <!-- Botón de submit -->
          <button
            class="submit-button-volleyball"
            type="submit"
            :disabled="cargando || exito || !passwordsMatch || !newPassword || !confirmPassword"
            :class="{ 'success': exito }"
          >
            <div class="button-inner">
              <svg v-if="exito" class="success-icon-small" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
              <div v-else-if="cargando" class="spinner-volleyball">
                <div class="spinner-ball"></div>
              </div>
              <svg v-else class="reset-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
              </svg>
              <span v-if="cargando">Restableciendo...</span>
              <span v-else-if="exito">Contraseña restablecida</span>
              <span v-else>Restablecer contraseña</span>
            </div>
          </button>
        </form>

        <!-- Separador -->
        <div class="divider-volleyball" v-if="tokenValido && !exito">
          <div class="divider-line"></div>
        </div>

        <!-- Enlace de volver -->
        <div class="back-link-container" v-if="tokenValido && !exito">
          <router-link to="/login" class="link-text-volleyball">
            <svg class="back-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
            </svg>
            Volver al inicio de sesión
          </router-link>
        </div>

        <!-- Mensaje de éxito -->
        <div v-if="exito" class="success-container">
          <div class="success-countdown">
            <p>Serás redirigido al inicio de sesión en <strong>{{ countdown }}</strong> segundos</p>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter, useRoute } from "vue-router"
import authService from "@/services/authService"
import "@/assets/css/login.css"
import Swal from "sweetalert2"

const router = useRouter()
const route = useRoute()

// Variables reactivas
const token = ref("")
const newPassword = ref("")
const confirmPassword = ref("")
const cargando = ref(false)
const exito = ref(false)
const tokenValido = ref(true)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const countdown = ref(3)

// Computed para validar que las contraseñas coincidan
const passwordsMatch = computed(() => {
  if (!newPassword.value || !confirmPassword.value) return true
  return newPassword.value === confirmPassword.value
})

// Computed para la fortaleza de la contraseña
const passwordStrength = computed(() => {
  if (!newPassword.value) return ''
  const length = newPassword.value.length
  if (length < 6) return 'weak'
  if (length < 10) return 'medium'
  return 'strong'
})

const passwordStrengthPercent = computed(() => {
  if (!newPassword.value) return 0
  const length = newPassword.value.length
  if (length < 6) return (length / 6) * 33
  if (length < 10) return 33 + ((length - 6) / 4) * 33
  return 100
})

const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value
  if (strength === 'weak') return 'Contraseña débil'
  if (strength === 'medium') return 'Contraseña media'
  return 'Contraseña fuerte'
})

// Función para manejar el foco de los inputs
function handleInputFocus(event) {
  event.target.parentElement.classList.add('input-focused')
}

// Obtener token de la URL al montar el componente
onMounted(() => {
  const tokenParam = route.query.token
  if (tokenParam) {
    token.value = tokenParam
  } else {
    tokenValido.value = false
    Swal.fire({
      icon: "error",
      title: "Token inválido",
      text: "No se proporcionó un enlace válido. Solicita nuevamente la recuperación."
    })
  }
})

// Función para manejar el contador regresivo
function startCountdown() {
  countdown.value = 3
  const interval = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(interval)
      router.push("/login")
    }
  }, 1000)
}

// Función para manejar el restablecimiento de contraseña
async function handleResetPassword() {
  // Validaciones
  if (!newPassword.value || !confirmPassword.value) {
    Swal.fire({
      icon: "warning",
      title: "Campos incompletos",
      text: "Por favor completa ambos campos de contraseña."
    })
    return
  }

  if (newPassword.value.length < 6) {
    Swal.fire({
      icon: "warning",
      title: "Contraseña muy corta",
      text: "La contraseña debe tener al menos 6 caracteres."
    })
    return
  }

  if (!passwordsMatch.value) {
    Swal.fire({
      icon: "warning",
      title: "Contraseñas diferentes",
      text: "Asegúrate de que ambas contraseñas coincidan."
    })
    return
  }

  if (!token.value) {
    tokenValido.value = false
    Swal.fire({
      icon: "error",
      title: "Token inválido",
      text: "El token de recuperación no es válido o ha expirado."
    })
    return
  }

  cargando.value = true

  try {
    const resultado = await authService.resetPassword(
      token.value,
      newPassword.value,
      confirmPassword.value
    )

    if (resultado.success) {
      await Swal.fire({
        icon: "success",
        title: "Contraseña actualizada",
        text: resultado.message || "Tu contraseña se restableció correctamente.",
        confirmButtonText: "Ir al login"
      })
      exito.value = true
      startCountdown()
    } else {
      Swal.fire({
        icon: "error",
        title: "No se pudo restablecer",
        text: resultado.error || "Intenta nuevamente más tarde."
      })

      // Si el error es de token inválido o expirado
      if (resultado.error && (
        resultado.error.toLowerCase().includes('token') ||
        resultado.error.toLowerCase().includes('expirado') ||
        resultado.error.toLowerCase().includes('inválido')
      )) {
        tokenValido.value = false
      }
    }
  } catch (error) {
    Swal.fire({
      icon: "error",
      title: "Error de conexión",
      text: error.message || "No logramos comunicarnos con el servidor."
    })

    // Verificar si es un error de token
    if (error.message && (
      error.message.toLowerCase().includes('token') ||
      error.message.toLowerCase().includes('expirado') ||
      error.message.toLowerCase().includes('inválido')
    )) {
      tokenValido.value = false
    }
  } finally {
    cargando.value = false
  }
}
</script>


