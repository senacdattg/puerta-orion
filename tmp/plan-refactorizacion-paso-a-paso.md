# Plan de Refactorización CSS - Paso a Paso (Seguro)

## 🎯 Objetivo: Refactorizar sin romper estilos

## 📋 Mapeo: Dónde van los estilos de Vue

### **Regla general:**
- **Vista (views/)** → Archivos CSS por funcionalidad
- **Componente reutilizable (components/)** → `components/` o `shared/`
- **Componente de layout (components/layout/)** → `components/layout.css` (crear)

### **Mapeo específico:**

#### **Views (Páginas) → CSS:**

| Vista | Archivo CSS Destino | Notas |
|-------|---------------------|-------|
| `views/perfil.vue` | `perfiles.css` | Ya existe, consolidar aquí |
| `views/actualizar-info.vue` | `perfiles.css` | Consolidar estilos de actualización |
| `views/completar-perfil.vue` | `perfiles.css` | Consolidar estilos de completar |
| `views/eventos.vue` | `calendario.css` | Consolidar estilos de eventos |
| `views/calendario.vue` | `calendario.css` | Ya existe |
| `views/mensualidades.vue` | `mensualidades.css` | Ya existe |
| `views/login.vue` | `login.css` | Ya existe |
| `views/forgot-password.vue` | `login.css` | Usar estilos compartidos |
| `views/reset-password.vue` | `login.css` | Usar estilos compartidos |
| `views/Inicio.vue` | `inicio.css` | Ya existe |
| `views/vista-deportistas.vue` | `deportistas.css` | Ya existe |
| `views/ver-acudidos.vue` | `deportistas.css` | Consolidar estilos de acudidos |
| `views/AcudienteDashboard.vue` | `dashboards.css` | Ya existe |
| `views/DeportistaDashboard.vue` | `deportista-dashboard.css` | Ya existe |
| `views/admin-manager.vue` | `panel-admin.css` | Ya existe |
| `views/formulario-acudiente-completo.vue` | `formulario.css` | Ya existe |
| `views/formulario-deportista-completo.vue` | `formulario.css` | Consolidar |
| `views/registrar-acudiente.vue` | `formulario.css` | Consolidar |
| `views/registrar-deportista.vue` | `formulario.css` | Consolidar |
| `views/registrar-general.vue` | `formulario.css` | Consolidar |
| `views/roles-registro-vista.vue` | `roles.css` | Ya existe |
| `views/galeria-vista.vue` | `galeria.css` | Ya existe |

#### **Components → CSS:**

| Componente | Archivo CSS Destino | Notas |
|-----------|---------------------|-------|
| `components/layout/encabezado.vue` | `components/layout.css` | **CREAR** este archivo |
| `components/layout/pie.vue` | `components/layout.css` | Consolidar aquí |
| `components/layout/selector-roles.vue` | `components/layout.css` o `roles.css` | Layout común |
| `components/layout/DashboardHome.vue` | `dashboards.css` | Ya existe |
| `components/admin/tabla-usuarios.vue` | `panel-admin.css` | Consolidar estilos de tabla |
| `components/admin/panel-admin-componente.vue` | `panel-admin.css` | Ya existe |
| `components/admin/tabla-datos-dinamicos.vue` | `panel-admin.css` | Consolidar estilos de tabla |
| `components/admin/lista-mensualidades.vue` | `mensualidades.css` | Consolidar |
| `components/admin/modal-*.vue` | `modales.css` | Ya existe, consolidar |
| `components/deportistas/*.vue` | `deportistas.css` | Ya existe, consolidar |
| `components/formularios/*.vue` | `formulario.css` | Ya existe, consolidar |
| `components/roles/*.vue` | `roles.css` | Ya existe, consolidar |
| `components/ui/*.vue` | `shared/components.css` | Componentes UI genéricos |

---

## 🚀 Fase 1: Eliminar Variables Duplicadas (SIN TOCAR ESTILOS)

### **Paso 1.1: Agregar variables faltantes a `base/variables.css`**

Agregar estas variables que se usan pero no están definidas:

```css
/* En base/variables.css, agregar: */

/* Variantes de color secundario */
--color-secundario-oro: #FFD700;      /* Unificar #FFD700 */
--color-borde-primario: #0d47a1;      /* Variante más oscura */
--color-fondo-seccion: #f6f7fb;       /* Fondo común de secciones */

/* Espaciados específicos */
--espaciado-tarjeta: 1.5rem;          /* Padding común de tarjetas */
--espaciado-seccion: 2rem;            /* Espaciado entre secciones */

/* Sombras específicas */
--sombra-tarjeta: 0 4px 20px rgba(0, 0, 0, 0.1);
--sombra-tarjeta-hover: 0 8px 30px rgba(0, 0, 0, 0.15);

/* Bordes específicos */
--borde-tarjeta: 2px solid var(--color-primario);
--borde-tarjeta-secundario: 3px solid var(--color-primario);
```

