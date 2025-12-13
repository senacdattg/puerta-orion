<template>
    <div id="titulo-club" class="titulo-club">
      <div class="bloque bloque-amarillo">CLUB DEPORTIVO</div>
      <div class="bloque bloque-azul">PUERTA DE ORIÓN</div>
    </div>
  </template>
  
  <script>
  export default {
    name: "TituloClub",
    props: {
      url: {
        type: String,
        required: false
      }
    },
    mounted() {
      if (this.url) {
        fetch(this.url)
          .then(res => res.text())
          .then(html => {
            this.$el.innerHTML = html
          })
          .catch(err => {
            console.error("❌ Error al cargar el logo:", err);
          });
      }
    }
  };
  </script>