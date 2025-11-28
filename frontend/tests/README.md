# Tests - Frontend Puerta de Orión

## Estructura de Tests

```
tests/
├── unit/              # Tests unitarios
│   ├── components/    # Tests de componentes Vue
│   ├── composables/  # Tests de composables
│   ├── services/     # Tests de servicios
│   ├── stores/       # Tests de stores Pinia
│   └── utils/        # Tests de utilidades
├── integration/       # Tests de integración
├── fixtures/          # Datos de prueba reutilizables
├── mocks/            # Mocks de servicios y dependencias
├── utils/            # Utilidades para tests
└── setup.js          # Configuración global de tests
```

## Ejecutar Tests

```bash
# Ejecutar todos los tests una vez
npm run test

# Ejecutar tests en modo watch
npm run test:watch

# Ejecutar tests con UI interactiva
npm run test:ui

# Ejecutar tests con cobertura
npm run test:coverage
```

## Cobertura

Los tests están configurados para mantener un mínimo de 80% de cobertura en:
- Líneas de código
- Funciones
- Ramas
- Declaraciones

## Escribir Nuevos Tests

### Estructura de un Test

```javascript
import { describe, it, expect, beforeEach, vi } from 'vitest'

describe('Component/Function Name', () => {
  beforeEach(() => {
    // Setup antes de cada test
  })

  it('should do something', () => {
    // Arrange
    const input = 'test'
    
    // Act
    const result = functionToTest(input)
    
    // Assert
    expect(result).toBe('expected')
  })
})
```

### Principios AAA (Arrange-Act-Assert)

1. **Arrange**: Configura el estado inicial
2. **Act**: Ejecuta la acción a probar
3. **Assert**: Verifica el resultado

### Buenas Prácticas

- Usa nombres descriptivos para tests
- Un test debe verificar una sola cosa
- Usa fixtures para datos de prueba
- Mockea dependencias externas
- No uses `waitFor` innecesariamente
- Evita `setTimeout` y hacks
- Prioriza pruebas basadas en comportamiento

## Fixtures

Los fixtures están en `tests/fixtures/` y proporcionan datos de prueba consistentes:

```javascript
import { mockUser, mockToken } from '../../fixtures/auth'
```

## Mocks

Los mocks están en `tests/mocks/` y proporcionan implementaciones falsas de servicios:

```javascript
import { mockAuthService } from '../../mocks/services'
```

## Utilidades de Test

Las utilidades en `tests/utils/` proporcionan helpers comunes:

```javascript
import { mountComponent, createTestRouter } from '../utils/test-utils'
```

