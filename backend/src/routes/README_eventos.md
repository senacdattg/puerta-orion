# API de Eventos Deportivos

Documentación completa de los endpoints para la gestión de eventos, sesiones y tipos de evento del sistema Puerta Orion.

## 📋 Tabla de Contenidos

- [Eventos](#eventos)
- [Sesiones](#sesiones)
- [Tipos de Evento](#tipos-de-evento)
- [Endpoints Adicionales](#endpoints-adicionales)

---

## 🎯 Eventos

### 1. Listar Eventos
**GET** `/api/eventos`

Lista todos los eventos con filtros opcionales y paginación.

#### Query Parameters:
- `page` (int, opcional): Número de página (default: 1)
- `per_page` (int, opcional): Registros por página (default: 10)
- `search` (string, opcional): Búsqueda por nombre
- `categoria_id` (int, opcional): Filtrar por categoría
- `tipo_evento_id` (int, opcional): Filtrar por tipo de evento
- `fecha_desde` (string, opcional): Filtrar desde fecha (YYYY-MM-DD)
- `fecha_hasta` (string, opcional): Filtrar hasta fecha (YYYY-MM-DD)

#### Ejemplo de Respuesta:
```json
{
  "success": true,
  "data": [
    {
      "id_evento": 1,
      "nombre": "Torneo Regional de Fútbol",
      "fecha_evento": "2024-03-15",
      "duracion": "02:00:00",
      "id_categoria": 1,
      "id_tipo_evento": 1,
      "id_sesion": 1,
      "categoria": {
        "id_categoria": 1,
        "nombre_categoria": "Sub-12"
      },
      "sesion": {
        "id_sesion": 1,
        "nombre": "Mañana"
      },
      "tipo_evento": {
        "id_tipo_evento": 1,
        "nombre": "Competencia"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 45,
    "pages": 5
  }
}
```

---

### 2. Obtener Evento por ID
**GET** `/api/eventos/{id}`

Obtiene la información detallada de un evento específico.

#### Parámetros de URL:
- `id` (int): ID del evento

#### Ejemplo de Respuesta:
```json
{
  "success": true,
  "data": {
    "id_evento": 1,
    "nombre": "Torneo Regional de Fútbol",
    "fecha_evento": "2024-03-15",
    "duracion": "02:00:00",
    "id_categoria": 1,
    "id_tipo_evento": 1,
    "id_sesion": 1,
    "categoria": {
      "id_categoria": 1,
      "codigo_categoria": 101,
      "nombre_categoria": "Sub-12",
      "edad_minima": 10,
      "edad_maxima": 12,
      "estado": true
    },
    "sesion": {
      "id_sesion": 1,
      "nombre": "Mañana",
      "descripcion": "Sesión matutina de 8:00 a 12:00"
    },
    "tipo_evento": {
      "id_tipo_evento": 1,
      "nombre": "Competencia",
      "descripcion": "Eventos de competencia oficial"
    }
  }
}
```

---

### 3. Crear Evento
**POST** `/api/eventos`

Crea un nuevo evento deportivo.

#### Body JSON:
```json
{
  "nombre": "Torneo Regional de Fútbol",
  "fecha_evento": "2024-03-15",
  "duracion": "02:00:00",
  "id_categoria": 1,
  "id_tipo_evento": 1,
  "id_sesion": 1
}
```

#### Campos:
- `nombre` (string, requerido): Nombre del evento (mínimo 3 caracteres)
- `fecha_evento` (string, requerido): Fecha en formato YYYY-MM-DD
- `duracion` (string, requerido): Duración en formato HH:MM o HH:MM:SS
- `id_categoria` (int, requerido): ID de la categoría
- `id_tipo_evento` (int, requerido): ID del tipo de evento
- `id_sesion` (int, requerido): ID de la sesión

#### Ejemplo de Respuesta:
```json
{
  "success": true,
  "message": "Evento creado exitosamente",
  "data": {
    "id_evento": 1,
    "nombre": "Torneo Regional de Fútbol",
    "fecha_evento": "2024-03-15",
    "duracion": "02:00:00",
    "id_categoria": 1,
    "id_tipo_evento": 1,
    "id_sesion": 1
  }
}
```

---

### 4. Actualizar Evento
**PUT** `/api/eventos/{id}`

Actualiza un evento existente.

#### Parámetros de URL:
- `id` (int): ID del evento

#### Body JSON (todos los campos son opcionales):
```json
{
  "nombre": "Torneo Nacional de Fútbol",
  "fecha_evento": "2024-03-20",
  "duracion": "03:00:00",
  "id_categoria": 2,
  "id_tipo_evento": 1,
  "id_sesion": 2
}
```

#### Ejemplo de Respuesta:
```json
{
  "success": true,
  "message": "Evento actualizado exitosamente",
  "data": {
    "id_evento": 1,
    "nombre": "Torneo Nacional de Fútbol",
    "fecha_evento": "2024-03-20",
    "duracion": "03:00:00",
    "id_categoria": 2,
    "id_tipo_evento": 1,
    "id_sesion": 2
  }
}
```

---

### 5. Eliminar Evento
**DELETE** `/api/eventos/{id}`

Elimina un evento del sistema.

#### Parámetros de URL:
- `id` (int): ID del evento

#### Ejemplo de Respuesta:
```json
{
  "success": true,
  "message": "Evento \"Torneo Regional de Fútbol\" eliminado exitosamente"
}
```

---

## 📅 Sesiones

### 1. Listar Sesiones
**GET** `/api/sesiones`

Lista todas las sesiones de entrenamiento disponibles.

#### Query Parameters:
- `page` (int, opcional): Número de página
- `per_page` (int, opcional): Registros por página
- `search` (string, opcional): Búsqueda por nombre

#### Ejemplo de Respuesta:
```json
{
  "success": true,
  "data": [
    {
      "id_sesion": 1,
      "nombre": "Mañana",
      "descripcion": "Sesión matutina de 8:00 a 12:00"
    },
    {
      "id_sesion": 2,
      "nombre": "Tarde",
      "descripcion": "Sesión vespertina de 14:00 a 18:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 2,
    "pages": 1
  }
}
```

---

### 2. Obtener Sesión por ID
**GET** `/api/sesiones/{id}`

#### Ejemplo de Respuesta:
```json
{
  "success": true,
  "data": {
    "id_sesion": 1,
    "nombre": "Mañana",
    "descripcion": "Sesión matutina de 8:00 a 12:00"
  }
}
```

---

### 3. Crear Sesión
**POST** `/api/sesiones`

#### Body JSON:
```json
{
  "nombre": "Noche",
  "descripcion": "Sesión nocturna de 18:00 a 22:00"
}
```

#### Campos:
- `nombre` (string, requerido): Nombre de la sesión (único, mínimo 3 caracteres)
- `descripcion` (string, opcional): Descripción de la sesión

#### Ejemplo de Respuesta:
```json
{
  "success": true,
  "message": "Sesión creada exitosamente",
  "data": {
    "id_sesion": 3,
    "nombre": "Noche",
    "descripcion": "Sesión nocturna de 18:00 a 22:00"
  }
}
```

---

### 4. Actualizar Sesión
**PUT** `/api/sesiones/{id}`

#### Body JSON:
```json
{
  "nombre": "Noche Extendida",
  "descripcion": "Sesión nocturna de 18:00 a 23:00"
}
```

---

### 5. Eliminar Sesión
**DELETE** `/api/sesiones/{id}`

⚠️ **Nota:** No se puede eliminar una sesión que tenga eventos asociados.

---

## 🏆 Tipos de Evento

### 1. Listar Tipos de Evento
**GET** `/api/tipos-evento`

Lista todos los tipos de evento disponibles.

#### Query Parameters:
- `page` (int, opcional): Número de página
- `per_page` (int, opcional): Registros por página
- `search` (string, opcional): Búsqueda por nombre

#### Ejemplo de Respuesta:
```json
{
  "success": true,
  "data": [
    {
      "id_tipo_evento": 1,
      "nombre": "Competencia",
      "descripcion": "Eventos de competencia oficial"
    },
    {
      "id_tipo_evento": 2,
      "nombre": "Entrenamiento",
      "descripcion": "Sesiones de práctica y entrenamiento"
    },
    {
      "id_tipo_evento": 3,
      "nombre": "Exhibición",
      "descripcion": "Eventos de demostración"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 3,
    "pages": 1
  }
}
```

---

### 2. Obtener Tipo de Evento por ID
**GET** `/api/tipos-evento/{id}`

---

### 3. Crear Tipo de Evento
**POST** `/api/tipos-evento`

#### Body JSON:
```json
{
  "nombre": "Amistoso",
  "descripcion": "Partidos amistosos sin clasificación"
}
```

---

### 4. Actualizar Tipo de Evento
**PUT** `/api/tipos-evento/{id}`

---

### 5. Eliminar Tipo de Evento
**DELETE** `/api/tipos-evento/{id}`

⚠️ **Nota:** No se puede eliminar un tipo de evento que tenga eventos asociados.

---

## 🔍 Endpoints Adicionales

### 1. Eventos Próximos
**GET** `/api/eventos/proximos`

Lista los eventos próximos (desde hoy en adelante).

#### Query Parameters:
- `limit` (int, opcional): Número máximo de eventos (default: 10)
- `categoria_id` (int, opcional): Filtrar por categoría

#### Ejemplo de Respuesta:
```json
{
  "success": true,
  "data": [
    {
      "id_evento": 5,
      "nombre": "Entrenamiento Sub-14",
      "fecha_evento": "2024-02-15",
      "duracion": "01:30:00",
      "categoria": {
        "id_categoria": 2,
        "nombre_categoria": "Sub-14"
      },
      "sesion": {
        "id_sesion": 1,
        "nombre": "Mañana"
      },
      "tipo_evento": {
        "id_tipo_evento": 2,
        "nombre": "Entrenamiento"
      }
    }
  ],
  "total": 8
}
```

---

### 2. Eventos por Categoría
**GET** `/api/eventos/categoria/{categoria_id}`

Lista todos los eventos de una categoría específica.

#### Parámetros de URL:
- `categoria_id` (int): ID de la categoría

#### Ejemplo de Respuesta:
```json
{
  "success": true,
  "data": [
    {
      "id_evento": 1,
      "nombre": "Torneo Regional",
      "fecha_evento": "2024-03-15",
      "duracion": "02:00:00",
      "sesion": {
        "id_sesion": 1,
        "nombre": "Mañana"
      },
      "tipo_evento": {
        "id_tipo_evento": 1,
        "nombre": "Competencia"
      }
    }
  ],
  "categoria": {
    "id_categoria": 1,
    "codigo_categoria": 101,
    "nombre_categoria": "Sub-12",
    "edad_minima": 10,
    "edad_maxima": 12,
    "estado": true
  },
  "total": 12
}
```

---

## 🔒 Validaciones

### Evento:
- **nombre**: Mínimo 3 caracteres
- **fecha_evento**: Formato YYYY-MM-DD válido
- **duracion**: Formato HH:MM o HH:MM:SS válido
- **id_categoria**: Debe existir en la base de datos
- **id_tipo_evento**: Debe existir en la base de datos
- **id_sesion**: Debe existir en la base de datos

### Sesión:
- **nombre**: Mínimo 3 caracteres, único
- **descripcion**: Opcional

### Tipo de Evento:
- **nombre**: Mínimo 3 caracteres, único
- **descripcion**: Opcional

---

## ❌ Códigos de Error

- **400 Bad Request**: Datos inválidos o faltantes
- **404 Not Found**: Recurso no encontrado
- **500 Internal Server Error**: Error del servidor

### Ejemplos de Errores:

```json
{
  "success": false,
  "error": "El campo nombre es requerido"
}
```

```json
{
  "success": false,
  "error": "Evento con ID 99 no encontrado"
}
```

```json
{
  "success": false,
  "error": "No se puede eliminar la sesión porque tiene 5 evento(s) asociado(s)"
}
```

---

## 📝 Notas Importantes

1. **Fechas**: Siempre use formato ISO (YYYY-MM-DD)
2. **Duración**: Puede ser HH:MM o HH:MM:SS (ejemplo: "02:30" o "02:30:00")
3. **Paginación**: Por defecto, la API devuelve 10 registros por página
4. **Relaciones**: Los eventos están vinculados a categorías, sesiones y tipos de evento
5. **Eliminación**: No se pueden eliminar sesiones o tipos de evento que tengan eventos asociados
6. **Ordenamiento**: Los eventos se ordenan por fecha descendente (más recientes primero)

---

## 🧪 Ejemplos de Prueba con cURL

### Crear un evento:
```bash
curl -X POST http://localhost:5000/api/eventos \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Torneo Infantil 2024",
    "fecha_evento": "2024-04-15",
    "duracion": "03:00:00",
    "id_categoria": 1,
    "id_tipo_evento": 1,
    "id_sesion": 1
  }'
```

### Listar eventos próximos:
```bash
curl http://localhost:5000/api/eventos/proximos?limit=5
```

### Buscar eventos:
```bash
curl "http://localhost:5000/api/eventos?search=torneo&fecha_desde=2024-03-01"
```

---

## 📦 Estructura de Datos Completa

```typescript
interface Evento {
  id_evento: number;
  nombre: string;
  fecha_evento: string;  // YYYY-MM-DD
  duracion: string;      // HH:MM:SS
  id_categoria: number;
  id_tipo_evento: number;
  id_sesion: number;
  categoria?: Categoria;
  sesion?: Sesion;
  tipo_evento?: TipoEvento;
}

interface Sesion {
  id_sesion: number;
  nombre: string;
  descripcion?: string;
}

interface TipoEvento {
  id_tipo_evento: number;
  nombre: string;
  descripcion?: string;
}
```

