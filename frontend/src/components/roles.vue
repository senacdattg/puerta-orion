<template>
    <main class="contenedor-roles">
      <div class="contenedor">
        <div class="titulo">ROLES DEL USUARIO</div>
  
        <div class="tarjetas">
          <div
            v-for="(rol, index) in roles"
            :key="index"
            class="sub-contenedor"
            :class="{ inactivo: !usuarioRoles.includes(rol.nombre) }"
          >
            <div class="icono-rol">
              <i :class="rol.icono"></i>
            </div>
            <h1 class="sub-titulo">{{ rol.nombre }}</h1>
          </div>
        </div>
  
        <button class="boton" @click="$emit('volver')">Volver</button>
      </div>
    </main>
  </template>
  
  <script>
  export default {
    name: "RolesUsuario",
    props: {
      // Roles que tiene el usuario (ejemplo: ['Deportista', 'Entrenador'])
      usuarioRoles: {
        type: Array,
        default: () => []
      }
    },
    data() {
      return {
        roles: [
          { nombre: "Aspirante", icono: "fas fa-user-plus" },
          { nombre: "Deportista", icono: "fas fa-running" },
          { nombre: "Acudiente", icono: "fa-solid fa-user-group" },
          { nombre: "Entrenador", icono: "fa-solid fa-chalkboard-user" },
          { nombre: "Administrador", icono: "fa-solid fa-user-gear" }
        ]
      };
    }
  };
  </script>
  
  <style scoped>
  @import "@/assets/css/roles.css";
  
  /* Extra: estilo gris para roles inactivos */
  .sub-contenedor.inactivo {
    background-color: #d3d3d3; /* gris claro */
    color: #666;
    cursor: not-allowed;
  }
  
  .sub-contenedor.inactivo .icono-rol,
  .sub-contenedor.inactivo .sub-titulo {
    color: #666;
    border-color: #666;
  }
  </style>