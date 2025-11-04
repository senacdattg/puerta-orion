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
            <div class="modal-content" @click.stop>
                <div class="modal-header">
                    <h3>{{ modoEdicion ? 'Editar Evento' : (puedeCrear ? 'Agregar Evento' : 'Ver Evento') }}</h3>
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
                            :disabled="!puedeCrear && !modoEdicion" />
                    </div>

                    <div class="campo-formulario">
                        <label for="tipo">
                            <i class="fas fa-tag"></i>
                            Tipo de evento *
                        </label>
                        <select id="tipo" v-model="nuevoEvento.idTipoEvento" required class="select-evento"
                            :disabled="!puedeCrear && !modoEdicion">
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
                            :disabled="!puedeCrear && !modoEdicion" />
                    </div>

                    <div class="fila-dos-columnas">
                        <div class="campo-formulario">
                            <label for="horaInicio">
                                <i class="fas fa-clock"></i>
                                Hora Inicio *
                            </label>
                            <input id="horaInicio" v-model="nuevoEvento.horaInicio" type="time" required class="input-evento"
                                :disabled="!puedeCrear && !modoEdicion" />
                        </div>
                        <div class="campo-formulario">
                            <label for="horaFin">
                                <i class="fas fa-clock"></i>
                                Hora Fin *
                            </label>
                            <input id="horaFin" v-model="nuevoEvento.horaFin" type="time" required class="input-evento"
                                :disabled="!puedeCrear && !modoEdicion" />
                        </div>
                    </div>

                    <div class="campo-formulario">
                        <label for="categoria">
                            <i class="fas fa-layer-group"></i>
                            Categoría *
                        </label>
                        <select id="categoria" v-model="nuevoEvento.idCategoria" required class="select-evento"
                            :disabled="!puedeCrear && !modoEdicion">
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
                            required class="input-evento" :disabled="!puedeCrear && !modoEdicion" />
                    </div>

                    <div class="campo-formulario">
                        <label for="descripcion">
                            <i class="fas fa-align-left"></i>
                            Descripción
                        </label>
                        <textarea id="descripcion" v-model="nuevoEvento.descripcion"
                            placeholder="Detalles adicionales del evento..." rows="3" class="textarea-evento"
                            :disabled="!puedeCrear && !modoEdicion"></textarea>
                    </div>

                    <div class="botones-modal">
                        <button 
                            type="button" 
                            @click="cerrarModal" 
                            class="btn-secundario"
                            style="flex: 0 0 150px !important; width: 150px !important; min-width: 150px !important; max-width: 150px !important; height: 48px !important; min-height: 48px !important; max-height: 48px !important; padding: 12px 24px !important; box-sizing: border-box !important; display: flex !important; align-items: center !important; justify-content: center !important;"
                        >
                            Cerrar
                        </button>
                        <button 
                            v-if="puedeEliminar && modoEdicion" 
                            type="button" 
                            @click="eliminarEvento" 
                            class="btn-eliminar"
                            style="flex: 0 0 150px !important; width: 150px !important; min-width: 150px !important; max-width: 150px !important; height: 48px !important; min-height: 48px !important; max-height: 48px !important; padding: 12px 24px !important; box-sizing: border-box !important; display: flex !important; align-items: center !important; justify-content: center !important;"
                        >
                            Eliminar
                        </button>
                        <button 
                            v-if="puedeCrear || (puedeEditar && modoEdicion)" 
                            type="submit" 
                            class="btn-principal"
                            style="flex: 0 0 150px !important; width: 150px !important; min-width: 150px !important; max-width: 150px !important; height: 48px !important; min-height: 48px !important; max-height: 48px !important; padding: 12px 24px !important; box-sizing: border-box !important; display: flex !important; align-items: center !important; justify-content: center !important;"
                        >
                            {{ modoEdicion ? 'ACTUALIZAR' : 'Guardar' }}
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Modal para seleccionar evento a editar -->
        <div v-if="selectorEventosVisible" class="modal-overlay" @click="cerrarSelectorEventos">
            <div class="modal-content selector-eventos" @click.stop>
                <div class="modal-header">
                    <h3>{{ puedeEditar ? 'Eventos del Día' : 'Eventos del Día' }}</h3>
                    <button @click="cerrarSelectorEventos" class="btn-cerrar">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

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

        <!-- Botón flotante para agregar evento (solo para roles con permisos de creación) -->
        <button v-if="puedeCrear" @click="abrirModal" class="btn-flotante" title="Agregar evento">
            <i class="fas fa-plus"></i>
        </button>
    </div>
