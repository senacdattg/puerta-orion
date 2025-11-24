<template>
    <div class="calendario-container">
        <!-- Título principal del calendario -->
        <div class="titulo-principal">
            <h1>Calendario de Entrenamientos y Eventos</h1>
        </div>

        <!-- Header del calendario con navegación -->
        <div class="calendar-header">
            <div class="header-left">
                <h2 class="mes-titulo">{{ mesActual }} {{ añoActual }}</h2>
                <p class="fecha-actual">{{ obtenerFechaActualFormateada() }}</p>
            </div>

            <div class="header-controls">
                <button @click="mesAnterior" class="btn-nav" title="Mes anterior">
                    <i class="fas fa-chevron-left"></i>
                </button>
                <button @click="irHoy" class="btn-hoy" title="Ir a hoy">
                    Hoy
                </button>
                <button @click="mesSiguiente" class="btn-nav" title="Mes siguiente">
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
        </div>

        <!-- Días de la semana -->
        <div class="dias-semana">
            <div v-for="dia in diasSemana" :key="dia" class="dia-semana">
                {{ dia }}
            </div>
        </div>

        <!-- Grid del calendario -->
        <div class="calendario-grid">
            <div v-for="(dia, index) in diasCalendario" :key="index" @click="seleccionarDia(dia)" :class="[
                'dia-calendario',
                {
                    'dia-otro-mes': !dia.esMesActual,
                    'dia-hoy': dia.esHoy,
                    'dia-con-eventos': dia.eventos && dia.eventos.length > 0
                }
            ]">
                <div class="numero-dia">{{ dia.numero }}</div>

                <!-- Indicador de eventos -->
                <div v-if="dia.eventos && dia.eventos.length > 0" class="indicador-eventos">
                    <span class="contador-eventos">{{ dia.eventos.length }}</span>
                    <div class="puntos-eventos">
                        <span v-for="(evento, idx) in dia.eventos.slice(0, 3)" :key="idx"
                            :class="['punto-evento', `tipo-${evento.tipo.toLowerCase()}`]">
                        </span>
                    </div>
                </div>

                <!-- Botón para agregar evento (siempre visible si hay permisos) -->
                <button v-if="puedeCrear && dia.esMesActual"
                    @click="agregarEventoADia(dia, $event)"
                    class="btn-agregar-dia"
                    title="Agregar evento">
                    <i class="fas fa-plus"></i>
                </button>
            </div>
        </div>

        <!-- Modal para agregar/editar eventos -->
        <div v-if="modalVisible" class="modal-overlay" @click="cerrarModal">
            <div class="modal-content mensualidades-modal calendario-modal modal-sm" @click.stop>
                <div class="modal-header">
                    <h2 class="modal-title">
                        <i :class="modoEdicion ? 'fas fa-edit' : 'fas fa-plus-circle'"></i>
                        {{ modoEdicion ? 'Editar Evento' : (puedeCrear ? 'Agregar Evento' : 'Ver Evento') }}
                    </h2>
                    <button @click="cerrarModal" class="btn-cerrar" title="Cerrar">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <div class="modal-body">
                <form id="form-evento-calendario" @submit.prevent="guardarEvento" class="formulario-evento">
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
                                <input id="titulo" v-model="nuevoEvento.titulo" type="text"
                                    placeholder="Ej: Entrenamiento de fuerza" required class="input-edicion"
                                    :disabled="!puedeCrear && !modoEdicion" @input="manejarTitulo" />
                            </div>

                            <div class="campo-formulario">
                                <label for="tipo">
                                    <i class="fas fa-tag"></i>
                                    Tipo de evento *
                                </label>
                                <select id="tipo" v-model="nuevoEvento.idTipoEvento" required class="select-edicion"
                                    :disabled="!puedeCrear && !modoEdicion">
                                    <option disabled value="">Selecciona un tipo</option>
                                    <option v-for="tipo in tiposEvento" :key="tipo.id_tipo_evento" :value="tipo.id_tipo_evento">
                                        {{ tipo.nombre }}
                                    </option>
                                </select>
                            </div>

                            <div class="campo-formulario">
                                <label for="categoria">
                                    <i class="fas fa-layer-group"></i>
                                    Categoría *
                                </label>
                                <select id="categoria" v-model="nuevoEvento.idCategoria" required class="select-edicion"
                                    :disabled="!puedeCrear && !modoEdicion">
                                    <option disabled value="">Selecciona una categoría</option>
                                    <option v-for="categoria in categorias" :key="categoria.id_categoria" :value="categoria.id_categoria">
                                        {{ categoria.nombre_categoria }}
                                    </option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="linea-abajo" style="margin:12px 0;"></div>

                    <!-- Sección: Fecha y hora -->
                    <div class="seccion-form">
                        <h6>Fecha y hora</h6>
                        <p class="descripcion-seccion">Define cuándo y a qué hora se realizará el evento.</p>
                        <div class="grid-detalles">
                            <div class="campo-formulario">
                                <label for="fecha">
                                    <i class="fas fa-calendar"></i>
                                    Fecha *
                                </label>
                                <input
                                    id="fecha"
                                    v-model="nuevoEvento.fecha"
                                    type="date"
                                    required
                                    class="input-edicion"
                                    :disabled="fechaBloqueada || (!puedeCrear && !modoEdicion)"
                                    :readonly="fechaBloqueada || (!puedeCrear && !modoEdicion)"
                                />
                            </div>
                        </div>
                        <div class="grid-detalles" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;align-items:start;margin-top:16px;">
                            <div class="campo-formulario">
                                <label for="horaInicio">
                                    <i class="fas fa-clock"></i>
                                    Hora Inicio *
                                </label>
                                <input id="horaInicio" v-model="nuevoEvento.horaInicio" type="time" required class="input-edicion"
                                    :disabled="!puedeCrear && !modoEdicion" />
                            </div>
                            <div class="campo-formulario">
                                <label for="horaFin">
                                    <i class="fas fa-clock"></i>
                                    Hora Fin *
                                </label>
                                <input id="horaFin" v-model="nuevoEvento.horaFin" type="time" required class="input-edicion"
                                    :disabled="!puedeCrear && !modoEdicion" />
                            </div>
                        </div>
                    </div>
                    <div class="linea-abajo" style="margin:12px 0;"></div>

                    <!-- Sección: Ubicación y detalles -->
                    <div class="seccion-form">
                        <h6>Ubicación y detalles</h6>
                        <p class="descripcion-seccion">Especifica dónde se realizará y añade información adicional.</p>
                        <div class="grid-detalles">
                            <div class="campo-formulario">
                                <label for="lugar">
                                    <i class="fas fa-map-marker-alt"></i>
                                    Lugar *
                                </label>
                                <input id="lugar" v-model="nuevoEvento.lugar" type="text" placeholder="Ej: Gimnasio principal"
                                    required class="input-edicion" :disabled="!puedeCrear && !modoEdicion" @input="manejarLugar" />
                            </div>

                            <div class="campo-formulario">
                                <label for="descripcion">
                                    <i class="fas fa-align-left"></i>
                                    Descripción
                                </label>
                                <textarea id="descripcion" v-model="nuevoEvento.descripcion"
                                    placeholder="Detalles adicionales del evento..." rows="3" class="input-edicion"
                                    :disabled="!puedeCrear && !modoEdicion" @input="manejarDescripcion"></textarea>
                            </div>
                        </div>
                    </div>
                </form>
                </div>

                <div class="modal-footer">
                    <button
                        type="button"
                        @click="cerrarModal"
                        class="btn btn-secondary"
                    >
                        Cerrar
                    </button>
                    <button
                        v-if="puedeEliminar && modoEdicion"
                        type="button"
                        @click="eliminarEvento"
                        class="btn btn-danger"
                    >
                        Eliminar
                    </button>
                    <button
                        v-if="puedeCrear || (puedeEditar && modoEdicion)"
                        type="submit"
                        form="form-evento-calendario"
                        class="btn btn-primary"
                    >
                        {{ modoEdicion ? 'Actualizar' : 'Guardar' }}
                    </button>
                </div>
            </div>
        </div>

        <!-- Modal para seleccionar evento a editar -->
        <div v-if="selectorEventosVisible" class="modal-overlay" @click="cerrarSelectorEventos">
            <div class="modal-content mensualidades-modal selector-eventos calendario-modal modal-sm" @click.stop>
                <div class="modal-header">
                    <h2 class="modal-title">
                        <i class="fas fa-calendar-day"></i>
                        Eventos del Día
                    </h2>
                    <button @click="cerrarSelectorEventos" class="btn-cerrar">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <div class="modal-body">
                    <div class="panel-selector-eventos">
                        <div class="lista-eventos">
                            <div v-for="evento in eventosDelDia" :key="evento.id"
                                @click="puedeEditar ? editarEvento(evento) : verEvento(evento)" class="evento-item"
                                :class="{ 'evento-item-usuario': !puedeEditar }">
                                <div class="evento-info">
                                    <div class="evento-titulo">{{ evento.titulo }}</div>
                                    <div class="evento-detalles">
                                        <span class="evento-tipo tipo-{{ evento.tipo.toLowerCase() }}">
                                            {{ evento.tipo }}
                                        </span>
                                        <span v-if="evento.categoria?.nombre_categoria" class="evento-categoria">
                                            <i class="fas fa-tag"></i>
                                            {{ evento.categoria.nombre_categoria }}
                                        </span>
                                        <span class="evento-hora">
                                            <i class="fas fa-clock"></i>
                                            {{ evento.horaInicio || evento.hora }} - {{ evento.horaFin || '' }}
                                        </span>
                                        <span class="evento-lugar">
                                            <i class="fas fa-map-marker-alt"></i>
                                            {{ evento.lugar }}
                                        </span>
                                    </div>
                                    <div v-if="!puedeEditar" class="evento-descripcion">
                                        <i class="fas fa-align-left"></i>
                                        {{ evento.descripcion || 'Sin descripción' }}
                                    </div>
                                </div>
                                <i :class="puedeEditar ? 'fas fa-edit' : 'fas fa-eye'"
                                    :title="puedeEditar ? 'Editar evento' : 'Ver detalles'"></i>
                            </div>
                        </div>

                        <!-- Botón para agregar nuevo evento (solo si tiene permisos de creación) -->
                        <div v-if="puedeCrear" class="botones-selector">
                            <button @click="abrirModalDesdeSelector" class="btn-agregar-evento">
                                <i class="fas fa-plus"></i>
                                Agregar Otro Evento
                            </button>
                        </div>

                        <!-- Mensaje informativo -->
                        <div v-if="puedeCrear && eventosDelDia.length > 0" class="info-multiple-eventos">
                            <i class="fas fa-info-circle"></i>
                            <span>Puedes agregar varios eventos en este día. Solo verifica que los horarios no se solapen.</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Botón flotante para agregar evento (solo para roles con permisos de creación) -->
        <button v-if="puedeCrear" @click="abrirModal()" class="btn-flotante" title="Agregar evento">
            <i class="fas fa-plus"></i>
        </button>
    </div>
