<template>
  <div class="perfil-deportista-vista">
    <div class="perfil-header">
      <h2>{{ modoEdicion ? '✏️ Editar Deportista' : '📋 Información del Deportista' }}</h2>
      <button class="btn-cerrar" @click="modoEdicion ? cancelarEdicion() : $emit('cerrar')" :title="modoEdicion ? 'Cancelar' : 'Cerrar'">
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
              <span v-if="!modoEdicion">{{ obtenerNombreCompleto() || 'No disponible' }}</span>
              <span v-else class="readonly-field">{{ obtenerNombreCompleto() || 'No disponible' }}</span>
            </div>
            <div class="info-row">
              <label>Primer nombre:</label>
              <span v-if="!modoEdicion">{{ datos.persona?.primer_nombre || datos.nombre1 || '—' }}</span>
              <input v-else v-model="formData.primer_nombre" type="text" class="input-editable" />
            </div>
            <div class="info-row">
              <label>Segundo nombre:</label>
              <span v-if="!modoEdicion">{{ datos.persona?.segundo_nombre || datos.nombre2 || '—' }}</span>
              <input v-else v-model="formData.segundo_nombre" type="text" class="input-editable" />
            </div>
            <div class="info-row">
              <label>Primer apellido:</label>
              <span v-if="!modoEdicion">{{ datos.persona?.primer_apellido || datos.apellido1 || '—' }}</span>
              <input v-else v-model="formData.primer_apellido" type="text" class="input-editable" />
            </div>
            <div class="info-row">
              <label>Segundo apellido:</label>
              <span v-if="!modoEdicion">{{ datos.persona?.segundo_apellido || datos.apellido2 || '—' }}</span>
              <input v-else v-model="formData.segundo_apellido" type="text" class="input-editable" />
            </div>
            <div class="info-row">
              <label>Tipo de documento:</label>
              <span v-if="!modoEdicion">{{ obtenerTipoDocumento() || '—' }}</span>
              <select v-else v-model="formData.id_tipo_documento" class="input-editable">
                <option :value="null">Seleccione...</option>
                <option v-for="tipo in catalogos.tiposDocumento" :key="tipo.id_tipo_documento || tipo.id" 
                        :value="tipo.id_tipo_documento || tipo.id">
                  {{ tipo.nombre || tipo.nombre_documento || tipo.tipo }}
                </option>
              </select>
            </div>
            <div class="info-row">
              <label>Documento:</label>
              <span v-if="!modoEdicion">{{ datos.persona?.documento || datos.documento || '—' }}</span>
              <input v-else v-model="formData.documento" type="text" class="input-editable" />
            </div>
            <div class="info-row">
              <label>Correo electrónico:</label>
              <span v-if="!modoEdicion">{{ datos.persona?.correo_electronico || datos.correo || '—' }}</span>
              <input v-else v-model="formData.correo_electronico" type="email" class="input-editable" />
            </div>
            <div class="info-row">
              <label>Teléfono:</label>
              <span v-if="!modoEdicion">{{ datos.persona?.telefono || datos.telefono || '—' }}</span>
              <input v-else v-model="formData.telefono" type="tel" class="input-editable" />
            </div>
            <div class="info-row">
              <label>Dirección:</label>
              <span v-if="!modoEdicion">{{ datos.persona?.direccion || datos.direccion || '—' }}</span>
              <input v-else v-model="formData.direccion" type="text" class="input-editable" />
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
              <span v-if="!modoEdicion">{{ formatearFechaNacimiento(fechaNacimiento) || '—' }}</span>
              <input v-else v-model="formData.fecha_nacimiento" type="date" class="input-editable" 
                     :max="new Date().toISOString().split('T')[0]" />
            </div>
            <div class="info-row">
              <label>Peso:</label>
              <span v-if="!modoEdicion">{{ datosDeportista.peso !== undefined && datosDeportista.peso !== null ? datosDeportista.peso + ' kg' : '—' }}</span>
              <div v-else class="input-with-unit">
                <input v-model="formData.peso" type="number" step="0.1" class="input-editable" placeholder="0.0" />
                <span class="unit">kg</span>
              </div>
            </div>
            <div class="info-row">
              <label>Altura:</label>
              <span v-if="!modoEdicion">{{ datosDeportista.altura !== undefined && datosDeportista.altura !== null ? datosDeportista.altura + ' m' : '—' }}</span>
              <div v-else class="input-with-unit">
                <input v-model="formData.altura" type="number" step="0.01" class="input-editable" placeholder="0.00" />
                <span class="unit">m</span>
              </div>
            </div>
            <div class="info-row">
              <label>Tipo sanguíneo:</label>
              <span v-if="!modoEdicion">{{ obtenerTipoSanguineo() || '—' }}</span>
              <select v-else v-model="formData.id_tipo_sanguineo" class="input-editable">
                <option :value="null">Seleccione...</option>
                <option v-for="tipo in catalogos.tiposSanguineos" :key="tipo.id_tipo_sangre || tipo.id" 
                        :value="tipo.id_tipo_sangre || tipo.id">
                  {{ tipo.tipo_sangre || tipo.nombre || tipo.tipo }}
                </option>
              </select>
            </div>
            <div class="info-row">
              <label>Ciudad de residencia:</label>
              <span v-if="!modoEdicion">{{ obtenerCiudad() || '—' }}</span>
              <select v-else v-model="formData.id_ciudad_recidencia" class="input-editable">
                <option :value="null">Seleccione...</option>
                <option v-for="ciudad in catalogos.ciudades" :key="ciudad.id_ciudad || ciudad.id" 
                        :value="ciudad.id_ciudad || ciudad.id">
                  {{ ciudad.nombre_ciudad || ciudad.nombre || ciudad.ciudad }}
                </option>
              </select>
            </div>
            <div class="info-row">
              <label>EPS:</label>
              <span v-if="!modoEdicion">{{ obtenerEPS() || '—' }}</span>
              <select v-else v-model="formData.id_eps" class="input-editable">
                <option :value="null">Seleccione...</option>
                <option v-for="eps in catalogos.eps" :key="eps.id_eps || eps.id" 
                        :value="eps.id_eps || eps.id">
                  {{ eps.nombre_eps || eps.nombre || eps.eps }}
                </option>
              </select>
            </div>
          </div>

          <!-- Información Deportiva Detallada -->
          <div class="info-subsection" v-if="datos.informacion_deportiva || modoEdicion">
            <h4>⚽ Detalles Deportivos</h4>
            <div class="info-grid">
              <div class="info-row">
                <label>Deporte principal:</label>
                <span v-if="!modoEdicion">{{ obtenerDeporte() || '—' }}</span>
                <select v-else v-model="formData.id_deporte" class="input-editable" required>
                  <option :value="null">Seleccione...</option>
                  <option v-for="deporte in catalogos.deportes" :key="deporte.id_deporte || deporte.id" 
                          :value="deporte.id_deporte || deporte.id">
                    {{ deporte.nombre || deporte.nombre_deporte || deporte.deporte }}
                  </option>
                </select>
              </div>
              <div class="info-row">
                <label>Practica otro deporte:</label>
                <span v-if="!modoEdicion">
                  <span class="badge" :class="datos.informacion_deportiva?.practica_otro_deporte ? 'badge-success' : 'badge-muted'">
                    {{ datos.informacion_deportiva?.practica_otro_deporte !== undefined ? (datos.informacion_deportiva.practica_otro_deporte ? 'Sí' : 'No') : '—' }}
                  </span>
                </span>
                <div v-else class="radio-group">
                  <label class="radio-option">
                    <input type="radio" :value="true" v-model="formData.practica_otro_deporte" />
                    Sí
                  </label>
                  <label class="radio-option">
                    <input type="radio" :value="false" v-model="formData.practica_otro_deporte" />
                    No
                  </label>
                </div>
              </div>
              <div class="info-row">
                <label>Participa en escuela:</label>
                <span v-if="!modoEdicion">
                  <span class="badge" :class="datos.informacion_deportiva?.participa_escuela ? 'badge-success' : 'badge-muted'">
                    {{ datos.informacion_deportiva?.participa_escuela !== undefined ? (datos.informacion_deportiva.participa_escuela ? 'Sí' : 'No') : '—' }}
                  </span>
                </span>
                <div v-else class="radio-group">
                  <label class="radio-option">
                    <input type="radio" :value="true" v-model="formData.participa_escuela" />
                    Sí
                  </label>
                  <label class="radio-option">
                    <input type="radio" :value="false" v-model="formData.participa_escuela" />
                    No
                  </label>
                </div>
              </div>
              <div class="info-row" v-if="modoEdicion || datos.informacion_deportiva?.participa_escuela">
                <label>Escuela:</label>
                <span v-if="!modoEdicion">{{ obtenerEscuela() || '—' }}</span>
                <select v-else v-model="formData.id_escuela" class="input-editable" :disabled="!formData.participa_escuela">
                  <option :value="null">Seleccione...</option>
                  <option v-for="escuela in catalogos.escuelas" :key="escuela.id_escuela || escuela.id" 
                          :value="escuela.id_escuela || escuela.id">
                    {{ escuela.nombre_escuela || escuela.nombre || escuela.escuela }}
                  </option>
                </select>
              </div>
              <div class="info-row">
                <label>Institución de registro:</label>
                <span v-if="!modoEdicion">{{ obtenerInstitucion() || '—' }}</span>
                <select v-else v-model="formData.id_institucion_registro" class="input-editable" required>
                  <option :value="null">Seleccione...</option>
                  <option v-for="inst in catalogos.instituciones" :key="inst.id_institucion || inst.id_institucion_registro || inst.id" 
                          :value="inst.id_institucion || inst.id_institucion_registro || inst.id">
                    {{ inst.nombre_institucion || inst.nombre || inst.institucion }}
                  </option>
                </select>
              </div>
              <div class="info-row">
                <label>Recomendación médica:</label>
                <span v-if="!modoEdicion">
                  <span class="badge" :class="datos.informacion_deportiva?.recomendacion_medica ? 'badge-warning' : 'badge-success'">
                    {{ datos.informacion_deportiva?.recomendacion_medica !== undefined ? (datos.informacion_deportiva.recomendacion_medica ? 'Sí' : 'No') : '—' }}
                  </span>
                </span>
                <div v-else class="radio-group">
                  <label class="radio-option">
                    <input type="radio" :value="true" v-model="formData.recomendacion_medica" />
                    Sí
                  </label>
                  <label class="radio-option">
                    <input type="radio" :value="false" v-model="formData.recomendacion_medica" />
                    No
                  </label>
                </div>
              </div>
              <div class="info-row" v-if="modoEdicion || datos.informacion_deportiva?.descripcion_recomendacion">
                <label>Descripción recomendación:</label>
                <span v-if="!modoEdicion">{{ datos.informacion_deportiva.descripcion_recomendacion || '—' }}</span>
                <textarea v-else v-model="formData.descripcion_recomendacion" class="input-editable" rows="3"></textarea>
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
        <template v-if="!modoEdicion">
          <button class="btn-editar-perfil" @click="$emit('editar')">
            <i class="fas fa-edit"></i> Actualizar
          </button>
          <button class="btn-cerrar-perfil" @click="$emit('cerrar')">
            Cerrar
          </button>
        </template>
        <template v-else>
          <button class="btn-guardar-perfil" @click="guardarCambios" :disabled="guardando">
            <i class="fas fa-save"></i> {{ guardando ? 'Guardando...' : 'Guardar Cambios' }}
          </button>
          <button class="btn-cancelar-perfil" @click="cancelarEdicion" :disabled="guardando">
            Cancelar
          </button>
        </template>
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
import { ref, onMounted, computed, watch } from 'vue';
import catalogosService from '@/services/catalogosService';
import deportistasService from '@/services/deportistasService';

