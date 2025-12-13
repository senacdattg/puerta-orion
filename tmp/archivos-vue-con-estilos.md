# Archivos Vue que Aún Tienen Estilos CSS

## 📊 Resumen Total

**Total de archivos con estilos:** 13 archivos

---

## ✅ Archivos con Estilos VACÍOS (Solo comentarios o vacíos)

Estos archivos tienen bloques `<style>` pero están vacíos o solo tienen comentarios. **Pueden eliminarse directamente:**

1. **`components/admin/tabla-datos-dinamicos.vue`** (línea 287)
   - `<style scoped>` → **VACÍO** ✅ Eliminar

2. **`views/forgot-password.vue`** (línea 188)
   - `<style scoped>` → **VACÍO** ✅ Eliminar

3. **`components/admin/admin-dashboard.vue`** (línea 51)
   - `<style scoped>` → Solo comentario: `/* Los estilos están en /assets/css/dashboards.css */` ✅ Eliminar

4. **`views/mensualidades.vue`** (línea 257)
   - `<style>` → Solo import: `@import '../assets/css/mensualidades.css';` ⚠️ **Mover import a script o eliminar** (el import en CSS no funciona en `<style>` de Vue)

---

## 📝 Archivos con Estilos PEQUEÑOS (Fácil de mover)

Estos tienen estilos simples que se pueden mover fácilmente:

5. **`components/datos-dinamicos/sexo.vue`** (línea 61)
   - **Estilos:** `.campo-nombre-centrado` (7 líneas)
   - **Destino:** `shared/components.css` o `formulario.css`
   - **Dificultad:** ⭐ Fácil

6. **`components/datos-dinamicos/ciudad.vue`** (línea 61)
   - **Estilos:** `.campo-nombre-centrado` (7 líneas) - **DUPLICADO de sexo.vue**
   - **Destino:** `shared/components.css` o `formulario.css`
   - **Dificultad:** ⭐ Fácil

7. **`components/datos-dinamicos/tipo-documento.vue`** (línea 56)
   - **Estilos:** `.campo-nombre-centrado` (7 líneas) - **DUPLICADO de sexo.vue**
   - **Destino:** `shared/components.css` o `formulario.css`
   - **Dificultad:** ⭐ Fácil

8. **`components/datos-dinamicos/eps.vue`** (línea 114)
   - **Estilos:** `.campo-nombre-centrado` (7 líneas) - **DUPLICADO de sexo.vue**
   - **Destino:** `shared/components.css` o `formulario.css`
   - **Dificultad:** ⭐ Fácil

9. **`components/datos-dinamicos/tipo-evento.vue`** (línea 94)
   - **Estilos:** `.fila-texto` (18 líneas)
   - **Destino:** `formulario.css`
   - **Dificultad:** ⭐ Fácil

10. **`components/roles/roles-usurio.vue`** (línea 108)
    - **Estilos:** `.selector-rol`, `.label`, `.select-rol` (3 líneas)
    - **Destino:** `roles.css` o `components/layout.css`
    - **Dificultad:** ⭐ Fácil

---

## 🔧 Archivos con Estilos MEDIANOS (Requieren más atención)

11. **`components/admin/modal-registro-usuario.vue`** (línea 85)
    - **Estilos:** ~255 líneas
    - **Contenido:** Estilos de modal, formulario, botones, responsive
    - **Destino:** `modales.css` (consolidar con otros modales)
    - **Dificultad:** ⭐⭐ Media
    - **Nota:** Tiene valores hardcodeados que deben reemplazarse por variables

12. **`components/galeria/galeria.vue`** (línea 607)
    - **Estilos:** ~388 líneas
    - **Contenido:** Estilos de galería, tarjetas, botones, modales, formularios
    - **Destino:** `galeria.css` (ya existe, consolidar aquí)
    - **Dificultad:** ⭐⭐ Media
    - **Nota:** Tiene valores hardcodeados que deben reemplazarse por variables

---

## 📋 Plan de Acción Recomendado

