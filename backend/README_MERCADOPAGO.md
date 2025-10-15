# 🚀 Integración Mercado Pago - Puerta Orion

## 📋 Requisitos Previos

### 1. Dependencias
```bash
pip install -r requirements.txt
```

### 2. Variables de Entorno
Copia `env_example.txt` como `.env` y configura:

```env
# Mercado Pago - Credenciales de Sandbox
MERCADOPAGO_ACCESS_TOKEN=TEST-tu_access_token_de_sandbox_aqui
MERCADOPAGO_PUBLIC_KEY=TEST-tu_public_key_de_sandbox_aqui
MERCADOPAGO_WEBHOOK_SECRET=tu_webhook_secret_aqui
MERCADOPAGO_ENVIRONMENT=sandbox
```

### 3. Base de Datos
```bash
flask db upgrade
```

### 4. Datos Básicos
Crear datos mínimos necesarios:
- TipoDocumento
- Sexo  
- MetodoPago
- Categoria
- Persona (para pruebas)

## 🧪 Pruebas

### Consultar Saldo
```bash
GET /api/cuota/1/saldo
```

### Crear Pago Completo
```bash
POST /api/mercadopago/crear-preferencia
{
    "tipo_pago": "cuota",
    "id_cuota": 1,
    "nombre_pagador": "Juan Pérez",
    "email_pagador": "juan@email.com",
    "telefono_pagador": "1234567890"
}
```

### Crear Pago Parcial
```bash
POST /api/mercadopago/crear-preferencia
{
    "tipo_pago": "cuota",
    "id_cuota": 1,
    "monto": 30.00,
    "nombre_pagador": "Juan Pérez",
    "email_pagador": "juan@email.com",
    "telefono_pagador": "1234567890"
}
```

## 📊 Endpoints Disponibles

- `GET /api/cuota/{id}/saldo` - Consultar saldo pendiente
- `POST /api/mercadopago/crear-preferencia` - Crear pago
- `GET /api/mercadopago/verificar-pago/{id}` - Verificar estado
- `GET /api/mercadopago/transacciones` - Listar transacciones
- `GET /api/mercadopago/estadisticas` - Estadísticas generales

## ⚠️ Notas Importantes

- Las migraciones están incluidas en el repositorio
- Usar credenciales de Sandbox para desarrollo
- No subir archivos `.env` al repositorio
