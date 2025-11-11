<template>
  <main class="contenedor-galeria">

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
              <option v-for="tipo in tipos" :key="tipo.id_tipo_evento" :value="tipo.nombre">{{ tipo.nombre }}</option>
            </select>
            <button @click="limpiarFiltros" class="btn-limpiar-filtros">Limpiar filtros</button>
          </div>
        </div>
      </div>


      <div class="cuadricula-tarjetas">
        <div v-for="(evento, index) in eventosFiltrados" :key="index" class="tarjeta evento"
          @click="verDetalleEvento(index)">
          <div v-if="!evento.url_imagen" class="imagen-placeholder">
            <i :class="evento.icono"></i>
            <span>Imagen del evento</span>
          </div>
          <img v-else :src="evento.url_imagen" :alt="evento.nombre" class="foto-evento" />

          <div class="contenido-tarjeta">
            <div class="nombre-evento">{{ evento.nombre }}</div>
            <div class="fecha-evento">{{ evento.fecha }}</div>
            <div class="descripcion-evento">{{ evento.descripcion }}</div>
            <div class="tipo" :class="claseTipo(evento.tipo)">
              {{ evento.tipo }}
            </div>
          </div>
        </div>

        <div v-if="puedeCrearFoto" class="boton-agregar" @click="abrirFormulario">
          +
        </div>
      </div>

      <!-- Mensaje cuando no hay resultados -->
      <div v-if="!cargando && eventosFiltrados.length === 0" class="sin-resultados mejorado sin-resultados--con-boton">
        <div class="empty-card">
          <div class="empty-icon">🗂️</div>
          <h4 class="empty-title">No se encontraron fotos</h4>
          <p class="empty-sub">Prueba limpiar los filtros o sube una nueva foto.</p>
          <div class="empty-actions">
            <button @click="limpiarFiltros" class="btn btn-primary">Limpiar filtros</button>
            <button v-if="puedeCrearFoto" @click="abrirFormulario" class="btn btn-secondary">Nueva foto</button>
          </div>
        </div>
      </div>

    </div>

    <!-- Modal de formulario -->
    <div v-if="mostrarFormulario" class="modal-overlay">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editando !== null ? (puedeEditarFoto ? 'Editar Evento' : 'Ver Evento') : 'Agregar Evento' }}</h3>
          <button class="btn-cerrar" title="Cerrar" @click="cerrarFormulario">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <form @submit.prevent="guardarEvento" class="formulario-evento">
          <div class="campo-formulario">
            <label for="titulo">
              <i class="fas fa-heading"></i>
              Título del evento *
            </label>
            <input id="titulo" v-model="form.titulo" type="text" placeholder="Ej: Megaweekend" class="input-evento" :readonly="!puedeEditarFoto" @input="manejarTitulo" />
          </div>
          <div class="campo-formulario">
            <label for="archivo_imagen">
              <i class="fas fa-camera"></i>
              Imagen *
            </label>

            <!-- Mostrar imagen actual cuando se está editando -->
            <div v-if="editando !== null && !cambiandoImagen && eventos[editando]" class="imagen-actual">
              <img :src="eventos[editando].url_imagen" :alt="eventos[editando].nombre" class="imagen-preview" />
              <p class="texto-imagen-actual">Imagen actual</p>
              <button type="button" @click="cambiarImagen" class="btn-cambiar-imagen" v-if="puedeEditarFoto">
                <i class="fas fa-edit"></i> Cambiar imagen
              </button>
            </div>

            <!-- Input de archivo -->
            <div v-if="(editando === null || cambiandoImagen) && puedeEditarFoto">
              <input
                id="archivo_imagen"
                ref="fileInput"
                type="file"
                accept="image/*"
                @change="manejarSeleccionArchivo"
                class="input-evento"
                :required="imagenRequerida"
              />
              <div v-if="archivoSeleccionado" class="archivo-info">
                <i class="fas fa-file-image"></i>
                {{ archivoSeleccionado.name }}
                <button type="button" @click="limpiarArchivo" class="btn-limpiar">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>
          <div class="campo-formulario">
            <label for="id_tipo_evento">
              <i class="fas fa-tag"></i>
              Tipo de evento *
            </label>
            <select v-model="form.id_tipo_evento" class="select-evento" :disabled="!puedeEditarFoto" required>
              <option value="">Selecciona tipo de evento</option>
              <option v-for="tipo in tipos" :key="tipo.id_tipo_evento" :value="tipo.id_tipo_evento">{{ tipo.nombre }}</option>
            </select>
          </div>
          <div class="campo-formulario">
            <label for="id_categoria">
              <i class="fas fa-list"></i>
              Categoría
            </label>
            <select v-model="form.id_categoria" class="select-evento" :disabled="!puedeEditarFoto">
              <option value="">Selecciona categoría</option>
              <option v-for="categoria in categorias" :key="categoria.id_categoria" :value="categoria.id_categoria">{{ categoria.nombre_categoria }}</option>
            </select>
          </div>
          <div class="campo-formulario">
            <label for="descripcion">
              <i class="fas fa-align-left"></i>
              Descripción *
            </label>
            <textarea id="descripcion" v-model="form.descripcion" placeholder="Descripción del evento"
              class="input-evento" :readonly="!puedeEditarFoto" @input="manejarDescripcion"></textarea>
          </div>

          <div class="acciones centrado">
            <button type="submit" class="btn-principal" v-if="puedeEditarFoto">{{ editando !== null ? 'Actualizar' : 'Crear' }}</button>
            <button type="button" class="btn-principal" v-if="!puedeEditarFoto" @click="cerrarFormulario">Cerrar</button>
            <button type="button" class="btn-secundario" v-if="editando !== null && puedeEliminarFoto" @click="eliminarEvento">Eliminar</button>
          </div>
        </form>

      </div>




    </div>

  </main>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import galeriaService from '@/services/galeriaService'
