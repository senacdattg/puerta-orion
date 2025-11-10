<template>
  <main class="ver-acudidos-page">
    <Encabezado />
    <div class="ver-acudidos-container">
      <div class="ver-acudidos-header">
        <h1 class=" ver-acudidos-title">
          <i class="fas fa-users"></i>
          Gestión de Acudidos
        </h1>
        <p class="ver-acudidos-subtitle">Gestiona y asigna deportistas a tu cuenta</p>
      </div>

      <!-- Botón de acudir a un deportista -->
      <div class="action-header">
        <button class="btn-create-new" @click="abrirModalAcudir">
          <i class="fas fa-user-plus"></i>
          Acudir a un Deportista
        </button>
      </div>

      <!-- Lista de acudidos o estado vacío -->
      <div v-if="acudidos.length > 0" class="acudidos-grid">
        <div
          v-for="acudido in acudidos"
          :key="acudido.id"
          class="acudido-card"
        >
          <div class="card-header">
            <div class="acudido-avatar">
              <i class="fas fa-user"></i>
            </div>
            <div class="acudido-info">
              <h3>{{ acudido.nombre_completo }}</h3>
              <p>{{ acudido.categoria }}</p>
            </div>
          </div>

          <div class="card-content">
            <div class="info-item">
              <i class="fas fa-calendar"></i>
              <span>Edad: {{ acudido.edad }} años</span>
            </div>
            <div class="info-item">
              <i class="fas fa-envelope"></i>
              <span>{{ acudido.correo_electronico }}</span>
            </div>
            <div class="info-item">
              <i class="fas fa-phone"></i>
              <span>{{ acudido.telefono }}</span>
            </div>
          </div>

          <div class="card-actions">
            <button class="btn-action btn-view" @click="verDetalle(acudido)">
              <i class="fas fa-eye"></i>
              Ver Detalle
            </button>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-user-friends"></i>
        </div>
        <h3>No tienes acudidos registrados</h3>
        <p>Asigna deportistas a tu cuenta para gestionar su información</p>
        <button class="btn-primary" @click="abrirModalAcudir">
          <i class="fas fa-user-plus"></i>
          Acudir a un Deportista
        </button>
      </div>
    </div>

    <!-- Modal para buscar y asociar deportista -->
    <div v-if="mostrarModalAcudir" class="modal-overlay" @click.self="cerrarModalAcudir">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Acudir a un Deportista</h2>
          <button class="btn-cerrar-modal" @click="cerrarModalAcudir">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <!-- Búsqueda de deportista -->
          <div class="busqueda-deportista">
            <label>Buscar deportista:</label>
            <div class="input-busqueda">
              <input
                type="text"
                v-model="busquedaDeportista"
                @input="buscarDeportistas"
                placeholder="Buscar por nombre o documento..."
                class="input-text"
              />
              <i class="fas fa-search"></i>
            </div>
            <div v-if="buscando" class="cargando-busqueda">
              <p>Buscando...</p>
            </div>
          </div>

          <!-- Lista de deportistas encontrados -->
          <div v-if="deportistasEncontrados.length > 0" class="deportistas-lista">
            <h3>Deportistas encontrados:</h3>
            <div
              v-for="deportista in deportistasEncontrados"
              :key="deportista.id_deportista"
              class="deportista-item"
              :class="{ 'seleccionado': deportistaSeleccionado?.id_deportista === deportista.id_deportista }"
              @click="seleccionarDeportista(deportista)"
            >
              <div class="deportista-info">
                <strong>{{ deportista.nombre }}</strong>
                <span v-if="deportista.documento">Documento: {{ deportista.documento }}</span>
                <span v-if="deportista.categoria">Categoría: {{ deportista.categoria }}</span>
              </div>
              <i class="fas fa-check-circle" v-if="deportistaSeleccionado?.id_deportista === deportista.id_deportista"></i>
            </div>
          </div>

          <div v-else-if="busquedaDeportista && !buscando && deportistasEncontrados.length === 0" class="sin-resultados-busqueda">
            <p>No se encontraron deportistas con ese criterio de búsqueda.</p>
          </div>

          <!-- Formulario de asociación -->
          <div v-if="deportistaSeleccionado" class="formulario-asociacion">
            <h3>Datos de la asociación:</h3>
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
          <button class="btn-cancelar" @click="cerrarModalAcudir">
            Cancelar
          </button>
          <button
            class="btn-confirmar"
            @click="asociarDeportista"
            :disabled="!deportistaSeleccionado || !idParentesco || asociando"
          >
            <span v-if="asociando">Asociando...</span>
            <span v-else>Asociar Deportista</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para ver perfil completo del deportista -->
    <div v-if="mostrarModalPerfil" class="modal-overlay" @click.self="cerrarModalPerfil">
      <div class="modal-content modal-perfil">
        <div class="modal-body">
          <div v-if="cargandoPerfil" class="cargando">
            <p>Cargando información...</p>
          </div>
          <PerfilDeportistaVista
            v-else-if="deportistaSeleccionadoPerfil"
            :datos="deportistaSeleccionadoPerfil"
            :modoEdicion="modoEdicionPerfil"
            @cerrar="cerrarModalPerfil"
            @editar="habilitarEdicionPerfil"
            @cancelar="cancelarEdicionPerfil"
            @guardar="manejarGuardadoPerfil"
          />
          <div v-else class="error">
            <p>No se pudo cargar la información del deportista</p>
          </div>
        </div>
      </div>
    </div>

    <FooterEnhanced />
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Encabezado from '@/components/layout/encabezado.vue'
import FooterEnhanced from '@/components/layout/pie.vue'
import { useAuthStore } from '@/stores/auth'
import deportistasService from '@/services/deportistasService'
import authService from '@/services/authService'
import catalogosService from '@/services/catalogosService'
import PerfilDeportistaVista from '@/components/deportistas/perfil-deportista-vista.vue'
import Swal from 'sweetalert2'