### **Paso 1.2: Reemplazar variables duplicadas en `shared/components.css`**

**Antes:**
```css
/* shared/components.css */
:root {
  --color-primario: #0047ab;
  /* ... variables duplicadas ... */
}
```

**Después:**
```css
/* shared/components.css */
@import '../base/variables.css';

/* Ya no necesita definir :root, usar las de variables.css */
```

### **Paso 1.3: Reemplazar variables duplicadas en `inicio.css`**

**Antes:**
```css
/* inicio.css */
:root {
  --primary-color: #0047ab;
  --secondary-color: #f7d600;
  /* ... variables duplicadas ... */
}
```

**Después:**
```css
/* inicio.css */
@import './base/variables.css';

/* Usar variables de base/variables.css:
   --primary-color → var(--color-primario)
   --secondary-color → var(--color-secundario)
*/
```

### **Paso 1.4: Reemplazar variables duplicadas en `mensualidades.css`**

**Antes:**
```css
/* mensualidades.css */
:root {
  --color-primario: #0047ab;
  /* ... variables duplicadas ... */
}
```

**Después:**
```css
/* mensualidades.css */
@import './base/variables.css';
@import './listados.css';

/* Eliminar bloque :root duplicado */
```

**✅ Resultado Fase 1:** Todas las variables vienen de un solo lugar, sin cambiar estilos visibles

---

## 🔧 Fase 2: Reemplazar Valores Hardcodeados (GRADUAL, un archivo a la vez)

### **Paso 2.1: `main.css` - Reemplazar colores hardcodeados**

**Buscar y reemplazar:**
- `#0047ab` → `var(--color-primario)`
- `#f4d800` o `#FFD700` → `var(--color-secundario)` o `var(--color-secundario-oro)`
- `#ffffff` → `var(--color-blanco)`
- `#f8f9fa` → `var(--color-gris-claro)`
- `#6c757d` → `var(--color-gris)`
- `0 4px 20px rgba(0, 0, 0, 0.1)` → `var(--sombra-media)`

**Probar después de cada archivo:** Verificar que no se rompa el diseño

### **Paso 2.2: `perfiles.css` - Reemplazar colores hardcodeados**

Mismo proceso que `main.css`

### **Paso 2.3: `panel-admin.css` - Reemplazar colores hardcodeados**

Mismo proceso

### **Paso 2.4: Resto de archivos - Uno por uno**

Seguir el mismo patrón en todos los archivos CSS

**✅ Resultado Fase 2:** Todos los valores vienen de variables, fácil cambiar colores

---

## 📦 Fase 3: Crear Archivo para Layout (NUEVO)

### **Paso 3.1: Crear `components/layout.css`**

Extraer estilos comunes de:
- `components/layout/encabezado.vue`
- `components/layout/pie.vue`
- `components/layout/selector-roles.vue`
- `main.css` (estilos de encabezado, pie, menús)

**Estructura:**
```css
/* components/layout.css */
@import '../base/variables.css';

/* ===== ENCABEZADO ===== */
.encabezado { }
.encabezado-header { }
.menu-toggle { }
.menu-categorias { }

/* ===== PIE/FOOTER ===== */
.footer { }
.footer-enhanced { }
.footer-content { }

/* ===== SELECTOR DE ROLES ===== */
.selector-roles { }
.selector-roles-content { }
```

### **Paso 3.2: Importar en `main.js`**

```javascript
import '@/assets/css/components/layout.css'
```

### **Paso 3.3: Eliminar estilos duplicados de `main.css`**

**✅ Resultado Fase 3:** Layout separado, más organizado

---

## 🎨 Fase 4: Crear Componentes Reutilizables (OPCIONAL, gradual)

### **Paso 4.1: Crear `components/cards.css`**

Extraer estilos comunes de tarjetas:
- `deportistas.css` → `.tarjeta-deportista`
- `perfiles.css` → `.tarjeta-perfil`
- `panel-admin.css` → `.stat-card`
- `tarjetas.css` → todos

**Estructura:**
```css
/* components/cards.css */
@import '../base/variables.css';

/* Clase base común */
.card {
  background: var(--color-blanco);
  border-radius: var(--radio-borde);
  padding: var(--espaciado-tarjeta);
  box-shadow: var(--sombra-tarjeta);
  transition: var(--transicion);
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: var(--sombra-tarjeta-hover);
}

/* Modificadores específicos */
.card--profile { }
.card--deportista { }
.card--stat { }
```

### **Paso 4.2: Usar en archivos CSS existentes**

No reemplazar inmediatamente, ir gradualmente:
1. Agregar nuevas clases que usen `.card`
2. Mantener clases antiguas funcionando
3. Migrar gradualmente

