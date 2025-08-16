<!-- src/components/formulario-actualizar-deportista.vue -->
<template>
  <form class="formulario-datos">
    <!-- Sección 1: Información Básica -->
    <section class="seccion-formulario" v-show="indiceActual === 0">
      <h3>Actualizar perfil</h3>

      <div class="fila-formulario">
        <input v-model="form.nombre1" type="text" placeholder="¿Cuál es su primer nombre?" required />
        <input v-model="form.nombre2" type="text" placeholder="¿Cuál es su segundo nombre?" />
        <input v-model="form.apellido1" type="text" placeholder="¿Cuál es su primer apellido?" required />
        <input v-model="form.apellido2" type="text" placeholder="¿Cuál es su segundo apellido?" />
      </div>

      <hr class="form-divider" />

      <div class="fila-formulario">
        <select v-model="form.tipoDocumento" required>
          <option value="" disabled>¿Cuál es su tipo de documento?</option>
          <option>Cédula</option>
          <option>Tarjeta de identidad</option>
          <option>Pasaporte</option>
        </select>
        <input v-model="form.numeroDocumento" type="text" placeholder="¿Cuál es su número de documento?" required />
      </div>

      <hr class="form-divider" />

      <div class="fila-formulario">
        <input v-model="form.fechaNacimiento" type="date" placeholder="¿En qué fecha nació?" required />
        <select v-model="form.genero" required>
          <option value="" disabled>¿Cuál es su género?</option>
          <option>Masculino</option>
          <option>Femenino</option>
        </select>
      </div>

      <hr class="form-divider" />

      <div class="fila-formulario">
        <input v-model="form.correo" type="text" placeholder="¿Cuál es su correo electrónico?" />
        <input v-model="form.telefono" type="text" placeholder="¿Cuál es su número telefónico?" />
      </div>

      <hr class="form-divider" />

      <div class="fila-formulario">
        <select v-model="form.ciudad" required>
          <option value="" disabled>¿Cuál es su ciudad de residencia?</option>
          <option>Retorno</option>
          <option>San Jose</option>
          <option>Otro</option>
        </select>
        <input v-model="form.direccion" type="text" placeholder="¿Cuál es su dirección de residencia?" />
      </div>

      <hr class="form-divider" />

      <div>
        <div class="fila-formulario">
          <input v-model="form.password" type="password" placeholder="Contraseña" />
          <input v-model="form.password2" type="password" placeholder="Confirmar contraseña" />
        </div>

        <hr class="form-divider" />

        <div class="botones-formulario" style="justify-content: center; gap: 10px;">
          <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguiente">Siguiente</button>
        </div>

        <hr class="form-divider" />
      </div>
    </section>

    <!-- Sección 2: Antecedentes Médicos -->
    <section class="seccion-formulario" v-show="indiceActual === 1">
      <h3>Antecedentes Médicos</h3>

      <div class="fila-formulario">
        <select v-model="form.eps" required>
          <option value="" disabled>¿A que EPS está afiliado?</option>
          <option>Nueva EPS</option>
          <option>PONAL</option>
          <option>Otro</option>
        </select>
      </div>

      <hr class="form-divider" />

      <div class="fila-formulario bloque-radio">
        <label>¿Existe algún tipo de recomendación médica que se deba tener presente para la actividad deportiva?</label>
        <div class="opciones">
          <input type="radio" id="reco-si" name="recomendacion-medica" value="si" v-model="form.recomendacionMedica" />
          <label for="reco-si">Sí</label>
          <input type="radio" id="reco-no" name="recomendacion-medica" value="no" v-model="form.recomendacionMedica" />
          <label for="reco-no">No</label>
        </div>

        <div class="campo-condicional" v-show="form.recomendacionMedica === 'si'">
          <label for="recomendacion-medica-texto">Describa la recomendación:</label>
          <textarea id="recomendacion-medica-texto" v-model="form.descripcionRecomendacion" placeholder="Escriba aquí..."></textarea>
        </div>
      </div>

      <hr class="form-divider" />

      <div class="fila-formulario">
        <select v-model="form.grupoSanguineo" required>
          <option value="" disabled>¿Cuál es su grupo sanguíneo?</option>
          <option>A+</option>
          <option>A-</option>
          <option>Otro</option>
        </select>
      </div>

      <hr class="form-divider" />

      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario anterior" style="width: 120px;" @click="anterior">Anterior</button>
        <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguiente">Siguiente</button>
      </div>

      <hr class="form-divider" />
    </section>

    <!-- Sección 3: Información Escolar -->
    <section class="seccion-formulario" v-show="indiceActual === 2">
      <h3>Información Escolar</h3>

      <div class="fila-formulario">
        <select v-model="form.institucion" required>
          <option value="" disabled>¿En qué institución educativa estudia actualmente?</option>
          <option>SENA</option>
          <option>SANTANDER</option>
          <option>Otro</option>
        </select>
      </div>

      <hr class="form-divider" />

      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario anterior" style="width: 120px;" @click="anterior">Anterior</button>
        <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguiente">Siguiente</button>
      </div>

      <hr class="form-divider" />
    </section>

    <!-- Sección 4: Información Deportiva -->
    <section class="seccion-formulario" v-show="indiceActual === 3">
      <h3>Información Deportiva</h3>

      <div class="bloque-radio">
        <label for="radio-deporte-si">¿Practica o ha practicado antes otro deporte además del voleibol?</label>
        <div class="opciones">
          <input type="radio" id="deporte-si" name="deporte" value="si" v-model="form.practicaOtroDeporte" />
          <label for="deporte-si">Sí</label>
          <input type="radio" id="deporte-no" name="deporte" value="no" v-model="form.practicaOtroDeporte" />
          <label for="deporte-no">No</label>
        </div>

        <div class="campo-condicional" v-show="form.practicaOtroDeporte === 'si'">
          <label for="deporte-texto">¿Cuál deporte?</label>
          <textarea id="deporte-texto" v-model="form.deporteCual" placeholder="Escriba aquí..."></textarea>
        </div>
      </div>

      <hr class="form-divider" />

      <div class="bloque-radio">
        <label for="escuela-si">¿Participa o ha participado en otras escuelas de formación?</label>
        <div class="opciones">
          <input type="radio" id="escuela-si" name="escuela-formacion" value="si" v-model="form.participaEscuela" />
          <label for="escuela-si">Sí</label>

          <input type="radio" id="escuela-no" name="escuela-formacion" value="no" v-model="form.participaEscuela" />
          <label for="escuela-no">No</label>
        </div>

        <div class="campo-condicional" v-show="form.participaEscuela === 'si'">
          <label for="escuela-texto">¿En cuál escuela ha participado?</label>
          <textarea id="escuela-texto" v-model="form.escuelaCual" placeholder="Escriba aquí..."></textarea>
        </div>
      </div>

      <hr class="form-divider" />

      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario anterior" style="width: 120px;" @click="anterior">Anterior</button>
        <button type="button" class="boton-formulario siguiente" style="width: 120px;" @click="siguiente">Siguiente</button>
      </div>

      <hr class="form-divider" />
    </section>

    <!-- Sección 5: Información del Acudiente -->
    <section class="seccion-formulario" v-show="indiceActual === 4">
      <h3>Información del Acudiente</h3>

      <div class="fila-formulario">
        <input v-model="form.acudienteNombre1" type="text" placeholder="¿Cuál es el primer nombre de su acudiente?" required />
        <input v-model="form.acudienteNombre2" type="text" placeholder="¿Cuál es el segundo nombre de su acudiente?" />
        <input v-model="form.acudienteApellido1" type="text" placeholder="¿Cuál es el primer apellido de su acudiente?" required />
        <input v-model="form.acudienteApellido2" type="text" placeholder="¿Cuál es el segundo apellido de su acudiente?" />
      </div>

      <hr class="form-divider" />

      <div class="fila-formulario fila-centro">
        <select v-model="form.parentesco" required>
          <option value="" disabled>¿Qué parentesco tienen?</option>
          <option>Padre</option>
          <option>Madre</option>
          <option>Hermano</option>
          <option>Otro</option>
        </select>
      </div>

      <hr class="form-divider" />

      <div class="fila-formulario">
        <input v-model="form.acudienteFechaNac" type="date" placeholder="¿En qué fecha nació el acudiente?" required />
      </div>

      <hr class="form-divider" />

      <div class="fila-formulario">
        <select v-model="form.acudienteTipoDoc" required>
          <option value="" disabled>¿Cuál es el tipo de documento de su acudiente?</option>
          <option>Cédula</option>
          <option>Contraseña</option>
          <option>Pasaporte</option>
        </select>
        <input v-model="form.acudienteNumeroDoc" type="text" placeholder="¿Cuál es el número de documento de su acudiente?" required />
      </div>

      <hr class="form-divider" />

      <div class="fila-formulario">
        <input v-model="form.acudienteCorreo" type="text" placeholder="¿Cuál es el correo electrónico de su acudiente?" />
        <input v-model="form.acudienteTelefono" type="text" placeholder="¿Cuál es el número telefónico de su acudiente?" />
      </div>

      <hr class="form-divider" />

      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario anterior" style="width: 120px;" @click="anterior">Anterior</button>
      </div>

      <hr class="form-divider" />

      <div class="botones-formulario" style="justify-content: center; gap: 10px;">
        <button type="button" class="boton-formulario" style="width: 120px;" @click="aceptar">Aceptar actualización</button>
        <button type="button" class="boton-formulario" style="width: 120px;" @click="cancelar">Cancelar actualización</button>
      </div>
    </section>
  </form>