</template>

<script>
import calendarioService from '@/services/calendarioService.js';
import { useAuthStore } from '@/stores/auth';

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
            cargando: false,
            error: null,
            tiposEvento: [],
            categorias: []
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
                // Si hay eventos, mostrar selector que permite ver/editar o agregar nuevo
                this.eventosDelDia = dia.eventos;
                this.mostrarSelectorEventos(dia.fecha);
            } else if (this.puedeCrear) {
                // Solo roles con permisos de creación pueden crear eventos en días vacíos
                this.nuevoEvento.fecha = dia.fecha;
                this.abrirModal();
            }
            // Si no tiene permisos de creación y no hay eventos, no hace nada
        },

        agregarEventoADia(dia, event) {
            // Prevenir que el click en el botón también active seleccionarDia
            if (event) {
                event.stopPropagation();
            }
            if (!dia.esMesActual || !this.puedeCrear) return;
            this.nuevoEvento.fecha = dia.fecha;
            this.abrirModal();
        },

        abrirModal() {
            if (!this.puedeCrear) return; // Solo roles con permisos de creación pueden abrir modal

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

        mostrarSelectorEventos(fecha = null) {
            this.selectorEventosVisible = true;
            // Guardar la fecha del día seleccionado para poder agregar un nuevo evento
            if (fecha) {
                this.nuevoEvento.fecha = fecha;
            }
        },

        cerrarSelectorEventos() {
            this.selectorEventosVisible = false;
            this.eventosDelDia = [];
        },

        abrirModalDesdeSelector() {
            // Cerrar el selector y abrir el modal de creación
            this.selectorEventosVisible = false;
            this.abrirModal();
            // La fecha ya está guardada en nuevoEvento.fecha desde mostrarSelectorEventos
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
            if (!this.puedeCrear && !this.puedeEditar) return; // Verificar permisos

            // Validar datos del evento
            const errores = calendarioService.validarEvento(this.nuevoEvento);
            if (errores.length > 0) {
                alert('Errores de validación:\n' + errores.join('\n'));
                return;
            }

            try {
                this.cargando = true;

                if (this.modoEdicion) {
                    if (!this.puedeEditar) {
                        alert('No tienes permisos para editar eventos');
                        return;
                    }
                    await calendarioService.actualizarEvento(this.eventoSeleccionado.id, this.nuevoEvento);
                    this.mostrarNotificacion('Evento actualizado exitosamente', 'success');
                } else {
                    if (!this.puedeCrear) {
                        alert('No tienes permisos para crear eventos');
                        return;
                    }
                    await calendarioService.crearEvento(this.nuevoEvento);
                    this.mostrarNotificacion('Evento creado exitosamente', 'success');

                    // Recargar eventos del calendario
                    await calendarioService.cargarEventos();
                    this.actualizarCalendario();

                    // Verificar si hay eventos en esa fecha antes de preguntar
                    const fechaActual = this.nuevoEvento.fecha;
                    const eventosDelDia = calendarioService.obtenerEventosPorFecha(fechaActual);

                    // Solo preguntar si ya hay eventos en ese día (más de 1 porque acabamos de crear uno)
                    if (eventosDelDia && eventosDelDia.length > 1) {
                        const quiereAgregarOtro = confirm('¿Deseas agregar otro evento en este mismo día?');

                        if (quiereAgregarOtro) {
                            // Limpiar formulario pero mantener la fecha y el modal abierto
                            this.limpiarFormulario();
                            this.nuevoEvento.fecha = fechaActual;
                            // El modal permanece abierto para agregar otro evento
                            return;
                        }
                    }

                    // Cerrar el modal si no quiere agregar otro o si no hay eventos previos
                    this.cerrarModal();
                    return;
                }

                // Esto solo se ejecuta si es edición
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
            if (!this.puedeEliminar) return; // Solo roles con permisos de eliminación pueden eliminar

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
