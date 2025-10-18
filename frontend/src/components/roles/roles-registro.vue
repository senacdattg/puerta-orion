<template>
  <main class="contenedor-roles">
    <div class="contenedor">
      <div class="titulo"> REGISTRO ROLES </div>

      <div class="tarjetas">
        <div v-for="(rol, index) in roles" :key="index" class="sub-contenedor" @click="irFormulario(rol.ruta)">
          <div class="icono-rol">
            <i :class="rol.icono"></i>
          </div>
          <h1 class="sub-titulo">{{ rol.nombre }}</h1>
        </div>
      </div>

      <button class="boton" @click="accionBoton">Volver</button>
    </div>
  </main>
</template>

<script setup>
import { useRouter } from "vue-router"
import { ref } from "vue"

const router = useRouter()

const props = defineProps({
  usuarioRoles: {
    type: Array,
    default: () => []
  }
})

const roles = ref([
  { nombre: "Aspirante", icono: "fas fa-user-plus", ruta: '/registrar-general'},
  { nombre: "Deportista", icono: "fas fa-running", ruta: '/registrar-deportista'},
  { nombre: "Acudiente", icono: "fa-solid fa-user-group", ruta: '/registrar-general'}
])

function irFormulario(ruta) {
  router.push(ruta)
}

function accionBoton() {
  router.push("/login")
}
</script>
