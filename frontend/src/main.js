// Estilos globales
import '@/assets/styles/variables.css'
import '@/assets/styles/global.css'

// Estilos específicos por módulo
import '@/assets/css/main.css'
import '@/assets/css/inicio.css'
import '@/assets/css/deportistas.css'
import '@/assets/css/formulario.css'
import '@/assets/css/login.css'
import '@/assets/css/tarjetas.css'
import '@/assets/css/roles.css'
import '@/assets/css/galeria.css'
import '@/assets/css/calendario.css'
import '@/assets/css/frame-calendario.css'
import '@/assets/css/mensualidades.css'
import '@/assets/css/panel-admin.css'
import '@/assets/css/perfiles.css'
import '@/assets/css/dashboards.css'

// Librerías externas
import '@fortawesome/fontawesome-free/css/all.min.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Vue y plugins
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Inicializar el store de autenticación al montar la app
const authStore = useAuthStore()
authStore.inicializar()

app.mount('#app')
