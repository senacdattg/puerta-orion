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
              @focus="handleInputFocus()"
              @blur="handleInputBlur()"
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
                @focus="handleInputFocus()"
                @blur="handleInputBlur()"
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
import { ref, onMounted, onBeforeUnmount } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import "@/assets/css/login.css"
import Swal from "sweetalert2"

// Definir nombre del componente para evitar error del linter
defineOptions({
  name: 'LoginComponent'
})

const router = useRouter()
const authStore = useAuthStore()

// Variables reactivas
const username = ref("")
const password = ref("")
const cargando = ref(false)
const showPassword = ref(false)

// Funciones para manejar el foco de los inputs (reservadas para futuras mejoras)
function handleInputFocus() {
  // Función reservada para futuras mejoras de UX
}

function handleInputBlur() {
  // Función reservada para futuras mejoras de UX
}

// Función para manejar el login
async function handleLogin() {
  if (!username.value || !password.value) {
    Swal.fire({
      icon: "warning",
      title: "Campos incompletos",
      text: "Por favor completa el usuario y la contraseña.",
      confirmButtonText: "Entendido"
    })
    return
  }

  cargando.value = true

  try {
    const resultado = await authStore.login({
      username: username.value,
      password: password.value
    })

    if (resultado.success) {

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

      await Swal.fire({
        icon: "success",
        title: "¡Inicio de sesión exitoso!",
        text: "Redirigiendo a tu panel...",
        timer: 1500,
        timerProgressBar: true,
        showConfirmButton: false
      })

      router.push(rutaDestino)
    } else {
      Swal.fire({
        icon: "error",
        title: "No pudimos iniciar sesión",
        text: resultado.error || "Verifica tus credenciales e inténtalo nuevamente.",
        confirmButtonText: "Intentar de nuevo"
      })
    }
  } catch (error) {
    Swal.fire({
      icon: "error",
      title: "Error de conexión",
      text: error.message || "No logramos comunicarnos con el servidor.",
      confirmButtonText: "Reintentar"
    })
  } finally {
    cargando.value = false
  }
}

// Limpiar estilos del body cuando se monta el login
onMounted(() => {
  document.body.classList.remove('has-fixed-header', 'has-static-sidebar', 'menu-closing')
  document.body.style.paddingTop = '0'
  document.body.style.paddingLeft = '0'
})

// Restaurar al desmontar (aunque no debería ser necesario)
onBeforeUnmount(() => {
  document.body.style.paddingTop = ''
  document.body.style.paddingLeft = ''
})
</script>


