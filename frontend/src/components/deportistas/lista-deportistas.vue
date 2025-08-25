<template>
  <div class="lista-deportistas">
    <!-- Contenedor de búsqueda y filtros -->
    <div class="contenedor-filtros">
      <div class="buscador">
        <input
          type="search"
          v-model="busqueda"
          placeholder="Buscar deportistas..."
          class="entrada-busqueda"
        />
        <span class="icono-busqueda">🔍</span>
      </div>

      <div class="filtros">
        <select v-model="filtroCategoria" class="filtro-select">
          <option value="">Todas las categorías</option>
          <option value="infantil">Infantil</option>
          <option value="juvenil">Juvenil</option>
          <option value="adulto">Adulto</option>
        </select>

        <select v-model="filtroEstado" class="filtro-select">
          <option value="">Todos los estados</option>
          <option value="activo">Activo</option>
          <option value="inactivo">Inactivo</option>
          <option value="suspendido">Suspendido</option>
        </select>
      </div>
    </div>

    <!-- Estadísticas rápidas -->
    <div class="estadisticas">
      <div class="stat-card">
        <span class="stat-numero">{{ deportistasFiltrados.length }}</span>
        <span class="stat-label">Total</span>
      </div>
      <div class="stat-card">
        <span class="stat-numero">{{ deportistasActivos }}</span>
        <span class="stat-label">Activos</span>
      </div>
      <div class="stat-card">
        <span class="stat-numero">{{ deportistasInactivos }}</span>
        <span class="stat-label">Inactivos</span>
      </div>
    </div>

    <!-- Grid de tarjetas de deportistas -->
    <div class="grid-deportistas">
      <TarjetaDeportista
        v-for="deportista in deportistasFiltrados"
        :key="deportista.id"
        :deportista="deportista"
        @editar="editarDeportista"
        @eliminar="eliminarDeportista"
      />
    </div>

    <!-- Mensaje cuando no hay resultados -->
    <div v-if="deportistasFiltrados.length === 0" class="sin-resultados">
      <p>No se encontraron deportistas con los filtros aplicados</p>
      <button @click="limpiarFiltros" class="boton-limpiar">
        Limpiar filtros
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import TarjetaDeportista from './tarjeta-deportista.vue';

// Props siguiendo SRP - solo recibe la lista de deportistas
const props = defineProps({
  deportistas: {
    type: Array,
    required: true,
    default: () => []
  }
});

// Emits para comunicación con el componente padre
const emit = defineEmits(['editar', 'eliminar']);

// Estado local para filtros (KISS - simple y directo)
const busqueda = ref('');
const filtroCategoria = ref('');
const filtroEstado = ref('');

// Computed properties para filtrado (DRY - lógica centralizada)
const deportistasFiltrados = computed(() => {
  return props.deportistas.filter(deportista => {
    const cumpleBusqueda = !busqueda.value ||
      deportista.nombre.toLowerCase().includes(busqueda.value.toLowerCase()) ||
      deportista.categoria.toLowerCase().includes(busqueda.value.toLowerCase());

    const cumpleCategoria = !filtroCategoria.value ||
      deportista.categoria === filtroCategoria.value;

    const cumpleEstado = !filtroEstado.value ||
      deportista.estado === filtroEstado.value;

    return cumpleBusqueda && cumpleCategoria && cumpleEstado;
  });
});

// Estadísticas computadas
const deportistasActivos = computed(() =>
  props.deportistas.filter(d => d.estado === 'activo').length
);

const deportistasInactivos = computed(() =>
  props.deportistas.filter(d => d.estado === 'inactivo').length
);

// Funciones simples (KISS)
function editarDeportista(deportista) {
  emit('editar', deportista);
}

function eliminarDeportista(deportista) {
  emit('eliminar', deportista);
}

function limpiarFiltros() {
  busqueda.value = '';
  filtroCategoria.value = '';
  filtroEstado.value = '';
}
</script>
