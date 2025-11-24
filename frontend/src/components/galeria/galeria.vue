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
      <div class="modal-content mensualidades-modal galeria-modal modal-sm" @click.stop>
         <div class="modal-header">
           <h2 class="modal-title">
             <i :class="editando !== null ? (puedeEditarFoto ? 'fas fa-edit' : 'fas fa-eye') : 'fas fa-plus-circle'"></i>
             {{ editando !== null ? (puedeEditarFoto ? 'Editar Evento' : 'Ver Evento') : 'Agregar Evento' }}
           </h2>
           <button class="btn-cerrar" title="Cerrar" @click="cerrarFormulario">
             <i class="fas fa-times"></i>
           </button>
         </div>

        <div class="modal-body">
        <form id="form-galeria" @submit.prevent="guardarEvento" class="formulario-evento">
          <!-- Sección: Información básica -->
          <div class="seccion-form">
            <h6>Información básica</h6>
            <p class="descripcion-seccion">Identifica el evento con un título, tipo y categoría.</p>
            <div class="grid-detalles">
              <div class="campo-formulario">
                <label for="titulo">
                  <i class="fas fa-heading"></i>
                  Título del evento *
                </label>
                <input id="titulo" v-model="form.titulo" type="text" placeholder="Ej: Megaweekend" class="input-edicion" :readonly="!puedeEditarFoto" @input="manejarTitulo" />
              </div>
              <div class="campo-formulario">
                <label for="id_tipo_evento">
                  <i class="fas fa-tag"></i>
                  Tipo de evento *
                </label>
                <select id="id_tipo_evento" v-model="form.id_tipo_evento" class="select-edicion" :disabled="!puedeEditarFoto" required>
                  <option value="">Selecciona tipo de evento</option>
                  <option v-for="tipo in tipos" :key="tipo.id_tipo_evento" :value="tipo.id_tipo_evento">{{ tipo.nombre }}</option>
                </select>
              </div>
              <div class="campo-formulario">
                <label for="id_categoria">
                  <i class="fas fa-list"></i>
                  Categoría
                </label>
                <select id="id_categoria" v-model="form.id_categoria" class="select-edicion" :disabled="!puedeEditarFoto">
                  <option value="">Selecciona categoría</option>
                  <option v-for="categoria in categorias" :key="categoria.id_categoria" :value="categoria.id_categoria">{{ categoria.nombre_categoria }}</option>
                </select>
              </div>
            </div>
          </div>
          <div class="linea-abajo" style="margin:12px 0;"></div>

          <!-- Sección: Imagen -->
          <div class="seccion-form">
            <h6>Imagen</h6>
            <p class="descripcion-seccion">Sube una imagen para el evento.</p>
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
                  class="input-edicion"
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
          </div>
          <div class="linea-abajo" style="margin:12px 0;"></div>

          <!-- Sección: Descripción -->
          <div class="seccion-form">
            <h6>Descripción</h6>
            <p class="descripcion-seccion">Añade detalles adicionales sobre el evento.</p>
            <div class="campo-formulario">
              <label for="descripcion">
                <i class="fas fa-align-left"></i>
                Descripción *
              </label>
              <textarea id="descripcion" v-model="form.descripcion" placeholder="Descripción del evento"
                class="input-edicion" :readonly="!puedeEditarFoto" @input="manejarDescripcion" rows="3"></textarea>
            </div>
          </div>
        </form>
        </div>

        <div class="modal-footer">
          <button type="button" @click="cerrarFormulario" class="btn btn-secondary">
            Cerrar
          </button>
          <button type="button" v-if="editando !== null && puedeEliminarFoto" @click="eliminarEvento" class="btn btn-danger">
            Eliminar
          </button>
          <button type="submit" form="form-galeria" v-if="puedeEditarFoto" class="btn btn-primary">
            {{ editando !== null ? 'Actualizar' : 'Crear' }}
          </button>
        </div>

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
    validarFormulario() {
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
      return errores
    },
    async mostrarErroresValidacion(errores) {
      await Swal.fire({
        icon: 'error',
        title: 'Corrige los errores',
        html: errores.join('<br>')
      })
    },
    construirFormData() {
      const formData = new FormData()
      formData.append('file', this.archivoSeleccionado)
      formData.append('titulo', this.form.titulo)
      formData.append('descripcion', this.form.descripcion || '')
      if (this.form.id_tipo_evento) {
        formData.append('id_tipo_evento', this.form.id_tipo_evento)
      }
      if (this.form.id_categoria) {
        formData.append('id_categoria', this.form.id_categoria)
      }
      return formData
    },
    async actualizarEventoConImagen() {
      const formData = this.construirFormData()
      await galeriaService.eliminarImagen(this.eventos[this.editando].id)
      await galeriaService.crearImagenConArchivo(formData)
    },
    async actualizarEventoSinImagen() {
      const datosImagen = {
        titulo: this.form.titulo,
        descripcion: this.form.descripcion,
        id_tipo_evento: this.form.id_tipo_evento ? parseInt(this.form.id_tipo_evento) : null,
        id_categoria: this.form.id_categoria ? parseInt(this.form.id_categoria) : null
      }
      await galeriaService.actualizarImagen(this.eventos[this.editando].id, datosImagen)
    },
    async crearNuevoEvento() {
      const formData = this.construirFormData()
      await galeriaService.crearImagenConArchivo(formData)
    },
    async manejarErrorGuardado(error) {
      console.error('Error guardando evento:', error)
      await Swal.fire({
        icon: 'error',
        title: 'Error al guardar',
        text: error.message || 'No se pudo guardar el evento.'
      })
    },
    async finalizarGuardado() {
      await this.cargarEventos()
      this.mostrarFormulario = false
    },
    async guardarEvento() {
      try {
        this.normalizarFormulario()
        const errores = this.validarFormulario()
        if (errores.length > 0) {
          await this.mostrarErroresValidacion(errores)
          return
        }

        if (this.editando !== null) {
          if (this.archivoSeleccionado) {
            await this.actualizarEventoConImagen()
          } else {
            await this.actualizarEventoSinImagen()
          }
        } else {
          await this.crearNuevoEvento()
        }

        await this.finalizarGuardado()
      } catch (error) {
        await this.manejarErrorGuardado(error)
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


