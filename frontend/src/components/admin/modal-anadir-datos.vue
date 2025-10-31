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

      <div class="modal-body">
        <div class="seleccion-rol">
          <h3 class="paso-titulo">Selecciona el tipo de dato a gestionar</h3>
          <p class="paso-descripcion">Elige una categoría para crear o administrar datos base del sistema</p>

          <div class="roles-grid">
            <div
              v-for="item in items"
              :key="item.id"
              class="rol-option"
              @click="abrirSeccion(item)"
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

      <div class="modal-footer">
        <div class="footer-acciones">
          <button class="btn btn--outline" @click="cerrar">Cancelar</button>
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

const emit = defineEmits(['cerrar'])

const items = ref([
  { id: 'tipo_documento', nombre: 'Tipos de Documento', icono: 'fas fa-id-card', descripcion: 'Gestiona los tipos de documento' },
  { id: 'sexo', nombre: 'Sexo', icono: 'fas fa-venus-mars', descripcion: 'Gestiona valores de sexo' },
  { id: 'categoria', nombre: 'Categorías', icono: 'fas fa-layer-group', descripcion: 'Gestiona categorías deportivas' },
  { id: 'ciudad', nombre: 'Ciudades', icono: 'fas fa-city', descripcion: 'Gestiona ciudades de residencia' },
  { id: 'eps', nombre: 'EPS', icono: 'fas fa-hospital', descripcion: 'Gestiona entidades de salud' },
  { id: 'metodo_pago', nombre: 'Métodos de Pago', icono: 'fas fa-money-check-alt', descripcion: 'Gestiona métodos de pago' }
])

function cerrar() {
  emit('cerrar')
}

function abrirSeccion(item) {
  // Por ahora solo notifica; en el futuro puede navegar o abrir sub-formularios
  alert(`Abrir gestión para: ${item.nombre}`)
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
.rol-icono{width:60px;height:60px;background:linear-gradient(135deg,#0047ab 0%,#0d47a1 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:1.5rem;flex-shrink:0}
.rol-info{flex:1;text-align:left}
.rol-nombre{font-size:1.2rem;font-weight:600;color:#333;margin:0 0 8px 0}
.rol-descripcion{color:#666;margin:0;font-size:.9rem;line-height:1.4}
.modal-footer{background:#f8f9fa;padding:20px 30px;border-top:1px solid #e0e0e0}
.footer-acciones{display:flex;justify-content:flex-end;gap:15px}
.btn{display:inline-flex;align-items:center;gap:8px;padding:12px 24px;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s ease;text-decoration:none}
.btn--outline{background-color:transparent;color:#6c757d;border:2px solid #6c757d}
.btn--outline:hover{background-color:#6c757d;color:#fff}
@media (max-width:768px){.modal-content{margin:10px;max-height:95vh}.modal-body{padding:20px}.roles-grid{grid-template-columns:1fr}.rol-option{flex-direction:column;text-align:center;padding:20px}.footer-acciones{flex-direction:column}.btn{width:100%;justify-content:center}}
</style>