**✅ Resultado Fase 4:** Menos duplicación

---

## 📝 Fase 5: Extraer Estilos de Vue (GRADUAL, uno por uno)

### **Estrategia segura:**

1. **No eliminar estilos scoped de inmediato**
2. **Agregar estilos a CSS primero**
3. **Probar que funciona igual**
4. **Luego eliminar estilos scoped del Vue**

### **Ejemplo: `views/perfil.vue`**

**Paso 5.1:** Copiar estilos scoped de `perfil.vue` a `perfiles.css`

**Paso 5.2:** Agregar prefijo específico para evitar conflictos:
```css
/* perfiles.css */
/* Estilos específicos de perfil.vue */
.perfil-page { }  /* Prefijo para identificar */
.perfil-container { }
.perfil-header { }
```

**Paso 5.3:** Probar que funciona igual

**Paso 5.4:** Eliminar bloque `<style scoped>` de `perfil.vue`

**Repetir para cada componente uno por uno**

---

## ✅ Checklist de Seguridad

Antes de hacer cambios:
- [ ] Hacer backup o commit actual
- [ ] Probar en navegador que funciona
- [ ] Verificar que no hay errores de consola
- [ ] Comparar visualmente antes/después

Después de cada cambio:
- [ ] Probar en navegador
- [ ] Verificar responsive (móvil, tablet, desktop)
- [ ] Verificar que no hay errores de consola
- [ ] Commit si funciona correctamente

---

## 🎯 Orden Recomendado de Implementación

### **Semana 1: Fundación (Sin riesgo)**
1. ✅ Fase 1: Eliminar variables duplicadas (Paso 1.1 - 1.4)
2. ✅ Probar que todo funciona igual
3. ✅ Commit

### **Semana 2: Reemplazar Hardcodeados (Riesgo bajo)**
4. ✅ Fase 2: Reemplazar valores hardcodeados (Paso 2.1 - 2.4)
5. ✅ Probar después de cada archivo
6. ✅ Commit después de cada archivo

### **Semana 3: Organizar Layout (Riesgo medio)**
7. ✅ Fase 3: Crear `components/layout.css`
8. ✅ Extraer estilos de layout de `main.css`
9. ✅ Probar que layout funciona igual
10. ✅ Commit

### **Semana 4+: Extraer de Vue (Riesgo medio-alto)**
11. ✅ Fase 5: Extraer estilos de Vue (uno por uno)
12. ✅ Probar después de cada componente
13. ✅ Commit después de cada componente

### **Opcional: Componentes reutilizables (Riesgo bajo)**
14. ✅ Fase 4: Crear `components/cards.css` cuando tengas tiempo
15. ✅ Migrar gradualmente

---

## 🔍 Cómo Verificar que No Se Rompió Nada

### **Después de cada cambio:**
1. Abrir navegador en diferentes rutas
2. Verificar estilos visualmente
3. Probar responsive (F12 → toggle device toolbar)
4. Verificar consola del navegador (F12 → Console)
5. Verificar Network tab (que no haya errores 404 de CSS)

### **Testing rápido:**
```bash
# En frontend/
npm run build  # Verificar que compila
npm run dev    # Verificar en navegador
```

---

## 📚 Documentación de Referencia

### **Dónde buscar estilos:**
- **Variable no encontrada?** → `base/variables.css`
- **Estilo de tarjeta?** → `components/cards.css` (cuando exista) o archivo específico
- **Estilo de layout?** → `components/layout.css` (cuando exista) o `main.css`
- **Estilo de vista?** → Archivo CSS con mismo nombre (ej: `perfil.vue` → `perfiles.css`)

### **Nomenclatura propuesta:**
- **Páginas:** `.nombre-pagina-page` (ej: `.perfil-page`, `.eventos-page`)
- **Containers:** `.nombre-pagina-container` (ej: `.perfil-container`)
- **Componentes reutilizables:** `.componente-nombre` (ej: `.card`, `.btn`)
- **Modificadores:** `.base--modificador` (ej: `.card--profile`)

---

## 🚨 Si Algo Se Rompe

### **Rollback inmediato:**
```bash
git checkout HEAD -- frontend/src/assets/css/
# O recuperar del backup
```

### **Debug:**
1. Abrir DevTools (F12)
2. Verificar qué estilos se están aplicando
3. Verificar si hay errores de CSS (rojo en console)
4. Verificar si hay conflictos de especificidad
5. Agregar `!important` temporal si es necesario (luego arreglar)

---

## 💡 Tips Finales

1. **Hacer cambios pequeños:** Un archivo a la vez
2. **Probar frecuentemente:** Después de cada cambio
3. **Commits frecuentes:** Commit después de cada archivo que funcione
4. **No tener prisa:** Mejor lento y seguro que rápido y roto
5. **Pedir ayuda:** Si algo no funciona, volver atrás

