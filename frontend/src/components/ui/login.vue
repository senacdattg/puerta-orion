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
          <h1 class="login-title-volleyball">Puerta de Orión</h1>
          <p class="login-subtitle-volleyball">Inicia sesión en la cancha</p>
        </div>

        <!-- Mensajes de error y éxito -->
        <Transition name="bounce">
          <div v-if="mensajeError" class="alert-volleyball alert-error-volleyball">
            <svg class="alert-icon-volleyball" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <span>{{ mensajeError }}</span>
          </div>
        </Transition>
        <Transition name="bounce">
          <div v-if="mensajeExito" class="alert-volleyball alert-success-volleyball">
            <svg class="alert-icon-volleyball" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span>{{ mensajeExito }}</span>
          </div>
        </Transition>

        <form class="login-form-volleyball" @submit.prevent="handleLogin">
          <!-- Campo de usuario -->
          <div class="input-group-volleyball" :class="{ 'input-active': username }">
            <label class="input-label-volleyball">
              <svg class="input-icon-volleyball" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
              </svg>
              Usuario
            </label>
            <input
              type="text"
              v-model="username"
              class="form-input-volleyball"
              placeholder="Ingresa tu usuario"
              required
              :disabled="cargando"
              @input="limpiarMensajes"
              @focus="handleInputFocus('username')"
              @blur="handleInputBlur('username')"
            />
          </div>

          <!-- Campo de contraseña -->
          <div class="input-group-volleyball" :class="{ 'input-active': password }">
            <label class="input-label-volleyball">
              <svg class="input-icon-volleyball" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
              </svg>
              Contraseña
            </label>
            <div class="password-wrapper">
              <input
                :type="showPassword ? 'text' : 'password'"
                v-model="password"
                class="form-input-volleyball"
                placeholder="Ingresa tu contraseña"
                required
                :disabled="cargando"
                @input="limpiarMensajes"
                @focus="handleInputFocus('password')"
                @blur="handleInputBlur('password')"
              />
              <button
                type="button"
                class="password-toggle-volleyball"
                @click="showPassword = !showPassword"
                :disabled="cargando"
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

          <!-- Enlace de recuperación -->
          <div class="forgot-link-volleyball">
            <router-link to="/forgot-password" class="link-text-volleyball">
              ¿Olvidaste tu contraseña?
            </router-link>
          </div>

          <!-- Botón de submit con animación de saque -->
          <button
            class="submit-button-volleyball"
            type="submit"
            :disabled="cargando || !username || !password"
            :class="{ 'serving': cargando }"
          >
            <div class="button-inner">
              <svg v-if="!cargando" class="serve-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z"/>
                <path d="M12 8v8m-4-4h8" stroke="currentColor" stroke-width="2" fill="none"/>
              </svg>
              <div v-else class="spinner-volleyball">
                <div class="spinner-ball"></div>
              </div>
              <span v-if="cargando">Iniciando sesión...</span>
              <span v-else>Saque de inicio</span>
            </div>
            <!-- Efecto de balón volando -->
            <div class="ball-trail" v-if="cargando">
              <div class="trail-dot" v-for="n in 5" :key="n" :style="{ animationDelay: `${n * 0.1}s` }"></div>
            </div>
          </button>
        </form>

        <!-- Separador -->
        <div class="divider-volleyball">
          <div class="divider-line"></div>
          <span class="divider-text">o</span>
          <div class="divider-line"></div>
        </div>

        <!-- Registro -->
        <div class="register-link-volleyball">
          <span class="register-text">¿No tienes una cuenta?</span>
          <router-link to="/registrar-general" class="link-primary-volleyball">
            Regístrate aquí
          </router-link>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import "@/assets/css/login.css"

const router = useRouter()
const authStore = useAuthStore()

// Variables reactivas
const username = ref("")
const password = ref("")
const cargando = ref(false)
const mensajeError = ref("")
const mensajeExito = ref("")
const showPassword = ref(false)

// Función para limpiar mensajes
function limpiarMensajes() {
  mensajeError.value = ""
  mensajeExito.value = ""
}

// Función para manejar el foco de los inputs
function handleInputFocus(field) {
  // Puedes agregar lógica adicional aquí si es necesario
}

function handleInputBlur(field) {
  // Puedes agregar lógica adicional aquí si es necesario
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

      // Verificar si el usuario tiene múltiples roles
      const userRoles = resultado.user?.roles || []
      const roleNames = userRoles.map(role => typeof role === 'string' ? role : role.nombre_rol)

      // Si tiene un solo rol, redirigir directamente
      // Si tiene múltiples roles, mostrar selección
      let rutaDestino = "/seleccionar-rol"
      
      if (roleNames.length === 1) {
        // Un solo rol, establecer automáticamente (esto también cargará los permisos)
        await authStore.setActiveRole(roleNames[0])
        
        // Determinar ruta según el rol único
        if (roleNames.includes('SuperAdmin') || roleNames.includes('Administrador')) {
          rutaDestino = "/admin-manager"
        } else if (roleNames.includes('Entrenador')) {
          rutaDestino = "/home"
        } else if (roleNames.includes('Deportista')) {
          rutaDestino = "/deportista/dashboard"
        } else if (roleNames.includes('Acudiente')) {
          rutaDestino = "/acudiente/dashboard"
        } else {
          rutaDestino = "/home"
        }
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

<style scoped>
/* Estilos específicos del componente - complementan login.css */
</style>
