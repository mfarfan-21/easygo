# Easy Go CV Builder - Backend

Backend de Python (FastAPI) para el generador de CVs con IA de Easy Go.

## 🚀 Características

- ✅ Optimización de CVs con GPT-4 de OpenAI
- ✅ Generación de PDFs profesionales con ReportLab
- ✅ API RESTful con FastAPI
- ✅ Sugerencias inteligentes basadas en descripciones de trabajo
- ✅ CORS configurado para desarrollo y producción

## 📋 Requisitos

- Python 3.8 o superior
- Cuenta de OpenAI con API Key
- pip (gestor de paquetes de Python)

## 🔧 Instalación

### 1. Crear entorno virtual (recomendado)

```bash
cd backend
python3 -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia el archivo de ejemplo y configura tus credenciales:

```bash
cp .env.example .env
```

Edita el archivo `.env` y agrega tu API Key de OpenAI:

```env
OPENAI_API_KEY=tu-clave-api-de-openai-aqui
PORT=8000
DEBUG=True
```

**Para obtener tu API Key de OpenAI:**
1. Ve a https://platform.openai.com/api-keys
2. Inicia sesión o crea una cuenta
3. Crea una nueva API key
4. Copia la clave y pégala en `.env`

### 4. Iniciar el servidor

```bash
# Opción 1: Usando Python directamente
python main.py

# Opción 2: Usando uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en `http://localhost:8000`

## 📚 Documentación de la API

Una vez que el servidor esté corriendo, puedes acceder a la documentación interactiva en:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Endpoints Disponibles

### `GET /`
Información básica de la API

### `GET /health`
Verifica el estado de la API y servicios configurados

### `POST /api/cv/suggestions`
Genera sugerencias basadas en una descripción de trabajo

**Body:**
```json
{
  "job_description": "Descripción del puesto..."
}
```

### `POST /api/cv/optimize`
Optimiza el contenido del CV con GPT-4

**Body:** Objeto `CVRequest` completo (ver modelos)

### `POST /api/cv/generate`
Genera un PDF del CV optimizado con IA

**Body:** Objeto `CVRequest` completo

**Response:** Archivo PDF descargable

### `POST /api/cv/generate-without-optimization`
Genera un PDF del CV sin optimización (más rápido)

**Body:** Objeto `CVRequest` completo

**Response:** Archivo PDF descargable

## 📝 Estructura del Proyecto

```
backend/
├── main.py                 # Aplicación FastAPI principal
├── requirements.txt        # Dependencias de Python
├── .env                    # Variables de entorno (NO SUBIR A GIT)
├── .env.example           # Ejemplo de variables de entorno
├── models/
│   └── cv_models.py       # Modelos Pydantic
├── services/
│   ├── openai_service.py  # Integración con OpenAI
│   └── pdf_generator.py   # Generación de PDFs
└── generated_cvs/         # Directorio para CVs generados (creado automáticamente)
```

## 🧪 Probar la API

Puedes probar la API usando curl, Postman, o la interfaz Swagger UI:

### Ejemplo con curl:

```bash
# Health check
curl http://localhost:8000/health

# Generar sugerencias
curl -X POST http://localhost:8000/api/cv/suggestions \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Senior Python Developer with 5 years experience..."}'
```

## 🔒 Seguridad

- **NUNCA** subas tu archivo `.env` a Git
- Mantén tu `OPENAI_API_KEY` privada
- Usa variables de entorno para todas las credenciales
- En producción, configura CORS solo para tus dominios específicos

## 🚀 Despliegue en Producción

### IONOS VPS (Ubuntu 20.04)

1. **Conectarse al VPS:**
```bash
ssh root@217.160.4.109
```

2. **Instalar Python y dependencias:**
```bash
apt update
apt install python3 python3-pip python3-venv -y
```

3. **Clonar el repositorio o subir archivos:**
```bash
# Opción con git
git clone tu-repositorio.git
cd tu-repositorio/backend

# O subir con scp desde tu máquina local:
# scp -r backend/ root@217.160.4.109:/var/www/easygo/
```

4. **Configurar entorno virtual:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Configurar variables de entorno:**
```bash
nano .env
# Agregar OPENAI_API_KEY y otras variables
```

6. **Configurar servicio systemd:**
```bash
nano /etc/systemd/system/easygo-api.service
```

Contenido del archivo:
```ini
[Unit]
Description=Easy Go CV Builder API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/easygo/backend
Environment="PATH=/var/www/easygo/backend/venv/bin"
ExecStart=/var/www/easygo/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

7. **Iniciar servicio:**
```bash
systemctl daemon-reload
systemctl start easygo-api
systemctl enable easygo-api
systemctl status easygo-api
```

8. **Configurar Nginx como proxy inverso:**
```bash
nano /etc/nginx/sites-available/easygo-api
```

```nginx
server {
    listen 80;
    server_name api.tudominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/easygo-api /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## 📞 Soporte

Si tienes problemas:
1. Verifica que Python 3.8+ está instalado: `python3 --version`
2. Verifica que todas las dependencias están instaladas: `pip list`
3. Verifica que el archivo `.env` está configurado correctamente
4. Revisa los logs del servidor para errores específicos

## 📄 Licencia

Este proyecto es parte de Easy Go - AI Website Builder
