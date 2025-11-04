# 🚀 Deploy Backend a Render

## Repositorio Backend
**GitHub**: https://github.com/mfarfan-21/easygo.git  
**Render Dashboard**: https://dashboard.render.com/

---

## 📋 Pasos para Deploy

### 1. **Subir Cambios al Repositorio Backend**

```bash
# Desde /Users/Fernanda/Desktop/easygowebapp/backend
cd /Users/Fernanda/Desktop/easygowebapp/backend

# Si aún no tienes el repositorio remoto configurado
git init
git remote add origin https://github.com/mfarfan-21/easygo.git

# Agregar todos los archivos
git add .

# Commit con mensaje descriptivo
git commit -m "🎫 Token System: Rate limiting, cache, retry & circuit breaker"

# Push a GitHub
git push -u origin main
```

### 2. **Configurar en Render**

1. Ve a https://dashboard.render.com/
2. Selecciona tu servicio backend existente: `easygo-1-mxb7`
3. Click en "Manual Deploy" → "Deploy latest commit"
4. O configura auto-deploy desde GitHub

### 3. **Variables de Entorno en Render**

Asegúrate de tener estas variables configuradas en Render:

```bash
# OpenAI API Key (REQUERIDO)
OPENAI_API_KEY=sk-proj-...

# Supabase (opcional para validación de usuarios)
SUPABASE_URL=https://sjcerbejmrjcjcgqngdg.supabase.co
SUPABASE_SERVICE_KEY=tu_service_key_aqui

# Configuración
DEBUG=False
```

Para agregar/editar variables:
1. Dashboard → Tu servicio → Environment
2. Add Environment Variable
3. Save Changes (esto redesplegará automáticamente)

### 4. **Verificar Deploy**

```bash
# Health check
curl https://easygo-1-mxb7.onrender.com/health

# Debería retornar:
{
  "status": "healthy",
  "services": {
    "openai": "configured",
    "pdf_generator": "ready"
  }
}

# Ver documentación API
https://easygo-1-mxb7.onrender.com/api/docs
```

---

## 🔧 Configuración de CORS

El backend ya está configurado para aceptar requests desde tu dominio:

```python
# En main.py
origins = [
    "http://localhost:5173",
    "https://easygo.com.es",
    "*"  # En producción, permite todos los orígenes
]
```

Si necesitas restringir solo a tu dominio, cambia a:

```python
origins = [
    "https://easygo.com.es",
    "https://www.easygo.com.es"
]
```

---

## 🎫 Sistema de Tokens

El backend ahora incluye:

### **Endpoints Nuevos**
```bash
# Ver balance de tokens
GET /api/user/tokens
Header: X-User-ID: <supabase_user_id>

# Estadísticas del sistema
GET /api/system/stats

# Todos los endpoints de CV ahora requieren X-User-ID
POST /api/cv/suggestions
POST /api/cv/optimize
POST /api/cv/generate
POST /api/cv/generate-without-optimization
```

### **Costos de Tokens**
- `suggestions`: 1 token
- `optimize`: 2 tokens
- `generate`: 2 tokens
- `generate-without-optimization`: 1 token

### **Características**
- ✅ **5 tokens gratis** por usuario nuevo
- ✅ **Rate limiting**: 10 requests/minuto
- ✅ **Caché**: 10 minutos (requests duplicadas gratis)
- ✅ **Retry logic**: 3 intentos con exponential backoff
- ✅ **Circuit breaker**: Protección contra fallos de OpenAI

---

## 📊 Monitoreo en Render

### **Ver Logs**
1. Dashboard → Tu servicio → Logs
2. Busca mensajes como:
   - `✓ Consumed 2 tokens from user xxx`
   - `✓ Cache HIT for user xxx`
   - `OpenAI API error (attempt 1/3)`

### **Métricas**
1. Dashboard → Tu servicio → Metrics
2. Monitorea:
   - CPU usage
   - Memory usage
   - Request count
   - Response time

---

## 🔄 Auto-Deploy desde GitHub

