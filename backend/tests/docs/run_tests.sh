#!/bin/bash
# Script para ejecutar tests de manera conveniente

echo "🧪 Ejecutando tests de Puerta Orion..."
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Opciones por defecto
COVERAGE=true
VERBOSE="-v"
MARKERS=""

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cov)
            COVERAGE=false
            shift
            ;;
        --vv)
            VERBOSE="-vv"
            shift
            ;;
        --markers)
            MARKERS="-m $2"
            shift 2
            ;;
        --file)
            FILE="$2"
            shift 2
            ;;
        *)
            echo "Opción desconocida: $1"
            echo "Uso: ./run_tests.sh [--no-cov] [--vv] [--markers MARKER] [--file FILE]"
            exit 1
            ;;
    esac
done

# Construir comando
CMD="pytest $VERBOSE"

if [ "$COVERAGE" = true ]; then
    CMD="$CMD --cov=src --cov-report=term-missing --cov-report=html"
fi

if [ -n "$MARKERS" ]; then
    CMD="$CMD $MARKERS"
fi

if [ -n "$FILE" ]; then
    CMD="$CMD $FILE"
else
    CMD="$CMD tests/"
fi

echo -e "${BLUE}Comando:${NC} $CMD"
echo ""

# Ejecutar
eval $CMD

# Mostrar reporte de cobertura si se generó
if [ "$COVERAGE" = true ]; then
    echo ""
    echo -e "${GREEN}✅ Reporte de cobertura generado en htmlcov/index.html${NC}"
fi

