<template>
  <main class="contenedor-galeria">

    <!-- Heading principal -->
    <h1 class="titulo-principal-galeria">Eventos del Club</h1>

    <!-- Sección de contenido con cuadrícula -->
    <div class="seccion-contenido grande">

      <div class="bloque-subtitulo">
        <span class="subtitulo-bloque">Categorías de búsqueda</span>

        <div class="contenedor-filtros">
          <div class="buscador">
            <input type="search" v-model="busqueda" placeholder="Buscar eventos ..." class="entrada-busqueda" />
            <span class="icono-busqueda">🔍</span>
          </div>
          <div class="filtros">
            <select v-model="filtroEvento" class="filtro-select">
              <option value="">Filtrar por eventos</option>
              <option v-for="tipo in tipos" :key="tipo" :value="tipo">{{ tipo }}</option>
            </select>
            <select v-model="filtroMes" class="filtro-select">
              <option value="">Filtrar por mes</option>
              <option v-for="mes in meses" :key="mes" :value="mes">{{ mes }}</option>
            </select>
          </div>
        </div>
      </div>


      <div class="cuadricula-tarjetas">
        <div v-for="(evento, index) in eventosFiltrados" :key="index" class="tarjeta evento"
          @click="esAdmin && editarEvento(index)">
          <div v-if="!evento.imagen" class="imagen-placeholder">
            <i :class="evento.icono"></i>
            <span>Imagen del evento</span>
          </div>
          <img v-else :src="evento.imagen" :alt="evento.nombre" class="foto-evento" />

          <div class="nombre-evento">{{ evento.nombre }}</div>
          <div class="fecha-evento">{{ evento.fecha }}</div>
          <div class="descripcion-evento">{{ evento.descripcion }}</div>
          <div class="tipo" :class="claseTipo(evento.tipo)">
            {{ evento.tipo }}
          </div>
        </div>

        <div v-if="esAdmin" class="boton-agregar" @click="abrirFormulario">
          +
        </div>
      </div>

    </div>

    <!-- Modal de formulario -->
    <div v-if="mostrarFormulario" class="modal-overlay">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editando !== null ? 'Editar Evento' : 'Agregar Evento' }}</h3>
          <button class="btn-cerrar" title="Cerrar" @click="cerrarFormulario">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <form @submit.prevent="guardarEvento" class="formulario-evento">
          <div class="campo-formulario">
            <label for="nombre">
              <i class="fas fa-heading"></i>
              Título del evento *
            </label>
            <input id="nombre" v-model="form.nombre" type="text" placeholder="Ej: Megaweekend" class="input-evento" />
          </div>
          <div class="campo-formulario">
            <label for="fecha">
              <i class="fas fa-calendar"></i>
              Fecha *
            </label>
            <input id="fecha" v-model="form.fecha" type="date" class="input-evento" />
          </div>
          <div class="campo-formulario">
            <label for="tipo">
              <i class="fas fa-tag"></i>
              Tipo de evento *
            </label>
            <select v-model="form.tipo" class="select-evento">
              <option disabled value="">Selecciona categoría</option>
              <option v-for="tipo in tipos" :key="tipo" :value="tipo">{{ tipo }}</option>
            </select>
          </div>
          <div class="campo-formulario">
            <label for="imagen">
              <i class="fas fa-camera"></i>
              Imagen *
            </label>
            <input id="imagen" v-model="form.imagen" type="url" placeholder="URL de imagen" class="input-evento" />
          </div>
          <div class="campo-formulario">
            <label for="descripcion">
              <i class="fas fa-align-left"></i>
              Descripción
            </label>
            <textarea id="descripcion" v-model="form.descripcion" placeholder="Descripción"
              class="input-evento"></textarea>
          </div>

          <div class="acciones centrado">
            <button class="btn-principal" @click="guardarEvento">Aceptar</button>
            <button class="btn-secundario" v-if="editando !== null" @click="eliminarEvento">Eliminar</button>
          </div>
        </form>

      </div>




    </div>

  </main>
</template>

<script>

