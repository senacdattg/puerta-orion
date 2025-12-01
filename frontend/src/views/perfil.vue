<template>
  <main class="perfil-page">
    <Encabezado />


    <div class="perfil-container">
      <div class="perfil-header">
        <div class="perfil-hero">
          <div class="avatar">
            <i class="fas fa-user-circle"></i>
          </div>
          <div class="hero-info">
            <h1 class="perfil-title">Mi Perfil</h1>
            <p class="perfil-subtitle">Consulta y gestiona tu información personal y de roles</p>
          </div>
          <div class="hero-actions">
            <button class="btn btn-primary btn-icon" @click="editarPerfil">
              <i class="fas fa-edit icon"></i>
              Editar perfil
            </button>
          </div>
        </div>
      </div>

      <div class="perfil-content" :class="{ 'is-loading': isLoading }">
        <!-- Loading state -->
        <div class="skeleton" v-if="isLoading">
          <div class="skeleton-row" v-for="n in 6" :key="n"></div>
        </div>

        <div v-else-if="!usuario" class="empty-state">
          <i class="fas fa-user"></i>
          <p>No se pudo cargar la información del usuario.</p>
        </div>

        <div v-else class="grid">
          <!-- Mensaje de error si no se pudo cargar el detalle pero hay usuario -->
          <div v-if="!detalle || Object.keys(detalle).length === 0" class="perfil-card" style="grid-column: 1 / -1;">
            <div class="card-header">
              <h3>⚠️ Información del Perfil</h3>
            </div>
            <div class="card-content">
              <div class="alert alert-warning" style="padding: 15px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; color: #856404; margin-bottom: 15px;">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>No se pudo cargar la información completa del perfil.</strong>
                <p style="margin: 10px 0 0 0; font-size: 0.9em;">
                  El backend retornó: "Usuario no encontrado o inactivo".
                  <br>
                  Esto puede deberse a que el usuario está inactivo en la base de datos.
                </p>
              </div>
              <!-- Mostrar información básica del usuario del store -->
              <div v-if="usuario" class="info-grid">
                <div class="info-row">
                  <span class="info-label">ID Usuario:</span>
                  <span>{{ usuario.id_usuario }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Username:</span>
                  <span>{{ usuario.username || usuario.usuario }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Estado:</span>
                  <span>
                    <span class="badge" :class="usuario.estado ? 'badge-success' : 'badge-muted'">
                      {{ usuario.estado ? 'Activo' : 'Inactivo' }}
                    </span>
                  </span>
                </div>
                <div class="info-row" v-if="usuario.persona">
                  <span class="info-label">Persona (del store):</span>
                  <span>{{ usuario.persona.nombre_completo || usuario.persona.documento || 'No disponible' }}</span>
                </div>
                <div class="info-row" v-if="usuario.roles && usuario.roles.length > 0">
                  <span class="info-label">Roles:</span>
                  <span>
                    <span
                      v-for="(rol, index) in usuario.roles"
                      :key="getRolId(rol)"
                      class="badge badge-info mr-1"
                    >
                      {{ getNombreRol(rol) }}<span v-if="index < usuario.roles.length - 1">, </span>
                    </span>
                  </span>
                </div>
              </div>
              <div class="mt-3">
                <strong>Acción recomendada:</strong>
                <ol style="margin: 10px 0 0 20px; font-size: 0.9em;">
                  <li>Verificar en la base de datos que el usuario ID {{ usuario?.id_usuario }} tenga <code>estado = 1</code></li>
                  <li>Verificar que el usuario tenga una persona asociada</li>
                  <li>Revisar los logs del backend para más detalles</li>
                </ol>
              </div>
            </div>
          </div>
          <div class="perfil-card">
            <div class="card-header">
              <h3>Información Personal</h3>
            </div>

            <div class="card-content" v-if="detalle?.persona">
              <!-- Mensaje de advertencia si hay datos incompletos -->
              <div v-if="detalle?.error || detalle?.warning" class="alert alert-warning" style="margin-bottom: 15px; padding: 12px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; color: #856404;">
                <i class="fas fa-exclamation-triangle"></i> {{ detalle?.error || detalle?.warning }}
              </div>
              <div class="info-row">
                <span class="info-label">Nombre completo:</span>
                <span>{{ `${detalle.persona.primer_nombre || ''} ${detalle.persona.segundo_nombre || ''} ${detalle.persona.primer_apellido || ''} ${detalle.persona.segundo_apellido || ''}`.trim() || 'No disponible' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Primer nombre:</span>
                <span>{{ detalle.persona.primer_nombre || '—' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Segundo nombre:</span>
                <span>{{ detalle.persona.segundo_nombre || '—' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Primer apellido:</span>
                <span>{{ detalle.persona.primer_apellido || '—' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Segundo apellido:</span>
                <span>{{ detalle.persona.segundo_apellido || '—' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Correo electrónico:</span>
                <span>{{ detalle.persona.correo_electronico || '—' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Tipo de documento:</span>
                <span>{{ nombreTipoDocumento(detalle.persona.id_tipo_documento) || '—' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Número de documento:</span>
                <span>{{ detalle.persona.documento || '—' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Teléfono:</span>
                <span>{{ detalle.persona.telefono || '—' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Dirección:</span>
                <span>{{ detalle.persona.direccion || '—' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Sexo:</span>
                <span>{{ nombreSexo(detalle.persona.id_sexo) }}</span>
              </div>
            </div>
            <div class="card-content" v-else-if="detalle && !detalle.persona">
              <div class="alert alert-warning" style="padding: 15px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; color: #856404;">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Información incompleta:</strong> Este usuario no tiene una persona asociada en el sistema.
                {{ detalle?.error || 'Por favor, contacte al administrador para completar el registro.' }}
              </div>
              <div v-if="detalle?.usuario" class="info-row">
                <span class="info-label">Usuario:</span>
                <span>{{ detalle.usuario.usuario || '—' }}</span>
              </div>
            </div>
            <div class="card-content" v-else-if="detalle === null || (detalle && Object.keys(detalle).length === 0)">
              <div class="alert alert-info" style="padding: 15px; background: #d1ecf1; border: 1px solid #bee5eb; border-radius: 8px; color: #0c5460;">
                <i class="fas fa-info-circle"></i>
                <strong>Cargando información...</strong> Por favor espera mientras se obtienen los datos del perfil.
              </div>
            </div>
            <div class="card-content" v-else>
              <div class="alert alert-warning" style="padding: 15px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; color: #856404;">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>No hay información personal disponible</strong>
                <p style="margin: 10px 0 0 0; font-size: 0.9em;">No se pudo cargar la información del perfil. Por favor, intenta recargar la página.</p>
              </div>
            </div>
          </div>

          <div class="perfil-card" v-if="usuario?.roles && usuario.roles.length > 1">
            <div class="card-header">
              <h3>Gestión de Roles</h3>
              <p class="card-subtitle">Cambia entre tus diferentes paneles de acceso</p>
            </div>

            <div class="card-content">
              <SelectorRoles />

              <div class="roles-info">
                <h4>Roles asignados:</h4>
                <div class="roles-list">
                  <div
                    v-for="rol in rolesAsignadosFiltrados"
                    :key="getRolId(rol)"
                    class="role-badge"
                    :class="getRoleClass(getNombreRol(rol))"
                  >
                    <i :class="getRoleIcon(getNombreRol(rol))"></i>
                    {{ getNombreRolCompleto(rol) }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="perfil-card" v-else-if="usuario?.roles && usuario.roles.length === 1">
            <div class="card-header">
              <h3>Rol Asignado</h3>
            </div>

            <div class="card-content">
              <div class="role-badge single" :class="getRoleClass(getNombreRol(usuario.roles[0]))">
                <i :class="getRoleIcon(getNombreRol(usuario.roles[0]))"></i>
                {{ getNombreRolCompleto(usuario.roles[0]) }}
              </div>
            </div>
          </div>

          <!-- Paneles por rol -->
          <div class="perfil-grid" v-if="detalle && detalle.persona">
            <!-- Deportista - Solo mostrar si el rol activo es Deportista -->
            <div class="perfil-card full-width" v-if="detalle?.deportista && authStore.activeRole === 'Deportista'">
              <div class="card-header">
                <h3>🏃 Información de Deportista</h3>
              </div>
              <div class="card-content deportista-section">
                <div class="info-grid">
                  <div class="info-row"><span class="info-label">Fecha nacimiento:</span><span>{{ formatearFechaNacimiento(detalle.deportista?.fecha_nacimiento) || '—' }}</span></div>
                  <div class="info-row"><span class="info-label">Tipo sanguíneo:</span><span>{{ nombreSangre(detalle.deportista.id_tipo_sanguineo) }}</span></div>
                  <div class="info-row"><span class="info-label">Ciudad residencia:</span><span>{{ nombreCiudad(detalle.deportista.id_ciudad_recidencia) }}</span></div>
                  <div class="info-row"><span class="info-label">EPS:</span><span>{{ nombreEPS(detalle.deportista.id_eps) }}</span></div>
                </div>

                <div class="metrics-grid">
                  <div class="metric-card">
                    <span class="info-label">Peso</span>
                    <span class="metric-value">{{ detalle.deportista.peso ?? '—' }} kg</span>
                  </div>
                  <div class="metric-card">
                    <span class="info-label">Altura</span>
                    <span class="metric-value">{{ detalle.deportista.altura ?? '—' }} m</span>
                  </div>
                </div>

                <!-- Información Deportiva -->
                <div class="info-subsection" v-if="detalle?.informacion_deportiva">
                  <h4>⚽ Información Deportiva</h4>
                  <div class="info-grid">
                    <div class="info-row"><span class="info-label">Categoría:</span><span>{{ nombreCategoria(detalle.informacion_deportiva.id_categoria) }}</span></div>
                    <div class="info-row"><span class="info-label">Practica otro deporte:</span><span><span class="badge" :class="detalle.informacion_deportiva.practica_otro_deporte ? 'badge-success' : 'badge-muted'">{{ detalle.informacion_deportiva.practica_otro_deporte ? 'Sí' : 'No' }}</span></span></div>
                    <div class="info-row"><span class="info-label">Participa en escuela:</span><span><span class="badge" :class="detalle.informacion_deportiva.participa_escuela ? 'badge-success' : 'badge-muted'">{{ detalle.informacion_deportiva.participa_escuela ? 'Sí' : 'No' }}</span></span></div>
                    <div class="info-row"><span class="info-label">Recomendación médica:</span><span><span class="badge" :class="detalle.informacion_deportiva.recomendacion_medica ? 'badge-warning' : 'badge-success'">{{ detalle.informacion_deportiva.recomendacion_medica ? 'Sí' : 'No' }}</span></span></div>
                    <div class="info-row" v-if="detalle.informacion_deportiva.descripcion_recomendacion"><span class="info-label">Descripción:</span><span>{{ detalle.informacion_deportiva.descripcion_recomendacion }}</span></div>
                    <div class="info-row"><span class="info-label">Escuela:</span><span>{{ nombreEscuela(detalle.informacion_deportiva.id_escuela) }}</span></div>
                    <div class="info-row"><span class="info-label">Deporte:</span><span>{{ nombreDeporte(detalle.informacion_deportiva.id_deporte) }}</span></div>
                    <div class="info-row"><span class="info-label">Institución registro:</span><span>{{ nombreInstitucionRegistro(detalle.informacion_deportiva.id_institucion_registro) }}</span></div>
                  </div>
                </div>

                <!-- Diagnósticos -->
                <div class="info-subsection" v-if="detalle?.diagnostico && detalle.diagnostico.length > 0">
                  <h4>🏥 Diagnósticos Médicos</h4>
                  <div class="info-grid">
                    <div class="info-row" v-if="detalle.tipo_enfermedad"><span class="info-label">Tipo enfermedad:</span><span>{{ nombreTipoEnfermedad(detalle.tipo_enfermedad) }}</span></div>
                    <div class="info-row"><span class="info-label">Diagnósticos:</span>
                      <div class="badges-list">
                        <span class="badge badge-info" v-for="diagId in detalle.diagnostico" :key="diagId">{{ nombreDiagnostico(diagId) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Acudientes del Deportista - Solo mostrar si el rol activo es Deportista -->
            <div class="perfil-card full-width" v-if="detalle?.deportista && authStore.activeRole === 'Deportista'">
              <div class="card-header">
                <h3>👨‍👩‍👧 Acudientes Asociados</h3>
              </div>
              <div class="card-content">
                <!-- Recordatorio si no hay acudientes -->
                <div v-if="!acudientesDeportista || acudientesDeportista.length === 0" class="alert alert-warning" style="padding: 15px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; color: #856404; margin-bottom: 15px;">
                  <i class="fas fa-exclamation-triangle"></i>
                  <strong>¡Importante!</strong>
                  <p style="margin: 10px 0 0 0; font-size: 0.9em;">
                    Debes asignar al menos un acudiente a tu perfil. Puedes asignar hasta 3 acudientes.
                  </p>
                </div>

                <!-- Lista de acudientes -->
                <div v-else class="acudientes-list">
                  <div
                    v-for="acudiente in acudientesDeportista"
                    :key="acudiente.id_acudiente"
                    class="acudiente-item"
                    style="padding: 12px; border: 1px solid #dee2e6; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;"
                  >
                    <div>
                      <strong>{{ acudiente.nombre_completo || acudiente.persona?.nombre_completo }}</strong>
                      <p style="margin: 5px 0; color: #6c757d; font-size: 0.9em;">
                        Parentesco: {{ acudiente.parentesco || acudiente.parentesco_nombre }}
                        <span v-if="acudiente.es_responsable" class="badge badge-success" style="margin-left: 10px;">Responsable</span>
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Botón para asignar acudiente -->
                <div class="perfil-actions" style="margin-top: 20px;">
                  <button
                    class="btn btn-primary"
                    @click="abrirModalAsignarAcudiente"
                    :disabled="acudientesDeportista && acudientesDeportista.length >= 3"
                  >
                    <i class="fas fa-user-plus"></i>
                    {{ acudientesDeportista && acudientesDeportista.length >= 3 ? 'Máximo de acudientes alcanzado (3)' : 'Asignar Acudiente' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para asignar acudiente -->
    <div v-if="mostrarModalAsignarAcudiente" class="modal-overlay" @click.self="cerrarModalAsignarAcudiente">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Asignar Acudiente</h2>
          <button class="btn-cerrar-modal" @click="cerrarModalAsignarAcudiente">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="buscar-acudiente-input">Buscar acudiente por cédula:</label>
            <div class="input-busqueda">
              <input
                id="buscar-acudiente-input"
                type="text"
                v-model="busquedaAcudiente"
                @input="buscarAcudientes"
                placeholder="Ingrese número de cédula..."
                class="input-text"
              />
              <button @click="buscarAcudientes" class="btn btn-primary">
                Buscar
              </button>
            </div>
          </div>

          <div v-if="acudientesEncontrados.length > 0" class="acudientes-lista">
            <div
              v-for="acudiente in acudientesEncontrados"
              :key="acudiente.id_acudiente"
              class="acudiente-card"
              :class="{ 'seleccionado': acudienteSeleccionado?.id_acudiente === acudiente.id_acudiente }"
              @click="seleccionarAcudiente(acudiente)"
            >
              <strong>{{ acudiente.persona?.nombre_completo || acudiente.nombre_completo }}</strong>
              <p>Cédula: {{ acudiente.persona?.documento || acudiente.documento }}</p>
            </div>
          </div>

          <div v-if="acudienteSeleccionado" class="formulario-asociacion">
            <div class="form-group">
              <label for="parentesco-select">Parentesco:</label>
              <select id="parentesco-select" v-model="idParentesco" class="select-input" required>
                <option value="">Seleccione un parentesco</option>
                <option
                  v-for="parentesco in parentescos"
                  :key="parentesco.id_parentesco"
                  :value="parentesco.id_parentesco"
                >
                  {{ parentesco.nombre }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="esResponsable" />
                Es responsable legal
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="cerrarModalAsignarAcudiente">
            Cancelar
          </button>
          <button
            class="btn btn-primary"
            @click="asociarAcudiente"
            :disabled="!acudienteSeleccionado || !idParentesco || asociando"
          >
            <span v-if="asociando">Asociando...</span>
            <span v-else>Asociar</span>
          </button>
        </div>
      </div>
    </div>

    <FooterEnhanced />
  </main>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { API_CONFIG, LOG_CONFIG } from '@/config/environment'
import Encabezado from '@/components/layout/encabezado.vue'
import FooterEnhanced from '@/components/layout/pie.vue'
import SelectorRoles from '@/components/layout/selector-roles.vue'
import Swal from 'sweetalert2'

defineOptions({
  name: 'PerfilPage'
})

const router = useRouter()
const authStore = useAuthStore()
const usuario = ref(null)
const detalle = ref(null)

// Mostrar todos los roles asignados (sin filtrar "Usuario")
// El backend ya maneja la lógica de visibilidad en rolesSelector
const rolesAsignadosFiltrados = computed(() => {
  if (!usuario.value?.roles) return []
  // Mostrar todos los roles que el usuario tiene
  return usuario.value.roles
})
const isLoading = computed(() => authStore.isLoading)

// Acudientes del deportista
const acudientesDeportista = ref([])
const mostrarModalAsignarAcudiente = ref(false)
const busquedaAcudiente = ref('')
const acudientesEncontrados = ref([])
const acudienteSeleccionado = ref(null)
const parentescos = ref([])
const idParentesco = ref('')
const esResponsable = ref(false)
const asociando = ref(false)

// Catálogos para mapear IDs a nombres legibles
const catalogos = ref({
  categorias: [],
  gruposSanguineos: [],
  ciudades: [],
  eps: [],
  tiposDocumento: [],
  sexos: [],
  deportes: [],
  escuelas: [],
  institucionesRegistro: [],
  tiposEnfermedad: [],
  diagnosticos: []
})

const baseURL = API_CONFIG.baseURL

async function cargarCatalogosPerfil() {
  try {
    const endpoints = [
      `${baseURL}/api/catalogos/categorias`,
      `${baseURL}/api/deportistas/catalogos/grupos-sanguineos`,
      `${baseURL}/api/deportistas/catalogos/ciudades-residencia`,
      `${baseURL}/api/deportistas/catalogos/eps`,
      `${baseURL}/api/catalogos/tipos-documento`,
      `${baseURL}/api/catalogos/sexos`,
      `${baseURL}/api/deportistas/catalogos/deportes`,
      `${baseURL}/api/deportistas/catalogos/escuelas`,
      `${baseURL}/api/deportistas/catalogos/instituciones-registro`,
      `${baseURL}/api/catalogos/tipos-enfermedad`,
      `${baseURL}/api/deportistas/catalogos/diagnosticos`
    ]

    const responses = await Promise.all(
      endpoints.map((url) => fetch(url))
    )

    const toData = async (res) => {
      try {
        if (!res.ok) {
          console.warn(`⚠️ Endpoint falló con status ${res.status}:`, res.url)
          return []
        }
        const json = await res.json()
        return json?.data || []
      } catch (e) {
        console.warn(`⚠️ Error al procesar respuesta:`, res.url, e)
        return []
      }
    }

    const [
      categorias,
      gruposSanguineos,
      ciudades,
      eps,
      tiposDocumento,
      sexos,
      deportes,
      escuelas,
      institucionesRegistro,
      tiposEnfermedad,
      diagnosticos
    ] = await Promise.all(responses.map(toData))

    catalogos.value.categorias = categorias
    catalogos.value.gruposSanguineos = gruposSanguineos
    catalogos.value.ciudades = ciudades
    catalogos.value.eps = eps
    catalogos.value.tiposDocumento = tiposDocumento
    catalogos.value.sexos = sexos
    catalogos.value.deportes = deportes
    catalogos.value.escuelas = escuelas
    catalogos.value.institucionesRegistro = institucionesRegistro
    catalogos.value.tiposEnfermedad = tiposEnfermedad
    catalogos.value.diagnosticos = diagnosticos
  } catch (e) {
    console.error('Error al cargar catálogos del perfil:', e)
  }
}

// Helpers de mapeo seguros
const nombreCategoria = (id) => {
  if (!id) return '—'
  const item = catalogos.value.categorias.find(c => c.id_categoria === id || c.id === id)
  return item?.nombre_categoria || item?.nombre || '—'
}
const nombreSangre = (id) => {
  if (!id) return '—'
  const item = catalogos.value.gruposSanguineos.find(x => x.id_tipo_sangre === id || x.id === id)
  return item?.tipo_sangre || item?.nombre_tipo_sangre || item?.nombre || '—'
}
const nombreCiudad = (id) => {
  if (!id) return '—'
  const item = catalogos.value.ciudades.find(x => x.id_ciudad === id || x.id === id)
  return item?.nombre_ciudad || item?.nombre || '—'
}
const nombreEPS = (id) => {
  if (!id) return '—'
  const item = catalogos.value.eps.find(x => x.id_eps === id || x.id === id)
  return item?.nombre_eps || item?.nombre || '—'
}
const nombreTipoDocumento = (id) => {
  if (!id) return '—'
  const item = catalogos.value.tiposDocumento.find(x => x.id_documento === id || x.id === id)
  return item?.nombre_documento || item?.nombre || '—'
}
const nombreSexo = (id) => {
  if (!id) return '—'
  const item = catalogos.value.sexos.find(x => x.id_sexo === id || x.id === id)
  return item?.nombre_sexo || item?.nombre || '—'
}
const nombreDeporte = (id) => {
  if (!id) return '—'
  const item = catalogos.value.deportes.find(x => x.id_deporte === id || x.id === id)
  return item?.nombre_deporte || item?.nombre || '—'
}
const nombreEscuela = (id) => {
  if (!id) return '—'
  const item = catalogos.value.escuelas.find(x => x.id_escuela === id || x.id === id)
  return item?.nombre_escuela || item?.nombre || '—'
}
const nombreInstitucionRegistro = (id) => {
  if (!id) return '—'
  const item = catalogos.value.institucionesRegistro.find(x => x.id_institucion === id || x.id === id)
  return item?.nombre_institucion || item?.nombre || '—'
}
const nombreTipoEnfermedad = (id) => {
  if (!id) return '—'
  const item = catalogos.value.tiposEnfermedad.find(x => x.id_tipo_enfermedad === id || x.id === id)
  return item?.nombre_tipo_enfermedad || item?.nombre || '—'
}
const nombreDiagnostico = (id) => {
  if (!id) return '—'
  const item = catalogos.value.diagnosticos.find(x => x.id_diagnostico === id || x.id === id)
  return item?.nombre || item?.nombre_diagnostico || '—'
}

const formatearDateADDMYYYY = (dateObj) => {
  const dia = dateObj.getDate().toString().padStart(2, '0')
  const mes = (dateObj.getMonth() + 1).toString().padStart(2, '0')
  const año = dateObj.getFullYear()
  return `${dia}/${mes}/${año}`
}

const validarAno = (año) => {
  const añoActual = new Date().getFullYear()
  return año >= 1900 && año <= añoActual
}

const formatearFechaComoNumero = (fecha) => {
  if (!validarAno(fecha)) {
    return fecha.toString()
  }

  const fechaCompleta = new Date(fecha, 0, 1)
  return formatearDateADDMYYYY(fechaCompleta)
}

const esSoloAno = (fecha) => {
  return /^\d{4}$/.test(fecha)
}

const formatearSoloAno = (fecha) => {
  const año = Number.parseInt(fecha, 10)
  if (validarAno(año)) {
    return `01/01/${año}`
  }
  return fecha
}

const parsearFechaString = (fecha) => {
  const dateObj = new Date(fecha)
  if (!Number.isNaN(dateObj.getTime())) {
    return formatearDateADDMYYYY(dateObj)
  }
  return null
}

const formatearFechaComoString = (fecha) => {
  if (esSoloAno(fecha)) {
    return formatearSoloAno(fecha)
  }

  const fechaFormateada = parsearFechaString(fecha)
  if (fechaFormateada) {
    return fechaFormateada
  }

  return fecha
}

const formatearFechaComoDate = (fecha) => {
  if (!Number.isNaN(fecha.getTime())) {
    return formatearDateADDMYYYY(fecha)
  }
  return null
}

function formatearFechaNacimiento(fecha) {
  if (!fecha) return null

  if (typeof fecha === 'number') {
    return formatearFechaComoNumero(fecha)
  }

  if (typeof fecha === 'string') {
    return formatearFechaComoString(fecha)
  }

  if (fecha instanceof Date) {
    return formatearFechaComoDate(fecha)
  }

  return fecha
}

// Cargar acudientes del deportista
async function cargarAcudientesDeportista() {
  if (!detalle.value?.deportista?.id_deportista) {
    acudientesDeportista.value = []
    return
  }

  try {
    const idDeportista = detalle.value.deportista.id_deportista
    const response = await fetch(`${baseURL}/api/deportistas/${idDeportista}/acudientes`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (response.ok) {
      const result = await response.json()
      acudientesDeportista.value = result.data || []
    } else {
      acudientesDeportista.value = []
    }
  } catch (error) {
    console.error('Error al cargar acudientes del deportista:', error)
    acudientesDeportista.value = []
  }
}

async function cargarDetalle() {
  try {
    const ok = await authStore.loadUserProfileDetail()
    if (ok && authStore.userDetail) {
      detalle.value = authStore.userDetail
      if (detalle.value.deportista?.id_deportista) {
        await cargarAcudientesDeportista()
      }
    }
  } catch (err) {
    console.error('Error al cargar detalle:', err)
  }
}

// Funciones para asignar acudiente
async function abrirModalAsignarAcudiente() {
  mostrarModalAsignarAcudiente.value = true
  busquedaAcudiente.value = ''
  acudientesEncontrados.value = []
  acudienteSeleccionado.value = null
  idParentesco.value = ''
  esResponsable.value = false

  // Cargar parentescos
  try {
    const response = await fetch(`${baseURL}/api/catalogos/parentescos`)
    const result = await response.json()
    parentescos.value = result.data || []
  } catch (error) {
    console.error('Error al cargar parentescos:', error)
  }
}

function cerrarModalAsignarAcudiente() {
  mostrarModalAsignarAcudiente.value = false
  busquedaAcudiente.value = ''
  acudientesEncontrados.value = []
  acudienteSeleccionado.value = null
  idParentesco.value = ''
  esResponsable.value = false
}

async function buscarAcudientes() {
  const busqueda = busquedaAcudiente.value.trim()

  if (!busqueda || busqueda.length < 2) {
    acudientesEncontrados.value = []
    return
  }

  try {
    const response = await fetch(`${baseURL}/api/catalogos/acudientes?cedula=${busqueda}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    if (response.ok) {
      const result = await response.json()
      if (result.success && result.data) {
        acudientesEncontrados.value = [result.data]
      } else {
        acudientesEncontrados.value = []
        await Swal.fire({
          icon: 'info',
          title: 'Sin coincidencias',
          text: result.message || 'No encontramos un acudiente con ese documento.'
        })
      }
    } else {
      acudientesEncontrados.value = []
    }
  } catch (error) {
    console.error('Error al buscar acudientes:', error)
    acudientesEncontrados.value = []
    await Swal.fire({
      icon: 'error',
      title: 'Error de búsqueda',
      text: 'Ocurrió un problema al buscar acudientes. Intenta nuevamente.'
    })
  }
}

function seleccionarAcudiente(acudiente) {
  acudienteSeleccionado.value = acudiente
}

async function asociarAcudiente() {
  if (!acudienteSeleccionado.value || !idParentesco.value) {
    await Swal.fire({
      icon: 'warning',
      title: 'Información incompleta',
      text: 'Selecciona un acudiente y un parentesco para continuar.'
    })
    return
  }

  if (!detalle.value?.deportista?.id_deportista) {
    await Swal.fire({
      icon: 'error',
      title: 'Perfil incompleto',
      text: 'No encontramos la información del deportista. Actualiza la página y vuelve a intentarlo.'
    })
    return
  }

  asociando.value = true
  try {
    const datos = {
      id_deportista: detalle.value.deportista.id_deportista,
      id_parentesco: Number.parseInt(idParentesco.value, 10),
      es_responsable: esResponsable.value
    }

    const response = await fetch(`${baseURL}/api/deportistas/asociar-acudiente`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(datos)
    })

    const result = await response.json()

    if (response.ok && result.success) {
      await Swal.fire({
        icon: 'success',
        title: 'Acudiente asociado',
        text: 'El acudiente fue asociado correctamente al deportista.'
      })
      cerrarModalAsignarAcudiente()
      await cargarAcudientesDeportista()
      await cargarDetalle()
    } else {
      await Swal.fire({
        icon: 'error',
        title: 'No se pudo asociar',
        text: result.error || 'Ocurrió un error al asociar el acudiente.'
      })
    }
  } catch (error) {
    console.error('Error al asociar acudiente:', error)
    await Swal.fire({
      icon: 'error',
      title: 'Error inesperado',
      text: error.message || 'No logramos completar la asociación.'
    })
  } finally {
    asociando.value = false
  }
}

onMounted(async () => {
  usuario.value = authStore.user
  if (LOG_CONFIG.enabled) {
    console.log('🔍 Usuario actual del store:', usuario.value)
  }

  // Cargar catálogos y detalle en paralelo
  await Promise.all([
    cargarCatalogosPerfil(),
    (async () => {
      try {
        const ok = await authStore.loadUserProfileDetail()
        if (LOG_CONFIG.enabled) {
          console.log('📊 Resultado de loadUserProfileDetail:', ok)
          console.log('📊 authStore.userDetail:', authStore.userDetail)
        }

        if (ok && authStore.userDetail) {
          detalle.value = authStore.userDetail
          if (LOG_CONFIG.enabled) {
            console.log('✅ Detalle del usuario cargado:', detalle.value)
          }
        } else {
          if (LOG_CONFIG.enabled) {
            console.warn('⚠️ No se pudo cargar el detalle del usuario')
          }
          // Establecer detalle como objeto vacío para evitar errores de renderizado
          detalle.value = {}
        }
      } catch (err) {
        if (LOG_CONFIG.enabled) {
          console.error('❌ Error al cargar detalle:', err)
        }
        detalle.value = {}
      }
    })()
  ])

  if (LOG_CONFIG.enabled) {
    console.log('📊 Estado final - detalle.value:', detalle.value)
    console.log('📊 Estado final - usuario.value:', usuario.value)
  }

  // Cargar acudientes solo si el usuario es deportista Y el rol activo es Deportista
  if (detalle.value?.deportista?.id_deportista && authStore.activeRole === 'Deportista') {
    await cargarAcudientesDeportista()
  }
})

watch(() => authStore.userDetail, (nuevo) => {
  if (LOG_CONFIG.enabled) {
    console.log('👀 Watch detectado cambio en userDetail:', nuevo)
  }
  if (nuevo) {
    detalle.value = nuevo
    // Cargar acudientes solo si el rol activo es Deportista
    if (nuevo.deportista?.id_deportista && authStore.activeRole === 'Deportista') {
      cargarAcudientesDeportista()
    }
  }
}, { immediate: true, deep: true })

watch(() => authStore.user, (nuevo) => {
  if (LOG_CONFIG.enabled) {
    console.log('👀 Watch detectado cambio en user:', nuevo)
  }
  if (nuevo) {
    usuario.value = nuevo
  }
}, { immediate: true, deep: true })

// Observar cambios en el rol activo para cargar/ocultar información según el rol
watch(() => authStore.activeRole, async (nuevoRol) => {
  console.log('👀 Watch detectado cambio en activeRole:', nuevoRol)
  // Si cambia a Deportista y hay información de deportista, cargar acudientes
  if (nuevoRol === 'Deportista' && detalle.value?.deportista?.id_deportista) {
    await cargarAcudientesDeportista()
  }
})

const editarPerfil = () => {
  router.push('/actualizar-info')
}

const getRoleClass = (rol) => {
  const classes = {
    'Administrador': 'role-admin',
    'Entrenador': 'role-coach',
    'Deportista': 'role-athlete',
    'Acudiente': 'role-guardian',
    'usuario': 'role-user'
  }
  return classes[rol] || 'role-default'
}

const getRoleIcon = (rol) => {
  const icons = {
    'Administrador': 'fas fa-crown',
    'Entrenador': 'fas fa-whistle',
    'Deportista': 'fas fa-running',
    'Acudiente': 'fas fa-user-friends',
    'usuario': 'fas fa-user',
    'Usuario': 'fas fa-user'
  }
  return icons[rol] || 'fas fa-user'
}

const getNombreRol = (rol) => {
  if (typeof rol === 'string') return rol
  if (typeof rol === 'object' && rol !== null && rol.nombre_rol) {
    return rol.nombre_rol
  }
  return 'usuario'
}

const getNombreRolCompleto = (rol) => {
  const nombres = {
    'Deportista': '🏃 Deportista',
    'Acudiente': '👨‍👩‍👧 Acudiente',
    'Entrenador': '⚽ Entrenador',
    'Administrador': '👤 Administrador',
    'SuperAdmin': '👑 Super Admin',
    'Usuario': '👤 Usuario',
    'usuario': '👤 Usuario'
  }
  return nombres[getNombreRol(rol)] || getNombreRol(rol)
}

const getRolId = (rol) => {
  if (typeof rol === 'object' && rol !== null && rol.id_rol) {
    return rol.id_rol
  }
  return getNombreRol(rol)
}
</script>

<style scoped>
/* Estilos para info-label: mantiene la apariencia de los labels originales */
.info-label {
  font-weight: 600;
  color: #495057;
  margin-right: 0.5rem;
  display: inline-block;
  min-width: 150px;
}

/* Asegurar que info-row mantenga el mismo estilo que antes */
.info-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.info-row .info-label {
  flex-shrink: 0;
}
</style>

