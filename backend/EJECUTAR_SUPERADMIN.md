# 🚀 Guía Rápida - Crear Super Administrador

## ⚡ Ejecución Rápida (Recomendado)

```bash
cd backend
python ejecutar_superadmin.py
```

Este comando ejecutará los seeders del sistema de permisos:
- ✅ Permisos del sistema (54+ permisos)
- ✅ Roles (SuperAdmin, Administrador, Entrenador, Deportista, Acudiente)
- ✅ **Super Administrador**

**Nota**: Si necesitas ejecutar TODOS los seeders (incluyendo catálogos básicos):
```bash
python -m src.seeders.seed
```

---

## 🔑 Credenciales del Super Administrador

```
Usuario: superadmin
Contraseña: SuperAdmin2024!
```

---

## 🎯 ¿Qué Hace el Super Administrador?

1. **Acceso Total**: Tiene TODOS los permisos del sistema
2. **Redirección Automática**: Al hacer login, va directo al panel de admin (`/admin-manager`)
3. **Gestión Completa**: Puede gestionar usuarios, roles, permisos, deportistas, eventos, pagos, etc.

---

## 📋 Instrucciones Paso a Paso

### Paso 1: Activar entorno virtual (si no está activo)

```bash
cd backend
.\venv\Scripts\activate  # Windows
# o
source venv/bin/activate  # Linux/Mac
```

### Paso 2: Ejecutar seeders

```bash
python ejecutar_superadmin.py
```

### Paso 3: Verificar la salida

Deberías ver algo como:

```
====================================================================
🌱 INICIANDO SEEDERS DEL SISTEMA PUERTA_ORION
====================================================================

📦 PASO 1: Insertando catálogos básicos...
---------------------------------------------------------------------
  📄 Insertando tipos de documento...
     ✅ 5 tipos de documento creados

📦 PASO 3: Configurando sistema de permisos...
---------------------------------------------------------------------
  🔑 Insertando permisos del sistema...
     ✅ 60 permisos creados exitosamente

  👥 Insertando roles del sistema...
     ✅ Rol 'SuperAdmin' creado
     🔑 60 permisos asignados a 'SuperAdmin'

📦 PASO 4: Creando Super Administrador...
---------------------------------------------------------------------
  👑 Creando Super Administrador...
     ✅ Super Administrador creado exitosamente

     🔑 CREDENCIALES DE ACCESO:
        Usuario: superadmin
        Contraseña: SuperAdmin2024!
        Rol: SuperAdmin

     ⚠️  IMPORTANTE: Cambia la contraseña después del primer login
```

### Paso 4: Iniciar el servidor backend

```bash
python app.py
```

### Paso 5: Iniciar el frontend

```bash
cd ../frontend
npm run dev
```

### Paso 6: Probar el login

1. Ve a `http://localhost:5173/login`
2. Ingresa:
   - Usuario: `superadmin`
   - Contraseña: `SuperAdmin2024!`
3. Deberías ser redirigido automáticamente a `/admin-manager`

---

## 🛠️ Si Ya Tienes Datos en la Base de Datos

Si ya ejecutaste algunos seeders antes, el script detectará los datos existentes y no los duplicará:

```bash
python -m src.seeders.seed
```

Verás mensajes como:
```
ℹ️  5 permisos ya existían
ℹ️  Rol 'SuperAdmin' ya existe
ℹ️  Super Administrador ya existe
```

---

## 🔧 Ejecutar Solo Permisos, Roles y Super Admin

El script `ejecutar_superadmin.py` ya incluye los tres pasos:

```bash
cd backend
python ejecutar_superadmin.py
```

Este script es inteligente:
- ✅ No duplica permisos existentes
- ✅ No duplica roles existentes
- ✅ Detecta si el super admin ya existe

---

## 📁 Archivos Creados

```
backend/
├── src/
│   └── seeders/
│       ├── seed_permisos.py       ← NUEVO: 60+ permisos del sistema
│       ├── seed_roles.py          ← NUEVO: 5 roles con permisos
│       └── seed_superadmin.py     ← NUEVO: Crea super usuario
├── SUPERADMIN_README.md           ← NUEVO: Documentación completa
└── EJECUTAR_SUPERADMIN.md         ← NUEVO: Guía rápida (este archivo)

frontend/
└── src/
    └── components/
        └── ui/
            └── login.vue          ← MODIFICADO: Redirección automática
```

---

## ✅ Verificación

Para verificar que todo funciona:

### En la Base de Datos

```sql
-- Verificar permisos
SELECT COUNT(*) FROM puerta_orion_permisos;
-- Debería retornar 60+

-- Verificar roles
SELECT * FROM puerta_orion_roles;
-- Debería mostrar: SuperAdmin, Administrador, Entrenador, Deportista, Acudiente

-- Verificar super usuario
SELECT u.usuario, u.estado, r.nombre_rol 
FROM puerta_orion_usuario u
JOIN puerta_orion_usuario_rol ur ON u.id_usuario = ur.id_usuario
JOIN puerta_orion_roles r ON ur.id_rol = r.id_rol
WHERE u.usuario = 'superadmin';
-- Debería mostrar: superadmin | True | SuperAdmin
```

### En el Frontend

1. Login exitoso con `superadmin` / `SuperAdmin2024!`
2. Redirección automática a `/admin-manager`
3. Acceso completo a todas las funcionalidades

---

## 🐛 Problemas Comunes

### Error: "ModuleNotFoundError"

**Solución**: Asegúrate de estar en el directorio correcto

```bash
cd backend
python -m src.seeders.seed
```

### Error: "No module named 'backend'"

**Solución**: Ejecuta desde el directorio raíz del backend

```bash
# Desde PUERTA_ORION/
cd backend
python -m src.seeders.seed
```

### Error: "Rol 'SuperAdmin' no encontrado"

**Solución**: Ejecuta primero los seeders de permisos y roles

```bash
python -m src.seeders.seed_permisos
python -m src.seeders.seed_roles
python -m src.seeders.seed_superadmin
```

### Error: "No hay tipos de documento disponibles"

**Solución**: Ejecuta todos los seeders

```bash
python -m src.seeders.seed
```

---

## 🎉 ¡Listo!

Ahora tienes un Super Administrador completamente funcional con:
- ✅ 60+ permisos del sistema
- ✅ 5 roles configurados
- ✅ Acceso total al sistema
- ✅ Redirección automática al panel de admin

---

**⚠️ IMPORTANTE**: Cambia la contraseña por defecto después del primer login por seguridad.

---

Para documentación completa, consulta: `SUPERADMIN_README.md`