import Swal from 'sweetalert2'

const MAX_TITULO = 120
const MAX_DESCRIPCION = 500

export default {
  name: "EventosClub",
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      busqueda: "",
      filtroEvento: "",
      tipos: [],
      categorias: [],
      eventos: [],
      cargando: false,

      // Nuevo estado para formulario
      mostrarFormulario: false,
      editando: null, // índice del evento que se edita o null
      archivoSeleccionado: null,
      cambiandoImagen: false, // controla si se está cambiando la imagen
      form: {
        titulo: "",
        tipo: "",
        fecha: "",
        descripcion: "",
        id_tipo_evento: "",
        id_categoria: ""
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

        return coincideTipo && coincideNombre;
      });
    },

    imagenRequerida() {
      return this.editando === null || this.cambiandoImagen;
    },

    // Permisos de galería
    puedeVerGaleria() {
      return this.authStore.hasPermission('ver_galeria');
    },

    puedeCrearFoto() {
      return this.authStore.hasPermission('crear_foto');
    },

    puedeEditarFoto() {
      return this.authStore.hasPermission('editar_foto');
    },

    puedeEliminarFoto() {
      return this.authStore.hasPermission('eliminar_foto');
    },

    puedeSubirFoto() {
      return this.authStore.hasPermission('subir_foto');
    },

    puedeGestionarGaleria() {
      return this.authStore.hasPermission('gestionar_galeria');
    }
  },
  methods: {
    normalizarEspacios(valor = "") {
      return valor ? valor.replace(/\s+/g, " ").trim() : ""
    },
    normalizarTitulo(valor = "") {
      if (valor === null || valor === undefined) return ""
      const texto = valor.toString()
      const permitido = texto.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9.\-\s]/g, "")
      const colapsado = permitido.replace(/\s{2,}/g, " ")
      return colapsado.slice(0, MAX_TITULO)
    },
    normalizarDescripcion(valor = "") {
      if (valor === null || valor === undefined) return ""
      const texto = valor.toString()
      const permitido = texto.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9#\-.,;:¿?¡!()\s]/g, "")
      const colapsado = permitido.replace(/\s{2,}/g, " ")
      return colapsado.slice(0, MAX_DESCRIPCION)
    },
    manejarTitulo(event) {
      const valor = event?.target?.value ?? this.form.titulo
      this.form.titulo = this.normalizarTitulo(valor)
    },
    manejarDescripcion(event) {
      const valor = event?.target?.value ?? this.form.descripcion
      this.form.descripcion = this.normalizarDescripcion(valor)
    },
    normalizarFormulario() {
      this.form.titulo = this.normalizarTitulo(this.form.titulo)
      this.form.descripcion = this.normalizarDescripcion(this.form.descripcion)
    },
    async cargarDatos() {
      this.cargando = true
      try {
        await Promise.all([
          this.cargarEventos(),
          this.cargarCatalogos()
        ])
      } catch (error) {
        console.error('Error cargando datos:', error)
      } finally {
        this.cargando = false
      }
    },

    async cargarEventos() {
      try {
        const imagenes = await galeriaService.cargarImagenes()
        // Convertir imágenes de galería al formato de eventos
        this.eventos = imagenes.map(imagen => ({
          id: imagen.id_galeria,
          nombre: imagen.titulo,
          tipo: imagen.tipo_evento ? imagen.tipo_evento.nombre : 'Sin tipo',
          fecha: this.formatearFecha(imagen.fecha_subida),
          descripcion: imagen.descripcion || '',
          url_imagen: imagen.url_imagen,
          categoria: imagen.categoria ? imagen.categoria.nombre_categoria : 'Sin categoría',
          id_tipo_evento: imagen.id_tipo_evento,
          id_categoria: imagen.id_categoria
        }))
      } catch (error) {
        console.error('Error cargando eventos:', error)
        this.eventos = []
      }
    },

    async cargarCatalogos() {
      try {
        const catalogos = await galeriaService.cargarCatalogos()
        this.tipos = catalogos.tiposEvento
        this.categorias = catalogos.categorias
      } catch (error) {
        console.error('Error cargando catálogos:', error)
        this.tipos = []
        this.categorias = []
      }
    },

    formatearFecha(fecha) {
      if (!fecha) return ''
      return new Date(fecha).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },

    abrirFormulario() {
      this.editando = null;
      this.archivoSeleccionado = null;
      this.cambiandoImagen = false;
      this.form = {
        titulo: "",
        fecha: "",
        descripcion: "",
        tipo: "",
        id_tipo_evento: "",
        id_categoria: ""
      };
      this.normalizarFormulario();
      this.mostrarFormulario = true;
    },
    cerrarFormulario() {
      this.mostrarFormulario = false;
      this.limpiarFormulario();
    },

    verDetalleEvento(index) {
      // Si tiene permisos de edición, abre el formulario de edición
      if (this.puedeEditarFoto) {
        this.editarEvento(index);
      } else {
        // Si no tiene permisos, solo muestra la información (solo lectura)
        this.mostrarInformacion(index);
      }
    },

    mostrarInformacion(index) {
      const evento = this.eventos[index];
      this.editando = index;

      // Cargar datos en el formulario pero en modo solo lectura
      this.form = {
        titulo: evento.nombre,
        fecha: evento.fecha,
        descripcion: evento.descripcion,
        tipo: evento.tipo,
        id_tipo_evento: evento.id_tipo_evento || "",
        id_categoria: evento.id_categoria || ""
      };
      this.normalizarFormulario();

      this.archivoSeleccionado = null;
      this.cambiandoImagen = false;
      this.mostrarFormulario = true;
    },
    editarEvento(index) {
      this.editando = index;
      const evento = this.eventos[index];

      this.form = {
        titulo: evento.nombre,
        fecha: evento.fecha,
        descripcion: evento.descripcion,
        tipo: evento.tipo,
        id_tipo_evento: evento.id_tipo_evento || "",
        id_categoria: evento.id_categoria || ""
      };
      this.normalizarFormulario();
      this.archivoSeleccionado = null;
      this.cambiandoImagen = false;
      this.mostrarFormulario = true;
    },
    async manejarSeleccionArchivo(event) {
      const file = event.target.files[0];
      if (file) {
        // Validar tipo de archivo
        if (!file.type.startsWith('image/')) {
          await Swal.fire({
            icon: 'warning',
            title: 'Archivo inválido',
            text: 'Selecciona una imagen en formato válido.'
          });
          event.target.value = '';
          return;
        }

        // Validar tamaño (16MB máximo)
        if (file.size > 16 * 1024 * 1024) {
          await Swal.fire({
            icon: 'warning',
            title: 'Archivo demasiado grande',
            text: 'El tamaño máximo permitido es 16MB.'
          });
          event.target.value = '';
          return;
        }

        this.archivoSeleccionado = file;
      }
    },
    cambiarImagen() {
      this.cambiandoImagen = true;
      this.archivoSeleccionado = null;
    },
    limpiarArchivo() {
      this.archivoSeleccionado = null;
      // Limpiar el input si existe
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = '';
      }
    },
    async guardarEvento() {
      try {
        this.normalizarFormulario();
        // Validar campos requeridos
        const errores = []
        if (!this.form.titulo) {
          errores.push('El título es obligatorio')
        }
        if (!this.form.id_tipo_evento) {
          errores.push('Debes seleccionar un tipo de evento')
        }
        if (this.imagenRequerida && !this.archivoSeleccionado) {
          errores.push('Debes seleccionar una imagen')
        }
        if (errores.length > 0) {
          await Swal.fire({
            icon: 'error',
            title: 'Corrige los errores',
            html: errores.join('<br>')
          });
          return
        }

        if (this.editando !== null) {
          // Actualizar evento existente
          if (this.archivoSeleccionado) {
            // Si se seleccionó una nueva imagen, usar el endpoint de archivos
            const formData = new FormData();
            formData.append('file', this.archivoSeleccionado);
            formData.append('titulo', this.form.titulo);
            formData.append('descripcion', this.form.descripcion || '');
            if (this.form.id_tipo_evento) {
              formData.append('id_tipo_evento', this.form.id_tipo_evento);
            }
            if (this.form.id_categoria) {
              formData.append('id_categoria', this.form.id_categoria);
            }

            // Primero eliminar la imagen actual
            await galeriaService.eliminarImagen(this.eventos[this.editando].id);
            // Luego crear la nueva
            await galeriaService.crearImagenConArchivo(formData);
          } else {
            // Solo actualizar datos sin cambiar imagen
            const datosImagen = {
              titulo: this.form.titulo,
              descripcion: this.form.descripcion,
              id_tipo_evento: this.form.id_tipo_evento ? parseInt(this.form.id_tipo_evento) : null,
              id_categoria: this.form.id_categoria ? parseInt(this.form.id_categoria) : null
            }
            await galeriaService.actualizarImagen(this.eventos[this.editando].id, datosImagen);
          }
        } else {
          // Crear nuevo evento con archivo
          const formData = new FormData();
          formData.append('file', this.archivoSeleccionado);
          formData.append('titulo', this.form.titulo);
          formData.append('descripcion', this.form.descripcion || '');
          if (this.form.id_tipo_evento) {
            formData.append('id_tipo_evento', this.form.id_tipo_evento);
          }
          if (this.form.id_categoria) {
            formData.append('id_categoria', this.form.id_categoria);
          }

          await galeriaService.crearImagenConArchivo(formData);
        }

        await this.cargarEventos(); // Recargar la lista
        this.mostrarFormulario = false;
      } catch (error) {
        console.error('Error guardando evento:', error);
        await Swal.fire({
          icon: 'error',
          title: 'Error al guardar',
          text: error.message || 'No se pudo guardar el evento.'
        });
      }
    },

    async eliminarEvento() {
      if (this.editando === null) {
        return;
      }

      if (!this.puedeEliminarFoto) {
        return;
      }

      const evento = this.eventos[this.editando];
      if (!evento || !evento.id) {
        return;
      }

      try {
        await galeriaService.eliminarImagen(evento.id);
        await this.cargarEventos(); // Recargar la lista

        // Cerrar formulario y resetear estado
        this.mostrarFormulario = false;
        this.editando = null;
        this.limpiarFormulario();
      } catch (error) {
        console.error('Error eliminando evento:', error);
        await Swal.fire({
          icon: 'error',
          title: 'Error al eliminar',
          text: error.message || 'No se pudo eliminar el evento.'
        });
      }
    },

    cancelarFormulario() {
      this.mostrarFormulario = false;
    },
    limpiarFormulario() {
      this.form = {
        titulo: "",
        fecha: "",
        descripcion: "",
        tipo: "",
        id_tipo_evento: "",
        id_categoria: ""
      };
      this.normalizarFormulario();
      this.archivoSeleccionado = null;
      this.editando = null;
      this.cambiandoImagen = false;
    },
    limpiarFiltros() {
      this.busqueda = '';
      this.filtroEvento = '';
    },
    claseTipo(tipo) {
      if (!tipo) return '';

      return tipo
        // elimina todos los emojis conocidos
        .replace(/[\p{Emoji_Presentation}\p{Emoji}\uFE0F]/gu, '')
        .trim()
        .toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[áàäâ]/g, 'a')
        .replace(/[éèëê]/g, 'e')
        .replace(/[íìïî]/g, 'i')
        .replace(/[óòöô]/g, 'o')
        .replace(/[úùüû]/g, 'u')
        .replace(/ñ/g, 'n')
        .replace(/[^a-z0-9-]/g, '');
    }
  },
  async mounted() {
    // Cargar permisos del usuario primero
    await this.authStore.loadUserPermissions();

    // Luego cargar los datos de la galería
    await this.cargarDatos();
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

.archivo-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 8px 12px;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #495057;
}

