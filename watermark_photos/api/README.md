# API de Marca de Agua

Esta API permite aplicar marcas de agua a imágenes de forma sencilla. Está basada en el script local `watermark_local.py` pero adaptada para funcionar como un servicio web desplegado en fly.io.

## Características

- Recibe imágenes a través de una API REST
- Procesa imágenes recibidas por correo electrónico
- Aplica una marca de agua con el texto "@pedro.rj2 #código"
- Devuelve la imagen procesada con la marca de agua
- Permite especificar un código personalizado para la marca de agua
- Muestra estadísticas de uso en la página principal

## Cómo usar la API

### Usando curl

```bash
curl -X POST -F "image=@ruta/a/tu/imagen.jpg" -F "code=codigo_opcional" https://tu-app.fly.dev/watermark -o imagen_con_marca.jpg
```

### Usando Python

```python
import requests

url = "https://tu-app.fly.dev/watermark"
files = {"image": open("ruta/a/tu/imagen.jpg", "rb")}
data = {"code": "codigo_opcional"}  # El código es opcional

response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    with open("imagen_con_marca.jpg", "wb") as f:
        f.write(response.content)
    print("Imagen guardada correctamente")
else:
    print(f"Error: {response.json()}")
```

### Usando correo electrónico

Puedes enviar imágenes por correo electrónico y recibir las versiones con marca de agua como respuesta:

1. Envía un correo electrónico a la dirección configurada en el servicio
2. Adjunta una o más imágenes al correo
3. El servicio procesará automáticamente las imágenes y te enviará las versiones con marca de agua

## Parámetros

- `image`: La imagen a la que se aplicará la marca de agua (obligatorio)
- `code`: Código personalizado para la marca de agua (opcional)

## Despliegue en fly.io

Para desplegar esta API en fly.io, sigue estos pasos:

1. Instala la CLI de fly.io:
   ```bash
   # En Windows con PowerShell
   iwr https://fly.io/install.ps1 -useb | iex

   # En macOS o Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. Inicia sesión en fly.io:
   ```bash
   fly auth login
   ```

3. Navega a la carpeta de la API:
   ```bash
   cd watermark_photos/api
   ```

4. Lanza la aplicación:
   ```bash
   fly launch
   ```
   - Durante el proceso, puedes usar la configuración del archivo `fly.toml` incluido
   - Selecciona la región más cercana a ti

5. Despliega la aplicación:
   ```bash
   fly deploy
   ```

6. Verifica que la aplicación está funcionando:
   ```bash
   fly status
   ```

7. Abre la aplicación en el navegador:
   ```bash
   fly open
   ```

## Desarrollo local

Para ejecutar la API localmente:

1. Navega a la carpeta de la API:
   ```bash
   cd watermark_photos/api
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta la aplicación:
   ```bash
   python app.py
   ```

4. La API estará disponible en `http://localhost:8080`

## Configuración del procesador de correos electrónicos

Para configurar el procesador de correos electrónicos, sigue estos pasos:

1. Edita el archivo `email_processor.py` y configura las siguientes variables:
   ```python
   EMAIL_ADDRESS = "tu_correo@gmail.com"  # Reemplaza con tu dirección de correo
   EMAIL_PASSWORD = "tu_contraseña"  # Reemplaza con tu contraseña o contraseña de aplicación
   IMAP_SERVER = "imap.gmail.com"  # Servidor IMAP (cambia si no usas Gmail)
   SMTP_SERVER = "smtp.gmail.com"  # Servidor SMTP (cambia si no usas Gmail)
   SMTP_PORT = 587  # Puerto SMTP (cambia si es necesario)
   ```

2. Si usas Gmail, necesitarás crear una contraseña de aplicación:
   - Ve a tu cuenta de Google > Seguridad > Verificación en dos pasos
   - Activa la verificación en dos pasos si no está activada
   - Ve a "Contraseñas de aplicaciones"
   - Crea una nueva contraseña para "Otra aplicación (nombre personalizado)"
   - Usa esta contraseña en la configuración

3. Instala las dependencias adicionales:
   ```bash
   pip install imaplib email smtplib requests
   ```

## Iniciar todos los servicios

Para iniciar tanto la API como el procesador de correos electrónicos, puedes usar el script `start_services.py`:

```bash
python start_services.py
```

Este script iniciará ambos servicios y los reiniciará automáticamente si alguno se detiene.

## Procesamiento por lotes

Si quieres procesar todas las imágenes de una carpeta de una sola vez, puedes usar el script `process_with_api.py` que se encuentra en la carpeta principal de `watermark_photos`:

```bash
cd ..
python process_with_api.py
```

Este script tomará todas las imágenes de la carpeta `input`, las procesará usando la API y guardará los resultados en la carpeta `output`.

## Notas

- La API guarda temporalmente las imágenes procesadas y realiza una limpieza periódica
- Para un uso en producción, considera implementar un sistema de almacenamiento más robusto
- La aplicación está configurada para usar recursos mínimos en fly.io, lo que la hace económica para uso personal
- El procesador de correos electrónicos verifica nuevos correos cada 60 segundos
- Para mayor seguridad, considera almacenar las credenciales de correo electrónico en variables de entorno en lugar de en el código
