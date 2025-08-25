<template>
    <main class="tabla-mensualidades">
      <div class="contenedor">
        <div class="titulo">
          <h1>Mensualidades</h1>
        </div>
  
        <div class="contenido-principal">
          <div class="secciones">
  
            <!-- Filtro -->
            <div class="filtro">
              <h2 class="subtitulo">Filtrar Deportistas</h2>
              <input
                type="text"
                v-model="filtroNombre"
                placeholder="Nombre del deportista"
                class="input"
              />
              <textarea
                v-model="comentario"
                placeholder="Comentarios..."
                rows="5"
                class="textarea"
              ></textarea>
            </div>
  
            <!-- Historial -->
            <div class="historial">
              <div class="caja-historial">
                <h2 class="subtitulo">Historial de Pagos</h2>
                <table class="tabla">
                  <thead>
                    <tr>
                      <th>Nombre</th>
                      <th>Mes</th>
                      <th>Valor</th>
                      <th>Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(pago, index) in pagosFiltrados"
                      :key="index"
                      @click="mostrarPopup(pago)"
                    >
                      <td>{{ pago.nombre }}</td>
                      <td>{{ pago.mes }}</td>
                      <td>{{ pago.valor }}</td>
                      <td :class="pago.estado === 'Pagado' ? 'estado-pagado' : 'estado-pendiente'">
                        {{ pago.estado }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
  
          </div>
        </div>
  
        <!-- Popup -->
        <div v-if="popupVisible" class="popup">
          <div class="popup-contenido">
            <h3>Detalle del Pago</h3>
            <p><strong>Nombre:</strong> {{ popupData.nombre }}</p>
            <p><strong>Mes:</strong> {{ popupData.mes }}</p>
            <p><strong>Valor:</strong> {{ popupData.valor }}</p>
            <p><strong>Estado:</strong> {{ popupData.estado }}</p>
            <button @click="cerrarPopup">Cerrar</button>
          </div>
        </div>
      </div>
    </main>
  </template>
  
  <script>
  export default {
    name: "Mensualidades",
    data() {
      return {
        filtroNombre: "",
        comentario: "",
        pagos: [
          { nombre: "Juan Pérez", mes: "Julio", valor: "$80.000", estado: "Pagado" },
          { nombre: "Ana Gómez", mes: "Julio", valor: "$80.000", estado: "Pendiente" },
          { nombre: "Luis Torres", mes: "Agosto", valor: "$90.000", estado: "Pagado" }
        ],
        popupVisible: false,
        popupData: {}
      };
    },
    computed: {
      pagosFiltrados() {
        if (!this.filtroNombre) return this.pagos;
        return this.pagos.filter(p =>
          p.nombre.toLowerCase().includes(this.filtroNombre.toLowerCase())
        );
      }
    },
    methods: {
      mostrarPopup(pago) {
        this.popupData = pago;
        this.popupVisible = true;
      },
      cerrarPopup() {
        this.popupVisible = false;
      }
    }
  };
  </script>