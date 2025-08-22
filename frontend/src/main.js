import './assets/css/main.css'
import './assets/css/deportistas.css'
import './assets/css/formulario.css'
import './assets/css/login.css'
import './assets/css/tarjetas.css'
import './assets/css/mensualidades.css'
import './assets/css/roles.css'
import './assets/css/galeria.css'
import "./assets/css/calendario.css";
import "./assets/css/frame-calendario.css";
import '@fortawesome/fontawesome-free/css/all.min.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'


import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
