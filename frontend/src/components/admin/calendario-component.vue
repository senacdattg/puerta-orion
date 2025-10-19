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
            </div>
        </div>

        <!-- Modal para agregar/editar eventos -->
        <div v-if="modalVisible" class="modal-overlay" @click="cerrarModal">
            <div class="modal-content" @click.stop>
                <div class="modal-header">
                    <h3>{{ modoEdicion ? 'Editar Evento' : (esAdmin ? 'Agregar Evento' : 'Ver Evento') }}</h3>
                    <button @click="cerrarModal" class="btn-cerrar" title="Cerrar">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <form @submit.prevent="guardarEvento" class="formulario-evento">
                    <div class="campo-formulario">
                        <label for="titulo">
                            <i class="fas fa-heading"></i>
                            Título del evento *
                        </label>
                        <input id="titulo" v-model="nuevoEvento.titulo" type="text"
                            placeholder="Ej: Entrenamiento de fuerza" required class="input-evento"
                            :disabled="!esAdmin" />
                    </div>

                    <div class="campo-formulario">
                        <label for="tipo">
                            <i class="fas fa-tag"></i>
                            Tipo de evento *
                        </label>
                        <select id="tipo" v-model="nuevoEvento.idTipoEvento" required class="select-evento"
                            :disabled="!esAdmin">
                            <option value="">Seleccionar tipo</option>
                            <option v-for="tipo in tiposEvento" :key="tipo.id_tipo_evento" :value="tipo.id_tipo_evento">
                                {{ tipo.nombre }}
                            </option>
                        </select>
                    </div>

                    <div class="campo-formulario">
                        <label for="fecha">
                            <i class="fas fa-calendar"></i>
                            Fecha *
                        </label>
                        <input id="fecha" v-model="nuevoEvento.fecha" type="date" required class="input-evento"
                            :disabled="!esAdmin" />
                    </div>

                    <div class="fila-dos-columnas">
                        <div class="campo-formulario">
                            <label for="horaInicio">
                                <i class="fas fa-clock"></i>
                                Hora Inicio *
                            </label>
                            <input id="horaInicio" v-model="nuevoEvento.horaInicio" type="time" required class="input-evento"
                                :disabled="!esAdmin" />
                        </div>
                        <div class="campo-formulario">
                            <label for="horaFin">
                                <i class="fas fa-clock"></i>
                                Hora Fin *
                            </label>
                            <input id="horaFin" v-model="nuevoEvento.horaFin" type="time" required class="input-evento"
                                :disabled="!esAdmin" />
                        </div>
                    </div>

                    <div class="campo-formulario">
                        <label for="categoria">
                            <i class="fas fa-layer-group"></i>
                            Categoría *
                        </label>
                        <select id="categoria" v-model="nuevoEvento.idCategoria" required class="select-evento"
                            :disabled="!esAdmin">
                            <option value="">Seleccionar categoría</option>
                            <option v-for="categoria in categorias" :key="categoria.id_categoria" :value="categoria.id_categoria">
                                {{ categoria.nombre_categoria }}
                            </option>
                        </select>
                        
                    </div>

                    <div class="campo-formulario">
                        <label for="lugar">
                            <i class="fas fa-map-marker-alt"></i>
                            Lugar *
                        </label>
                        <input id="lugar" v-model="nuevoEvento.lugar" type="text" placeholder="Ej: Gimnasio principal"
                            required class="input-evento" :disabled="!esAdmin" />
                    </div>

                    <div class="campo-formulario">
                        <label for="descripcion">
                            <i class="fas fa-align-left"></i>
                            Descripción
                        </label>
                        <textarea id="descripcion" v-model="nuevoEvento.descripcion"
                            placeholder="Detalles adicionales del evento..." rows="3" class="textarea-evento"
                            :disabled="!esAdmin"></textarea>
                    </div>

                    <div class="botones-modal">
                        <button type="button" @click="cerrarModal" class="btn-secundario">
                            <i class="fas fa-times"></i>
                            Cerrar
                        </button>
                        <button v-if="esAdmin && modoEdicion" type="button" @click="eliminarEvento"
                            class="btn-eliminar">
                            <i class="fas fa-trash"></i>
                            Eliminar
                        </button>
                        <button v-if="esAdmin" type="submit" class="btn-principal">
                            <i :class="modoEdicion ? 'fas fa-save' : 'fas fa-plus'"></i>
                            {{ modoEdicion ? 'Actualizar' : 'Guardar' }}
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Modal para seleccionar evento a editar -->
        <div v-if="selectorEventosVisible" class="modal-overlay" @click="cerrarSelectorEventos">
            <div class="modal-content selector-eventos" @click.stop>
                <div class="modal-header">
                    <h3>{{ esAdmin ? 'Seleccionar Evento' : 'Eventos del Día' }}</h3>
                    <button @click="cerrarSelectorEventos" class="btn-cerrar">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <div class="lista-eventos">
                    <div v-for="evento in eventosDelDia" :key="evento.id"
                        @click="esAdmin ? editarEvento(evento) : verEvento(evento)" class="evento-item"
                        :class="{ 'evento-item-usuario': !esAdmin }">
                        <div class="evento-info">
                            <div class="evento-titulo">{{ evento.titulo }}</div>
                            <div class="evento-detalles">
                                <span class="evento-tipo tipo-{{ evento.tipo.toLowerCase() }}">
                                    {{ evento.tipo }}
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
                            <div v-if="!esAdmin" class="evento-descripcion">
                                <i class="fas fa-align-left"></i>
                                {{ evento.descripcion || 'Sin descripción' }}
                            </div>
                        </div>
                        <i :class="esAdmin ? 'fas fa-edit' : 'fas fa-eye'"
                            :title="esAdmin ? 'Editar evento' : 'Ver detalles'"></i>
                    </div>
                </div>
            </div>
        </div>

        <!-- Botón flotante para agregar evento (solo admin) -->
        <button v-if="esAdmin" @click="abrirModal" class="btn-flotante" title="Agregar evento">
            <i class="fas fa-plus"></i>
        </button>
    </div>
