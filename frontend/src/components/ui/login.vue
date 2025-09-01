<template>
    <main class="contenedor-formulario">
      <form class="formulario" @submit.prevent="handleLogin">
        <img src="@/assets/imgs/icono.png" alt="text" class="icono-formulario" />
        <label class="etiqueta-formulario">Inicio de Sesión</label>
  
        <div class="fila-texto">
          <input type="email" v-model="email" placeholder="Correo" required />
        </div>
  
        <div class="fila-texto">
          <input type="password" v-model="password" placeholder="Contraseña" required />
        </div>
  
        <button class="boton-formulario" type="submit" @click="accionBoton">Iniciar sesión</button>

  
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

  import { useRouter } from "vue-router"
  
  const router = useRouter()

  function accionBoton() {
  router.push("/");
}
  
  // Variables reactivas

  

  </script>