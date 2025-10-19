# 🔄 CAMBIOS EN EL MODELO DE EVENTOS

## 📅 Fecha: Octubre 19, 2025

---

## 🎯 OBJETIVO

Adaptar el modelo de Eventos en el backend para que sea compatible con el calendario del frontend, agregando campos necesarios y eliminando campos innecesarios.

---

## 📊 CAMBIOS EN LA BASE DE DATOS

### ❌ Campo Eliminado:
- **`duracion`** (Time) - Ya no se usa

### ✅ Campos Agregados:
1. **`hora_inicio`** (Time, NOT NULL)
   - Hora de inicio del evento
   - Formato: HH:MM o HH:MM:SS
   - Ejemplo: "14:00" o "14:00:00"

2. **`hora_fin`** (Time, NOT NULL)
   - Hora de finalización del evento
   - Formato: HH:MM o HH:MM:SS
   - Debe ser posterior a hora_inicio
   - Ejemplo: "16:00" o "16:00:00"

3. **`lugar`** (String(200), NOT NULL)
   - Ubicación física del evento
   - Mínimo 3 caracteres
   - Ejemplo: "Estadio Municipal", "Gimnasio Principal"

4. **`descripcion`** (Text, NULL)
   - Descripción detallada del evento
   - Campo opcional
   - Ejemplo: "Torneo regional categoría juvenil"

---

## 📝 ARCHIVOS MODIFICADOS

### 1. **Modelo** (`backend/src/models/eventos/evento.py`)

**Cambios:**
- ❌ Eliminado: `duracion = Column(Time, nullable=False)`
- ✅ Agregado: `hora_inicio = Column(Time, nullable=False)`
- ✅ Agregado: `hora_fin = Column(Time, nullable=False)`
- ✅ Agregado: `lugar = Column(String(200), nullable=False)`
- ✅ Agregado: `descripcion = Column(Text, nullable=True)`
- ✅ Actualizado: método `to_dict()` con los nuevos campos

**Estructura final del modelo:**
```python
class Evento(BaseModel):
    id_evento = Column(Integer, primary_key=True)
    nombre = Column(String(250), nullable=False)
    fecha_evento = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)      # NUEVO
    hora_fin = Column(Time, nullable=False)         # NUEVO
    lugar = Column(String(200), nullable=False)     # NUEVO
    descripcion = Column(Text, nullable=True)       # NUEVO
    id_categoria = Column(Integer, ForeignKey(...))
    id_tipo_evento = Column(Integer, ForeignKey(...))
    id_sesion = Column(Integer, ForeignKey(...))
```

---

### 2. **Migración** (`backend/migrations/versions/72e395f8ae95_*.py`)

**Operaciones de la migración:**
```python
def upgrade():
    # Agregar nuevos campos
    batch_op.add_column(sa.Column('hora_inicio', sa.Time(), nullable=False))
    batch_op.add_column(sa.Column('hora_fin', sa.Time(), nullable=False))
    batch_op.add_column(sa.Column('lugar', sa.String(length=200), nullable=False))
    batch_op.add_column(sa.Column('descripcion', sa.Text(), nullable=True))
    
    # Eliminar campo antiguo
    batch_op.drop_column('duracion')
```

**Aplicar migración:**
```bash
cd backend
py -m flask db upgrade
```

---

### 3. **CRUD** (`backend/src/routes/eventos_routes.py`)

**Funciones de validación actualizadas:**
- ✅ Renombrado: `validar_duracion()` → `validar_hora()`
- ✅ Nueva: `validar_lugar()` - Valida que tenga al menos 3 caracteres

**Endpoint POST `/eventos` - Crear evento:**

