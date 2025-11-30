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
        <!-- Modo vista (solo lectura) -->
        <template v-if="editando !== null && !puedeEditarFoto">
          <!-- Información principal del evento -->
          <div class="seccion-principal evento-header">
            <div class="evento-header-content">
              <h4 class="evento-titulo-grande">{{ form.titulo || 'Sin título' }}</h4>
              <span class="evento-badge-grande" :class="obtenerClaseTipoEvento(obtenerNombreTipoEvento(form.id_tipo_evento))">
                {{ obtenerNombreTipoEvento(form.id_tipo_evento) || 'Evento' }}
                </span>
            </div>
          </div>

          <!-- Información general -->
          <div class="seccion-detalles evento-detalles">
            <h5 class="evento-titulo-seccion">
              <i class="fas fa-info-circle"></i>
              Información General
            </h5>

            <div class="grid-detalles evento-grid">
              <!-- Primera fila: Tipo y Categoría lado a lado -->
              <div class="detalle-item evento-item">
                <div class="detalle-icono">
                  <i class="fas fa-tag"></i>
                </div>
                <div class="detalle-contenido">
                <span class="detalle-label evento-label-grande">Tipo de evento</span>
                  <span class="detalle-valor evento-valor-grande">{{ obtenerNombreTipoEvento(form.id_tipo_evento) || 'Sin tipo' }}</span>
              </div>
              </div>
              <div class="detalle-item evento-item">
                <div class="detalle-icono">
                  <i class="fas fa-layer-group"></i>
                </div>
                <div class="detalle-contenido">
                <span class="detalle-label evento-label-grande">Categoría</span>
                  <span class="detalle-valor evento-valor-grande">{{ obtenerNombreCategoria(form.id_categoria) || 'Sin categoría' }}</span>
              </div>
              </div>

              <!-- Segunda fila: Fecha debajo -->
              <div class="detalle-item evento-item evento-fecha-completa" style="grid-column: span 2;">
                <div class="detalle-icono">
                  <i class="fas fa-calendar-alt"></i>
                </div>
                <div class="detalle-contenido">
                <span class="detalle-label evento-label-grande">Fecha</span>
                  <span class="detalle-valor evento-valor-grande">{{ formatearFechaCompleta(form.fecha) || form.fecha || 'Sin fecha' }}</span>
              </div>
              </div>

              <!-- Tercera fila: Imagen (si existe) -->
              <div class="detalle-item evento-item evento-imagen-completa" v-if="eventos[editando]?.url_imagen" style="grid-column: span 2;">
                <div class="detalle-icono">
                  <i class="fas fa-image"></i>
                </div>
                <div class="detalle-contenido">
                  <span class="detalle-label evento-label-grande">Imagen</span>
                  <img :src="eventos[editando].url_imagen" :alt="form.titulo" @click="abrirImagenCompleta(eventos[editando].url_imagen)" style="cursor: pointer;" />
                </div>
              </div>

              <!-- Cuarta fila: Descripción (si existe) -->
              <div class="detalle-item evento-item evento-descripcion-completa" v-if="form.descripcion" style="grid-column: span 2;">
                <div class="detalle-icono">
                  <i class="fas fa-align-left"></i>
                </div>
                <div class="detalle-contenido">
                <span class="detalle-label evento-label-grande">Descripción</span>
                  <span class="detalle-valor evento-valor-grande evento-descripcion-texto">{{ form.descripcion || 'Sin descripción' }}</span>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- Modo edición/creación -->
        <form v-else id="form-galeria" @submit.prevent="guardarEvento" class="formulario-evento">
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
                <img :src="eventos[editando].url_imagen" :alt="eventos[editando].nombre" class="imagen-preview" @click="abrirImagenCompleta(eventos[editando].url_imagen)" style="cursor: pointer;" />
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
          <!-- Botones en modo vista (solo lectura) -->
          <template v-if="editando !== null && !puedeEditarFoto">
            <button type="button" @click="cerrarFormulario" class="btn btn-secondary">
              Cerrar
            </button>
          </template>

          <!-- Botones en modo edición/creación -->
          <template v-else>
            <button type="button" @click="cerrarFormulario" class="btn btn-secondary">
              Cerrar
            </button>
            <button type="button" v-if="editando !== null && puedeEliminarFoto" @click="eliminarEvento" class="btn btn-danger">
              Eliminar
            </button>
            <button type="submit" form="form-galeria" v-if="puedeEditarFoto" class="btn btn-primary">
              {{ editando !== null ? 'Actualizar' : 'Crear' }}
            </button>
          </template>
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
      },
      // Guardar estado inicial para comparar cambios
      formInicial: null,
      archivoInicial: null,
      scrollPositionGuardada: undefined // Guardar posición del scroll
    };
  },
  computed: {
    eventosFiltrados() {
      return this.eventos.filter(evento => {
        const coincideTipo =
          !this.filtroEvento || evento.tipo === this.filtroEvento;

        const coincideNombre =
          !this.busqueda ||
          (evento.nombre && typeof evento.nombre === 'string' && evento.nombre.toLowerCase().includes(this.busqueda.toLowerCase()));

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
  watch: {
    mostrarFormulario(newValue) {
      if (newValue) {
        // Guardar la posición actual del scroll
        const scrollPosition = globalThis.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;

        // Aplicar la posición guardada al body antes de fijarlo
        document.body.style.top = `-${scrollPosition}px`;
        document.body.classList.add('modal-open');
        document.documentElement.classList.add('modal-open');

        // Guardar la posición en el componente para restaurarla después
        this.scrollPositionGuardada = scrollPosition;
      } else {
        // Remover las clases y estilos
        document.body.classList.remove('modal-open');
        document.documentElement.classList.remove('modal-open');
        document.body.style.top = '';

        // Restaurar la posición del scroll
        if (this.scrollPositionGuardada !== undefined) {
          globalThis.scrollTo(0, this.scrollPositionGuardada);
          this.scrollPositionGuardada = undefined;
        }
      }
    }
  },
  beforeUnmount() {
    // Limpiar el estado del scroll si el componente se desmonta con el modal abierto
    document.body.classList.remove('modal-open');
    document.documentElement.classList.remove('modal-open');
    document.body.style.top = '';
  },
  methods: {
    // Helper function to safely clone objects
    clonarObjeto(obj) {
      try {
        return structuredClone(obj);
      } catch {
        // Fallback to JSON method if structuredClone fails
        // NOSONAR: S6781 - JSON.parse/stringify is needed as fallback when structuredClone fails
        return JSON.parse(JSON.stringify(obj));
      }
    },

    normalizarEspacios(valor = "") {
      return valor ? valor.replace(/\s+/g, " ").trim() : "" // NOSONAR: S7781 - replaceAll() no acepta regex
    },
    normalizarTitulo(valor = "") {
      if (valor === null || valor === undefined) return ""
      const texto = valor.toString()
      const permitido = texto.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9.\-\s]/g, "") // NOSONAR: S7781 - replaceAll() no acepta regex
      const colapsado = permitido.replace(/\s{2,}/g, " ") // NOSONAR: S7781 - replaceAll() no acepta regex
      return colapsado.slice(0, MAX_TITULO)
    },
    normalizarDescripcion(valor = "") {
      if (valor === null || valor === undefined) return ""
      const texto = valor.toString()
      const permitido = texto.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9#\-.,;:¿?¡!()\s]/g, "") // NOSONAR: S7781 - replaceAll() no acepta regex
      const colapsado = permitido.replace(/\s{2,}/g, " ") // NOSONAR: S7781 - replaceAll() no acepta regex
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
          fechaOriginal: imagen.fecha_subida, // Guardar fecha original para formatear correctamente
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

      // Guardar estado inicial cuando se abre el formulario
      // Using structuredClone for deep cloning (modern replacement for JSON.parse/stringify)
      this.formInicial = this.clonarObjeto(this.form);
      this.archivoInicial = null;
    },
    // Función para normalizar valores para comparación
    normalizarValorParaComparacion(valor) {
      if (valor === null || valor === undefined) {
        return ''
      }
      if (typeof valor === 'string') {
        return valor.trim()
      }
      if (typeof valor === 'number') {
        return valor
      }
      if (typeof valor === 'boolean') {
        return valor
      }
      return valor
    },

    // Verificar si hay cambios
    verificarCambios() {
      if (!this.formInicial) {
        return false
      }

      // Verificar cambios en el formulario
      const campos = [
        'titulo', 'descripcion', 'id_tipo_evento', 'id_categoria'
      ]

      for (const campo of campos) {
        const valorInicial = this.normalizarValorParaComparacion(this.formInicial[campo])
        const valorActual = this.normalizarValorParaComparacion(this.form[campo])
        if (valorInicial !== valorActual) {
          return true
        }
      }

      // Verificar si se cambió la imagen
      if (this.archivoSeleccionado !== this.archivoInicial) {
        return true
      }

      // Verificar si se activó el cambio de imagen
      if (this.cambiandoImagen && !this.archivoSeleccionado) {
        return true
      }

      return false
    },

    // Extraer mensaje de error de manera legible
    extraerMensajeError(error) {
      if (!error) {
        return 'No se pudo completar la operación. Por favor, intenta nuevamente.'
      }

      if (typeof error === 'string') {
        return error
      }

      if (error.message) {
        return error.message
      }

      if (error.error) {
        return typeof error.error === 'string' ? error.error : JSON.stringify(error.error)
      }

      if (error.details) {
        return typeof error.details === 'string' ? error.details : JSON.stringify(error.details)
      }

      if (typeof error === 'object') {
        try {
          const errorStr = JSON.stringify(error)
          if (errorStr.length > 200) {
            return 'Error al procesar la solicitud. Verifica que todos los datos sean correctos.'
          }
          return errorStr
        } catch {
          return 'Error desconocido. Por favor, intenta nuevamente.'
        }
      }

      return 'Error desconocido. Por favor, intenta nuevamente.'
    },

    async cerrarFormulario() {
      // Verificar si hay cambios sin guardar
      const tieneCambios = this.verificarCambios()

      if (tieneCambios) {
        const result = await Swal.fire({
          icon: 'question',
          title: '¿Descartar cambios?',
          text: '¿Estás seguro de que deseas cerrar? Los cambios sin guardar se perderán.',
          showCancelButton: true,
          confirmButtonText: 'Sí, cerrar',
          cancelButtonText: 'Continuar',
          confirmButtonColor: '#dc3545',
          cancelButtonColor: '#6c757d'
        })

        if (!result.isConfirmed) {
          return
        }
      }

      this.mostrarFormulario = false;
      this.limpiarFormulario();
      this.formInicial = null;
      this.archivoInicial = null;
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
      // Usar fecha original si está disponible para formatear correctamente
      this.form = {
        titulo: evento.nombre,
        fecha: evento.fechaOriginal || evento.fecha,
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

      // Usar fecha original si está disponible para formatear correctamente
      this.form = {
        titulo: evento.nombre,
        fecha: evento.fechaOriginal || evento.fecha,
        descripcion: evento.descripcion,
        tipo: evento.tipo,
        id_tipo_evento: evento.id_tipo_evento || "",
        id_categoria: evento.id_categoria || ""
      };
      this.normalizarFormulario();
      this.archivoSeleccionado = null;
      this.cambiandoImagen = false;
      this.mostrarFormulario = true;

      // Guardar estado inicial cuando se inicia la edición
      // Using structuredClone for deep cloning (modern replacement for JSON.parse/stringify)
      this.formInicial = this.clonarObjeto(this.form);
      this.archivoInicial = null;
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
      // Mostrar loading mientras se procesa
      Swal.fire({
        title: 'Guardando cambios...',
        text: 'Por favor espera mientras procesamos tu solicitud.',
        allowOutsideClick: false,
        allowEscapeKey: false,
        didOpen: () => {
          Swal.showLoading()
        }
      })

      try {
        const formData = this.construirFormData()
        await galeriaService.eliminarImagen(this.eventos[this.editando].id)
        await galeriaService.crearImagenConArchivo(formData)

        // Cerrar el loading
        Swal.close()
      } catch (error) {
        Swal.close()
        throw error
      }
    },
    async actualizarEventoSinImagen() {
      // Mostrar loading mientras se procesa
      Swal.fire({
        title: 'Guardando cambios...',
        text: 'Por favor espera mientras procesamos tu solicitud.',
        allowOutsideClick: false,
        allowEscapeKey: false,
        didOpen: () => {
          Swal.showLoading()
        }
      })

      try {
        const datosImagen = {
          titulo: this.form.titulo,
          descripcion: this.form.descripcion,
          id_tipo_evento: this.form.id_tipo_evento ? Number.parseInt(this.form.id_tipo_evento) : null,
          id_categoria: this.form.id_categoria ? Number.parseInt(this.form.id_categoria) : null
        }
        await galeriaService.actualizarImagen(this.eventos[this.editando].id, datosImagen)

        // Cerrar el loading
        Swal.close()
      } catch (error) {
        Swal.close()
        throw error
      }
    },
    async crearNuevoEvento() {
      // Mostrar loading mientras se procesa
      Swal.fire({
        title: 'Creando evento...',
        text: 'Por favor espera mientras procesamos tu solicitud.',
        allowOutsideClick: false,
        allowEscapeKey: false,
        didOpen: () => {
          Swal.showLoading()
        }
      })

      try {
        const formData = this.construirFormData()
        await galeriaService.crearImagenConArchivo(formData)

        // Cerrar el loading
        Swal.close()
      } catch (error) {
        Swal.close()
        throw error
      }
    },
    async manejarErrorGuardado(error) {
      console.error('Error guardando evento:', error)
      const mensajeError = this.extraerMensajeError(error)
      await Swal.fire({
        icon: 'error',
        title: 'Error al guardar',
        html: `<p><strong>No se pudo guardar el evento.</strong></p><p>${mensajeError}</p>`,
        confirmButtonText: 'Entendido',
        confirmButtonColor: '#dc3545'
      })
    },
    async finalizarGuardado() {
      await this.cargarEventos()

      // Mostrar notificación de éxito
      const esEdicion = this.editando !== null;
      const titulo = esEdicion ? '¡Evento actualizado exitosamente!' : '¡Evento creado exitosamente!';
      const mensaje = esEdicion
        ? 'La información del evento se ha guardado correctamente en el sistema.'
        : 'El evento se ha creado correctamente en el sistema.';
      await Swal.fire({
        icon: 'success',
        title: titulo,
        text: mensaje,
        confirmButtonText: 'Aceptar',
        confirmButtonColor: '#004AAD'
      })

      // Actualizar estado inicial después de guardar exitosamente
      // Using structuredClone for deep cloning (modern replacement for JSON.parse/stringify)
      this.formInicial = this.clonarObjeto(this.form);
      this.archivoInicial = this.archivoSeleccionado;

      this.mostrarFormulario = false
      this.limpiarFormulario()
      this.formInicial = null
      this.archivoInicial = null
    },
    async guardarEvento() {
      try {
        // Verificar si hay cambios antes de continuar (solo para edición)
        if (this.editando !== null) {
          const tieneCambios = this.verificarCambios()

          if (!tieneCambios) {
            await Swal.fire({
              icon: 'info',
              title: 'Sin cambios',
              text: 'No se han realizado modificaciones en el evento. No hay nada que guardar.',
              confirmButtonText: 'Entendido',
              confirmButtonColor: '#004AAD'
            })
            return
          }
        }

        this.normalizarFormulario()
        const errores = this.validarFormulario()
        if (errores.length > 0) {
          await Swal.fire({
            icon: 'error',
            title: 'Corrige los errores',
            html: `<p><strong>Por favor corrige los siguientes errores:</strong></p><p>${errores.join('<br>')}</p>`,
            confirmButtonText: 'Entendido',
            confirmButtonColor: '#dc3545'
          })
          return
        }

        // Confirmación antes de guardar
        const esEdicion = this.editando !== null;
        const tituloConfirmacion = esEdicion ? '¿Actualizar evento?' : '¿Crear evento?';
        const textoConfirmacion = esEdicion
          ? '¿Estás seguro de que deseas guardar los cambios en este evento?'
          : '¿Estás seguro de que deseas crear este evento?';
        const textoBoton = esEdicion ? 'Sí, actualizar' : 'Sí, crear';
        const confirmacion = await Swal.fire({
          icon: 'question',
          title: tituloConfirmacion,
          text: textoConfirmacion,
          showCancelButton: true,
          confirmButtonText: textoBoton,
          cancelButtonText: 'Cancelar',
          confirmButtonColor: '#004AAD',
          cancelButtonColor: '#6c757d'
        })

        if (!confirmacion.isConfirmed) {
          return
        }

        if (esEdicion) {
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

      // Confirmación antes de eliminar
      const confirmacion = await Swal.fire({
        icon: 'warning',
        title: '¿Eliminar evento?',
        text: `¿Estás seguro de que deseas eliminar "${evento.nombre}"? Esta acción no se puede deshacer.`,
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d'
      });

      if (!confirmacion.isConfirmed) {
        return;
      }

      // Mostrar loading mientras se procesa
      Swal.fire({
        title: 'Eliminando evento...',
        text: 'Por favor espera mientras procesamos tu solicitud.',
        allowOutsideClick: false,
        allowEscapeKey: false,
        didOpen: () => {
          Swal.showLoading()
        }
      })

      try {
        await galeriaService.eliminarImagen(evento.id);

        // Cerrar el loading
        Swal.close()

        await this.cargarEventos(); // Recargar la lista

        // Mostrar notificación de éxito
        await Swal.fire({
          icon: 'success',
          title: '¡Evento eliminado exitosamente!',
          text: 'El evento se ha eliminado correctamente del sistema.',
          confirmButtonText: 'Aceptar',
          confirmButtonColor: '#004AAD'
        });

        // Cerrar formulario y resetear estado
        this.mostrarFormulario = false;
        this.editando = null;
        this.limpiarFormulario();
        this.formInicial = null;
        this.archivoInicial = null;
      } catch (error) {
        // Cerrar el loading si aún está abierto
        Swal.close()

        console.error('Error eliminando evento:', error);
        const mensajeError = this.extraerMensajeError(error);

        await Swal.fire({
          icon: 'error',
          title: 'Error al eliminar',
          html: `<p><strong>No se pudo eliminar el evento.</strong></p><p>${mensajeError}</p>`,
          confirmButtonText: 'Entendido',
          confirmButtonColor: '#dc3545'
        });
      }
    },

    cancelarFormulario() {
      this.mostrarFormulario = false;
    },

    obtenerNombreTipoEvento(idTipoEvento) {
      if (!idTipoEvento) return null;
      const tipo = this.tipos.find(t => t.id_tipo_evento === idTipoEvento);
      return tipo ? tipo.nombre : null;
    },

    obtenerNombreCategoria(idCategoria) {
      if (!idCategoria) return null;
      const categoria = this.categorias.find(c => c.id_categoria === idCategoria);
      return categoria ? categoria.nombre_categoria : null;
    },

    formatearFechaCompleta(fechaStr) {
      if (!fechaStr) return null;

      try {
        // Si viene con timestamp completo, extraer solo la parte de fecha
        let fechaParaParsear = fechaStr;
        if (fechaStr.includes('T')) {
          // Extraer solo la parte de fecha (antes de la T)
          fechaParaParsear = fechaStr.split('T')[0];
        }

      // Intentar parsear la fecha
        const fecha = new Date(fechaParaParsear + 'T00:00:00');
      if (Number.isNaN(fecha.getTime())) {
          // Si falla, retornar solo la parte de fecha si tiene formato ISO
          if (fechaStr.includes('T')) {
            return fechaStr.split('T')[0];
          }
        return fechaStr;
      }

      const diasSemana = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
      const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
      const diaSemana = diasSemana[fecha.getDay()];
      const dia = fecha.getDate();
      const mes = meses[fecha.getMonth()];
      const año = fecha.getFullYear();
      return `${diaSemana}, ${dia} de ${mes} de ${año}`;
      } catch {
        // Si hay error, retornar solo la parte de fecha si tiene formato ISO
        if (fechaStr && fechaStr.includes('T')) {
          return fechaStr.split('T')[0];
        }
        return fechaStr;
      }
    },

    abrirImagenCompleta(urlImagen) {
      if (!urlImagen) return;

      Swal.fire({
        html: `<img src="${urlImagen}" alt="Imagen del evento" style="max-width: 100%; max-height: 85vh; width: auto; height: auto; object-fit: contain; border-radius: 8px;" />`,
        showCloseButton: true,
        showConfirmButton: false,
        padding: '1rem',
        background: 'rgba(0, 0, 0, 0.95)',
        width: '95%',
        customClass: {
          popup: 'swal-imagen-completa',
          htmlContainer: 'swal-imagen-completa-container'
        },
        didOpen: () => {
          // Permitir cerrar con ESC
          const handleEscape = (event) => {
            if (event.key === 'Escape') {
              Swal.close();
              document.removeEventListener('keydown', handleEscape);
            }
          };
          document.addEventListener('keydown', handleEscape);
        }
      });
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
      // Resetear estado inicial cuando se limpia el formulario
      this.formInicial = null;
      this.archivoInicial = null;
    },
    limpiarFiltros() {
      this.busqueda = '';
      this.filtroEvento = '';
    },
    obtenerClaseTipoEvento(tipoNombre) {
      if (!tipoNombre) return 'tipo-evento';
      // Normalizar el nombre del tipo para que coincida con las clases CSS
      const tipoNormalizado = tipoNombre.toLowerCase()
        .normalize('NFD')
        .replaceAll(/[\u0300-\u036f]/g, '') // Eliminar acentos
        .trim();

      // Mapear nombres comunes a las clases CSS
      if (tipoNormalizado.includes('entrenamiento')) {
        return 'tipo-entrenamiento';
      } else if (tipoNormalizado.includes('competencia')) {
        return 'tipo-competencia';
      } else if (tipoNormalizado.includes('exhibicion')) {
        return 'tipo-exhibicion';
      } else if (tipoNormalizado.includes('torneo')) {
        return 'tipo-torneo';
      } else if (tipoNormalizado.includes('evento')) {
        return 'tipo-evento';
      }

      // Por defecto, usar el nombre normalizado
      return `tipo-${tipoNormalizado}`;
    },

    claseTipo(tipo) {
      if (!tipo) return '';

      return tipo
        // elimina todos los emojis conocidos
        .replace(/[\p{Emoji_Presentation}\p{Emoji}\uFE0F]/gu, '') // NOSONAR: S7781 - replaceAll() no acepta regex Unicode
        .trim()
        .toLowerCase()
        .replace(/\s+/g, '-') // NOSONAR: S7781 - replaceAll() no acepta regex
        .replace(/[áàäâ]/g, 'a') // NOSONAR: S7781 - replaceAll() no acepta regex
        .replace(/[éèëê]/g, 'e') // NOSONAR: S7781 - replaceAll() no acepta regex
        .replace(/[íìïî]/g, 'i') // NOSONAR: S7781 - replaceAll() no acepta regex
        .replace(/[óòöô]/g, 'o') // NOSONAR: S7781 - replaceAll() no acepta regex
        .replace(/[úùüû]/g, 'u') // NOSONAR: S7781 - replaceAll() no acepta regex
        .replace(/ñ/g, 'n') // NOSONAR: S7781 - replaceAll() no acepta regex
        .replace(/[^a-z0-9-]/g, ''); // NOSONAR: S7781 - replaceAll() no acepta regex
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