export default {
  name: "EventosClub",
  data() {
    return {
      esAdmin: true,
      busqueda: "",
      filtroMes: "",
      filtroEvento: "",
      tipos: ["🏆 Competencias", "🏋️ Entrenamientos", "🎉 Eventos"],
      meses: [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
      ],

      eventos: [
        {
          nombre: "Torneo Nacional de Voleibol",
          tipo: "🏆 Competencias",
          fecha: "15 de Noviembre, 2023",
          descripcion:
            "Competición nacional con los mejores equipos juveniles de voleibol del país.",
          imagen: null
        },
        {
          nombre: "Clínica de Voleo y Bloqueo",
          tipo: "🏋️ Entrenamientos",
          fecha: "5 de Diciembre, 2023",
          descripcion:
            "Entrenamiento especializado en técnicas de ataque y defensa en la red.",
          icono: "fas fa-volleyball-ball",
          imagen: null
        },
        {
          nombre: "Cena de Navidad del Club",
          tipo: "🎉 Eventos",
          fecha: "20 de Diciembre, 2023",
          descripcion:
            "Celebración navideña para deportistas, entrenadores y familias del club.",
          icono: "fas fa-utensils",
          imagen: null
        },
        {
          nombre: "Campeonato Regional Sub-18",
          tipo: "🏆 Competencias",
          fecha: "10 de Enero, 2024",
          descripcion:
            "Participación de nuestro equipo juvenil en el campeonato regional.",
          icono: "fas fa-trophy",
          imagen: null
        },
        {
          nombre: "Escuela de Verano Vóley Playa",
          tipo: "🏋️ Entrenamientos",
          fecha: "15 de Julio, 2023",
          descripcion:
            "Programa intensivo de vóley playa para todas las edades.",
          icono: "fas fa-umbrella-beach",
          imagen: null
        },
        {
          nombre: "Torneo de Invierno",
          tipo: "🏆 Competencias",
          fecha: "20 de Marzo, 2023",
          descripcion:
            "Competición indoor para mantener el ritmo en temporada baja.",
          imagen:
            "https://images.unsplash.com/photo-1565998129-8f5d5a9c8c1b?auto=format&fit=crop&w=800&q=80"
        },
        {
          nombre: "Día del Deporte Familiar",
          tipo: "🎉 Eventos",
          fecha: "15 de Mayo, 2023",
          descripcion:
            "Jornada de integración familiar con mini-torneos y actividades.",
          imagen:
            "https://images.unsplash.com/photo-1517649763962-0c2a4163f8b7?auto=format&fit=crop&w=800&q=80"
        },
        {
          nombre: "Clínica de Saque y Recepción",
          tipo: "🏋️ Entrenamientos",
          fecha: "5 de Septiembre, 2023",
          descripcion:
            "Mejora tus fundamentos con nuestra clínica especializada.",
          imagen:
            "https://images.unsplash.com/photo-1571019614234-f95f8d9d1bca?auto=format&fit=crop&w=800&q=80"
        }
      ],

      // Nuevo estado para formulario
      mostrarFormulario: false,
      editando: false, // índice del evento que se edita o null
      form: {
        nombre: "",
        tipo: "",
        fecha: "",
        descripcion: "",
        imagen: ""
      }
    };
  },
  computed: {
    eventosFiltrados() {
      return this.eventos.filter(evento => {
        const coincideTipo =
          !this.filtroEvento || evento.tipo === this.filtroEvento;

        const coincideNombre =
          !this.busqueda ||
          evento.nombre.toLowerCase().includes(this.busqueda.toLowerCase());

        const coincideMes =
          !this.filtroMes ||
          evento.fecha.toLowerCase().includes(this.filtroMes.toLowerCase());

        return coincideTipo && coincideNombre && coincideMes;
      });
    }
  },
  methods: {
    abrirFormulario() {
      this.editando = null;
      this.form = { nombre: "", fecha: "", descripcion: "", tipo: "", imagen: "" };
      this.mostrarFormulario = true;
    },
    cerrarFormulario() {
      this.mostrarFormulario = false;
      this.limpiarFormulario();
    },
    editarEvento(index) {
      this.editando = index;
      this.form = { ...this.eventos[index] };
      this.mostrarFormulario = true;
    },
    guardarEvento() {
      if (this.editando !== null) {
        this.eventos[this.editando] = { ...this.form };
      } else {
        this.eventos.push({ ...this.form });
      }
      this.mostrarFormulario = false;
    },
    cancelarFormulario() {
      this.mostrarFormulario = false;
    },
    limpiarFormulario() {
      this.form = {
        nombre: "",
        fecha: "",
        descripcion: "",
        tipo: "",
        imagen: ""
      };
      this.editando = null;
    },
    eliminarEvento() {
      if (this.editando !== null) {
        this.eventos.splice(this.editando, 1);
      }
      this.mostrarFormulario = false;
    },
    claseTipo(tipo) {
      return tipo
        // elimina todos los emojis conocidos
        .replace(/[\p{Emoji_Presentation}\p{Emoji}\uFE0F]/gu, '')
        .trim()
        .toLowerCase()
        .replace(/\s+/g, '-');
    }
  }
};
</script>

<style>
.acciones {
  display: flex;
  justify-content: space-between;
  margin-top: 5px;
}

.acciones.centrado {
  justify-content: center;
  /* centra todos los botones horizontalmente */
  gap: 10px;
  /* opcional: separa los botones un poco */
}
</style>