</template>

<script>
import { computed, watch, onUnmounted } from 'vue';
import calendarioService from '@/services/calendarioService.js';
import { useAuthStore } from '@/stores/auth';
import Swal from 'sweetalert2';

const LOCALE_COL = 'es-CO';
const MAX_TITULO = 120;
const MAX_LUGAR = 120;
const MAX_DESCRIPCION = 500;

export default {
    name: 'CalendarioComponent',
    props: {
        rol: {
            type: String,
            default: 'Usuario'
        }
    },
    setup() {
        const authStore = useAuthStore();
        return { authStore };
    },
    data() {
        return {
            fechaActual: new Date(),
            mesActual: '',
            añoActual: '',
            diasSemana: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
            diasCalendario: [],
            modalVisible: false,
            selectorEventosVisible: false,
            modoEdicion: false,
            eventoSeleccionado: null,
            eventosDelDia: [],
            nuevoEvento: {
                titulo: '',
                idTipoEvento: '',
                idCategoria: '',
                lugar: '',
                horaInicio: '',
                horaFin: '',
                descripcion: '',
                fecha: null
            },
            // Guardar estado inicial para comparar cambios
            nuevoEventoInicial: null,
            fechaBloqueada: false,
            cargando: false,
            error: null,
            tiposEvento: [],
            categorias: [],
            scrollPositionGuardada: undefined // Guardar posición del scroll
        };
    },

    computed: {
        esAdmin() {
            return this.rol === 'SuperAdmin' || this.rol === 'Administrador';
        },

        // Permisos específicos basados en los permisos de la BD
        puedeCrear() {
            return this.authStore.puedeCrearEventos || this.authStore.permissions.includes('crear_evento');
        },

        puedeEditar() {
            return this.authStore.puedeEditarEventos || this.authStore.permissions.includes('editar_evento');
        },

        puedeEliminar() {
            return this.authStore.puedeEliminarEventos || this.authStore.permissions.includes('eliminar_evento');
        },

        puedeVer() {
            return this.authStore.puedeVerEventos || this.authStore.permissions.includes('ver_evento') || this.authStore.permissions.includes('ver_calendario');
        }
    },

    watch: {
        modalVisible(newValue) {
            if (newValue) {
                // Guardar la posición actual del scroll
                const scrollPosition = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
                
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
                    window.scrollTo(0, this.scrollPositionGuardada);
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

    beforeUnmount() {
        // Limpiar el estado del scroll si el componente se desmonta con el modal abierto
        document.body.classList.remove('modal-open');
        document.documentElement.classList.remove('modal-open');
        document.body.style.top = '';
    },

    async mounted() {
        console.log('🔍 Calendario montado con rol:', this.rol);

        // Cargar permisos del usuario desde el backend
        try {
            await this.authStore.loadUserPermissions();
            console.log('✅ Permisos cargados desde el backend:', this.authStore.permissions);
        } catch (error) {
            console.error('❌ Error cargando permisos:', error);
        }

        console.log('🔍 Permisos del usuario:', {
            puedeCrear: this.puedeCrear,
            puedeEditar: this.puedeEditar,
            puedeEliminar: this.puedeEliminar,
            puedeVer: this.puedeVer
        });
        await this.inicializarComponente();
    },

    methods: {
        normalizarEspacios(valor = '') {
            return valor ? valor.replace(/\s+/g, ' ').trim() : '';
        },

        normalizarTitulo(valor = '') {
            if (!valor) return '';
            const mayus = valor.toLocaleUpperCase(LOCALE_COL);
            const limpio = mayus.replace(/[^A-Z0-9ÁÉÍÓÚÜÑ.\-\s]/g, '');
            return this.normalizarEspacios(limpio).slice(0, MAX_TITULO);
        },

        normalizarLugar(valor = '') {
            if (!valor) return '';
            const mayus = valor.toLocaleUpperCase(LOCALE_COL);
            const limpio = mayus.replace(/[^A-Z0-9ÁÉÍÓÚÜÑ#\-.\s]/g, '');
            return this.normalizarEspacios(limpio).slice(0, MAX_LUGAR);
        },

        normalizarDescripcion(valor = '') {
            if (!valor) return '';
            const mayus = valor.toLocaleUpperCase(LOCALE_COL);
            const limpio = mayus.replace(/[^A-Z0-9ÁÉÍÓÚÜÑ#\-.,;:¿?¡!()\s]/g, '');
            return this.normalizarEspacios(limpio).slice(0, MAX_DESCRIPCION);
        },

        manejarTitulo(event) {
            const valor = event?.target?.value ?? this.nuevoEvento.titulo;
            this.nuevoEvento.titulo = this.normalizarTitulo(valor);
        },

        manejarLugar(event) {
            const valor = event?.target?.value ?? this.nuevoEvento.lugar;
            this.nuevoEvento.lugar = this.normalizarLugar(valor);
        },

        manejarDescripcion(event) {
            const valor = event?.target?.value ?? this.nuevoEvento.descripcion;
            this.nuevoEvento.descripcion = this.normalizarDescripcion(valor);
        },

        normalizarCamposEvento() {
            this.nuevoEvento.titulo = this.normalizarTitulo(this.nuevoEvento.titulo);
            this.nuevoEvento.lugar = this.normalizarLugar(this.nuevoEvento.lugar);
            this.nuevoEvento.descripcion = this.normalizarDescripcion(this.nuevoEvento.descripcion);
        },

        async inicializarComponente() {
            try {
                this.cargando = true;
                this.error = null;

                // Primero mostrar el calendario vacío
                this.actualizarCalendario();

                // Luego cargar datos del backend en segundo plano
                try {
                    const catalogos = await calendarioService.cargarCatalogos();

                    // Intentar cargar eventos, pero no fallar si hay error 500
                    try {
                        await calendarioService.cargarEventos();
                    } catch (eventosError) {
                        console.warn('⚠️ Error cargando eventos del backend:', eventosError.message);
                        // Continuar sin eventos, el calendario seguirá funcionando
                    }

                    // Guardar catálogos en variables locales
                    this.tiposEvento = catalogos.tiposEvento || [];
                    this.categorias = catalogos.categorias || [];

                    // Actualizar el calendario con los eventos cargados (si los hay)
                    this.actualizarCalendario();
                } catch (apiError) {
                    console.warn('⚠️ Error cargando datos del backend:', apiError.message);
                    // El calendario ya está visible, solo no tendrá eventos
                }

            } catch (error) {
                console.error('❌ Error al inicializar calendario:', error);
                this.error = 'Error al cargar los datos del calendario';
                this.mostrarNotificacion('Error al cargar los datos del calendario', 'error');
            } finally {
                this.cargando = false;
            }
        },

        actualizarCalendario() {
            const año = this.fechaActual.getFullYear();
            const mes = this.fechaActual.getMonth();

            this.añoActual = año;
            this.mesActual = this.obtenerNombreMes(mes);

            const primerDia = new Date(año, mes, 1);
            const ultimoDia = new Date(año, mes + 1, 0);
            const primerDiaSemana = primerDia.getDay() || 7; // Lunes = 1, Domingo = 7


            this.diasCalendario = [];

            // Días del mes anterior
            for (let i = primerDiaSemana - 1; i > 0; i--) {
                const fecha = new Date(año, mes, 1 - i);
                this.diasCalendario.push({
                    fecha: this.formatearFecha(fecha),
                    numero: fecha.getDate(),
                    esMesActual: false,
                    esHoy: false,
                    eventos: []
                });
            }

            // Días del mes actual
            for (let dia = 1; dia <= ultimoDia.getDate(); dia++) {
                const fecha = new Date(año, mes, dia);
                const fechaFormateada = this.formatearFecha(fecha);
                const eventos = this.obtenerEventosPorFecha(fechaFormateada);

                this.diasCalendario.push({
                    fecha: fechaFormateada,
                    numero: dia,
                    esMesActual: true,
                    esHoy: this.esHoy(fecha),
                    eventos: eventos
                });
            }


            // Días del mes siguiente
            const diasRestantes = 42 - this.diasCalendario.length;
            for (let i = 1; i <= diasRestantes; i++) {
                const fecha = new Date(año, mes + 1, i);
                this.diasCalendario.push({
                    fecha: this.formatearFecha(fecha),
                    numero: fecha.getDate(),
                    esMesActual: false,
                    esHoy: false,
                    eventos: []
                });
            }
        },

        obtenerEventosPorFecha(fecha) {
            try {
                // Usar los eventos ya cargados en memoria
                return calendarioService.obtenerEventosPorFecha(fecha);
            } catch (error) {
                console.error('Error al obtener eventos por fecha:', error);
                return [];
            }
        },

        obtenerNombreMes(mes) {
            const meses = [
                'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
            ];
            return meses[mes];
        },

        formatearFecha(fecha) {
            return fecha.toISOString().split('T')[0];
        },

        obtenerFechaActualFormateada() {
            const hoy = new Date();
            const opciones = {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            };
            return hoy.toLocaleDateString('es-ES', opciones);
        },

        obtenerFechaActual() {
            return this.formatearFecha(new Date());
        },

        esHoy(fecha) {
            const hoy = new Date();
            return fecha.toDateString() === hoy.toDateString();
        },

        mesAnterior() {
            this.fechaActual.setMonth(this.fechaActual.getMonth() - 1);
            this.actualizarCalendario();
        },

        mesSiguiente() {
            this.fechaActual.setMonth(this.fechaActual.getMonth() + 1);
            this.actualizarCalendario();
        },

        irHoy() {
            this.fechaActual = new Date();
            this.actualizarCalendario();
        },

        seleccionarDia(dia) {
            if (!dia.esMesActual) return;

            if (dia.eventos && dia.eventos.length > 0) {
                // Si hay eventos, mostrar selector que permite ver/editar o agregar nuevo
                this.eventosDelDia = dia.eventos;
                this.mostrarSelectorEventos(dia.fecha);
            } else if (this.puedeCrear) {
                this.abrirModal({ fecha: dia.fecha, bloquear: true });
            }
            // Si no tiene permisos de creación y no hay eventos, no hace nada
        },

        agregarEventoADia(dia, event) {
            // Prevenir que el click en el botón también active seleccionarDia
            if (event) {
                event.stopPropagation();
            }
            if (!dia.esMesActual || !this.puedeCrear) return;
            this.abrirModal({ fecha: dia.fecha, bloquear: true });
        },

        abrirModal(opciones = {}) {
            const { fecha = null, bloquear = false } = opciones;
            if (!this.puedeCrear) return; // Solo roles con permisos de creación pueden abrir modal

            this.fechaBloqueada = bloquear;
            this.modalVisible = true;
            this.modoEdicion = false;
            this.limpiarFormulario(fecha);

            if (!this.fechaBloqueada && !this.nuevoEvento.fecha) {
                this.nuevoEvento.fecha = this.obtenerFechaActual();
            }
            
            // Guardar estado inicial cuando se abre el formulario
            this.nuevoEventoInicial = JSON.parse(JSON.stringify(this.nuevoEvento));
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
            if (!this.nuevoEventoInicial) {
                return false
            }

            const campos = [
                'titulo', 'idTipoEvento', 'idCategoria', 'lugar', 'horaInicio',
                'horaFin', 'descripcion', 'fecha'
            ]

            for (const campo of campos) {
                const valorInicial = this.normalizarValorParaComparacion(this.nuevoEventoInicial[campo])
                const valorActual = this.normalizarValorParaComparacion(this.nuevoEvento[campo])
                if (valorInicial !== valorActual) {
                    return true
                }
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

        async cerrarModal() {
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
            
            this.modalVisible = false;
            this.fechaBloqueada = false;
            this.limpiarFormulario();
            this.nuevoEventoInicial = null;
        },

        mostrarSelectorEventos(fecha = null) {
            this.selectorEventosVisible = true;
            // Guardar la fecha del día seleccionado para poder agregar un nuevo evento
            if (fecha) {
                this.nuevoEvento.fecha = fecha;
            }
            this.fechaBloqueada = true;
        },

        cerrarSelectorEventos() {
            this.selectorEventosVisible = false;
            this.eventosDelDia = [];
            this.fechaBloqueada = false;
        },

        abrirModalDesdeSelector() {
            // Cerrar el selector y abrir el modal de creación
            this.selectorEventosVisible = false;
            this.abrirModal({ fecha: this.nuevoEvento.fecha, bloquear: true });
            // La fecha ya está guardada en nuevoEvento.fecha desde mostrarSelectorEventos
        },

        editarEvento(evento) {
            if (!this.puedeEditar) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Acción no permitida',
                    text: 'No tienes permiso para editar eventos.'
                });
                return;
            }
            this.eventoSeleccionado = evento;
            this.nuevoEvento = {
                ...evento,
                idTipoEvento: evento.idTipoEvento || evento.tipo,
                idCategoria: evento.idCategoria || evento.id_categoria
            };
            this.normalizarCamposEvento();
            this.modoEdicion = true;
            this.selectorEventosVisible = false;
            this.fechaBloqueada = true;
            this.modalVisible = true;
            
            // Guardar estado inicial cuando se inicia la edición
            this.nuevoEventoInicial = JSON.parse(JSON.stringify(this.nuevoEvento));
        },

        verEvento(evento) {
            this.eventoSeleccionado = evento;
            this.nuevoEvento = { ...evento };
            this.normalizarCamposEvento();
            this.modoEdicion = false;
            this.selectorEventosVisible = false;
            this.fechaBloqueada = true;
            this.modalVisible = true;

            // Para usuarios no-admin, mostrar solo información de lectura
            if (!this.esAdmin) {
                // El modal ya está configurado para mostrar solo lectura
                // Los campos están deshabilitados automáticamente
            }
        },

        validarTitulo() {
            return !this.nuevoEvento.titulo ? 'El título debe tener al menos 3 caracteres' : null;
        },

        validarTipoEvento() {
            return !this.nuevoEvento.idTipoEvento ? 'Debe seleccionar un tipo de evento' : null;
        },

        validarFecha() {
            return !this.nuevoEvento.fecha ? 'Debe especificar una fecha' : null;
        },

        validarHoraInicio() {
            if (!this.nuevoEvento.horaInicio && !this.nuevoEvento.hora) {
                return 'Debe especificar una hora de inicio';
            }
            return null;
        },

        validarHoras() {
            if (!this.nuevoEvento.horaInicio || !this.nuevoEvento.horaFin) {
                return 'Debe especificar hora de inicio y fin';
            }
            return null;
        },

        validarCategoria() {
            return !this.nuevoEvento.idCategoria ? 'Debe seleccionar una categoría' : null;
        },

        validarLugar() {
            return !this.nuevoEvento.lugar ? 'El lugar debe tener al menos 3 caracteres' : null;
        },

        validarRangoHoras() {
            if (this.nuevoEvento.horaInicio && this.nuevoEvento.horaFin && this.nuevoEvento.horaFin <= this.nuevoEvento.horaInicio) {
                return 'La hora de fin debe ser posterior a la hora de inicio';
            }
            return null;
        },

        validarEvento() {
            const validaciones = [
                this.validarTitulo(),
                this.validarTipoEvento(),
                this.validarFecha(),
                this.validarHoraInicio(),
                this.validarHoras(),
                this.validarCategoria(),
                this.validarLugar(),
                this.validarRangoHoras()
            ];
            return validaciones.filter(error => error !== null);
        },

        async mostrarErroresValidacion(errores) {
            await Swal.fire({
                icon: 'error',
                title: 'Corrige los errores',
                html: errores.join('<br>')
            });
        },

        async validarPermisosEdicion() {
            if (!this.puedeEditar) {
                await Swal.fire({
                    icon: 'warning',
                    title: 'Sin permisos',
                    text: 'No tienes permisos para editar eventos.'
                });
                return false;
            }
            return true;
        },

        async validarPermisosCreacion() {
            if (!this.puedeCrear) {
                await Swal.fire({
                    icon: 'warning',
                    title: 'Sin permisos',
                    text: 'No tienes permisos para crear eventos.'
                });
                return false;
            }
            return true;
        },

        async actualizarEventoExistente() {
            if (!(await this.validarPermisosEdicion())) {
                return;
            }
            
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
                await calendarioService.actualizarEvento(this.eventoSeleccionado.id, this.nuevoEvento);

                // Cerrar el loading
                Swal.close()

                // El evento ya fue actualizado en la cache local en el servicio
                // Actualizar el calendario inmediatamente
                this.actualizarCalendario();

                await Swal.fire({
                    icon: 'success',
                    title: '¡Evento actualizado exitosamente!',
                    text: 'La información del evento se ha guardado correctamente en el sistema.',
                    confirmButtonText: 'Aceptar',
                    confirmButtonColor: '#004AAD'
                });

                // Intentar recargar eventos del servidor, pero no fallar si hay error
                try {
                    await calendarioService.cargarEventos();
                    this.actualizarCalendario();
                } catch (recargaError) {
                    console.warn('⚠️ Error al recargar eventos, pero el evento ya fue actualizado:', recargaError.message);
                    // El evento ya está actualizado en la cache local
                }

                // Actualizar estado inicial después de guardar exitosamente
                this.nuevoEventoInicial = JSON.parse(JSON.stringify(this.nuevoEvento));
                this.cerrarModal();
            } catch (error) {
                // Cerrar el loading si aún está abierto
                Swal.close()
                
                // Mostrar error específico al usuario
                const mensajeError = this.extraerMensajeError(error);

                await Swal.fire({
                    icon: 'error',
                    title: 'Error al actualizar evento',
                    html: `<p><strong>No se pudieron guardar los cambios.</strong></p><p>${mensajeError}</p>`,
                    confirmButtonText: 'Entendido',
                    confirmButtonColor: '#dc3545'
                });
                throw error; // Re-lanzar para que el catch superior lo maneje
            }
        },

        async preguntarAgregarOtroEvento(fechaActual) {
            const confirmacion = await Swal.fire({
                icon: 'question',
                title: '¿Agregar otro evento?',
                text: '¿Quieres crear otro evento para este mismo día?',
                showCancelButton: true,
                confirmButtonText: 'Sí, agregar',
                cancelButtonText: 'No',
                confirmButtonColor: '#004AAD',
                cancelButtonColor: '#6c757d'
            });

            if (confirmacion.isConfirmed) {
                this.limpiarFormulario();
                this.nuevoEvento.fecha = fechaActual;
                // Guardar estado inicial para el nuevo formulario
                this.nuevoEventoInicial = JSON.parse(JSON.stringify(this.nuevoEvento));
                return true;
            }
            return false;
        },

        async crearNuevoEvento() {
            if (!(await this.validarPermisosCreacion())) {
                return;
            }

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
                const nuevoEventoCreado = await calendarioService.crearEvento(this.nuevoEvento);

                // Cerrar el loading
                Swal.close()

                // El evento ya fue agregado a la cache local en el servicio
                // Actualizar el calendario inmediatamente con el evento nuevo
                this.actualizarCalendario();

                await Swal.fire({
                    icon: 'success',
                    title: '¡Evento creado exitosamente!',
                    text: 'El evento se ha creado correctamente en el sistema.',
                    confirmButtonText: 'Aceptar',
                    confirmButtonColor: '#004AAD'
                });

                // Intentar recargar eventos del servidor, pero no fallar si hay error
                try {
                    await calendarioService.cargarEventos();
                    this.actualizarCalendario();
                } catch (recargaError) {
                    console.warn('⚠️ Error al recargar eventos, pero el evento ya fue creado:', recargaError.message);
                    // El evento ya está en la cache local, así que el calendario ya se actualizó
                }

                const fechaActual = this.nuevoEvento.fecha;
                const quiereAgregarOtro = await this.preguntarAgregarOtroEvento(fechaActual);

                if (!quiereAgregarOtro) {
                    this.cerrarModal();
                }
            } catch (error) {
                // Cerrar el loading si aún está abierto
                Swal.close()
                
                // Mostrar error específico al usuario
                const mensajeError = this.extraerMensajeError(error);

                await Swal.fire({
                    icon: 'error',
                    title: 'Error al crear evento',
                    html: `<p><strong>No se pudo crear el evento.</strong></p><p>${mensajeError}</p>`,
                    confirmButtonText: 'Entendido',
                    confirmButtonColor: '#dc3545'
                });
                throw error; // Re-lanzar para que el catch superior lo maneje
            }
        },

        async guardarEvento() {
            if (!this.puedeCrear && !this.puedeEditar) return;

            // Verificar si hay cambios antes de continuar (solo para edición)
            if (this.modoEdicion) {
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

            this.normalizarCamposEvento();
            const errores = this.validarEvento();

            if (errores.length > 0) {
                await Swal.fire({
                    icon: 'error',
                    title: 'Corrige los errores',
                    html: `<p><strong>Por favor corrige los siguientes errores:</strong></p><p>${errores.join('<br>')}</p>`,
                    confirmButtonText: 'Entendido',
                    confirmButtonColor: '#dc3545'
                });
                return;
            }

            // Confirmación antes de guardar
            const confirmacion = await Swal.fire({
                icon: 'question',
                title: this.modoEdicion ? '¿Actualizar evento?' : '¿Crear evento?',
                text: this.modoEdicion 
                    ? '¿Estás seguro de que deseas guardar los cambios en este evento?'
                    : '¿Estás seguro de que deseas crear este evento?',
                showCancelButton: true,
                confirmButtonText: this.modoEdicion ? 'Sí, actualizar' : 'Sí, crear',
                cancelButtonText: 'Cancelar',
                confirmButtonColor: '#004AAD',
                cancelButtonColor: '#6c757d'
            });

            if (!confirmacion.isConfirmed) {
                return;
            }

            try {
                this.cargando = true;

                if (this.modoEdicion) {
                    await this.actualizarEventoExistente();
                } else {
                    await this.crearNuevoEvento();
                }
            } catch (error) {
                console.error('Error al guardar evento:', error);
                // El error ya fue mostrado en crearNuevoEvento o actualizarEventoExistente
                // Solo mostrar aquí si no se mostró antes
                if (!error.mostrado) {
                    const mensajeError = this.extraerMensajeError(error);
                    await Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        html: `<p><strong>Error al guardar el evento.</strong></p><p>${mensajeError}</p>`,
                        confirmButtonText: 'Entendido',
                        confirmButtonColor: '#dc3545'
                    });
                }
            } finally {
                this.cargando = false;
            }
        },

        async eliminarEvento() {
            if (!this.puedeEliminar) return; // Solo roles con permisos de eliminación pueden eliminar

            const confirmacion = await Swal.fire({
                icon: 'question',
                title: '¿Eliminar evento?',
                text: 'Esta acción no se puede deshacer.',
                showCancelButton: true,
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            });

            if (confirmacion.isConfirmed) {
                try {
                    this.cargando = true;
                    await calendarioService.eliminarEvento(this.eventoSeleccionado.id);
                    this.actualizarCalendario();
                    this.cerrarModal();
                    this.mostrarNotificacion('Evento eliminado exitosamente', 'success');
                } catch (error) {
                    console.error('Error al eliminar evento:', error);
                    this.mostrarNotificacion(error.message || 'Error al eliminar el evento', 'error');
                } finally {
                    this.cargando = false;
                }
            }
        },

        limpiarFormulario(fechaPrefijada = null) {
            const fechaBase = fechaPrefijada ?? (this.fechaBloqueada ? this.nuevoEvento.fecha : null);
            this.nuevoEvento = {
                titulo: '',
                idTipoEvento: '',
                idCategoria: '',
                lugar: '',
                horaInicio: '',
                horaFin: '',
                descripcion: '',
                fecha: fechaBase || null
            };
            if (this.fechaBloqueada && !this.nuevoEvento.fecha) {
                this.nuevoEvento.fecha = this.obtenerFechaActual();
            }
            if (!this.fechaBloqueada && !this.nuevoEvento.fecha) {
                this.nuevoEvento.fecha = this.obtenerFechaActual();
            }
            this.normalizarCamposEvento();
            this.eventoSeleccionado = null;
            this.modoEdicion = false;
            // Resetear estado inicial cuando se limpia el formulario
            this.nuevoEventoInicial = null;
        },

        mostrarNotificacion(mensaje, tipo) {
            // Implementar sistema de notificaciones
            console.log(`${tipo}: ${mensaje}`);
        }
    }
};
</script>
