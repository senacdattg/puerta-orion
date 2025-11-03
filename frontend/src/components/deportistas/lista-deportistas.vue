<template>
  <div class="lista-deportistas">

    <div class="seccion-contenido grande">

      <div class="bloque-subtitulo">
        <span class="subtitulo-bloque">Categorías de busqueda</span>

        <!-- Contenedor de búsqueda y filtros -->
        <div class="contenedor-filtros">
          <div class="buscador">
            <input type="search" v-model="busqueda" placeholder="Buscar deportistas..." class="entrada-busqueda" />
            <span class="icono-busqueda">🔍</span>
          </div>

          <div class="filtros">
            <select v-model="filtroCategoria" class="filtro-select" :disabled="cargandoCategorias">
              <option value="">Todas las categorías</option>
              <option v-for="categoria in categorias" :key="categoria.id_categoria" :value="normalizarCategoria(categoria.nombre_categoria)">
                {{ categoria.nombre_categoria }}
              </option>
            </select>

            <select v-model="filtroEstado" class="filtro-select">
              <option value="">Todos los estados</option>
              <option value="activo">Activo</option>
              <option value="inactivo">Inactivo</option>
              <option value="suspendido">Suspendido</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Estadísticas rápidas -->
      <div class="estadisticas ordenadas">
        <div id="statCard" class="stat-card stat-total">
          <span class="stat-numero">{{ deportistasFiltrados.length }}</span>
          <span class="stat-label">TOTAL</span>
        </div>
        <div id="statCard" class="stat-card stat-activos">
          <span class="stat-numero">{{ deportistasActivos }}</span>
          <span class="stat-label">ACTIVOS</span>
        </div>
        <div id="statCard" class="stat-card stat-inactivos">
          <span class="stat-numero">{{ deportistasInactivos }}</span>
          <span class="stat-label">INACTIVOS</span>
        </div>
      </div>

      <div class="linea-abajo"></div>

      <!-- Grid de tarjetas de deportistas -->
      <div class="grid-deportistas">
        <TarjetaDeportista v-for="deportista in deportistasFiltrados" :key="deportista.id" :deportista="deportista"
          @editar="editarDeportista" @eliminar="eliminarDeportista" @ver="verDeportista" />

        <!-- Botón para agregar deportista - Oculto en modo solo visualización -->
        <!-- <div class="boton-agregar" @click="agregarDeportista">
          +
        </div> -->
      </div>

      <!-- Mensaje cuando no hay resultados -->
      <div v-if="deportistasFiltrados.length === 0" class="sin-resultados mejorado">
        <div class="empty-card">
          <div class="empty-icon">🗂️</div>
          <h4 class="empty-title">No se encontraron deportistas</h4>
          <p class="empty-sub">Prueba limpiar los filtros o crea un nuevo deportista.</p>
          <div class="empty-actions">
            <button @click="limpiarFiltros" class="btn btn-primary">Limpiar filtros</button>
            <button @click="agregarDeportista" class="btn btn-secondary">Nuevo deportista</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import TarjetaDeportista from './tarjeta-deportista.vue';
import catalogosService from '@/services/catalogosService';

// Props siguiendo SRP - solo recibe la lista de deportistas
const props = defineProps({
  deportistas: {
    type: Array,
    required: true,
    default: () => []
  }
});

// Emits para comunicación con el componente padre
const emit = defineEmits(['editar', 'eliminar', 'agregar', 'ver']);

// Estado local para filtros (KISS - simple y directo)
const busqueda = ref('');
const filtroCategoria = ref('');
const filtroEstado = ref('');

// Categorías cargadas desde la base de datos
const categorias = ref([]);
const cargandoCategorias = ref(false);

// Normalizar nombre de categoría para comparación (debe estar antes del computed)
function normalizarCategoria(nombreCategoria) {
  if (!nombreCategoria) return '';
  return String(nombreCategoria).toLowerCase().trim();
}

// Computed properties para filtrado (DRY - lógica centralizada)
const deportistasFiltrados = computed(() => {
  const filtroCategoriaNormalizado = normalizarCategoria(filtroCategoria.value);

  return props.deportistas.filter(deportista => {
    const nombreDeportista = (deportista.nombre || '').toLowerCase().trim();

    // Normalizar categoría del deportista - puede venir en diferentes formatos
    // El backend devuelve categoria en lowercase, pero categoria_info.nombre_categoria puede tener mayúsculas
    let categoriaDeportista = '';
    if (deportista.categoria_info?.nombre_categoria) {
      // Preferir categoria_info si existe (más confiable)
      categoriaDeportista = normalizarCategoria(deportista.categoria_info.nombre_categoria);
    } else if (deportista.categoria) {
      // Fallback a categoria directo (ya viene en lowercase del backend)
      categoriaDeportista = normalizarCategoria(deportista.categoria);
    }

    const busquedaLower = busqueda.value.toLowerCase().trim();

    const cumpleBusqueda = !busqueda.value ||
      nombreDeportista.includes(busquedaLower) ||
      categoriaDeportista.includes(busquedaLower);

    // Comparar categorías normalizadas - debe ser exacta
    const cumpleCategoria = !filtroCategoria.value ||
      categoriaDeportista === filtroCategoriaNormalizado;

    const cumpleEstado = !filtroEstado.value ||
      (deportista.estado || '').toLowerCase().trim() === filtroEstado.value.toLowerCase().trim();

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

// Función deshabilitada - solo modo visualización
// function agregarDeportista() {
//   emit('agregar');
// }

function verDeportista(deportista) {
  emit('ver', deportista);
}

// Cargar categorías desde la base de datos
async function cargarCategorias() {
  cargandoCategorias.value = true;
  try {
    const categoriasData = await catalogosService.getCategorias();
    console.log('📦 Categorías recibidas del backend:', categoriasData);

    // El backend ya devuelve solo categorías activas (estado=True)
    // Ordenarlas por nombre
    if (Array.isArray(categoriasData)) {
      categorias.value = categoriasData
        .filter(cat => {
          // Asegurar que la categoría tenga nombre_categoria
          return cat && cat.nombre_categoria;
        })
        .sort((a, b) => {
          const nombreA = a.nombre_categoria || '';
          const nombreB = b.nombre_categoria || '';
          return nombreA.localeCompare(nombreB);
        });
      console.log('✅ Categorías procesadas y cargadas:', categorias.value);
    } else {
      console.warn('⚠️ Las categorías no son un array:', categoriasData);
      categorias.value = [];
    }
  } catch (error) {
    console.error('❌ Error al cargar categorías:', error);
    console.error('❌ Detalles del error:', error.message);
    // Mantener categorías vacías en caso de error
    categorias.value = [];
  } finally {
    cargandoCategorias.value = false;
  }
}

// Cargar categorías al montar el componente
onMounted(() => {
  cargarCategorias();
});
</script>


