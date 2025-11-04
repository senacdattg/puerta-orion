<template>
  <main class="perfil-page">
    <Encabezado />
    <TituloClub />

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
                  <label>ID Usuario:</label>
                  <span>{{ usuario.id_usuario }}</span>
                </div>
                <div class="info-row">
                  <label>Username:</label>
                  <span>{{ usuario.username || usuario.usuario }}</span>
                </div>
                <div class="info-row">
                  <label>Estado:</label>
                  <span>
                    <span class="badge" :class="usuario.estado ? 'badge-success' : 'badge-muted'">
                      {{ usuario.estado ? 'Activo' : 'Inactivo' }}
                    </span>
                  </span>
                </div>
                <div class="info-row" v-if="usuario.persona">
                  <label>Persona (del store):</label>
                  <span>{{ usuario.persona.nombre_completo || usuario.persona.documento || 'No disponible' }}</span>
                </div>
                <div class="info-row" v-if="usuario.roles && usuario.roles.length > 0">
                  <label>Roles:</label>
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
                <label>Nombre completo:</label>
                <span>{{ `${detalle.persona.primer_nombre || ''} ${detalle.persona.segundo_nombre || ''} ${detalle.persona.primer_apellido || ''} ${detalle.persona.segundo_apellido || ''}`.trim() || 'No disponible' }}</span>
              </div>
              <div class="info-row">
                <label>Primer nombre:</label>
                <span>{{ detalle.persona.primer_nombre || '—' }}</span>
              </div>
              <div class="info-row">
                <label>Segundo nombre:</label>
                <span>{{ detalle.persona.segundo_nombre || '—' }}</span>
              </div>
              <div class="info-row">
                <label>Primer apellido:</label>
                <span>{{ detalle.persona.primer_apellido || '—' }}</span>
              </div>
              <div class="info-row">
                <label>Segundo apellido:</label>
                <span>{{ detalle.persona.segundo_apellido || '—' }}</span>
              </div>
              <div class="info-row">
                <label>Correo electrónico:</label>
                <span>{{ detalle.persona.correo_electronico || '—' }}</span>
              </div>
              <div class="info-row">
                <label>Tipo de documento:</label>
                <span>{{ nombreTipoDocumento(detalle.persona.id_tipo_documento) || '—' }}</span>
              </div>
              <div class="info-row">
                <label>Número de documento:</label>
                <span>{{ detalle.persona.documento || '—' }}</span>
              </div>
              <div class="info-row">
                <label>Teléfono:</label>
                <span>{{ detalle.persona.telefono || '—' }}</span>
              </div>
              <div class="info-row">
                <label>Dirección:</label>
                <span>{{ detalle.persona.direccion || '—' }}</span>
              </div>
              <div class="info-row">
                <label>Sexo:</label>
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
                <label>Usuario:</label>
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
            <!-- Deportista -->
            <div class="perfil-card full-width" v-if="detalle?.deportista">
              <div class="card-header">
                <h3>🏃 Información de Deportista</h3>
              </div>
              <div class="card-content deportista-section">
                <div class="info-grid">
                  <div class="info-row"><label>Fecha nacimiento:</label><span>{{ formatearFechaNacimiento(detalle.deportista?.fecha_nacimiento) || '—' }}</span></div>
                  <div class="info-row"><label>Tipo sanguíneo:</label><span>{{ nombreSangre(detalle.deportista.id_tipo_sanguineo) }}</span></div>
                  <div class="info-row"><label>Ciudad residencia:</label><span>{{ nombreCiudad(detalle.deportista.id_ciudad_recidencia) }}</span></div>
                  <div class="info-row"><label>EPS:</label><span>{{ nombreEPS(detalle.deportista.id_eps) }}</span></div>
                </div>

                <div class="metrics-grid">
                  <div class="metric-card">
                    <label>Peso</label>
                    <span class="metric-value">{{ detalle.deportista.peso ?? '—' }} kg</span>
                  </div>
                  <div class="metric-card">
                    <label>Altura</label>
                    <span class="metric-value">{{ detalle.deportista.altura ?? '—' }} m</span>
                  </div>
                </div>

                <!-- Información Deportiva -->
                <div class="info-subsection" v-if="detalle?.informacion_deportiva">
                  <h4>⚽ Información Deportiva</h4>
                  <div class="info-grid">
                    <div class="info-row"><label>Categoría:</label><span>{{ nombreCategoria(detalle.informacion_deportiva.id_categoria) }}</span></div>
                    <div class="info-row"><label>Practica otro deporte:</label><span><span class="badge" :class="detalle.informacion_deportiva.practica_otro_deporte ? 'badge-success' : 'badge-muted'">{{ detalle.informacion_deportiva.practica_otro_deporte ? 'Sí' : 'No' }}</span></span></div>
                    <div class="info-row"><label>Participa en escuela:</label><span><span class="badge" :class="detalle.informacion_deportiva.participa_escuela ? 'badge-success' : 'badge-muted'">{{ detalle.informacion_deportiva.participa_escuela ? 'Sí' : 'No' }}</span></span></div>
                    <div class="info-row"><label>Recomendación médica:</label><span><span class="badge" :class="detalle.informacion_deportiva.recomendacion_medica ? 'badge-warning' : 'badge-success'">{{ detalle.informacion_deportiva.recomendacion_medica ? 'Sí' : 'No' }}</span></span></div>
                    <div class="info-row" v-if="detalle.informacion_deportiva.descripcion_recomendacion"><label>Descripción:</label><span>{{ detalle.informacion_deportiva.descripcion_recomendacion }}</span></div>
                    <div class="info-row"><label>Escuela:</label><span>{{ nombreEscuela(detalle.informacion_deportiva.id_escuela) }}</span></div>
                    <div class="info-row"><label>Deporte:</label><span>{{ nombreDeporte(detalle.informacion_deportiva.id_deporte) }}</span></div>
                    <div class="info-row"><label>Institución registro:</label><span>{{ nombreInstitucionRegistro(detalle.informacion_deportiva.id_institucion_registro) }}</span></div>
                  </div>
                </div>

                <!-- Diagnósticos -->
                <div class="info-subsection" v-if="detalle?.diagnostico && detalle.diagnostico.length > 0">
                  <h4>🏥 Diagnósticos Médicos</h4>
                  <div class="info-grid">
                    <div class="info-row" v-if="detalle.tipo_enfermedad"><label>Tipo enfermedad:</label><span>{{ nombreTipoEnfermedad(detalle.tipo_enfermedad) }}</span></div>
                    <div class="info-row"><label>Diagnósticos:</label>
                      <div class="badges-list">
                        <span class="badge badge-info" v-for="diagId in detalle.diagnostico" :key="diagId">{{ nombreDiagnostico(diagId) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Acudientes del Deportista -->
            <div class="perfil-card full-width" v-if="detalle?.deportista">
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
            <label>Buscar acudiente por cédula:</label>
            <div class="input-busqueda">
              <input
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
              <label>Parentesco:</label>
              <select v-model="idParentesco" class="select-input" required>
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
import { API_CONFIG } from '@/config/environment'
import Encabezado from '@/components/layout/encabezado.vue'
import TituloClub from '@/components/ui/titulo-club.vue'
import FooterEnhanced from '@/components/layout/pie.vue'
import SelectorRoles from '@/components/layout/selector-roles.vue'

defineOptions({
  name: 'PerfilPage'
})

const router = useRouter()
const authStore = useAuthStore()
const usuario = ref(null)
const detalle = ref(null)

// Calcular edad del deportista basándose en fecha_nacimiento
const edadDeportista = computed(() => {
  try {
    const deportista = detalle.value?.deportista || authStore.userDetail?.deportista || authStore.user?.deportista

    if (!deportista) return null

    const fechaNacimiento = deportista.fecha_nacimiento

    if (!fechaNacimiento) return null

    // Si fecha_nacimiento es solo el año (número)
    const añoActual = new Date().getFullYear()
    const añoNacimiento = typeof fechaNacimiento === 'number' ? fechaNacimiento : new Date(fechaNacimiento).getFullYear()
    const edad = añoActual - añoNacimiento

    return edad
  } catch (error) {
    console.error('Error al calcular edad:', error)
    return null
  }
})

// Verificar si el deportista es mayor de edad (>= 18 años)
const esMayorDeEdad = computed(() => {
  const edad = edadDeportista.value
  if (edad === null) return false
  return edad >= 18
})

// Verificar si el usuario es deportista
const esDeportista = computed(() => {
  const roles = usuario.value?.roles || []
  const nombresRoles = roles.map(r => {
    if (typeof r === 'string') return r
    if (typeof r === 'object' && r !== null && r.nombre_rol) return r.nombre_rol
    return null
  }).filter(Boolean)
  return nombresRoles.includes('Deportista')
})

// Verificar si el usuario ya tiene el rol Acudiente
const yaEsAcudiente = computed(() => {
  const roles = usuario.value?.roles || []
  const nombresRoles = roles.map(r => {
    if (typeof r === 'string') return r
    if (typeof r === 'object' && r !== null && r.nombre_rol) return r.nombre_rol
    return null
  }).filter(Boolean)
  return nombresRoles.includes('Acudiente')
})

// Filtrar roles asignados para ocultar "Usuario" según la lógica
const rolesAsignadosFiltrados = computed(() => {
  if (!usuario.value?.roles) return []

  // Si el usuario es deportista:
  // - Si es menor de edad: ocultar "Usuario"
  // - Si es mayor de edad pero ya es acudiente: ocultar "Usuario"
  // - Si es mayor de edad y NO es acudiente: mostrar "Usuario" (para que pueda registrarse como acudiente)
  if (esDeportista.value) {
    // Si es menor de edad, ocultar "Usuario"
    if (!esMayorDeEdad.value) {
      return usuario.value.roles.filter(rol => {
        const nombreRol = getNombreRol(rol)
        return nombreRol !== 'Usuario' && nombreRol !== 'usuario'
      })
    }
    // Si es mayor de edad pero ya es acudiente, ocultar "Usuario"
    if (yaEsAcudiente.value) {
      return usuario.value.roles.filter(rol => {
        const nombreRol = getNombreRol(rol)
        return nombreRol !== 'Usuario' && nombreRol !== 'usuario'
      })
    }
    // Si es mayor de edad y NO es acudiente, mostrar "Usuario"
    return usuario.value.roles
  }

  // Si no es deportista, mostrar todos los roles
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

// Función para formatear fecha de nacimiento
function formatearFechaNacimiento(fecha) {
  if (!fecha) return null

  // Si es un número (año solo), convertir a fecha completa (1 de enero de ese año)
  if (typeof fecha === 'number') {
    // Si es un año válido (4 dígitos), mostrarlo como fecha completa
    if (fecha >= 1900 && fecha <= new Date().getFullYear()) {
      // Crear fecha con 1 de enero del año dado
      const fechaCompleta = new Date(fecha, 0, 1) // Mes 0 = enero, día 1
      const dia = fechaCompleta.getDate().toString().padStart(2, '0')
      const mes = (fechaCompleta.getMonth() + 1).toString().padStart(2, '0')
      const año = fechaCompleta.getFullYear()
      return `${dia}/${mes}/${año}`
    }
    return fecha.toString()
  }

  // Si es un string (fecha completa o año)
  if (typeof fecha === 'string') {
    // Si es solo un año (4 dígitos)
    if (/^\d{4}$/.test(fecha)) {
      const año = parseInt(fecha)
      if (año >= 1900 && año <= new Date().getFullYear()) {
        return `01/01/${año}`
      }
    }

    // Intentar parsear como fecha ISO (YYYY-MM-DD) o otros formatos
    try {
      const dateObj = new Date(fecha)
      if (!isNaN(dateObj.getTime())) {
        // Formatear como DD/MM/YYYY
        const dia = dateObj.getDate().toString().padStart(2, '0')
        const mes = (dateObj.getMonth() + 1).toString().padStart(2, '0')
        const año = dateObj.getFullYear()
        return `${dia}/${mes}/${año}`
      }
    } catch (error) {
      console.warn('Error al formatear fecha:', error)
    }
    return fecha
  }

  // Si es un objeto Date
  if (fecha instanceof Date) {
    if (!isNaN(fecha.getTime())) {
      const dia = fecha.getDate().toString().padStart(2, '0')
      const mes = (fecha.getMonth() + 1).toString().padStart(2, '0')
      const año = fecha.getFullYear()
      return `${dia}/${mes}/${año}`
    }
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
        alert(result.message || 'No se encontró ningún acudiente')
      }
    } else {
      acudientesEncontrados.value = []
    }
  } catch (error) {
    console.error('Error al buscar acudientes:', error)
    acudientesEncontrados.value = []
  }
}

function seleccionarAcudiente(acudiente) {
  acudienteSeleccionado.value = acudiente
}

async function asociarAcudiente() {
  if (!acudienteSeleccionado.value || !idParentesco.value) {
    alert('Por favor, selecciona un acudiente y un parentesco.')
    return
  }

  if (!detalle.value?.deportista?.id_deportista) {
    alert('No se encontró información del deportista.')
    return
  }

  asociando.value = true
  try {
    const datos = {
      id_deportista: detalle.value.deportista.id_deportista,
      id_parentesco: parseInt(idParentesco.value),
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
      alert('✅ Acudiente asociado exitosamente')
      cerrarModalAsignarAcudiente()
      await cargarAcudientesDeportista()
      await cargarDetalle()
    } else {
      alert(`❌ Error al asociar acudiente: ${result.error || 'Error desconocido'}`)
    }
  } catch (error) {
    console.error('Error al asociar acudiente:', error)
    alert(`Error al asociar acudiente: ${error.message || 'Error desconocido'}`)
  } finally {
    asociando.value = false
  }
}

onMounted(async () => {
  usuario.value = authStore.user
  console.log('🔍 Usuario actual del store:', usuario.value)

  // Cargar catálogos y detalle en paralelo
  await Promise.all([
    cargarCatalogosPerfil(),
    (async () => {
      try {
        const ok = await authStore.loadUserProfileDetail()
        console.log('📊 Resultado de loadUserProfileDetail:', ok)
        console.log('📊 authStore.userDetail:', authStore.userDetail)

        if (ok && authStore.userDetail) {
          detalle.value = authStore.userDetail
          console.log('✅ Detalle del usuario cargado:', detalle.value)
        } else {
          console.warn('⚠️ No se pudo cargar el detalle del usuario')
          // Establecer detalle como objeto vacío para evitar errores de renderizado
          detalle.value = {}
        }
      } catch (err) {
        console.error('❌ Error al cargar detalle:', err)
        detalle.value = {}
      }
    })()
  ])

  console.log('📊 Estado final - detalle.value:', detalle.value)
  console.log('📊 Estado final - usuario.value:', usuario.value)

  // Cargar acudientes si el usuario es deportista
  if (detalle.value?.deportista?.id_deportista) {
    await cargarAcudientesDeportista()
  }
})

watch(() => authStore.userDetail, (nuevo) => {
  console.log('👀 Watch detectado cambio en userDetail:', nuevo)
  if (nuevo) {
    detalle.value = nuevo
    // Cargar acudientes cuando el detalle cambie y sea deportista
    if (nuevo.deportista?.id_deportista) {
      cargarAcudientesDeportista()
    }
  }
}, { immediate: true, deep: true })

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
.perfil-page {
  min-height: 100vh;
}

.perfil-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px;
}

/* Reducir el margen del TituloClub en el perfil */
.perfil-page :deep(.titulo-club) {
  margin-top: 10px;
  margin-bottom: 10px;
}

.perfil-header {
  margin-bottom: 24px;
}

.perfil-hero {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 20px;
  align-items: center;
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 20px 24px;
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: #fff;
  border: 2px solid #e5e7eb;
}
.avatar i { font-size: 48px; color: #64748b; }

.hero-info .perfil-title { margin: 0; font-size: 1.6rem; font-weight: 700; color: #1e293b; }
.hero-info .perfil-subtitle { margin: 6px 0 12px; color: #64748b; font-size: 0.95rem; }

.hero-badges { display: flex; gap: 10px; flex-wrap: wrap; }
.chip { display: inline-flex; align-items: center; gap: 6px; padding: 8px 12px; border-radius: 999px; border: 1px solid #e5e7eb; background: #fff; color: #334155; font-weight: 600chem; font-size: 0.875rem; }
.chip i { font-size: 0.875rem; color: inherit; }
.chip.primary { border-color: #c7d2fe; background: #eef2ff; color: #3730a3; }
.chip.success { border-color: #bbf7d0; background: #ecfdf5; color: #065f46; }
.chip.neutral { border-color: #e5e7eb; background: #f8fafc; color: #334155; }

.hero-actions .btn { white-space: nowrap; }

.perfil-content.is-loading { opacity: 0.7; }

.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 980px) { .grid { grid-template-columns: 1fr; } }

.perfil-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.perfil-card.full-width { grid-column: 1 / -1; }

.card-header { padding: 16px 20px; border-bottom: 1px solid #e5e7eb; background: #f8fafc; }
.card-header h3 { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }
.card-header .card-subtitle { margin: 4px 0 0; color: #64748b; font-size: 0.875rem; }
.card-content { padding: 16px 20px; }

.info-row { display: grid; grid-template-columns: 180px 1fr; gap: 12px; padding: 10px 0; border-bottom: 1px dashed #f1f5f9; align-items: start; }
.info-row:last-child { border-bottom: none; }
.info-row label { color: #64748b; font-weight: 600; font-size: 0.9rem; }
.info-row span { color: #1e293b; }

.roles-list { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }
.role-badge { display: inline-flex; align-items: center; gap: 8px; padding: 10px 14px; border-radius: 999px; font-weight: 700; font-size: 0.875rem; }
.role-badge.single { font-size: 1rem; }
.role-badge i { font-size: 1rem; }

.role-admin { background: #fef3c7; color: #92400e; }
.role-coach { background: #cffafe; color: #155e75; }
.role-athlete { background: #dcfce7; color: #166534; }
.role-guardian { background: #ede9fe; color: #5b21b6; }
.role-user, .role-default { background: #e2e8f0; color: #334155; }

.perfil-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; grid-column: 1 / -1; }
@media (max-width: 980px) { .perfil-grid { grid-template-columns: 1fr; } }

.deportista-section { display: flex; flex-direction: column; gap: 20px; }

.info-grid { display: grid; gap: 12px; }

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}
@media (max-width: 640px) { .metrics-grid { grid-template-columns: 1fr; } }

.metric-card {
  text-align: center;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}
.metric-card label {
  display: block;
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 600;
  margin-bottom: 8px;
}
.metric-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.info-subsection {
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}
.info-subsection h4 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
}

.badge { display: inline-block; padding: 4px 10px; border-radius: 999px; font-weight: 600; font-size: 0.8rem; }
.badge-success { background: #dcfce7; color: #166534; }
.badge-warning { background: #fef3c7; color: #92400e; }
.badge-muted { background: #e2e8f0; color: #334155; }
.badge-info { background: #dbeafe; color: #1e40af; margin-right: 6px; margin-bottom: 6px; display: inline-block; }

.badges-list { display: flex; flex-wrap: wrap; gap: 6px; }

.skeleton-row {
  height: 16px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 400% 100%;
  animation: shimmer 1.2s ease-in-out infinite;
  border-radius: 6px;
  margin: 10px 0;
}
@keyframes shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: 0 0; }
}

.info-grid {
  display: grid;
  gap: 12px;
}

.badge-info {
  background: #dbeafe;
  color: #1e40af;
  padding: 4px 10px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.8rem;
  margin-right: 6px;
  display: inline-block;
}

.mr-1 {
  margin-right: 6px;
}

.mt-3 {
  margin-top: 20px;
}

.empty-state {
  padding: 48px;
  text-align: center;
  color: #64748b;
}
.empty-state i {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 2px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.btn-cerrar-modal {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #64748b;
  padding: 0.5rem;
  border-radius: 4px;
  transition: all 0.3s;
}

.btn-cerrar-modal:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.input-busqueda {
  display: flex;
  gap: 0.5rem;
}

.input-busqueda .input-text {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
}

.input-busqueda .input-text:focus {
  outline: none;
  border-color: #0047ab;
}

.acudientes-lista {
  margin-top: 1rem;
}

.acudiente-card {
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.acudiente-card:hover {
  border-color: #0047ab;
  background: #f8fafc;
}

.acudiente-card.seleccionado {
  border-color: #0047ab;
  background: #eef2ff;
}

.acudiente-card strong {
  display: block;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.acudiente-card p {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
}

.formulario-asociacion {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 2px solid #e5e7eb;
}

.select-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: normal;
}

.checkbox-label input[type="checkbox"] {
  width: 1.2rem;
  height: 1.2rem;
  cursor: pointer;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 2px solid #e5e7eb;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: 2px solid #6c757d;
  border-radius: 8px;
  background: white;
  color: #6c757d;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: #f8f9fa;
  border-color: #495057;
}

.alert-warning {
  padding: 15px;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
  color: #856404;
  margin-bottom: 15px;
}

.alert-warning strong {
  display: block;
  margin-bottom: 0.5rem;
}

.perfil-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}
</style>