### **Configurar Webhook**
1. Render Dashboard → Settings
2. "Build & Deploy" section
3. Enable "Auto-Deploy"
4. Conecta tu GitHub repo: `mfarfan-21/easygo`
5. Branch: `main`

Ahora cada `git push` a `main` redesplegará automáticamente.

---

## 🧪 Testing del Sistema de Tokens

### **Test 1: Health Check**
```bash
curl https://easygo-1-mxb7.onrender.com/health
```

### **Test 2: Ver Balance de Tokens**
```bash
curl -X GET https://easygo-1-mxb7.onrender.com/api/user/tokens \
  -H "X-User-ID: test_user_123"
```

### **Test 3: Consumir Tokens (Suggestions)**
```bash
curl -X POST https://easygo-1-mxb7.onrender.com/api/cv/suggestions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test_user_123" \
  -d '{
    "job_description": "Senior Software Engineer at Google. React, Node.js, AWS."
  }'
```

### **Test 4: Verificar Rate Limiting**
```bash
# Hacer 11 requests rápidas (la 11va debería fallar)
for i in {1..11}; do
  curl -X POST https://easygo-1-mxb7.onrender.com/api/cv/suggestions \
    -H "Content-Type: application/json" \
    -H "X-User-ID: test_rate_limit" \
    -d '{"job_description": "test"}' &
done
```

### **Test 5: Verificar Caché**
```bash
# 1ra request (consume token)
curl -X POST https://easygo-1-mxb7.onrender.com/api/cv/suggestions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test_cache" \
  -d '{"job_description": "Python Developer"}'

# 2da request (caché, NO consume token)
curl -X POST https://easygo-1-mxb7.onrender.com/api/cv/suggestions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test_cache" \
  -d '{"job_description": "Python Developer"}'
```

---

## ⚠️ Troubleshooting

### **Error: "Missing X-User-ID header"**
- Solución: Todos los endpoints requieren el header `X-User-ID`
- El frontend lo envía automáticamente desde `apiService.js`

### **Error: "Insufficient tokens"**
- El usuario agotó sus 5 tokens gratis
- Necesitas implementar sistema de compra de tokens (Stripe)

### **Error: "Rate limit exceeded"**
- Usuario hizo más de 10 requests en 1 minuto
- Esperar hasta 1 minuto antes de reintentar

### **Error: "Circuit breaker is OPEN"**
- OpenAI API está fallando repetidamente
- El sistema se recuperará automáticamente en 60 segundos

### **Logs no aparecen en Render**
- Asegúrate de tener `print()` statements en Python
- Render captura stdout/stderr automáticamente

---

## 🔐 Seguridad

### **Headers Requeridos**
```python
X-User-ID: <supabase_user_id>  # Identificación del usuario
```

### **Validación de Usuarios** (Opcional - Próxima mejora)
Para mayor seguridad, puedes validar el JWT de Supabase:

```python
# En backend/main.py
from supabase import create_client

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

async def verify_user(authorization: str):
    # Extraer JWT del header
    token = authorization.replace("Bearer ", "")
    # Validar con Supabase
    user = supabase.auth.get_user(token)
    return user.id
```

---

## 📈 Próximos Pasos

1. **Persistencia de Tokens** (opcional)
   - Actualmente tokens están en memoria
   - Se resetean al reiniciar servidor
   - Considerar guardar en Supabase Database

2. **Sistema de Pagos**
   - Integrar Stripe para comprar tokens
   - Ya tienes `stripe_service.py` listo

3. **Analytics**
   - Registrar uso de tokens por usuario
   - Identificar features más usadas

4. **Notificaciones**
   - Email cuando tokens < 2
   - Alertas de rate limiting

---

## 📞 Contacto

**URL Backend**: https://easygo-1-mxb7.onrender.com  
**URL Frontend**: https://easygo.com.es/  
**GitHub Backend**: https://github.com/mfarfan-21/easygo.git  
**GitHub Frontend**: https://github.com/maferfarfan2122/easygo

**Última actualización**: 4 de noviembre, 2025