.archivo-info i {
  color: #28a745;
}

.btn-limpiar {
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.7rem;
  margin-left: auto;
}

.btn-limpiar:hover {
  background: #c82333;
}

.acciones-tarjeta {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.tarjeta:hover .acciones-tarjeta {
  opacity: 1;
}

.tarjeta {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 350px; /* Altura mínima para uniformidad */
}

.contenido-tarjeta {
  padding: 0 16px 16px 16px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.foto-evento {
  width: 100%;
  height: 200px; /* Aumentado de 120px a 200px */
  object-fit: contain;
  border-radius: 8px 8px 0 0;
  margin-bottom: 12px;
  display: block;
  max-width: 100%;
  background: #f8f9fa; /* Fondo sutil para cuando la imagen no llena todo el espacio */
}

.imagen-placeholder {
  width: 100%;
  height: 200px; /* Aumentado para coincidir con la altura de las imágenes */
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px 8px 0 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  border: 2px dashed #dee2e6;
}

.imagen-placeholder i {
  font-size: 2rem;
  color: #6c757d;
  margin-bottom: 8px;
}

.imagen-placeholder span {
  font-size: 0.9rem;
  color: #6c757d;
  font-style: italic;
}

.nombre-evento {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  line-height: 1.3;
}

.fecha-evento {
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 8px;
  font-weight: 500;
}

.descripcion-evento {
  font-size: 0.85rem;
  color: #495057;
  line-height: 1.4;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 3;
}

.tipo {
  font-size: 0.75rem;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
  text-align: center;
  margin-top: auto;
  align-self: center;
  border: 1px solid transparent;
  transition: all 0.3s ease;
  cursor: default;
}

.tipo:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* Colores específicos para cada tipo de evento */
.tipo.entrenamiento {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border-color: #28a745;
  box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
}

.tipo.competencia {
  background: linear-gradient(135deg, #dc3545, #e83e8c);
  color: white;
  border-color: #dc3545;
  box-shadow: 0 2px 4px rgba(220, 53, 69, 0.3);
}

.tipo.exhibición {
  background: linear-gradient(135deg, #ffc107, #fd7e14);
  color: white;
  border-color: #ffc107;
  box-shadow: 0 2px 4px rgba(255, 193, 7, 0.3);
}

.tipo.torneo {
  background: linear-gradient(135deg, #17a2b8, #6f42c1);
  color: white;
  border-color: #17a2b8;
  box-shadow: 0 2px 4px rgba(23, 162, 184, 0.3);
}

.tipo.evaluación-médica {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
  border-color: #6c757d;
  box-shadow: 0 2px 4px rgba(108, 117, 125, 0.3);
}

/* Color por defecto para tipos no definidos */
.tipo:not(.entrenamiento):not(.competencia):not(.exhibición):not(.torneo):not(.evaluación-médica) {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
  border-color: #6c757d;
  box-shadow: 0 2px 4px rgba(108, 117, 125, 0.3);
}

.btn-editar, .btn-eliminar {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s ease;
}

.btn-editar {
  background: #007bff;
  color: white;
}

.btn-editar:hover {
  background: #0056b3;
}

.btn-eliminar {
  background: #dc3545;
  color: white;
}

.btn-eliminar:hover {
  background: #c82333;
}

.imagen-actual {
  margin-top: 8px;
  width: 100%;
}

.imagen-actual img {
  width: 100%;
  max-height: 400px;
  min-height: 200px;
  border-radius: 8px;
  border: 2px solid #dee2e6;
  object-fit: contain;
  display: block;
  background: #f8f9fa;
}

.imagen-preview {
  width: 100%;
  max-height: 400px;
  min-height: 200px;
  border-radius: 8px;
  border: 2px solid #dee2e6;
  object-fit: contain;
  display: block;
  background: #f8f9fa;
}

.texto-imagen-actual {
  margin-top: 8px;
  font-size: 0.9rem;
  color: #6c757d;
  font-style: italic;
  text-align: center;
}

.btn-cambiar-imagen {
  margin-top: 8px;
  padding: 6px 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s ease;
  display: block;
  margin-left: auto;
  margin-right: auto;
}

.btn-cambiar-imagen:hover {
  background: #0056b3;
}

.btn-cambiar-imagen i {
  margin-right: 4px;
}

/* Mejorar estilos del formulario */
.campo-formulario {
  margin-bottom: 20px;
}

.campo-formulario label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
}

.campo-formulario label i {
  color: #007bff;
  width: 16px;
}

.input-evento, .select-evento {
  width: 100%;
  padding: 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.input-evento:focus, .select-evento:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.input-evento::placeholder {
  color: #6c757d;
}

/* Estilos para el modal */
.modal-content {
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 8px 8px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
}

.btn-cerrar {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
}

.btn-cerrar:hover {
  background: rgba(255, 255, 255, 0.3);
}

.formulario-evento {
  padding: 20px;
}

.btn-principal {
  background: #28a745;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: background 0.2s ease;
}

.btn-principal:hover {
  background: #218838;
}

.btn-secundario {
  background: #dc3545;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: background 0.2s ease;
}

.btn-secundario:hover {
  background: #c82333;
}

.btn-limpiar-filtros {
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background 0.2s ease;
  margin-left: 10px;
}

.btn-limpiar-filtros:hover {
  background: #5a6268;
}

/* Estilos para campos de solo lectura */
.input-evento[readonly] {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.select-evento[disabled] {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

textarea[readonly] {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}
</style>