</template>

<script setup>
import { ref } from "vue";

const indiceActual = ref(0);
const totalSecciones = 5;

const form = ref({
  // Básicos
  nombre1: "", nombre2: "", apellido1: "", apellido2: "",
  tipoDocumento: "", numeroDocumento: "",
  fechaNacimiento: "", genero: "",
  correo: "", telefono: "",
  ciudad: "", direccion: "",
  password: "", password2: "",

  // Médicos
  eps: "", grupoSanguineo: "",
  recomendacionMedica: "", descripcionRecomendacion: "",

  // Escolar
  institucion: "",

  // Deportivos
  practicaOtroDeporte: "", deporteCual: "",
  participaEscuela: "", escuelaCual: "",

  // Acudiente
  acudienteNombre1: "", acudienteNombre2: "",
  acudienteApellido1: "", acudienteApellido2: "",
  parentesco: "", acudienteFechaNac: "",
  acudienteTipoDoc: "", acudienteNumeroDoc: "",
  acudienteCorreo: "", acudienteTelefono: ""
});

function siguiente() {
  if (indiceActual.value < totalSecciones - 1) indiceActual.value++;
}
function anterior() {
  if (indiceActual.value > 0) indiceActual.value--;
}

function aceptar() {
  console.log("Formulario listo para enviar:", form.value);
  alert("Datos listos para enviar (revisa consola).");
}
function cancelar() {
  indiceActual.value = 0;
}
</script>
