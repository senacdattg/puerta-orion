# Tests Unitarios - Servicios

Este directorio contiene tests unitarios para los servicios de la aplicación.

## 📁 Estructura

```
unit/services/
├── __init__.py
├── conftest.py                    # Fixtures compartidas para todos los tests de servicios
├── README.md                      # Este archivo
│
├── test_init.py                   # Tests de inicialización del servicio
├── test_static_methods.py        # Tests de métodos estáticos
├── test_crear_preferencia.py     # Tests para crear preferencias de pago
├── test_verificar_pago.py        # Tests para verificar estado de pagos
├── test_procesar_webhook.py      # Tests para procesar webhooks
├── test_metodos_privados.py      # Tests para métodos privados
├── test_crear_pago_cuota.py      # Tests para crear pagos de cuota
├── test_crear_pago_mensualidad.py # Tests para crear pagos de mensualidad
└── test_obtener_metodo_pago.py   # Tests para obtener método de pago
```

## 🎯 Organización

Cada archivo de test se enfoca en una funcionalidad específica del servicio, lo que facilita:

- **Navegación**: Encontrar rápidamente los tests relacionados con una funcionalidad
- **Mantenimiento**: Modificar tests sin afectar otros
- **Legibilidad**: Archivos más pequeños y enfocados
- **Escalabilidad**: Fácil agregar nuevos tests sin crear archivos gigantes

## 🔧 Fixtures Compartidas

Las fixtures comunes están en `conftest.py`:

- `mock_env_vars`: Mock de variables de entorno
- `mock_sdk`: Mock del SDK de Mercado Pago
- `mercado_pago_service`: Instancia del servicio configurada para tests

## 📝 Convenciones de Nombres

- **Archivos**: `test_<funcionalidad>.py` (ej: `test_crear_preferencia.py`)
- **Clases**: `Test<Funcionalidad>` (ej: `TestCrearPreferencia`)
- **Métodos**: `test_<escenario>_<resultado>` (ej: `test_crear_preferencia_success`)

## 🚀 Ejecutar Tests

```bash
# Todos los tests de servicios
pytest tests/unit/services/

# Un archivo específico
pytest tests/unit/services/test_crear_preferencia.py

# Una clase específica
pytest tests/unit/services/test_crear_preferencia.py::TestCrearPreferencia

# Un test específico
pytest tests/unit/services/test_crear_preferencia.py::TestCrearPreferencia::test_crear_preferencia_success
```

## ✅ Buenas Prácticas

1. **Un archivo, una responsabilidad**: Cada archivo prueba una funcionalidad específica
2. **Fixtures compartidas**: Usar `conftest.py` para fixtures comunes
3. **Tests independientes**: Cada test debe poder ejecutarse de forma aislada
4. **Nombres descriptivos**: Los nombres deben explicar claramente qué se prueba