### **Fase 1: Eliminar Estilos Vacíos (5 minutos)**
1. ✅ `tabla-datos-dinamicos.vue` - Eliminar `<style scoped>` vacío
2. ✅ `forgot-password.vue` - Eliminar `<style scoped>` vacío
3. ✅ `admin-dashboard.vue` - Eliminar `<style scoped>` con solo comentario
4. ✅ `mensualidades.vue` - Eliminar `<style>` con import (mover import a `main.js` si es necesario)

### **Fase 2: Consolidar Estilos Duplicados (15 minutos)**
5. ✅ Crear clase común `.campo-nombre-centrado` en `shared/components.css`
6. ✅ Eliminar estilos de: `sexo.vue`, `ciudad.vue`, `tipo-documento.vue`, `eps.vue`
7. ✅ Mover `.fila-texto` de `tipo-evento.vue` a `formulario.css`
8. ✅ Mover estilos de `roles-usurio.vue` a `roles.css`

### **Fase 3: Consolidar Estilos Medianos (30-45 minutos)**
9. ✅ Mover estilos de `modal-registro-usuario.vue` a `modales.css`
10. ✅ Mover estilos de `galeria.vue` a `galeria.css`

---

## 🎯 Mapeo Específico: Dónde Va Cada Estilo

| Archivo Vue | Estilos | Destino CSS | Prioridad |
|-------------|--------|-------------|-----------|
| `tabla-datos-dinamicos.vue` | Vacío | ❌ Eliminar | 🔴 Alta |
| `forgot-password.vue` | Vacío | ❌ Eliminar | 🔴 Alta |
| `admin-dashboard.vue` | Solo comentario | ❌ Eliminar | 🔴 Alta |
| `mensualidades.vue` | Solo import | ❌ Eliminar (mover import) | 🔴 Alta |
| `sexo.vue` | `.campo-nombre-centrado` | `shared/components.css` | 🟡 Media |
| `ciudad.vue` | `.campo-nombre-centrado` | `shared/components.css` | 🟡 Media |
| `tipo-documento.vue` | `.campo-nombre-centrado` | `shared/components.css` | 🟡 Media |
| `eps.vue` | `.campo-nombre-centrado` | `shared/components.css` | 🟡 Media |
| `tipo-evento.vue` | `.fila-texto` | `formulario.css` | 🟡 Media |
| `roles-usurio.vue` | `.selector-rol`, `.select-rol` | `roles.css` | 🟡 Media |
| `modal-registro-usuario.vue` | ~255 líneas | `modales.css` | 🟢 Baja |
| `galeria.vue` | ~388 líneas | `galeria.css` | 🟢 Baja |

---

## 💡 Recomendación de Orden

1. **Primero:** Eliminar los 4 archivos con estilos vacíos (rápido, sin riesgo)
2. **Segundo:** Consolidar los 5 componentes de datos-dinamicos (fácil, reutilización)
3. **Tercero:** Mover `roles-usurio.vue` (fácil)
4. **Cuarto:** Mover `modal-registro-usuario.vue` (requiere más cuidado)
5. **Quinto:** Mover `galeria.vue` (requiere más cuidado)

---

## ⚠️ Notas Importantes

1. **`mensualidades.vue`:** El `@import` en `<style>` de Vue NO funciona. Si necesitas importar CSS, hazlo en el `<script>` con `import '@/assets/css/mensualidades.css'` o en `main.js`.

2. **Estilos duplicados:** Los 4 componentes de datos-dinamicos tienen el mismo estilo `.campo-nombre-centrado`. Crear una clase común en `shared/components.css`.

3. **Valores hardcodeados:** `modal-registro-usuario.vue` y `galeria.vue` tienen valores hardcodeados (`#0047ab`, `#6c757d`, etc.) que deberían reemplazarse por variables después de moverlos.

4. **Especificidad:** Al mover estilos scoped a CSS global, asegúrate de usar prefijos específicos para evitar conflictos (ej: `.modal-registro-` en lugar de `.modal-` genérico).