defineOptions({
  name: 'PerfilDeportistaVista'
});

const props = defineProps({
  datos: {
    type: Object,
    default: null
  },
  modoEdicion: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['cerrar', 'editar', 'guardar', 'cancelar']);

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

// Estado para datos editables
const formData = ref({
  // Información Personal
  primer_nombre: '',
  segundo_nombre: '',
  primer_apellido: '',
  segundo_apellido: '',
  documento: '',
  correo_electronico: '',
  telefono: '',
  direccion: '',
  id_tipo_documento: null,
  // Datos del Deportista
  fecha_nacimiento: '',
  id_tipo_sanguineo: null,
  id_ciudad_recidencia: null,
  id_eps: null,
  peso: null,
  altura: null,
  // Información Deportiva
  id_deporte: null,
  practica_otro_deporte: false,
  participa_escuela: false,
  id_escuela: null,
  id_institucion_registro: null,
  // Antecedentes Médicos
  tiene_enfermedades: false,
  tipo_enfermedad: null,
  diagnosticos: [],
  recomendacion_medica: false,
  descripcion_recomendacion: ''
});

const guardando = ref(false);

// Inicializar formulario con datos del deportista
function inicializarFormulario() {
  if (!props.datos) return;
  
  console.log('🔍 Inicializando formulario con datos:', props.datos);
  
  const persona = props.datos.persona || {};
  const deportista = props.datos.datos_deportista || props.datos.deportista || {};
  const infoDeportiva = props.datos.informacion_deportiva || {};
  const salud = props.datos.salud || {};
  
  // Buscar fecha de nacimiento en múltiples ubicaciones
  let fechaNac = persona.fecha_nacimiento || 
                 deportista.fecha_nacimiento || 
                 props.datos.fecha_nacimiento ||
                 null;
  
  console.log('📅 Fecha de nacimiento encontrada:', fechaNac);
  
  // Formatear fecha de nacimiento para input date
  if (fechaNac) {
    if (typeof fechaNac === 'number') {
      // Si es solo un año, crear fecha completa
      fechaNac = `${fechaNac}-01-01`;
    } else if (typeof fechaNac === 'string' && /^\d{4}$/.test(fechaNac)) {
      fechaNac = `${fechaNac}-01-01`;
    } else if (typeof fechaNac === 'string') {
      // Si ya tiene formato YYYY-MM-DD, usarlo directamente
      if (fechaNac.includes('-') && fechaNac.length >= 10) {
        // Ya está en formato correcto, solo tomar los primeros 10 caracteres
        fechaNac = fechaNac.substring(0, 10);
      } else {
        // Intentar parsear otros formatos
        try {
          const date = new Date(fechaNac);
          if (!isNaN(date.getTime())) {
            fechaNac = date.toISOString().split('T')[0];
          }
        } catch (e) {
          console.warn('Error al formatear fecha:', e);
          fechaNac = '';
        }
      }
    }
  }
  
  // Buscar tipo sanguíneo en múltiples ubicaciones
  // El backend lo devuelve en persona según registro_deportista_service.py línea 611
  let idTipoSanguineo = persona.id_tipo_sanguineo || 
                        deportista.id_tipo_sanguineo || 
                        props.datos.id_tipo_sanguineo || 
                        null;
  // Convertir a número si es string
  if (idTipoSanguineo !== null && idTipoSanguineo !== undefined) {
    idTipoSanguineo = Number(idTipoSanguineo) || null;
  }
  
  // Buscar ciudad de residencia en múltiples ubicaciones
  // El backend lo devuelve en persona según registro_deportista_service.py línea 612
  let idCiudad = persona.id_ciudad_recidencia || 
                 deportista.id_ciudad_recidencia || 
                 props.datos.id_ciudad_recidencia || 
                 null;
  // Convertir a número si es string
  if (idCiudad !== null && idCiudad !== undefined) {
    idCiudad = Number(idCiudad) || null;
  }
  
  // Buscar EPS en múltiples ubicaciones
  // El backend lo devuelve en persona según registro_deportista_service.py línea 613
  let idEPS = persona.id_eps || 
              deportista.id_eps || 
              props.datos.id_eps || 
              null;
  // Convertir a número si es string
  if (idEPS !== null && idEPS !== undefined) {
    idEPS = Number(idEPS) || null;
  }
  
  console.log('🔍 IDs encontrados:', {
    id_tipo_sanguineo: idTipoSanguineo,
    id_ciudad_recidencia: idCiudad,
    id_eps: idEPS,
    fecha_nacimiento: fechaNac
  });
  
  formData.value = {
    // Información Personal
    primer_nombre: persona.primer_nombre || props.datos.nombre1 || '',
    segundo_nombre: persona.segundo_nombre || props.datos.nombre2 || '',
    primer_apellido: persona.primer_apellido || props.datos.apellido1 || '',
    segundo_apellido: persona.segundo_apellido || props.datos.apellido2 || '',
    documento: persona.documento || props.datos.documento || '',
    correo_electronico: persona.correo_electronico || props.datos.correo || '',
    telefono: persona.telefono || props.datos.telefono || '',
    direccion: persona.direccion || props.datos.direccion || '',
    id_tipo_documento: persona.id_tipo_documento || props.datos.id_tipo_documento || null,
    // Datos del Deportista - Buscar en persona y deportista
    fecha_nacimiento: fechaNac || '',
    id_tipo_sanguineo: idTipoSanguineo,
    id_ciudad_recidencia: idCiudad,
    id_eps: idEPS,
    peso: deportista.peso !== undefined && deportista.peso !== null ? deportista.peso : (props.datos.peso !== undefined && props.datos.peso !== null ? props.datos.peso : null),
    altura: deportista.altura !== undefined && deportista.altura !== null ? deportista.altura : (props.datos.altura !== undefined && props.datos.altura !== null ? props.datos.altura : null),
    // Información Deportiva
    id_deporte: infoDeportiva.id_deporte || props.datos.id_deporte || null,
    practica_otro_deporte: infoDeportiva.practica_otro_deporte !== undefined ? infoDeportiva.practica_otro_deporte : false,
    participa_escuela: infoDeportiva.participa_escuela !== undefined ? infoDeportiva.participa_escuela : false,
    id_escuela: infoDeportiva.id_escuela || null,
    id_institucion_registro: infoDeportiva.id_institucion_registro || null,
    // Antecedentes Médicos
    tiene_enfermedades: salud.tipos_enfermedad_ids && salud.tipos_enfermedad_ids.length > 0 ? true : false,
    tipo_enfermedad: salud.tipos_enfermedad_ids && salud.tipos_enfermedad_ids.length > 0 ? salud.tipos_enfermedad_ids[0] : null,
    diagnosticos: salud.diagnosticos ? salud.diagnosticos.map(d => d.id_diagnostico || d) : [],
    recomendacion_medica: infoDeportiva.recomendacion_medica !== undefined ? infoDeportiva.recomendacion_medica : false,
    descripcion_recomendacion: infoDeportiva.descripcion_recomendacion || ''
  };
  
  console.log('✅ FormData inicializado:', formData.value);
}

// Watch para inicializar formulario cuando cambien los datos o se active modo edición
watch(
  () => props.modoEdicion,
  (nuevoModo) => {
    if (nuevoModo && props.datos) {
      console.log('🔄 Modo edición activado, inicializando formulario...');
      inicializarFormulario();
    }
  },
  { immediate: true }
);

// Watch para cuando cambien los datos
watch(
  () => props.datos,
  (nuevosDatos) => {
    if (nuevosDatos && props.modoEdicion) {
      console.log('🔄 Datos actualizados, reinicializando formulario...');
      inicializarFormulario();
    }
  },
  { deep: true, immediate: true }
);

// Cargar catálogos al montar el componente
onMounted(async () => {
  try {
    await cargarCatalogos();
    // catalogosCargados se establece dentro de cargarCatalogos()
    // Si ya estamos en modo edición y hay datos, inicializar
    if (props.modoEdicion && props.datos) {
      console.log('🔄 onMounted: Inicializando formulario en modo edición');
      inicializarFormulario();
    }
  } catch (error) {
    console.error('Error crítico al cargar catálogos:', error);
    // Aún así, permitir que se muestre el componente
    catalogosCargados.value = true;
  }
});

async function cargarCatalogos() {
  try {
    // Usar la variable de entorno correcta
    const baseURL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:5000';

    console.log('🔗 Base URL para catálogos:', baseURL);

    // Cargar todos los catálogos necesarios desde las rutas de deportistas
    const endpoints = [
      { url: `${baseURL}/api/deportistas/catalogos/grupos-sanguineos`, name: 'grupos-sanguineos' },
      { url: `${baseURL}/api/deportistas/catalogos/ciudades-residencia`, name: 'ciudades-residencia' },
      { url: `${baseURL}/api/deportistas/catalogos/eps`, name: 'eps' },
      { url: `${baseURL}/api/deportistas/catalogos/deportes`, name: 'deportes' },
      { url: `${baseURL}/api/deportistas/catalogos/escuelas`, name: 'escuelas' },
      { url: `${baseURL}/api/deportistas/catalogos/instituciones-registro`, name: 'instituciones-registro' },
      { url: `${baseURL}/api/deportistas/catalogos/tipos-enfermedad`, name: 'tipos-enfermedad' },
      { url: `${baseURL}/api/deportistas/catalogos/diagnosticos`, name: 'diagnosticos' },
      { url: `${baseURL}/api/catalogos/tipos-documento`, name: 'tipos-documento' }
    ];

    // Obtener token de autenticación
    const token = localStorage.getItem('token');
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const resultados = await Promise.all(
      endpoints.map(async (endpoint) => {
        try {
          console.log(`📡 Cargando catálogo: ${endpoint.name} desde ${endpoint.url}`);
          const response = await fetch(endpoint.url, {
            method: 'GET',
            headers: headers
          });
          
          if (!response.ok) {
            console.warn(`⚠️ ${endpoint.name} retornó ${response.status}: ${response.statusText}`);
            // Si es 401, puede ser que no requiera autenticación, intentar sin token
            if (response.status === 401 && token) {
              const responseWithoutAuth = await fetch(endpoint.url, {
                method: 'GET',
                headers: {
                  'Content-Type': 'application/json',
                  'Accept': 'application/json'
                }
              });
              if (responseWithoutAuth.ok) {
                const data = await responseWithoutAuth.json();
                return { name: endpoint.name, ok: true, data };
              }
            }
            return { name: endpoint.name, ok: false, data: null, error: `HTTP ${response.status}` };
          }
          
          const data = await response.json();
          console.log(`✅ ${endpoint.name} cargado:`, response.ok);
          return { name: endpoint.name, ok: response.ok, data };
        } catch (error) {
          console.error(`❌ Error al cargar ${endpoint.name}:`, error);
          return { name: endpoint.name, ok: false, data: null, error: error.message };
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
    // Marcar como cargado incluso si algunos catálogos fallaron
    catalogosCargados.value = true;
  } catch (error) {
    console.error('Error al cargar catálogos:', error);
    // Aún así, marcar como cargado para que el componente se muestre
    // El perfil puede funcionar sin todos los catálogos
    catalogosCargados.value = true;
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
  const idTipo = props.modoEdicion 
    ? formData.value.id_tipo_sanguineo
    : (props.datos?.persona?.id_tipo_sanguineo ||
       props.datos?.deportista?.id_tipo_sanguineo ||
       props.datos?.datos_deportista?.id_tipo_sanguineo ||
       props.datos?.id_tipo_sanguineo);
  if (!idTipo) return null;
  const tipo = catalogos.value.tiposSanguineos.find(t =>
    t.id_tipo_sangre === idTipo ||
    t.id_tipo_sanguineo === idTipo ||
    t.id === idTipo
  );
  return tipo?.tipo_sangre || tipo?.nombre || tipo?.tipo || null;
}

function obtenerCiudad() {
  const idCiudad = props.modoEdicion 
    ? formData.value.id_ciudad_recidencia
    : (props.datos?.persona?.id_ciudad_recidencia ||
       props.datos?.deportista?.id_ciudad_recidencia ||
       props.datos?.datos_deportista?.id_ciudad_recidencia ||
       props.datos?.id_ciudad_recidencia);
  if (!idCiudad) return null;
  const ciudad = catalogos.value.ciudades.find(c =>
    c.id_ciudad === idCiudad ||
    c.id === idCiudad ||
    c.id_ciudad_residencia === idCiudad
  );
  return ciudad?.nombre_ciudad || ciudad?.nombre || ciudad?.ciudad || null;
}

function obtenerEPS() {
  const idEPS = props.modoEdicion 
    ? formData.value.id_eps
    : (props.datos?.persona?.id_eps ||
       props.datos?.deportista?.id_eps ||
       props.datos?.datos_deportista?.id_eps ||
       props.datos?.id_eps);
  if (!idEPS) return null;
  const eps = catalogos.value.eps.find(e =>
    e.id_eps === idEPS ||
    e.id === idEPS
  );
  return eps?.nombre_eps || eps?.nombre || eps?.eps || null;
}

function obtenerDeporte() {
  const idDeporte = props.modoEdicion 
    ? formData.value.id_deporte
    : (props.datos?.informacion_deportiva?.id_deporte ||
       props.datos?.deportista?.id_deporte);
  if (!idDeporte) return null;
  const deporte = catalogos.value.deportes.find(d =>
    d.id_deporte === idDeporte ||
    d.id === idDeporte
  );
  return deporte?.nombre || deporte?.nombre_deporte || deporte?.deporte || null;
}

function obtenerEscuela() {
  const idEscuela = props.modoEdicion 
    ? formData.value.id_escuela
    : props.datos?.informacion_deportiva?.id_escuela;
  if (!idEscuela) return null;
  const escuela = catalogos.value.escuelas.find(e =>
    e.id_escuela === idEscuela ||
    e.id === idEscuela
  );
  return escuela?.nombre_escuela || escuela?.nombre || escuela?.escuela || null;
}

function obtenerInstitucion() {
  const idInst = props.modoEdicion 
    ? formData.value.id_institucion_registro
    : props.datos?.informacion_deportiva?.id_institucion_registro;
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
  if (props.modoEdicion) {
    // En modo edición, usar formData
    return {
      peso: formData.value.peso,
      altura: formData.value.altura,
      fecha_nacimiento: formData.value.fecha_nacimiento
    };
  }
  // El backend devuelve datos en 'datos_deportista' según obtener_informacion_completa_deportista
  return props.datos?.datos_deportista || props.datos?.deportista || props.datos || {};
});

const fechaNacimiento = computed(() => {
  if (props.modoEdicion) {
    return formData.value.fecha_nacimiento;
  }
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
  const idTipoDocumento = props.modoEdicion 
    ? formData.value.id_tipo_documento
    : (props.datos?.persona?.id_tipo_documento ||
       props.datos?.id_tipo_documento ||
       props.datos?.deportista?.id_tipo_documento);

  if (!idTipoDocumento) return null;

  const tipoDocumento = catalogos.value.tiposDocumento.find(t =>
    t.id_tipo_documento === idTipoDocumento ||
    t.id_documento === idTipoDocumento ||
    t.id === idTipoDocumento
  );

  return tipoDocumento?.nombre || tipoDocumento?.nombre_documento || tipoDocumento?.tipo || null;
}

// Función para guardar cambios
async function guardarCambios() {
  if (!props.datos) return;
  
  guardando.value = true;
  try {
    const idDeportista = props.datos.id_deportista || props.datos.id;
    
    // Preparar datos para enviar al backend
    const datosEnvio = {
      datos_deportista: {
        fecha_nacimiento: formData.value.fecha_nacimiento,
        id_tipo_sanguineo: formData.value.id_tipo_sanguineo,
        id_ciudad_recidencia: formData.value.id_ciudad_recidencia,
        id_eps: formData.value.id_eps,
        peso: formData.value.peso ? parseFloat(formData.value.peso) : null,
        altura: formData.value.altura ? parseFloat(formData.value.altura) : null
      },
      datos_informacion_deportiva: {
        id_deporte: formData.value.id_deporte,
        practica_otro_deporte: formData.value.practica_otro_deporte,
        participa_escuela: formData.value.participa_escuela,
        id_escuela: formData.value.id_escuela || null,
        id_institucion_registro: formData.value.id_institucion_registro,
        recomendacion_medica: formData.value.recomendacion_medica,
        descripcion_recomendacion: formData.value.descripcion_recomendacion || ''
      },
      datos_persona: {
        primer_nombre: formData.value.primer_nombre,
        segundo_nombre: formData.value.segundo_nombre || null,
        primer_apellido: formData.value.primer_apellido,
        segundo_apellido: formData.value.segundo_apellido || null,
        documento: formData.value.documento,
        correo_electronico: formData.value.correo_electronico,
        telefono: formData.value.telefono || null,
        direccion: formData.value.direccion || null,
        id_tipo_documento: formData.value.id_tipo_documento
      }
    };
    
    const response = await deportistasService.actualizarDeportista(idDeportista, datosEnvio);
    
    if (response.success || response.status === 'success') {
      alert('✅ Deportista actualizado exitosamente');
      emit('guardar', response.data || datosEnvio);
    } else {
      throw new Error(response.message || 'Error al actualizar deportista');
    }
  } catch (error) {
    console.error('Error al guardar:', error);
    alert(`❌ Error al guardar: ${error.message || 'Error desconocido'}`);
  } finally {
    guardando.value = false;
  }
}

function cancelarEdicion() {
  emit('cancelar');
}
</script>

<style scoped>
.perfil-deportista-vista {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 900px;
  width: 100%;
  max-height: calc(100vh - 100px); /* Altura máxima considerando el header */
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  z-index: 10000; /* Asegurar que esté por encima de todo */
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
  z-index: 11;
  flex-shrink: 0; /* Evitar que se comprima */
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

.btn-guardar-perfil {
  background: #28a745;
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

.btn-guardar-perfil:hover:not(:disabled) {
  background: #218838;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-guardar-perfil:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-guardar-perfil i {
  margin-right: 0.5rem;
}

.btn-cancelar-perfil {
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

.btn-cancelar-perfil:hover:not(:disabled) {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-cancelar-perfil:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-editable {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.95rem;
  transition: border-color 0.3s;
}

.input-editable:focus {
  outline: none;
  border-color: #004AAD;
  box-shadow: 0 0 0 2px rgba(0, 74, 173, 0.1);
}

.input-editable:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
}

.input-with-unit {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.input-with-unit .input-editable {
  flex: 1;
}

.unit {
  color: #6c757d;
  font-size: 0.9rem;
  min-width: 30px;
}

.readonly-field {
  color: #6c757d;
  font-style: italic;
}

.radio-group {
  display: flex;
  gap: 1rem;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.radio-option input[type="radio"] {
  cursor: pointer;
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

