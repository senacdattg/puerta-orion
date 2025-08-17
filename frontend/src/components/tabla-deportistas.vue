<template>
    <div class="tabla-deportistas">
      <div class="contenedor-principal">
        <!-- Buscador -->
        <div class="contenedor-busqueda">
          <input
            type="search"
            v-model="busqueda"
            placeholder="Search..."
            class="entrada-busqueda-circular"
          />
        </div>
  
        <!-- Tabla -->
        <div class="contenedor-secundario">
          <div class="tarjeta-tabla">
            <table>
              <thead>
                <tr>
                  <th>Columna 1</th>
                  <th>Columna 2</th>
                  <th>Columna 3</th>
                  <th>Columna 4</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(fila, index) in filasFiltradas" :key="index">
                  <td>{{ fila.col1 }}</td>
                  <td>{{ fila.col2 }}</td>
                  <td>{{ fila.col3 }}</td>
                  <td>{{ fila.col4 }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "TablaDeportistas",
    data() {
      return {
        busqueda: "",
        filas: [
          { col1: "Dato 1", col2: "Dato 2", col3: "Dato 3", col4: "Dato 4" },
          { col1: "Dato 5", col2: "Dato 6", col3: "Dato 7", col4: "Dato 8" }
        ]
      };
    },
    computed: {
      filasFiltradas() {
        if (!this.busqueda) return this.filas;
        return this.filas.filter(fila =>
          Object.values(fila).some(valor =>
            valor.toLowerCase().includes(this.busqueda.toLowerCase())
          )
        );
      }
    }
  };
  </script>
  