<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import ListaDeportistas from '../components/deportistas/lista-deportistas.vue';
import Pie from '../components/ui/pie.vue';
import { ref } from 'vue';

// Datos de ejemplo para demostrar la funcionalidad
const deportistas = ref([
  {
    id: 1,
    nombre: 'Carlos Rodríguez',
    categoria: 'juvenil',
    estado: 'activo',
    imagen: null
  },
  {
    id: 2,
    nombre: 'Ana Martínez',
    categoria: 'infantil',
    estado: 'activo',
    imagen: null
  },
  {
    id: 3,
    nombre: 'Luis García',
    categoria: 'adulto',
    estado: 'inactivo',
    imagen: null
  },
  {
    id: 4,
    nombre: 'María López',
    categoria: 'juvenil',
    estado: 'suspendido',
    imagen: null
  },
  {
    id: 5,
    nombre: 'Juan Pérez',
    categoria: 'infantil',
    estado: 'activo',
    imagen: null
  },
  {
    id: 6,
    nombre: 'Sofia Torres',
    categoria: 'adulto',
    estado: 'activo',
    imagen: null
  }
]);

</script>

<template>
  <main>
    <Encabezado rol="Admin"/>
    <ListaDeportistas
      :deportistas="deportistas"
      @editar="editarDeportista"
      @eliminar="eliminarDeportista"
    />
    <Pie />
  </main>
</template>

<style>
/* Importamos el CSS moderno para deportistas */
@import '../assets/css/deportistas-modern.css';
</style>
