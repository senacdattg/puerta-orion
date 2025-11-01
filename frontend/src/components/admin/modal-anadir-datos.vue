<template>
  <div v-if="mostrar" class="modal-overlay" @click="cerrar">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">
          <i class="fas fa-database"></i>
          Añadir Datos
        </h2>
        <button class="btn-cerrar" @click="cerrar">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- Paso 1: elegir entidad -->
      <div v-if="paso === 1" class="modal-body">
        <div class="seleccion-rol">
          <h3 class="paso-titulo">Selecciona el tipo de dato a gestionar</h3>
          <p class="paso-descripcion">Elige una categoría para crear o administrar datos base del sistema</p>

          <div class="roles-grid">
            <div
              v-for="item in items"
              :key="item.id"
              class="rol-option"
              :class="{ seleccionado: seleccionado?.id === item.id }"
              @click="seleccionar(item)"
            >
              <div class="rol-icono">
                <i :class="item.icono"></i>
              </div>
              <div class="rol-info">
                <h4 class="rol-nombre">{{ item.nombre }}</h4>
                <p class="rol-descripcion">{{ item.descripcion }}</p>
              </div>
              <div class="rol-check">
                <i v-if="seleccionado?.id === item.id" class="fas fa-check"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Paso 2: formulario simple para la entidad seleccionada -->
      <div v-else-if="paso === 2" class="modal-body">
        <button class="btn-volver" @click="volverPaso1">
          <i class="fas fa-arrow-left"></i>
          Volver
        </button>
        <div class="formulario">
          <div class="paso-header">
            <h3 class="paso-titulo">Crear {{ seleccionado?.nombre }}</h3>
          </div>

          <form @submit.prevent="enviar">
            <div class="form-grid">
              <!-- Campos para Categorías -->
              <template v-if="seleccionado?.id === 'categoria'">
                <div class="form-item">
                  <label class="label">Nombre de Categoría</label>
                  <input v-model.trim="form.nombre_categoria" type="text" class="input" placeholder="Ej: Pre-infantil" required />
                </div>
                <div class="form-item">
                  <label class="label">Edad Mínima</label>
                  <input v-model.number="form.edad_minima" type="number" class="input" placeholder="Ej: 5" required min="0" />
                </div>
                <div class="form-item">
                  <label class="label">Edad Máxima</label>
                  <input v-model.number="form.edad_maxima" type="number" class="input" placeholder="Ej: 7" required min="0" />
                </div>
                <div class="form-item">
                  <label class="label">Estado</label>
                  <select v-model="form.estado" class="input" required>
                    <option :value="true">Activo</option>
                    <option :value="false">Inactivo</option>
                  </select>
                </div>
              </template>
              
              <!-- Campos para otras entidades -->
              <template v-else>
                <div class="form-item">
                  <input v-model.trim="form.nombre" type="text" class="input" placeholder="Nombre" required />
                </div>
                <div v-if="seleccionado?.id === 'tipo-evento'" class="form-item">
                  <label class="label">Descripción (opcional)</label>
                  <textarea v-model.trim="form.descripcion" class="input" placeholder="Descripción del tipo de evento" rows="3"></textarea>
                </div>
                <div v-if="seleccionado?.id === 'eps'" class="form-item">
                  <label class="label">Código (opcional)</label>
                  <input v-model.trim="form.codigo" type="text" class="input" placeholder="Código EPS" />
                </div>
                <div v-if="seleccionado?.id === 'eps' || seleccionado?.id === 'metodo_pago'" class="form-item">
                  <label class="label">Estado</label>
                  <select v-model="form.estado" class="input" required>
                    <option :value="true">Activo</option>
                    <option :value="false">Inactivo</option>
                  </select>
                </div>
              </template>
            </div>

            <div class="footer-acciones">
              <button type="button" class="btn btn--outline" @click="volverPaso1">Cancelar</button>
              <button type="submit" class="btn btn--primary">Guardar</button>
            </div>
          </form>
        </div>
      </div>

      <div class="modal-footer">
        <div v-if="paso === 1" class="footer-acciones">
          <button class="btn btn--outline" @click="cerrar">Cancelar</button>
          <button class="btn btn--primary" :disabled="!seleccionado" @click="paso = 2">Continuar <i class="fas fa-arrow-right"></i></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  mostrar: { type: Boolean, default: false }
})

