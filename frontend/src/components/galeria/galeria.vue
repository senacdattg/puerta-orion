<template>
    <main class="contenedor-galeria">
      <!-- Filtros superiores -->
      <div class="seccion-filtros">
        <select v-model="filtroCategoria" class="form-select filtro-select">
          <option value="">Todos los eventos</option>
          <option value="Torneos">Torneos</option>
          <option value="Entrenamientos">Entrenamientos</option>
          <option value="Eventos Sociales">Eventos Sociales</option>
          <option value="Campeonatos">Campeonatos</option>
        </select>
  
        <input
          type="text"
          v-model="filtroNombre"
          class="form-control filtro-input"
          placeholder="Buscar por nombre del evento..."
        />
      </div>
  
      <!-- Heading principal -->
      <h1 class="heading-principal">Eventos del Club</h1>
  
      <!-- Sección de contenido con cuadrícula -->
      <div class="seccion-contenido grande">
        <div class="cuadricula-tarjetas">
          <div
            v-for="(evento, index) in eventosFiltrados"
            :key="index"
            class="tarjeta evento"
          >
            <div v-if="!evento.imagen" class="imagen-placeholder">
              <i :class="evento.icono"></i>
              <span>Imagen del evento</span>
            </div>
            <img
              v-else
              :src="evento.imagen"
              :alt="evento.nombre"
              class="foto-evento"
            />
  
            <div class="nombre-evento">{{ evento.nombre }}</div>
            <div class="fecha-evento">{{ evento.fecha }}</div>
            <div class="descripcion-evento">{{ evento.descripcion }}</div>
            <div class="categoria">{{ evento.categoria }}</div>
          </div>
        </div>
      </div>
    </main>
  </template>
  
  <script>
  export default {
    name: "EventosClub",
    data() {
      return {
        filtroCategoria: "",
        filtroNombre: "",
        eventos: [
          {
            nombre: "Torneo Nacional de Voleibol",
            categoria: "Torneos",
            fecha: "15 de Noviembre, 2023",
            descripcion:
              "Competición nacional con los mejores equipos juveniles de voleibol del país.",
            icono: "fas fa-volleyball-ball",
            imagen: null
          },
          {
            nombre: "Clínica de Voleo y Bloqueo",
            categoria: "Entrenamientos",
            fecha: "5 de Diciembre, 2023",
            descripcion:
              "Entrenamiento especializado en técnicas de ataque y defensa en la red.",
            icono: "fas fa-volleyball-ball",
            imagen: null
          },
          {
            nombre: "Cena de Navidad del Club",
            categoria: "Eventos Sociales",
            fecha: "20 de Diciembre, 2023",
            descripcion:
              "Celebración navideña para deportistas, entrenadores y familias del club.",
            icono: "fas fa-utensils",
            imagen: null
          },
          {
            nombre: "Campeonato Regional Sub-18",
            categoria: "Campeonatos",
            fecha: "10 de Enero, 2024",
            descripcion:
              "Participación de nuestro equipo juvenil en el campeonato regional.",
            icono: "fas fa-trophy",
            imagen: null
          },
          {
            nombre: "Escuela de Verano Vóley Playa",
            categoria: "Entrenamientos",
            fecha: "15 de Julio, 2023",
            descripcion:
              "Programa intensivo de vóley playa para todas las edades.",
            icono: "fas fa-umbrella-beach",
            imagen: null
          },
          {
            nombre: "Torneo de Invierno",
            categoria: "Torneos",
            fecha: "20 de Marzo, 2023",
            descripcion:
              "Competición indoor para mantener el ritmo en temporada baja.",
            imagen:
              "https://images.unsplash.com/photo-1565998129-8f5d5a9c8c1b?auto=format&fit=crop&w=800&q=80"
          },
          {
            nombre: "Día del Deporte Familiar",
            categoria: "Eventos Sociales",
            fecha: "15 de Mayo, 2023",
            descripcion:
              "Jornada de integración familiar con mini-torneos y actividades.",
            imagen:
              "https://images.unsplash.com/photo-1517649763962-0c2a4163f8b7?auto=format&fit=crop&w=800&q=80"
          },
          {
            nombre: "Clínica de Saque y Recepción",
            categoria: "Entrenamientos",
            fecha: "5 de Septiembre, 2023",
            descripcion:
              "Mejora tus fundamentos con nuestra clínica especializada.",
            imagen:
              "https://images.unsplash.com/photo-1571019614234-f95f8d9d1bca?auto=format&fit=crop&w=800&q=80"
          }
        ]
      };
    },
    computed: {
      eventosFiltrados() {
        return this.eventos.filter(evento => {
          const coincideCategoria =
            !this.filtroCategoria || evento.categoria === this.filtroCategoria;
          const coincideNombre =
            !this.filtroNombre ||
            evento.nombre.toLowerCase().includes(this.filtroNombre.toLowerCase());
          return coincideCategoria && coincideNombre;
        });
      }
    }
  };
  </script>
  