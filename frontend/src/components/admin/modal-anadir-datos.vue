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
            </div>
          </div>
        </div>
      </div>

      <!-- Paso 2: formulario simple para la entidad seleccionada -->
      <div v-else-if="paso === 2" class="modal-body">
        <div class="formulario">
          <div class="paso-header">
            <button class="btn-volver" @click="volverPaso1">
              <i class="fas fa-arrow-left"></i>
              Volver
            </button>
            <h3 class="paso-titulo">Crear {{ seleccionado?.nombre }}</h3>
          </div>

          <form @submit.prevent="enviar">
            <div class="form-grid">
              <div class="form-item">
                <label class="label">Nombre</label>
                <input v-model.trim="form.nombre" type="text" class="input" placeholder="Nombre" required />
              </div>
              <div v-if="seleccionado?.id === 'eps'" class="form-item">
                <label class="label">Código (opcional)</label>
                <input v-model.trim="form.codigo" type="text" class="input" placeholder="Código EPS" />
              </div>
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
import { ref } from 'vue'

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
  { id: 'metodo_pago', nombre: 'Métodos de Pago', icono: 'fas fa-money-check-alt', descripcion: 'Gestiona métodos de pago' }
])

const paso = ref(1)
const seleccionado = ref(null)
const form = ref({ nombre: '', codigo: '' })

function cerrar() {
  emit('cerrar')
}

function seleccionar(item){
  seleccionado.value = item
}

function volverPaso1(){
  paso.value = 1
  form.value = { nombre: '', codigo: '' }
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
.paso-titulo{font-size:1.4rem;font-weight:600;color:#333;margin:0 0 10px 0}
.paso-descripcion{color:#666;margin-bottom:30px;font-size:1rem}
.roles-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin-top:30px}
.rol-option{background:#fff;border:2px solid #e0e0e0;border-radius:12px;padding:25px;cursor:pointer;transition:all .3s ease;display:flex;align-items:center;gap:20px}
.rol-option:hover{border-color:#0047ab;transform:translateY(-2px);box-shadow:0 8px 25px rgba(0,71,171,.15)}
.rol-option.seleccionado{border-color:#0047ab;background:#f8fbff;box-shadow:0 8px 25px rgba(0,71,171,.2)}
.rol-icono{width:60px;height:60px;background:linear-gradient(135deg,#0047ab 0%,#0d47a1 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:1.5rem;flex-shrink:0}
.rol-info{flex:1;text-align:left}
.rol-nombre{font-size:1.2rem;font-weight:600;color:#333;margin:0 0 8px 0}
.rol-descripcion{color:#666;margin:0;font-size:.9rem;line-height:1.4}
.modal-footer{background:#f8f9fa;padding:20px 30px;border-top:1px solid #e0e0e0}
.footer-acciones{display:flex;justify-content:flex-end;gap:15px}
.form-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-bottom:16px}
.form-item{display:flex;flex-direction:column;gap:6px}
.label{font-size:.9rem;color:#555;font-weight:600}
.input{padding:10px 12px;border:2px solid #d1d5db;border-radius:8px;background:#fff;color:#333;font-size:.95rem}
.input:focus{outline:none;border-color:#0047ab;box-shadow:0 0 0 3px rgba(0,71,171,.15)}
.btn{display:inline-flex;align-items:center;gap:8px;padding:12px 24px;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s ease;text-decoration:none}
.btn--outline{background-color:transparent;color:#6c757d;border:2px solid #6c757d}
.btn--outline:hover{background-color:#6c757d;color:#fff}
@media (max-width:768px){.modal-content{margin:10px;max-height:95vh}.modal-body{padding:20px}.roles-grid{grid-template-columns:1fr}.rol-option{flex-direction:column;text-align:center;padding:20px}.footer-acciones{flex-direction:column}.btn{width:100%;justify-content:center}}
</style>


