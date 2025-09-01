# Estructura CSS Modular - PUERTA ORION

## 📁 Organización de Archivos

```
css/
├── base/
│   └── variables.css          # Variables CSS globales y clases utilitarias
├── components/
│   └── botones.css            # Estilos de botones reutilizables
├── deportistas-modern.css     # Estilos específicos para la vista de deportistas
├── deportistas.css            # Estilos legacy (a mantener por compatibilidad)
└── README.md                  # Este archivo
```

## 🎯 Principios Aplicados

### 1. **SRP (Single Responsibility Principle)**
- Cada archivo CSS tiene una responsabilidad específica
- `variables.css`: Solo variables y clases utilitarias
- `botones.css`: Solo estilos de botones
- `deportistas-modern.css`: Solo estilos de la vista de deportistas

### 2. **DRY (Don't Repeat Yourself)**
- Variables CSS centralizadas en `variables.css`
- Clases de botones reutilizables en `components/botones.css`
- Importaciones para evitar duplicación de código

### 3. **KISS (Keep It Simple, Stupid)**
- Estructura clara y fácil de entender
- Nombres de clases descriptivos y consistentes
- Separación lógica de responsabilidades

## 🚀 Uso

### Importar Variables Base
```css
@import './base/variables.css';
```

### Importar Componentes
```css
@import './components/botones.css';
```

### Usar Variables CSS
```css
.mi-clase {
  background-color: var(--color-primario);
  padding: var(--espaciado-lg);
  border-radius: var(--radio-borde);
}
```

### Usar Clases Utilitarias
```html
<div class="d-flex justify-center align-center p-4">
  <button class="btn btn-primary btn-lg">Botón Grande</button>
</div>
```

## 🎨 Sistema de Colores

- **Primario**: `#0047ab` (Azul)
- **Secundario**: `#f4d800` (Amarillo)
- **Éxito**: `#28a745` (Verde)
- **Peligro**: `#dc3545` (Rojo)
- **Info**: `#17a2b8` (Azul claro)
- **Advertencia**: `#ffc107` (Amarillo)

## 📱 Responsive Design

- **Mobile First**: Diseño optimizado para móviles
- **Breakpoints**: 576px, 768px, 992px, 1200px, 1400px
- **Clases utilitarias**: `.d-md-none`, `.d-sm-flex`, etc.

## 🔧 Mantenimiento

### Agregar Nuevas Variables
1. Editar `base/variables.css`
2. Usar en los archivos específicos
3. Documentar cambios

### Crear Nuevos Componentes
1. Crear archivo en `components/`
2. Seguir la nomenclatura establecida
3. Importar en los archivos que lo necesiten

### Modificar Estilos Existentes
1. Identificar el archivo correcto
2. Hacer cambios mínimos y específicos
3. Verificar que no se rompa la consistencia

## 📋 Convenciones de Nomenclatura

- **Variables**: `--color-primario`, `--espaciado-lg`
- **Clases**: `.btn-primary`, `.tarjeta-deportista`
- **Estados**: `.estado-activo`, `.estado-inactivo`
- **Responsive**: `.d-md-none`, `.d-sm-flex`

## 🎯 Beneficios

1. **Mantenibilidad**: Fácil de modificar y actualizar
2. **Reutilización**: Componentes que se pueden usar en múltiples vistas
3. **Consistencia**: Diseño uniforme en toda la aplicación
4. **Escalabilidad**: Fácil agregar nuevos estilos y componentes
5. **Performance**: CSS optimizado y organizado