const emit = defineEmits(['cerrar','guardar-dato'])

const items = ref([
  { id: 'tipo_documento', nombre: 'Tipos de Documento', icono: 'fas fa-id-card', descripcion: 'Gestiona los tipos de documento' },
  { id: 'sexo', nombre: 'Sexo', icono: 'fas fa-venus-mars', descripcion: 'Gestiona valores de sexo' },
  { id: 'categoria', nombre: 'Categorías', icono: 'fas fa-layer-group', descripcion: 'Gestiona categorías deportivas' },
  { id: 'ciudad', nombre: 'Ciudades', icono: 'fas fa-city', descripcion: 'Gestiona ciudades de residencia' },
  { id: 'eps', nombre: 'EPS', icono: 'fas fa-hospital', descripcion: 'Gestiona entidades de salud' },
  { id: 'metodo_pago', nombre: 'Métodos de Pago', icono: 'fas fa-money-check-alt', descripcion: 'Gestiona métodos de pago' },
  { id: 'tipo-evento', nombre: 'Tipo Evento', icono: 'fas fa-calendar-alt', descripcion: 'Gestiona tipos de eventos' }
])

const paso = ref(1)
const seleccionado = ref(null)
const form = ref({ 
  nombre: '', 
  codigo: '',
  descripcion: '',
  // Campos específicos para categorías
  nombre_categoria: '',
  edad_minima: null,
  edad_maxima: null,
  estado: true
})

function cerrar() {
  // Limpiar selección y resetear al cerrar
  seleccionado.value = null
  paso.value = 1
  form.value = { 
    nombre: '', 
    codigo: '',
    descripcion: '',
    nombre_categoria: '',
    edad_minima: null,
    edad_maxima: null,
    estado: true
  }
  emit('cerrar')
}

// Limpiar selección cuando se abre el modal
watch(() => props.mostrar, (nuevoValor) => {
  if (nuevoValor) {
    seleccionado.value = null
    paso.value = 1
    form.value = { 
      nombre: '', 
      codigo: '',
      descripcion: '',
      nombre_categoria: '',
      edad_minima: null,
      edad_maxima: null,
      estado: true
    }
  }
})

function seleccionar(item){
  seleccionado.value = item
}

function volverPaso1(){
  paso.value = 1
  form.value = { 
    nombre: '', 
    codigo: '',
    descripcion: '',
    nombre_categoria: '',
    edad_minima: null,
    edad_maxima: null,
    estado: true
  }
}

function enviar(){
  emit('guardar-dato', { entidad: seleccionado.value.id, ...form.value })
  volverPaso1()
  cerrar()
}
</script>

