<template>
  <header class="encabezado" >
    <i v-if="!sinMenu"
    class="fa-solid fa-bars menu-toggle"
    @click="toggleMenu"
    ></i>
    
    <img src="@/assets/imgs/logo.png" alt="Logo">
    <div class="menu-categorias" id="menu" v-show="menuVisible">
      <ul id="menu-opciones">
        <li v-for="(op, index) in opciones" :key="index">
          <a :href="op.link" @click="closeMenu">
            <i :class="op.icono + ' icono-menu'"></i> {{ op.texto }}
          </a>
        </li>
      </ul>
    </div>
  </header>
</template>

<script>
export default {
  name: "Encabezado",
  props: {
    rol: {
      type: String,
      default: document.body.getAttribute("data-rol") || ""
    },
    sinMenu: {
      type: Boolean,
      default: document.body.hasAttribute("data-sin-menu")
    }
  },
  data() {
    return {
      menuVisible: false,
      opciones: []
    };
  },
  mounted() {
    if (!this.sinMenu) {
      this.cargarOpciones();
      document.addEventListener("click", this.handleOutsideClick);
    }
  },
  beforeUnmount() {
    document.removeEventListener("click", this.handleOutsideClick);
  },
  methods: {
    toggleMenu() {
      this.menuVisible = !this.menuVisible;
    },
    closeMenu() {
      this.menuVisible = false;
    },
    handleOutsideClick(e) {
      if (!this.$el.contains(e.target)) {
        this.menuVisible = false;
      }
    },
    cargarOpciones() {
      const opcionesPorRol = {
        Aspirante: [
          { texto: "Inicio", link: "/inicio", icono: "fas fa-home" },
          { texto: "Perfil", link: "/perfil_aspirante", icono: "fas fa-user" },
          { texto: "Inscribirse", link: "#", icono: "fas fa-file-signature" },
        ],
        Entrenador: [
          { texto: "Inicio", link: "/inicio", icono: "fas fa-home" },
          { texto: "Perfil", link: "/perfil_entrenador", icono: "fas fa-user" },
          { texto: "Deportistas", link: "/tabla-deportistas", icono: "fas fa-users" },
        ],
        Acudiente: [
          { texto: "Inicio", link: "/inicio", icono: "fas fa-home" },
          { texto: "Perfil", link: "/perfil_acudiente", icono: "fas fa-user" },
          { texto: "Mensualidades", link: "/mensualidades_deportista", icono: "fas fa-wallet" },
        ],
        Deportista: [
          { texto: "Inicio", link: "/inicio", icono: "fas fa-home" },
          { texto: "Perfil", link: "/perfil_deportista", icono: "fas fa-user" },
          { texto: "Mensualidades", link: "/mensualidades_deportista", icono: "fas fa-wallet" },
        ],
        Admin: [
          { texto: "Inicio", link: "/inicio", icono: "fas fa-home" },
          { texto: "Perfil", link: "/perfil_admin", icono: "fas fa-user" },
          { texto: "Deportistas", link: "/tabla-deportistas-admin", icono: "fas fa-users" },
          { texto: "Mensualidades", link: "/tabla-mensualidades", icono: "fas fa-wallet" },
        ]
      };
      this.opciones = opcionesPorRol[this.rol] || [
        { texto: "Inicio", link: "/", icono: "fas fa-home" }
      ];
    }
  }
};
</script>

<style scoped>
@import "@/assets/css/main.css";
</style>
