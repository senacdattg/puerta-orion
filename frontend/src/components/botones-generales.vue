<template>
    <div class="botones-formulario" style="display: flex; justify-content: center; gap: 20px;">
      <button class="boton-formulario" style="width: 150px" @click="irInicio">Inicio</button>
      <button class="boton-formulario" style="width: 150px" @click="irCalendario">Calendario</button>
      <button class="boton-formulario" style="width: 150px" @click="irGaleria">Galería</button>
    </div>
  </template>
  
  <script setup>
  import { useRouter } from "vue-router"
  
  const router = useRouter()
  
  function irInicio() {
    router.push("/")
  }
  
  function irCalendario() {
    router.push("/calendario")
  }
  
  function irGaleria() {
    router.push("/galeria")
  }
  </script>
  