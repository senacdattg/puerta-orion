<template>
  <main class="contenedor-roles">
    <div class="contenedor">
      <div class="titulo">ROLES DEL USUARIO</div>

      <div class="tarjetas">
        <div v-for="(rol, index) in roles" :key="index" class="sub-contenedor"
          :class="{ inactivo: !usuarioRoles.includes(rol.nombre) }">
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
import { defineProps, ref } from "vue"

const router = useRouter()

const props = defineProps({
  usuarioRoles: {
    type: Array,
    default: () => []
  }
})

const roles = ref([
  { nombre: "Aspirante", icono: "fas fa-user-plus" },
  { nombre: "Deportista", icono: "fas fa-running" },
  { nombre: "Acudiente", icono: "fa-solid fa-user-group" },
  { nombre: "Entrenador", icono: "fa-solid fa-chalkboard-user" },
  { nombre: "Administrador", icono: "fa-solid fa-user-gear" }
])

function accionBoton() {
  router.push("/ver-general")
}
</script>