<style scoped>
.modal-overlay{position:fixed;inset:0;background-color:rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center;z-index:9999;padding:20px;backdrop-filter:blur(4px)}
.modal-content{background:#fff;border-radius:16px;width:100%;max-width:800px;max-height:90vh;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.3)}
.modal-header{background:linear-gradient(135deg,#0047ab 0%,#0d47a1 100%);color:#fff;padding:25px 30px;display:flex;justify-content:space-between;align-items:center}
.modal-title{font-size:1.5rem;font-weight:600;margin:0;display:flex;align-items:center;gap:12px}
.btn-cerrar{background:rgba(255,255,255,.2);border:none;color:#fff;width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer}
.modal-body{padding:30px;max-height:60vh;overflow-y:auto}
.paso-titulo{font-size:1.4rem;font-weight:600;color:#333;margin:0 0 10px 0;text-align:center}
.paso-descripcion{color:#666;margin-bottom:30px;font-size:1rem;text-align:center}
.formulario{display:flex;flex-direction:column;align-items:center;width:100%}
.formulario form{width:100%;max-width:400px;margin:0 auto;display:flex;flex-direction:column;align-items:center}
.formulario .paso-header{width:100%;max-width:400px;margin:0 auto;text-align:center}
.formulario .form-grid{width:100%}
.btn-volver{background-color:#6c757d;color:white;border:none;cursor:pointer;display:flex;align-items:center;gap:8px;font-size:14px;padding:10px 20px;border-radius:6px;transition:background-color .3s ease;margin-bottom:20px}
.btn-volver:hover{background-color:#5a6268}
.paso-header{display:flex;flex-direction:column;align-items:center;gap:15px;margin-bottom:25px}
.roles-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin-top:30px;justify-items:center;max-width:900px;margin-left:auto;margin-right:auto}
.roles-grid .rol-option{width:100%;max-width:400px}
.rol-option{background:#fff;border:2px solid #e0e0e0;border-radius:12px;padding:25px;cursor:pointer;transition:all .3s ease;display:flex;align-items:center;gap:20px}
.rol-option:hover{border-color:#0047ab;transform:translateY(-2px);box-shadow:0 8px 25px rgba(0,71,171,.15)}
.rol-option.seleccionado{border-color:#0047ab;background:#f8fbff;box-shadow:0 8px 25px rgba(0,71,171,.2)}
.rol-icono{width:60px;height:60px;background:linear-gradient(135deg,#0047ab 0%,#0d47a1 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:1.5rem;flex-shrink:0}
.rol-info{flex:1;text-align:left}
.rol-nombre{font-size:1.2rem;font-weight:600;color:#333;margin:0 0 8px 0}
.rol-descripcion{color:#666;margin:0;font-size:.9rem;line-height:1.4}
.rol-check{width:30px;height:30px;background:#28a745;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:.9rem;flex-shrink:0}
.modal-footer{background:#f8f9fa;padding:20px 30px;border-top:1px solid #e0e0e0}
.footer-acciones{display:flex;justify-content:center;gap:15px;width:100%}
.formulario .footer-acciones{justify-content:center}
.form-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-bottom:16px}
.form-item{display:flex;flex-direction:column;gap:6px;align-items:center}
.label{font-size:.9rem;color:#555;font-weight:600;text-align:center}
.input{padding:10px 12px;border:2px solid #d1d5db;border-radius:8px;background:#fff;color:#333;font-size:.95rem;font-family:inherit;resize:vertical;text-align:center;width:100%}
.input:focus{outline:none;border-color:#0047ab;box-shadow:0 0 0 3px rgba(0,71,171,.15)}
textarea.input{min-height:80px;line-height:1.5}
select.input{appearance:none;background-image:url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");background-position:right 8px center;background-repeat:no-repeat;background-size:16px;padding-right:40px;cursor:pointer}
.btn{display:inline-flex;align-items:center;gap:8px;padding:10px 20px;border:none;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer;text-decoration:none;justify-content:center}
.btn--outline{background-color:#6c757d;color:white;border:none}
.btn--outline:hover{background-color:#6c757d !important;color:white !important}
.btn--primary{background-color:#0047ab;color:white;border:none}
.btn--primary:hover{background-color:#0047ab !important;color:white !important}
.btn--primary:disabled{background-color:#ccc;cursor:not-allowed;opacity:0.6}
@media (max-width:768px){.modal-content{margin:10px;max-height:95vh}.modal-body{padding:20px}.roles-grid{grid-template-columns:1fr}.rol-option{flex-direction:column;text-align:center;padding:20px}.footer-acciones{flex-direction:column}.btn{width:100%;justify-content:center}}
</style>


