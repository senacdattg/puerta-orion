<template>
  <div class="perfil-deportista-vista">
    <div class="perfil-header">
      <h2>📋 Información del Deportista</h2>
      <button class="btn-cerrar" @click="$emit('cerrar')" title="Cerrar">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <div class="perfil-content" v-if="datos && catalogosCargados">
      <!-- Debug temporal - eliminar en producción -->
      <div style="display: none;">
        <pre>{{ JSON.stringify(datos, null, 2) }}</pre>
      </div>

      <!-- Información Personal -->
      <div class="perfil-card" v-if="datos.persona || datos.nombre1">
        <div class="card-header">
          <h3>👤 Información Personal</h3>
        </div>
        <div class="card-content">
          <div class="info-grid">
            <div class="info-row">
              <label>Nombre completo:</label>
              <span>{{ obtenerNombreCompleto() || 'No disponible' }}</span>
            </div>
            <div class="info-row" v-if="datos.persona?.primer_nombre">
              <label>Primer nombre:</label>
              <span>{{ datos.persona.primer_nombre || '—' }}</span>
            </div>
            <div class="info-row" v-if="datos.persona?.segundo_nombre">
              <label>Segundo nombre:</label>
              <span>{{ datos.persona.segundo_nombre || '—' }}</span>
            </div>
            <div class="info-row" v-if="datos.persona?.primer_apellido">
              <label>Primer apellido:</label>
              <span>{{ datos.persona.primer_apellido || '—' }}</span>
            </div>
            <div class="info-row" v-if="datos.persona?.segundo_apellido">
              <label>Segundo apellido:</label>
              <span>{{ datos.persona.segundo_apellido || '—' }}</span>
            </div>
            <div class="info-row">
              <label>Tipo de documento:</label>
              <span>{{ obtenerTipoDocumento() || '—' }}</span>
            </div>
            <div class="info-row">
              <label>Documento:</label>
              <span>{{ datos.persona?.documento || datos.documento || '—' }}</span>
            </div>
            <div class="info-row">
              <label>Correo electrónico:</label>
              <span>{{ datos.persona?.correo_electronico || datos.correo || '—' }}</span>
            </div>
            <div class="info-row">
              <label>Teléfono:</label>
              <span>{{ datos.persona?.telefono || datos.telefono || '—' }}</span>
            </div>
            <div class="info-row">
              <label>Dirección:</label>
              <span>{{ datos.persona?.direccion || datos.direccion || '—' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Información Deportiva -->
      <div class="perfil-card" v-if="datos.deportista || datos.categoria || datos.informacion_deportiva || datos.datos_deportista">
        <div class="card-header">
          <h3>🏃 Información Deportiva</h3>
        </div>
        <div class="card-content">
          <div class="info-grid">
            <div class="info-row">
              <label>Categoría:</label>
              <span>{{ obtenerCategoria() || '—' }}</span>
            </div>
            <div class="info-row">
              <label>Fecha de nacimiento:</label>
              <span>{{ formatearFechaNacimiento(fechaNacimiento) || '—' }}</span>
            </div>
            <div class="info-row">
              <label>Peso:</label>
              <span>{{ datosDeportista.peso !== undefined && datosDeportista.peso !== null ? datosDeportista.peso + ' kg' : '—' }}</span>
            </div>
            <div class="info-row">
              <label>Altura:</label>
              <span>{{ datosDeportista.altura !== undefined && datosDeportista.altura !== null ? datosDeportista.altura + ' m' : '—' }}</span>
            </div>
            <div class="info-row">
              <label>Tipo sanguíneo:</label>
              <span>{{ obtenerTipoSanguineo() || '—' }}</span>
            </div>
            <div class="info-row">
              <label>Ciudad de residencia:</label>
              <span>{{ obtenerCiudad() || '—' }}</span>
            </div>
            <div class="info-row">
              <label>EPS:</label>
              <span>{{ obtenerEPS() || '—' }}</span>
            </div>
          </div>

          <!-- Información Deportiva Detallada -->
          <div class="info-subsection" v-if="datos.informacion_deportiva">
            <h4>⚽ Detalles Deportivos</h4>
            <div class="info-grid">
              <div class="info-row">
                <label>Deporte principal:</label>
                <span>{{ obtenerDeporte() || '—' }}</span>
              </div>
              <div class="info-row">
                <label>Practica otro deporte:</label>
                <span>
                  <span class="badge" :class="datos.informacion_deportiva?.practica_otro_deporte ? 'badge-success' : 'badge-muted'">
                    {{ datos.informacion_deportiva?.practica_otro_deporte !== undefined ? (datos.informacion_deportiva.practica_otro_deporte ? 'Sí' : 'No') : '—' }}
                  </span>
                </span>
              </div>
              <div class="info-row">
                <label>Participa en escuela:</label>
                <span>
                  <span class="badge" :class="datos.informacion_deportiva?.participa_escuela ? 'badge-success' : 'badge-muted'">
                    {{ datos.informacion_deportiva?.participa_escuela !== undefined ? (datos.informacion_deportiva.participa_escuela ? 'Sí' : 'No') : '—' }}
                  </span>
                </span>
              </div>
              <div class="info-row">
                <label>Escuela:</label>
                <span>{{ obtenerEscuela() || '—' }}</span>
              </div>
              <div class="info-row">
                <label>Institución de registro:</label>
                <span>{{ obtenerInstitucion() || '—' }}</span>
              </div>
              <div class="info-row">
                <label>Recomendación médica:</label>
                <span>
                  <span class="badge" :class="datos.informacion_deportiva?.recomendacion_medica ? 'badge-warning' : 'badge-success'">
                    {{ datos.informacion_deportiva?.recomendacion_medica !== undefined ? (datos.informacion_deportiva.recomendacion_medica ? 'Sí' : 'No') : '—' }}
                  </span>
                </span>
              </div>
              <div class="info-row" v-if="datos.informacion_deportiva?.descripcion_recomendacion">
                <label>Descripción recomendación:</label>
                <span>{{ datos.informacion_deportiva.descripcion_recomendacion || '—' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Información de Salud - Diagnósticos y Enfermedades -->
      <div class="perfil-card" v-if="datos.salud && (datos.salud.diagnosticos || datos.salud.tipos_enfermedad_ids)">
        <div class="card-header">
          <h3>🏥 Información de Salud</h3>
        </div>
        <div class="card-content">
          <div class="info-grid">
            <!-- Tipos de Enfermedad -->
            <div class="info-row" v-if="datos.salud.tipos_enfermedad_ids && datos.salud.tipos_enfermedad_ids.length > 0">
              <label>Tipos de enfermedad:</label>
              <span>
                <span
                  v-for="idTipo in datos.salud.tipos_enfermedad_ids"
                  :key="idTipo"
                  class="badge badge-info"
                  style="margin-right: 0.5rem;"
                >
                  {{ obtenerTipoEnfermedad(idTipo) || `ID: ${idTipo}` }}
                </span>
                <span v-if="!datos.salud.tipos_enfermedad_ids.length">—</span>
              </span>
            </div>

            <!-- Diagnósticos -->
            <div class="info-row" v-if="datos.salud.diagnosticos && datos.salud.diagnosticos.length > 0">
              <label>Diagnósticos:</label>
              <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                <span
                  v-for="(diagnostico, index) in datos.salud.diagnosticos"
                  :key="diagnostico.id_diagnostico || index"
                  class="badge badge-warning"
                  style="display: inline-block; margin-right: 0.5rem;"
                >
                  {{ obtenerDiagnostico(diagnostico.id_diagnostico) || `ID: ${diagnostico.id_diagnostico}` }}
                </span>
              </div>
            </div>

            <!-- Mensaje si no hay diagnósticos -->
            <div class="info-row" v-if="!datos.salud.diagnosticos || datos.salud.diagnosticos.length === 0">
              <label>Diagnósticos:</label>
              <span>No hay diagnósticos registrados</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Botones de acción -->
      <div class="perfil-actions">
        <button class="btn-editar-perfil" @click="$emit('editar')">
          <i class="fas fa-edit"></i> Editar Información
        </button>
        <button class="btn-cerrar-perfil" @click="$emit('cerrar')">
          Cerrar
        </button>
      </div>
    </div>

    <div v-else-if="!catalogosCargados" class="cargando">
      <p>Cargando catálogos...</p>
    </div>
    <div v-else class="cargando">
      <p>Cargando información del deportista...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import catalogosService from '@/services/catalogosService';
import { getApiUrl } from '@/config/environment';

defineOptions({
  name: 'PerfilDeportistaVista'
});

const props = defineProps({
  datos: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['cerrar', 'editar']);

// Catálogos para mapear IDs a nombres
const catalogos = ref({
  tiposSanguineos: [],
  ciudades: [],
  eps: [],
  deportes: [],
  escuelas: [],
  instituciones: [],
  categorias: [],
  tiposEnfermedad: [],
  diagnosticos: [],
  tiposDocumento: []
});

// Estado de carga de catálogos
const catalogosCargados = ref(false);

// Cargar catálogos al montar el componente
onMounted(async () => {
  try {
    await cargarCatalogos();
    catalogosCargados.value = true;
  } catch (error) {
    console.error('Error al cargar catálogos:', error);
    catalogosCargados.value = false;
  }
});

async function cargarCatalogos() {
  try {
    console.log('🔗 Base URL para catálogos:', getApiUrl(''));

    // Cargar todos los catálogos necesarios desde las rutas de deportistas
    const endpoints = [
      { url: getApiUrl('/api/deportistas/catalogos/grupos-sanguineos'), name: 'grupos-sanguineos' },
      { url: getApiUrl('/api/deportistas/catalogos/ciudades-residencia'), name: 'ciudades-residencia' },
      { url: getApiUrl('/api/deportistas/catalogos/eps'), name: 'eps' },
      { url: getApiUrl('/api/deportistas/catalogos/deportes'), name: 'deportes' },
      { url: getApiUrl('/api/deportistas/catalogos/escuelas'), name: 'escuelas' },
      { url: getApiUrl('/api/deportistas/catalogos/instituciones-registro'), name: 'instituciones-registro' },
      { url: getApiUrl('/api/deportistas/catalogos/tipos-enfermedad'), name: 'tipos-enfermedad' },
      { url: getApiUrl('/api/deportistas/catalogos/diagnosticos'), name: 'diagnosticos' },
      { url: getApiUrl('/api/catalogos/tipos-documento'), name: 'tipos-documento' }
    ];

    const resultados = await Promise.all(
      endpoints.map(async (endpoint) => {
        try {
          console.log(`📡 Cargando catálogo: ${endpoint.name} desde ${endpoint.url}`);
          const response = await fetch(endpoint.url);
          const data = await response.json();
          console.log(`✅ ${endpoint.name} cargado:`, response.ok, data);
          return { name: endpoint.name, ok: response.ok, data };
        } catch (error) {
          console.error(`❌ Error al cargar ${endpoint.name}:`, error);
          return { name: endpoint.name, ok: false, data: null, error };
        }
      })
    );

    // También cargar categorías usando el servicio
    let categorias = [];
    try {
      categorias = await catalogosService.getCategorias();
      console.log('✅ Categorías cargadas:', categorias);
    } catch (error) {
      console.error('❌ Error al cargar categorías:', error);
    }

    const [sangre, ciudades, eps, deportes, escuelas, instituciones, tiposEnfermedad, diagnosticos, tiposDocumento] = resultados.map(r => r.data);

    // Mapear respuestas - algunas vienen con 'success', otras con 'data' directamente
    const procesarCatalogo = (respuesta, valorPorDefecto = []) => {
      if (!respuesta) return valorPorDefecto;
      if (Array.isArray(respuesta)) return respuesta;
      if (respuesta.success && Array.isArray(respuesta.data)) return respuesta.data;
      if (Array.isArray(respuesta.data)) return respuesta.data;
      return valorPorDefecto;
    };

    catalogos.value.tiposSanguineos = procesarCatalogo(sangre);
    catalogos.value.ciudades = procesarCatalogo(ciudades);
    catalogos.value.eps = procesarCatalogo(eps);
    catalogos.value.deportes = procesarCatalogo(deportes);
    catalogos.value.escuelas = procesarCatalogo(escuelas);
    catalogos.value.instituciones = procesarCatalogo(instituciones);
    catalogos.value.categorias = Array.isArray(categorias) ? categorias : [];
    catalogos.value.tiposEnfermedad = procesarCatalogo(tiposEnfermedad);
    catalogos.value.diagnosticos = procesarCatalogo(diagnosticos);
    catalogos.value.tiposDocumento = procesarCatalogo(tiposDocumento);

    // Logs de debugging
    console.log('📋 ========== RESUMEN DE CATÁLOGOS CARGADOS ==========');
    console.log('📋 Tipos sanguíneos:', catalogos.value.tiposSanguineos.length);
    console.log('📋 Ciudades:', catalogos.value.ciudades.length);
    console.log('📋 EPS:', catalogos.value.eps.length);
    console.log('📋 Deportes:', catalogos.value.deportes.length);
    console.log('📋 Escuelas:', catalogos.value.escuelas.length);
    console.log('📋 Instituciones:', catalogos.value.instituciones.length);
    console.log('📋 Categorías:', catalogos.value.categorias.length);
    console.log('📋 Tipos de enfermedad:', catalogos.value.tiposEnfermedad.length);
    console.log('📋 Diagnósticos:', catalogos.value.diagnosticos.length);
    console.log('📋 Tipos de documento:', catalogos.value.tiposDocumento.length);

    if (catalogos.value.tiposEnfermedad.length > 0) {
      console.log('📋 Ejemplo tipo enfermedad:', catalogos.value.tiposEnfermedad[0]);
    }
    if (catalogos.value.diagnosticos.length > 0) {
      console.log('📋 Ejemplo diagnóstico:', catalogos.value.diagnosticos[0]);
    }
    if (catalogos.value.tiposDocumento.length > 0) {
      console.log('📋 Ejemplo tipo documento:', catalogos.value.tiposDocumento[0]);
    }

    console.log('✅ Catálogos cargados completamente');
  } catch (error) {
    console.error('Error al cargar catálogos:', error);
  }
}

function obtenerNombreCompleto() {
  if (props.datos?.persona?.nombre_completo) {
    return props.datos.persona.nombre_completo;
  }
  if (props.datos?.persona) {
    const p = props.datos.persona;
    return `${p.primer_nombre || ''} ${p.segundo_nombre || ''} ${p.primer_apellido || ''} ${p.segundo_apellido || ''}`.trim();
  }
  if (props.datos?.nombre) {
    return props.datos.nombre;
  }
  if (props.datos?.nombre1 || props.datos?.apellido1) {
    return `${props.datos.nombre1 || ''} ${props.datos.nombre2 || ''} ${props.datos.apellido1 || ''} ${props.datos.apellido2 || ''}`.trim();
  }
  return null;
}

function obtenerTipoSanguineo() {
  const idTipo = props.datos?.persona?.id_tipo_sanguineo ||
                 props.datos?.deportista?.id_tipo_sanguineo ||
                 props.datos?.id_tipo_sanguineo;
  if (!idTipo) return null;
  const tipo = catalogos.value.tiposSanguineos.find(t =>
    t.id_tipo_sangre === idTipo ||
    t.id_tipo_sanguineo === idTipo ||
    t.id === idTipo
  );
  return tipo?.tipo_sangre || tipo?.nombre || tipo?.tipo || null;
}

function obtenerCiudad() {
  const idCiudad = props.datos?.persona?.id_ciudad_recidencia ||
                   props.datos?.deportista?.id_ciudad_recidencia ||
                   props.datos?.id_ciudad_recidencia;
  if (!idCiudad) return null;
  const ciudad = catalogos.value.ciudades.find(c =>
    c.id_ciudad === idCiudad ||
    c.id === idCiudad ||
    c.id_ciudad_residencia === idCiudad
  );
  return ciudad?.nombre_ciudad || ciudad?.nombre || ciudad?.ciudad || null;
}

function obtenerEPS() {
  const idEPS = props.datos?.persona?.id_eps ||
                props.datos?.deportista?.id_eps ||
                props.datos?.id_eps;
  if (!idEPS) return null;
  const eps = catalogos.value.eps.find(e =>
    e.id_eps === idEPS ||
    e.id === idEPS
  );
  return eps?.nombre_eps || eps?.nombre || eps?.eps || null;
}

function obtenerDeporte() {
  const idDeporte = props.datos?.informacion_deportiva?.id_deporte ||
                    props.datos?.deportista?.id_deporte;
  if (!idDeporte) return null;
  const deporte = catalogos.value.deportes.find(d =>
    d.id_deporte === idDeporte ||
    d.id === idDeporte
  );
  return deporte?.nombre || deporte?.nombre_deporte || deporte?.deporte || null;
}

function obtenerEscuela() {
  const idEscuela = props.datos?.informacion_deportiva?.id_escuela;
  if (!idEscuela) return null;
  const escuela = catalogos.value.escuelas.find(e =>
    e.id_escuela === idEscuela ||
    e.id === idEscuela
  );
  return escuela?.nombre_escuela || escuela?.nombre || escuela?.escuela || null;
}

function obtenerInstitucion() {
  const idInst = props.datos?.informacion_deportiva?.id_institucion_registro;
  if (!idInst) return null;
  const inst = catalogos.value.instituciones.find(i =>
    i.id_institucion === idInst ||
    i.id_institucion_registro === idInst ||
    i.id === idInst
  );
  return inst?.nombre_institucion || inst?.nombre || inst?.institucion || null;
}

function obtenerCategoria() {
  const idCategoria = props.datos?.informacion_deportiva?.id_categoria ||
                      props.datos?.id_categoria ||
                      props.datos?.deportista?.id_categoria;
  if (!idCategoria) return props.datos?.categoria || null;
  const categoria = catalogos.value.categorias.find(c => c.id_categoria === idCategoria);
  return categoria?.nombre_categoria || props.datos?.categoria || null;
}


// Acceso a datos del deportista (puede venir en diferentes estructuras)
const datosDeportista = computed(() => {
  // El backend devuelve datos en 'datos_deportista' según obtener_informacion_completa_deportista
  return props.datos?.datos_deportista || props.datos?.deportista || props.datos || {};
});

const fechaNacimiento = computed(() => {
  // Buscar fecha de nacimiento en diferentes ubicaciones según la estructura del backend
  return props.datos?.persona?.fecha_nacimiento ||
         props.datos?.datos_deportista?.fecha_nacimiento ||
         datosDeportista.value?.fecha_nacimiento ||
         props.datos?.deportista?.fecha_nacimiento ||
         props.datos?.fecha_nacimiento ||
         null;
});

// Función para formatear fecha de nacimiento
function formatearFechaNacimiento(fecha) {
  if (!fecha) return null;

  // Si es un número (año solo), convertir a fecha completa (1 de enero de ese año)
  if (typeof fecha === 'number') {
    // Si es un año válido (4 dígitos), mostrarlo como fecha completa
    if (fecha >= 1900 && fecha <= new Date().getFullYear()) {
      // Crear fecha con 1 de enero del año dado
      const fechaCompleta = new Date(fecha, 0, 1); // Mes 0 = enero, día 1
      const dia = fechaCompleta.getDate().toString().padStart(2, '0');
      const mes = (fechaCompleta.getMonth() + 1).toString().padStart(2, '0');
      const año = fechaCompleta.getFullYear();
      return `${dia}/${mes}/${año}`;
    }
    return fecha.toString();
  }

  // Si es un string (fecha completa o año)
  if (typeof fecha === 'string') {
    // Si es solo un año (4 dígitos)
    if (/^\d{4}$/.test(fecha)) {
      const año = parseInt(fecha);
      if (año >= 1900 && año <= new Date().getFullYear()) {
        return `01/01/${año}`;
      }
    }

    // Intentar parsear como fecha ISO (YYYY-MM-DD) o otros formatos
    try {
      const dateObj = new Date(fecha);
      if (!isNaN(dateObj.getTime())) {
        // Formatear como DD/MM/YYYY
        const dia = dateObj.getDate().toString().padStart(2, '0');
        const mes = (dateObj.getMonth() + 1).toString().padStart(2, '0');
        const año = dateObj.getFullYear();
        return `${dia}/${mes}/${año}`;
      }
    } catch (error) {
      console.warn('Error al formatear fecha:', error);
    }
    return fecha;
  }

  // Si es un objeto Date
  if (fecha instanceof Date) {
    if (!isNaN(fecha.getTime())) {
      const dia = fecha.getDate().toString().padStart(2, '0');
      const mes = (fecha.getMonth() + 1).toString().padStart(2, '0');
      const año = fecha.getFullYear();
      return `${dia}/${mes}/${año}`;
    }
  }

  return fecha;
}

function obtenerTipoEnfermedad(idTipoEnfermedad) {
  if (!idTipoEnfermedad) return null;

  // Si los catálogos aún no están cargados, retornar null
  if (!catalogosCargados.value || !catalogos.value.tiposEnfermedad || catalogos.value.tiposEnfermedad.length === 0) {
    console.warn('⚠️ Catálogos de tipos de enfermedad aún no cargados');
    return null;
  }

  // Convertir ID a número para comparación
  const idBuscado = Number(idTipoEnfermedad);

  // Intentar encontrar el tipo de enfermedad por diferentes campos posibles
  const tipo = catalogos.value.tiposEnfermedad.find(t => {
    if (!t) return false;
    const idTipo = Number(t.id_tipo_enfermedad || t.id || 0);
    return idTipo === idBuscado;
  });

  if (!tipo) {
    console.warn('⚠️ Tipo de enfermedad no encontrado para ID:', idTipoEnfermedad, 'Catálogos disponibles:', catalogos.value.tiposEnfermedad.map(t => ({ id: t.id_tipo_enfermedad || t.id, nombre: t.nombre || t.nombre_tipo_enfermedad })));
    return null;
  }

  // El backend retorna el campo 'nombre' según el modelo TipoEnfermedad
  const nombre = tipo.nombre || tipo.nombre_tipo_enfermedad || tipo.tipo_enfermedad || tipo.tipo || tipo.descripcion || null;
  console.log('✅ Tipo de enfermedad encontrado:', { id: idBuscado, nombre });
  return nombre;
}

function obtenerDiagnostico(idDiagnostico) {
  if (!idDiagnostico) return null;

  // Si los catálogos aún no están cargados, retornar null
  if (!catalogosCargados.value || !catalogos.value.diagnosticos || catalogos.value.diagnosticos.length === 0) {
    console.warn('⚠️ Catálogos de diagnósticos aún no cargados');
    return null;
  }

  // Convertir ID a número para comparación
  const idBuscado = Number(idDiagnostico);

  // Intentar encontrar el diagnóstico por diferentes campos posibles
  const diagnostico = catalogos.value.diagnosticos.find(d => {
    if (!d) return false;
    const idDiag = Number(d.id_diagnostico || d.id || 0);
    return idDiag === idBuscado;
  });

  if (!diagnostico) {
    console.warn('⚠️ Diagnóstico no encontrado para ID:', idDiagnostico, 'Catálogos disponibles:', catalogos.value.diagnosticos.map(d => ({ id: d.id_diagnostico || d.id, nombre: d.nombre || d.nombre_diagnostico })));
    return null;
  }

  // El backend retorna el campo 'nombre' según el modelo Diagnostico
  const nombre = diagnostico.nombre || diagnostico.nombre_diagnostico || diagnostico.diagnostico || diagnostico.descripcion || null;
  console.log('✅ Diagnóstico encontrado:', { id: idBuscado, nombre });
  return nombre;
}

function obtenerTipoDocumento() {
  const idTipoDocumento = props.datos?.persona?.id_tipo_documento ||
                           props.datos?.id_tipo_documento ||
                           props.datos?.deportista?.id_tipo_documento;

  if (!idTipoDocumento) return null;

  const tipoDocumento = catalogos.value.tiposDocumento.find(t =>
    t.id_tipo_documento === idTipoDocumento ||
    t.id_documento === idTipoDocumento ||
    t.id === idTipoDocumento
  );

  return tipoDocumento?.nombre || tipoDocumento?.nombre_documento || tipoDocumento?.tipo || null;
}
</script>

<style scoped>
.perfil-deportista-vista {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
}

.perfil-header {
  background: linear-gradient(135deg, #004AAD 0%, #003d8f 100%);
  color: white;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 12px 12px 0 0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.perfil-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.btn-cerrar {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.btn-cerrar:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.perfil-content {
  padding: 2rem;
}

.perfil-card {
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  overflow: hidden;
}

.card-header {
  background: #004AAD;
  color: white;
  padding: 1rem 1.5rem;
}

.card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.card-header h4 {
  margin: 1rem 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #004AAD;
}

.card-content {
  padding: 1.5rem;
}

.info-grid {
  display: grid;
  gap: 0.75rem;
}

.info-row {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #dee2e6;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row label {
  font-weight: 600;
  color: #495057;
}

.info-row span {
  color: #6c757d;
}

.info-subsection {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 2px solid #dee2e6;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.badge-success {
  background: #d4edda;
  color: #155724;
}

.badge-muted {
  background: #e9ecef;
  color: #495057;
}

.badge-warning {
  background: #fff3cd;
  color: #856404;
}

.badge-info {
  background: #17a2b8;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.perfil-actions {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 2px solid #dee2e6;
}

.btn-cerrar-perfil {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-cerrar-perfil:hover {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-editar-perfil {
  background: #004AAD;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-right: 1rem;
}

.btn-editar-perfil:hover {
  background: #003d8f;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-editar-perfil i {
  margin-right: 0.5rem;
}

.cargando {
  padding: 3rem;
  text-align: center;
  color: #6c757d;
}

@media (max-width: 768px) {
  .info-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .perfil-content {
    padding: 1rem;
  }
}
</style>