const authStore = useAuthStore()

const acudidos = ref([])

// Estado del modal de acudir
const mostrarModalAcudir = ref(false)
const busquedaDeportista = ref('')
const deportistasEncontrados = ref([])
const buscando = ref(false)
const deportistaSeleccionado = ref(null)
const parentescos = ref([])
const idParentesco = ref('')
const esResponsable = ref(false)
const asociando = ref(false)

onMounted(async () => {
  // Recargar el perfil del usuario para obtener información actualizada
  console.log('🔄 Recargando perfil del usuario...')
  await authStore.loadUserProfile()

  // Esperar un momento para que se actualice el perfil
  setTimeout(() => {
    cargarAcudidos()
  }, 500)
})

const cargarAcudidos = async () => {
  try {
    console.log('🔍 Usuario autenticado:', authStore.user)
    console.log('🔍 Token:', authStore.token ? 'Token existe' : 'No hay token')

    // Obtener el ID del acudiente desde el usuario autenticado
    const acudienteId = authStore.user?.acudiente?.id_acudiente
    console.log('🔍 ID del acudiente:', acudienteId)

    if (!acudienteId) {
      console.error('❌ No se encontró ID del acudiente en el usuario autenticado')
      console.log('💡 Info del usuario:', JSON.stringify(authStore.user, null, 2))
      acudidos.value = []
      return
    }

    console.log(`🌐 Llamando al endpoint: http://localhost:5000/api/deportistas/acudiente/${acudienteId}`)

    // Llamar al backend para obtener los deportistas asociados
    const response = await fetch(`http://localhost:5000/api/deportistas/acudiente/${acudienteId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    console.log('📡 Estado de la respuesta:', response.status)
    const result = await response.json()
    console.log('📦 Datos recibidos:', result)

    if (response.ok && result.success) {
      acudidos.value = result.data || []
      console.log(`✅ ${acudidos.value.length} deportista(s) cargado(s)`)
      console.log('📋 Deportistas:', acudidos.value)
    } else {
      console.error('❌ Error al cargar deportistas:', result.message)
      acudidos.value = []
    }
  } catch (error) {
    console.error('❌ Error cargando acudidos:', error)
    acudidos.value = []
  }
}

// Estado para el modal de perfil completo
const mostrarModalPerfil = ref(false)
const deportistaSeleccionadoPerfil = ref(null)
const cargandoPerfil = ref(false)
const modoEdicionPerfil = ref(false)

const verDetalle = async (acudido) => {
  cargandoPerfil.value = true
  mostrarModalPerfil.value = true
  deportistaSeleccionadoPerfil.value = null
  modoEdicionPerfil.value = false

  try {
    // Obtener información completa del deportista
    const response = await deportistasService.obtenerDeportistaPorId(acudido.id)

    if (response.success && response.data) {
      deportistaSeleccionadoPerfil.value = response.data
    } else {
      await Swal.fire({
        icon: 'error',
        title: 'No se pudo cargar el deportista',
        text: 'Intenta nuevamente más tarde.'
      })
      mostrarModalPerfil.value = false
    }
  } catch (error) {
    console.error('Error al obtener perfil del deportista:', error)
    await Swal.fire({
      icon: 'error',
      title: 'Error de conexión',
      text: 'Error al cargar la información del deportista.'
    })
    mostrarModalPerfil.value = false
  } finally {
    cargandoPerfil.value = false
  }
}

const cerrarModalPerfil = () => {
  mostrarModalPerfil.value = false
  deportistaSeleccionadoPerfil.value = null
  modoEdicionPerfil.value = false
}

const habilitarEdicionPerfil = () => {
  modoEdicionPerfil.value = true
}

const cancelarEdicionPerfil = () => {
  modoEdicionPerfil.value = false
}

const manejarGuardadoPerfil = async () => {
  modoEdicionPerfil.value = false

  try {
    if (deportistaSeleccionadoPerfil.value) {
      const idDeportista = deportistaSeleccionadoPerfil.value.id || deportistaSeleccionadoPerfil.value.id_deportista
      if (idDeportista) {
        const response = await deportistasService.obtenerDeportistaPorId(idDeportista)
        if ((response.status === 'success' || response.success) && response.data) {
          deportistaSeleccionadoPerfil.value = response.data
        }
      }
    }
  } catch (error) {
    console.error('Error al refrescar información del deportista:', error)
  }

  await cargarAcudidos()
}

// Funciones para el modal de acudir
const abrirModalAcudir = async () => {
  mostrarModalAcudir.value = true
  busquedaDeportista.value = ''
  deportistasEncontrados.value = []
  deportistaSeleccionado.value = null
  idParentesco.value = ''
  esResponsable.value = false

  // Cargar parentescos
  try {
    parentescos.value = await catalogosService.getParentescos()
    console.log('✅ Parentescos cargados:', parentescos.value)
  } catch (error) {
    console.error('❌ Error al cargar parentescos:', error)
    await Swal.fire({
      icon: 'error',
      title: 'No se pudieron cargar los parentescos',
      text: 'Por favor, intenta de nuevo.'
    })
  }
}

const cerrarModalAcudir = () => {
  mostrarModalAcudir.value = false
  busquedaDeportista.value = ''
  deportistasEncontrados.value = []
  deportistaSeleccionado.value = null
  idParentesco.value = ''
  esResponsable.value = false
}

const buscarDeportistas = async () => {
  const busqueda = busquedaDeportista.value.trim()

  if (!busqueda || busqueda.length < 2) {
    deportistasEncontrados.value = []
    return
  }

  buscando.value = true
  try {
    // Buscar todos los deportistas (paginación alta para buscar)
    const response = await deportistasService.listarDeportistas(1, 1000)

    if (response.success && response.data) {
      // Filtrar por nombre o documento
      deportistasEncontrados.value = response.data.filter(deportista => {
        const nombre = (deportista.nombre || '').toLowerCase()
        const documento = (deportista.documento || deportista.persona?.documento || '').toString().toLowerCase()
        const busquedaLower = busqueda.toLowerCase()

        return nombre.includes(busquedaLower) || documento.includes(busquedaLower)
      })

      console.log(`✅ ${deportistasEncontrados.value.length} deportista(s) encontrado(s)`)
    } else {
      deportistasEncontrados.value = []
    }
  } catch (error) {
    console.error('❌ Error al buscar deportistas:', error)
    await Swal.fire({
      icon: 'error',
      title: 'Error al buscar deportistas',
      text: 'Por favor, intenta de nuevo.'
    })
    deportistasEncontrados.value = []
  } finally {
    buscando.value = false
  }
}

const seleccionarDeportista = (deportista) => {
  deportistaSeleccionado.value = deportista
  console.log('✅ Deportista seleccionado:', deportista)
}

const asociarDeportista = async () => {
  if (!deportistaSeleccionado.value || !idParentesco.value) {
    await Swal.fire({
      icon: 'warning',
      title: 'Datos incompletos',
      text: 'Selecciona un deportista y un parentesco antes de continuar.'
    })
    return
  }

  // Validar que el usuario no se esté acudiendo a sí mismo
  const usuarioActual = authStore.user
  const idPersonaUsuario = usuarioActual?.persona?.id_persona || usuarioActual?.id_persona

  // Verificar si el deportista seleccionado tiene el mismo id_persona que el usuario actual
  if (deportistaSeleccionado.value.id_persona === idPersonaUsuario ||
      deportistaSeleccionado.value.persona?.id_persona === idPersonaUsuario) {
    await Swal.fire({
      icon: 'info',
      title: 'Acción no permitida',
      text: 'No puedes acudirte a ti mismo.'
    })
    return
  }

  asociando.value = true
  try {
    const datos = {
      id_deportista: deportistaSeleccionado.value.id_deportista,
      id_parentesco: parseInt(idParentesco.value),
      es_responsable: esResponsable.value
    }

    console.log('🔄 Asociando deportista con datos:', datos)

    // Primero intentar asociar como acudiente existente
    let response = await authService.asociarAcudienteDeportista(datos)

    // Si falla porque no es acudiente, intentar completar perfil
    if (!response.success && response.error && response.error.includes('no está registrado como acudiente')) {
      console.log('🔄 Usuario no es acudiente, completando perfil...')
      response = await authService.completarPerfilAcudiente(datos)
    }

    if (response.success) {
      await Swal.fire({
        icon: 'success',
        title: 'Deportista asociado',
        text: 'La asociación se realizó correctamente.',
        timer: 1500,
        showConfirmButton: false
      })
      cerrarModalAcudir()
      // Recargar la lista de acudidos
      await cargarAcudidos()
      // Recargar el perfil del usuario
      await authStore.loadUserProfile()
    } else {
      await Swal.fire({
        icon: 'error',
        title: 'No se pudo asociar',
        text: response.error || 'Error desconocido.'
      })
    }
  } catch (error) {
    console.error('❌ Error al asociar deportista:', error)
    await Swal.fire({
      icon: 'error',
      title: 'Error de conexión',
      text: error.message || 'No pudimos completar la asociación.'
    })
  } finally {
    asociando.value = false
  }
}
</script>

<style scoped>
.ver-acudidos-page {
  min-height: 100vh;
  background: linear-gradient(to bottom, #f0f8ff 0%, #e3f2fd 100%);
  padding: 2rem 1rem;
  padding-bottom: 0;
  display: flex;
  flex-direction: column;
}

.ver-acudidos-container {
  max-width: 1200px;
  margin: 0 auto;
  margin-bottom: 2rem;
  flex: 1;
}

/* Hacer que el footer se salga del padding del main y se comporte como footer */
.ver-acudidos-page :deep(.footer-enhanced) {
  margin-left: -1rem;
  margin-right: -1rem;
  width: calc(100% + 2rem);
  margin-top: auto;
}

.ver-acudidos-header {
  text-align: center;
  margin-bottom: 2rem;
}

.ver-acudidos-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.ver-acudidos-subtitle {
  font-size: 1.1rem;
  color: #6c757d;
  margin: 0;
}

/* Action Header */
.action-header {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

.btn-create-new {
  background: #f7d600;
  color: #0047ab;
  border: 2px solid #0047ab;
  padding: 1.2rem 3rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(247, 214, 0, 0.3);
}

.btn-create-new:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(247, 214, 0, 0.4);
  background: #ffc107;
}

.btn-create-new i {
  font-size: 1.3rem;
}

.acudidos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.acudido-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s ease;
}

.acudido-card:hover {
  transform: translateY(-4px);
}

.card-header {
  background: #0047ab;
  color: white;
  border-bottom: 3px solid #f7d600;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.acudido-avatar {
  width: 3rem;
  height: 3rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.acudido-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
}

.acudido-info p {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
}

.card-content {
  padding: 1.5rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  color: #6c757d;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item i {
  width: 1rem;
  color: #0047ab;
}

.card-actions {
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  display: flex;
  gap: 0.75rem;
}

.btn-action {
  flex: 1;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  transition: all 0.3s ease;
}

.btn-view {
  background: #0047ab;
  color: white;
}

.btn-view:hover {
  background: #003d8f;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 4rem;
  color: #6c757d;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: #6c757d;
  margin: 0 0 2rem 0;
}

.btn-primary {
  background: #f7d600;
  color: #0047ab;
  border: 2px solid #0047ab;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(247, 214, 0, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(247, 214, 0, 0.4);
  background: #ffc107;
}

/* Estilos del modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-content.modal-perfil {
  overflow: visible;
  max-height: none;
}

.modal-content.modal-perfil .modal-body {
  overflow: visible;
  padding: 0;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 2px solid #f0f0f0;
}

.modal-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.btn-cerrar-modal {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6c757d;
  cursor: pointer;
  padding: 0.5rem;
  transition: color 0.3s ease;
}

.btn-cerrar-modal:hover {
  color: #e70000;
}

.modal-body {
  padding: 1.5rem;
}

.busqueda-deportista {
  margin-bottom: 1.5rem;
}

.busqueda-deportista label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.input-busqueda {
  position: relative;
}

.input-text {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.input-text:focus {
  outline: none;
  border-color: #0047ab;
}

.input-busqueda i {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.cargando-busqueda {
  margin-top: 0.5rem;
  color: #6c757d;
  font-style: italic;
}

.deportistas-lista {
  margin-bottom: 1.5rem;
}

.deportistas-lista h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.deportista-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  margin-bottom: 0.5rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.deportista-item:hover {
  border-color: #0047ab;
  background: #f0f8ff;
}

.deportista-item.seleccionado {
  border-color: #0047ab;
  background: #e3f2fd;
}

.deportista-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.deportista-info strong {
  color: #2c3e50;
  font-size: 1rem;
}

.deportista-info span {
  color: #6c757d;
  font-size: 0.9rem;
}

.deportista-item i.fa-check-circle {
  color: #0047ab;
  font-size: 1.2rem;
}

.sin-resultados-busqueda {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

.formulario-asociacion {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 2px solid #f0f0f0;
}

.formulario-asociacion h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.select-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.select-input:focus {
  outline: none;
  border-color: #0047ab;
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
  border-top: 2px solid #f0f0f0;
}

.btn-cancelar {
  padding: 0.75rem 1.5rem;
  border: 2px solid #6c757d;
  border-radius: 8px;
  background: white;
  color: #6c757d;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancelar:hover {
  background: #f8f9fa;
  border-color: #495057;
}

.btn-confirmar {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  background: #0047ab;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-confirmar:hover:not(:disabled) {
  background: #003d8f;
}

.btn-confirmar:disabled {
  background: #ccc;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .ver-acudidos-page {
    padding: 1rem 0.5rem;
  }

  .ver-acudidos-title {
    font-size: 2rem;
  }

  .btn-create-new {
    width: 100%;
    padding: 1rem 2rem;
    font-size: 1rem;
  }

  .acudidos-grid {
    grid-template-columns: 1fr;
  }

  .card-header {
    flex-direction: column;
    text-align: center;
  }

  .card-actions {
    flex-direction: column;
  }

  .modal-content {
    max-width: 95%;
    max-height: 95vh;
  }

  .modal-footer {
    flex-direction: column;
  }

  .btn-cancelar,
  .btn-confirmar {
    width: 100%;
  }
}
</style>