</template>

<script>
import calendarioService from '@/services/calendarioService.js';

export default {
    name: 'CalendarioComponent',
    props: {
        rol: {
            type: String,
            default: 'Usuario'
        }
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
            cargando: false,
            error: null,
            tiposEvento: [],
            sesiones: [],
            categorias: []
        };
    },

    computed: {
        esAdmin() {
            return this.rol === 'Admin';
        }
    },

    async mounted() {
        await this.inicializarComponente();
    },

    methods: {
        async inicializarComponente() {
            try {
                this.cargando = true;
                this.error = null;
                
                // Primero mostrar el calendario vacío
                this.actualizarCalendario();
                
                // Luego cargar datos del backend en segundo plano
                try {
                    const catalogos = await calendarioService.cargarCatalogos();
                    await calendarioService.cargarEventos();
                    
                    // Guardar catálogos en variables locales
                    this.tiposEvento = catalogos.tiposEvento || [];
                    this.sesiones = catalogos.sesiones || [];
                    this.categorias = catalogos.categorias || [];
                    
                    
                    // Actualizar el calendario con los eventos cargados
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
                // 👉 Si hay eventos y es admin, abrir directamente el primero en modo edición
                if (this.esAdmin) {
                    this.editarEvento(dia.eventos[0]);
                } else {
                    // 👉 Si no es admin, mostrar el evento en modo lectura
                    this.verEvento(dia.eventos[0]);
                }
            } else if (this.esAdmin) {
                // 👉 Solo el admin puede crear eventos en días vacíos
                this.nuevoEvento.fecha = dia.fecha;
                this.abrirModal();
            }
        },

        abrirModal() {
            if (!this.esAdmin) return; // Solo admin puede abrir modal para crear

            this.modalVisible = true;
            this.modoEdicion = false;
            this.limpiarFormulario();

            if (!this.nuevoEvento.fecha) {
                this.nuevoEvento.fecha = this.obtenerFechaActual();
            }
        },

        cerrarModal() {
            this.modalVisible = false;
            this.limpiarFormulario();
        },

        mostrarSelectorEventos() {
            this.selectorEventosVisible = true;
        },

        cerrarSelectorEventos() {
            this.selectorEventosVisible = false;
            this.eventosDelDia = [];
        },

        editarEvento(evento) {
            this.eventoSeleccionado = evento;
            this.nuevoEvento = { 
                ...evento,
                idTipoEvento: evento.idTipoEvento || evento.tipo,
                idCategoria: evento.idCategoria || evento.id_categoria
            };
            this.modoEdicion = true;
            this.selectorEventosVisible = false;
            this.modalVisible = true;
        },

        verEvento(evento) {
            this.eventoSeleccionado = evento;
            this.nuevoEvento = { ...evento };
            this.modoEdicion = false;
            this.selectorEventosVisible = false;
            this.modalVisible = true;

            // Para usuarios no-admin, mostrar solo información de lectura
            if (!this.esAdmin) {
                // El modal ya está configurado para mostrar solo lectura
                // Los campos están deshabilitados automáticamente
            }
        },

        async guardarEvento() {
            if (!this.esAdmin) return; // Solo admin puede guardar

            // Validar datos del evento
            const errores = calendarioService.validarEvento(this.nuevoEvento);
            if (errores.length > 0) {
                alert('Errores de validación:\n' + errores.join('\n'));
                return;
            }

            try {
                this.cargando = true;
                
                if (this.modoEdicion) {
                    await calendarioService.actualizarEvento(this.eventoSeleccionado.id, this.nuevoEvento);
                    this.mostrarNotificacion('Evento actualizado exitosamente', 'success');
                } else {
                    await calendarioService.crearEvento(this.nuevoEvento);
                    this.mostrarNotificacion('Evento creado exitosamente', 'success');
                }

                this.actualizarCalendario();
                this.cerrarModal();
            } catch (error) {
                console.error('Error al guardar evento:', error);
                this.mostrarNotificacion(error.message || 'Error al guardar el evento', 'error');
            } finally {
                this.cargando = false;
            }
        },

        async eliminarEvento() {
            if (!this.esAdmin) return; // Solo admin puede eliminar

            if (confirm('¿Estás seguro de que quieres eliminar este evento?')) {
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

        limpiarFormulario() {
            this.nuevoEvento = {
                titulo: '',
                idTipoEvento: '',
                idCategoria: '',
                lugar: '',
                horaInicio: '',
                horaFin: '',
                descripcion: '',
                fecha: this.nuevoEvento.fecha || this.obtenerFechaActual()
            };
            this.eventoSeleccionado = null;
            this.modoEdicion = false;
        },

        mostrarNotificacion(mensaje, tipo) {
            // Implementar sistema de notificaciones
            console.log(`${tipo}: ${mensaje}`);
        }
    }
};
</script>