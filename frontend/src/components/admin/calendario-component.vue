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
            <div
                v-for="(dia, index) in diasCalendario"
                :key="index"
                @click="seleccionarDia(dia)"
                :class="[
                    'dia-calendario',
                    {
                        'dia-otro-mes': !dia.esMesActual,
                        'dia-hoy': dia.esHoy,
                        'dia-con-eventos': dia.eventos && dia.eventos.length > 0
                    }
                ]"
            >
                <div class="numero-dia">{{ dia.numero }}</div>

                <!-- Indicador de eventos -->
                <div v-if="dia.eventos && dia.eventos.length > 0" class="indicador-eventos">
                    <span class="contador-eventos">{{ dia.eventos.length }}</span>
                    <div class="puntos-eventos">
                        <span v-for="(evento, idx) in dia.eventos.slice(0, 3)"
                            :key="idx"
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
                        <input
                            id="titulo"
                            v-model="nuevoEvento.titulo"
                            type="text"
                            placeholder="Ej: Entrenamiento de fuerza"
                            required
                            class="input-evento"
                            :disabled="!esAdmin"
                        />
                    </div>

                    <div class="campo-formulario">
                        <label for="tipo">
                            <i class="fas fa-tag"></i>
                            Tipo de evento *
                        </label>
                        <select id="tipo" v-model="nuevoEvento.tipo" required class="select-evento" :disabled="!esAdmin">
                            <option disabled.value="">Seleccionar tipo</option>
                            <option value="Entrenamiento">🏋️ Entrenamiento</option>
                            <option value="Evento">🎉 Evento</option>
                            <option value="Competencia">🏆 Competencia</option>
                        </select>
                    </div>

                    <div class="fila-dos-columnas">
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
                                class="input-evento"
                                :disabled="!esAdmin"
                            />
                        </div>
                        <div class="campo-formulario">
                            <label for="hora">
                                <i class="fas fa-clock"></i>
                                Hora *
                            </label>
                            <input
                                id="hora"
                                v-model="nuevoEvento.hora"
                                type="time"
                                required
                                class="input-evento"
                                :disabled="!esAdmin"
                            />
                        </div>
                    </div>

                    <div class="campo-formulario">
                        <label for="lugar">
                            <i class="fas fa-map-marker-alt"></i>
                            Lugar *
                        </label>
                        <input
                            id="lugar"
                            v-model="nuevoEvento.lugar"
                            type="text"
                            placeholder="Ej: Gimnasio principal"
                            required
                            class="input-evento"
                            :disabled="!esAdmin"
                        />
                    </div>

                    <div class="campo-formulario">
                        <label for="descripcion">
                            <i class="fas fa-align-left"></i>
                            Descripción
                        </label>
                        <textarea
                            id="descripcion"
                            v-model="nuevoEvento.descripcion"
                            placeholder="Detalles adicionales del evento..."
                            rows="3"
                            class="textarea-evento"
                            :disabled="!esAdmin"
                        ></textarea>
                    </div>

                    <div class="botones-modal">
                        <button type="button" @click="cerrarModal" class="btn-secundario">
                            <i class="fas fa-times"></i>
                            Cerrar
                        </button>
                        <button v-if="esAdmin && modoEdicion" type="button" @click="eliminarEvento" class="btn-eliminar">
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
                    <div
                        v-for="evento in eventosDelDia"
                        :key="evento.id"
                        @click="esAdmin ? editarEvento(evento) : verEvento(evento)"
                        class="evento-item"
                        :class="{ 'evento-item-usuario': !esAdmin }"
                    >
                        <div class="evento-info">
                            <div class="evento-titulo">{{ evento.titulo }}</div>
                            <div class="evento-detalles">
                                <span class="evento-tipo tipo-{{ evento.tipo.toLowerCase() }}">
                                    {{ evento.tipo }}
                                </span>
                                <span class="evento-hora">
                                    <i class="fas fa-clock"></i>
                                    {{ evento.hora }}
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
                        <i :class="esAdmin ? 'fas fa-edit' : 'fas fa-eye'" :title="esAdmin ? 'Editar evento' : 'Ver detalles'"></i>
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
                tipo: '',
                lugar: '',
                hora: '',
                descripcion: '',
                fecha: null
            }
        };
    },

    computed: {
        esAdmin() {
            return this.rol === 'Admin';
        }
    },

    mounted() {
        this.actualizarCalendario();
    },

    methods: {
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
            return calendarioService.obtenerEventosPorFecha(fecha);
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
            if (dia.esMesActual) {
                if (dia.eventos && dia.eventos.length > 0) {
                    // Cualquier usuario puede ver eventos
                    this.eventosDelDia = dia.eventos;
                    this.mostrarSelectorEventos();
                } else if (this.esAdmin) {
                    // Solo el admin puede crear eventos
                    this.nuevoEvento.fecha = dia.fecha;
                    this.abrirModal();
                }
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
            this.nuevoEvento = { ...evento };
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
                if (this.modoEdicion) {
                    calendarioService.actualizarEvento(this.eventoSeleccionado.id, this.nuevoEvento);
                } else {
                    calendarioService.crearEvento(this.nuevoEvento);
                }

                this.actualizarCalendario();
                this.cerrarModal();
                this.mostrarNotificacion('Evento guardado exitosamente', 'success');
            } catch (error) {
                this.mostrarNotificacion(error.message, 'error');
            }
        },

        eliminarEvento() {
            if (!this.esAdmin) return; // Solo admin puede eliminar

            if (confirm('¿Estás seguro de que quieres eliminar este evento?')) {
                try {
                    calendarioService.eliminarEvento(this.eventoSeleccionado.id);
                    this.actualizarCalendario();
                    this.cerrarModal();
                    this.mostrarNotificacion('Evento eliminado exitosamente', 'success');
                } catch (error) {
                    this.mostrarNotificacion(error.message, 'error');
                }
            }
        },

        limpiarFormulario() {
            this.nuevoEvento = {
                titulo: '',
                tipo: '',
                lugar: '',
                hora: '',
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