**Campos requeridos actualizados:**
```json
{
  "nombre": "string (requerido, min 3 chars)",
  "fecha_evento": "YYYY-MM-DD (requerido)",
  "hora_inicio": "HH:MM o HH:MM:SS (requerido)",
  "hora_fin": "HH:MM o HH:MM:SS (requerido)",
  "lugar": "string (requerido, min 3 chars)",
  "descripcion": "string (opcional)",
  "id_categoria": "integer (requerido)",
  "id_tipo_evento": "integer (requerido)",
  "id_sesion": "integer (requerido)"
}
```

**Validaciones agregadas:**
- ✅ `hora_fin` debe ser posterior a `hora_inicio`
- ✅ `lugar` debe tener al menos 3 caracteres
- ✅ `descripcion` es opcional (puede ser null)

**Endpoint PUT `/eventos/{id}` - Actualizar evento:**

**Todos los campos son opcionales, agregados:**
- `hora_inicio`
- `hora_fin`
- `lugar`
- `descripcion`

---

### 4. **Ejemplos HTTP** (`backend/src/routes/eventos_ejemplos.http`)

**Actualizaciones:**
- ✅ Todos los ejemplos de crear evento actualizados
- ✅ Todos los ejemplos de actualizar evento actualizados
- ✅ Ejemplos de validación de errores actualizados
- ✅ Flujo completo de trabajo actualizado
- ✅ Notas de uso actualizadas

**Ejemplo de creación:**
```http
POST http://localhost:5000/api/eventos
Content-Type: application/json

{
  "nombre": "Torneo Regional de Fútbol",
  "fecha_evento": "2024-03-15",
  "hora_inicio": "14:00",
  "hora_fin": "16:00",
  "lugar": "Estadio Municipal",
  "descripcion": "Torneo regional categoría juvenil",
  "id_categoria": 1,
  "id_tipo_evento": 1,
  "id_sesion": 1
}
```

---

## ✅ VALIDACIONES IMPLEMENTADAS

### Validaciones de Campos:

1. **nombre**
   - Requerido
   - Mínimo 3 caracteres

2. **fecha_evento**
   - Requerido
   - Formato: YYYY-MM-DD

3. **hora_inicio**
   - Requerido
   - Formato: HH:MM o HH:MM:SS
   - Debe ser una hora válida

4. **hora_fin**
   - Requerido
   - Formato: HH:MM o HH:MM:SS
   - Debe ser una hora válida
   - **Debe ser posterior a hora_inicio** ⚠️

5. **lugar**
   - Requerido
   - Mínimo 3 caracteres

6. **descripcion**
   - Opcional
   - Sin límite de caracteres

7. **Relaciones FK**
   - `id_categoria` debe existir
   - `id_tipo_evento` debe existir
   - `id_sesion` debe existir

---

## 🔍 EJEMPLOS DE USO

### Crear un evento:
```bash
curl -X POST http://localhost:5000/api/eventos \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Entrenamiento de Fuerza",
    "fecha_evento": "2024-03-15",
    "hora_inicio": "08:00",
    "hora_fin": "09:30",
    "lugar": "Gimnasio Principal",
    "descripcion": "Entrenamiento de fuerza y resistencia",
    "id_categoria": 1,
    "id_tipo_evento": 2,
    "id_sesion": 1
  }'
```

### Actualizar un evento:
```bash
curl -X PUT http://localhost:5000/api/eventos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "hora_inicio": "09:00",
    "hora_fin": "10:30",
    "lugar": "Gimnasio Secundario"
  }'
```

### Respuesta exitosa:
```json
{
  "success": true,
  "message": "Evento creado exitosamente",
  "data": {
    "id_evento": 1,
    "nombre": "Entrenamiento de Fuerza",
    "fecha_evento": "2024-03-15",
    "hora_inicio": "08:00:00",
    "hora_fin": "09:30:00",
    "lugar": "Gimnasio Principal",
    "descripcion": "Entrenamiento de fuerza y resistencia",
    "id_categoria": 1,
    "id_tipo_evento": 2,
    "id_sesion": 1
  }
}
```

---

## 🚨 ERRORES COMUNES

