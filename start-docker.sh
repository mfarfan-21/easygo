#!/bin/bash

# Script para construir y ejecutar el backend en Docker

echo "🐳 Construyendo imagen Docker del backend..."
docker build -t easygo-backend .

if [ $? -eq 0 ]; then
    echo "✅ Imagen construida exitosamente"
    
    echo "🚀 Deteniendo contenedor anterior si existe..."
    docker stop easygo-backend-container 2>/dev/null
    docker rm easygo-backend-container 2>/dev/null
    
    echo "🚀 Iniciando contenedor del backend..."
    docker run -d \
        --name easygo-backend-container \
        -p 8000:8000 \
        --env-file .env \
        easygo-backend
    
    if [ $? -eq 0 ]; then
        echo "✅ Backend corriendo en http://localhost:8000"
        echo ""
        echo "📋 Comandos útiles:"
        echo "  Ver logs:     docker logs -f easygo-backend-container"
        echo "  Detener:      docker stop easygo-backend-container"
        echo "  Reiniciar:    docker restart easygo-backend-container"
        echo "  Eliminar:     docker rm -f easygo-backend-container"
        echo ""
        echo "🔍 Probando el backend..."
        sleep 3
        curl -s http://localhost:8000/health && echo "" || echo "⚠️  El backend aún está iniciando, espera unos segundos..."
    else
        echo "❌ Error al iniciar el contenedor"
        exit 1
    fi
else
    echo "❌ Error al construir la imagen"
    exit 1
fi
