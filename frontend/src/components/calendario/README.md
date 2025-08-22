# Componente de Calendario

## Descripción
Este componente implementa un calendario completo para la gestión de entrenamientos y eventos deportivos, siguiendo los principios de diseño SOLID y las mejores prácticas de Vue.js.

## Principios Aplicados

### 1. **SRP (Single Responsibility Principle)**
- **CalendarioComponent**: Responsable únicamente de la interfaz del calendario
- **CalendarioService**: Maneja toda la lógica de negocio y persistencia de datos
- **EstadisticasCalendario**: Se encarga solo de mostrar estadísticas y filtros

### 2. **URLs Amigables**
- Ruta implementada: `/calendario`
- Navegación intuitiva y SEO-friendly

### 3. **KISS (Keep It Simple, Stupid)**
- Interfaz limpia y fácil de usar
- Funcionalidades esenciales sin complejidad innecesaria
- Código legible y mantenible

## Estructura de Archivos

```
calendario/
├── calendario-component.vue      # Componente principal del calendario
├── README.md                     # Esta documentación
└── calendarioService.js         # Servicio de lógica de negocio

CSS Modulares:
├── calendario-index.css         # Archivo índice que centraliza todas las importaciones
├── calendario.css               # Estilos base del calendario (grid, celdas)
├── vista-calendario.css         # Estilos de la vista principal
├── botones-calendario.css       # Estilos de botones y navegación
└── modal.css                    # Estilos del modal de eventos
```

## Funcionalidades

### Calendario Principal
- Visualización mensual del calendario
- Navegación entre meses
- Resaltado del día actual
- Visualización de eventos por día
- Modal para crear/editar eventos

### Gestión de Eventos
- **Crear**: Nuevos entrenamientos, eventos o competencias
- **Editar**: Modificar eventos existentes
- **Eliminar**: Remover eventos del calendario
- **Validación**: Verificación completa de datos incluyendo fecha obligatoria
- **Campo de Fecha**: Input de fecha visible en el formulario
- **Etiquetas Descriptivas**: Cada campo tiene su etiqueta correspondiente
- **Formulario Organizado**: Estructura clara y fácil de entender

### Mejoras de UX/UI Implementadas
- **Diseño Limpio**: Interfaz moderna y minimalista
- **Colores por Tipo**: Diferentes colores para entrenamientos, eventos y competencias
- **Responsive Design**: Adaptable a dispositivos móviles
- **Indicadores Visuales**: Contadores y puntos de colores para eventos
- **Navegación Intuitiva**: Botón "Hoy" y navegación entre meses
- **Modal Selector**: Interfaz para elegir entre múltiples eventos
- **Botón Flotante**: Acceso rápido para agregar eventos

### Código Optimizado
- **Eliminación completa de código no utilizado**: Removidos todos los archivos CSS innecesarios
- **Archivos CSS consolidados**: Solo 2 archivos CSS esenciales (calendario + modal)
- **Funcionalidad esencial**: Solo características necesarias para el funcionamiento
- **Limpieza total**: Eliminados 6 archivos CSS duplicados y no utilizados

### Archivos Eliminados (Código No Utilizado)
- `calendario-mejorado.css` - Estilos avanzados no implementados
- `modal-mejorado.css` - Estilos de modal duplicados
- `calendario.css` - Estilos base duplicados
- `vista-calendario.css` - Estilos de vista no utilizados
- `botones-calendario.css` - Estilos de botones duplicados
- `modal.css` - Estilos de modal original no utilizados

### Archivos Mantenidos (Esenciales)
- `calendario-simplificado.css` - Estilos del calendario principal
- `modal-consolidado.css` - Estilos del modal y formularios
- `calendario-index.css` - Archivo índice de importaciones

### Tipos de Eventos
- **Entrenamiento**: Sesiones de práctica deportiva
- **Evento**: Actividades especiales o partidos amistosos
- **Competencia**: Torneos y competiciones oficiales



## Uso del Componente

### En una Vista
```vue
<template>
  <main>
    <Encabezado rol="Admin"/>
    <CalendarioComponent />
    <Pie />
  </main>
</template>
```

## Servicio de Calendario

El `CalendarioService` maneja:
- Persistencia en localStorage
- Validación de datos
- Operaciones CRUD de eventos

## Estilos

- **CSS Modular**: Estilos organizados en archivos específicos por funcionalidad
- **calendario.css**: Estilos base del calendario (grid, celdas de días)
- **vista-calendario.css**: Estilos de la vista principal y elementos de la interfaz
- **botones-calendario.css**: Estilos de botones de navegación y botón flotante
- **modal.css**: Estilos del modal para crear/editar eventos
- **Diseño Limpio**: Fondo blanco con borde azul sutil y barra amarilla en el encabezado
- **Colores**: Tema limpio con amarillo (#FFD700) solo en la barra del calendario
- **Efectos Visuales**: Hover effects, transiciones suaves y sombras
- **Responsive**: Diseño adaptable a diferentes tamaños de pantalla

## Dependencias

- Vue.js 3 (Composition API)
- Font Awesome para iconos
- CSS Grid para layout del calendario
- LocalStorage para persistencia

## Mejoras Futuras

- Integración con backend para persistencia en base de datos
- Notificaciones push para eventos próximos
- Exportación de calendario (iCal, PDF)
- Vista semanal y diaria
- Sincronización con calendarios externos
- Sistema de recordatorios por email/SMS