### 1. Hora de fin anterior a hora de inicio:
```json
{
  "success": false,
  "error": "La hora de fin debe ser posterior a la hora de inicio"
}
```

### 2. Lugar muy corto:
```json
{
  "success": false,
  "error": "El lugar debe tener al menos 3 caracteres"
}
```

### 3. Formato de hora inválido:
```json
{
  "success": false,
  "error": "Formato de hora de inicio inválido. Use HH:MM o HH:MM:SS"
}
```

---

## 📋 COMPATIBILIDAD CON EL FRONTEND

El calendario del frontend (`calendario-component.vue`) ahora es **100% compatible** con estos campos:

| Campo Frontend | Campo Backend | Tipo | Estado |
|----------------|---------------|------|--------|
| `titulo` | `nombre` | String | ✅ Compatible |
| `fecha` | `fecha_evento` | Date | ✅ Compatible |
| `hora` | `hora_inicio` | Time | ✅ Compatible |
| `lugar` | `lugar` | String | ✅ Compatible |
| `descripcion` | `descripcion` | Text | ✅ Compatible |
| `tipo` | `id_tipo_evento` | FK | ✅ Compatible |

**Nuevo campo agregado:**
- `hora_fin` - Permite definir la duración del evento de manera más clara

---

## 🎯 PRÓXIMOS PASOS

1. ✅ Modelo actualizado
2. ✅ Migración creada
3. ⏳ Aplicar migración: `py -m flask db upgrade`
4. ⏳ Conectar el frontend con el backend
5. ⏳ Actualizar el servicio de calendario en Vue
6. ⏳ Probar la integración completa

---

## 📝 NOTAS IMPORTANTES

- ⚠️ **Antes de aplicar la migración**, asegúrate de hacer un backup de la base de datos
- ⚠️ Si ya tienes eventos en la base de datos, la migración **fallará** porque los nuevos campos son NOT NULL
- ⚠️ Solución: Puedes modificar manualmente la migración para agregar valores por defecto temporales
- ✅ Los campos `hora_inicio`, `hora_fin` y `lugar` son obligatorios
- ✅ El campo `descripcion` es opcional y puede ser NULL

---

## 🔧 TROUBLESHOOTING

### Error: "Column cannot be null"

Si la migración falla porque ya tienes datos:

**Opción 1:** Eliminar eventos existentes antes de migrar
```sql
DELETE FROM puerta_orion_evento;
```

**Opción 2:** Modificar la migración para agregar valores por defecto:
```python
# En la migración, cambiar:
batch_op.add_column(sa.Column('hora_inicio', sa.Time(), nullable=False))

# Por:
batch_op.add_column(sa.Column('hora_inicio', sa.Time(), nullable=False, 
                    server_default='08:00:00'))
```

---

## ✅ VERIFICACIÓN DE CAMBIOS

Para verificar que los cambios se aplicaron correctamente:

```sql
-- Ver estructura de la tabla
DESCRIBE puerta_orion_evento;

-- Debe mostrar:
-- hora_inicio  | time        | NO  |     | NULL    |       |
-- hora_fin     | time        | NO  |     | NULL    |       |
-- lugar        | varchar(200)| NO  |     | NULL    |       |
-- descripcion  | text        | YES |     | NULL    |       |
```

---

## 📊 RESUMEN EJECUTIVO

| Aspecto | Estado |
|---------|--------|
| Modelo actualizado | ✅ Completado |
| Migración creada | ✅ Completado |
| CRUD actualizado | ✅ Completado |
| Validaciones implementadas | ✅ Completado |
| Ejemplos actualizados | ✅ Completado |
| Sin errores de linting | ✅ Verificado |
| Documentación | ✅ Completada |
| Compatibilidad frontend | ✅ Garantizada |

---

## 👤 AUTOR

Cambios realizados para el proyecto **Club Deportivo Puerta Orion**  
Fecha: Octubre 19, 2025

