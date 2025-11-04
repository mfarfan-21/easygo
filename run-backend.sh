#!/bin/bash

# Script simplificado para correr el backend en Docker

DOCKER="/Applications/Docker.app/Contents/Resources/bin/docker"
CONTAINER_NAME="backend-cv-$(date +%s)"

echo "🐳 Creando contenedor: $CONTAINER_NAME"

$DOCKER run -d \
    --name $CONTAINER_NAME \
    -p 8000:8000 \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    -e DEBUG=True \
    -e PORT=8000 \
    easygo-backend

if [ $? -eq 0 ]; then
    echo "✅ Backend corriendo en http://localhost:8000"
    echo "📦 Contenedor: $CONTAINER_NAME"
    echo ""
    echo "Comandos útiles:"
    echo "  Ver logs:    $DOCKER logs -f $CONTAINER_NAME"
    echo "  Detener:     $DOCKER stop $CONTAINER_NAME"
    echo "  Eliminar:    $DOCKER rm -f $CONTAINER_NAME"
else
    echo "❌ Error al crear el contenedor"
fi
