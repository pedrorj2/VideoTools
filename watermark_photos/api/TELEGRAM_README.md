# Bot de Telegram para Marca de Agua

Este bot de Telegram permite aplicar marcas de agua a imágenes de forma sencilla. Está integrado con la API de marca de agua y permite procesar imágenes directamente desde Telegram.

## Características

- Recibe imágenes a través de Telegram
- Procesa las imágenes usando la API de marca de agua
- Devuelve las imágenes procesadas al usuario
- Soporta imágenes enviadas como fotos o como archivos

## Configuración del bot

Para configurar el bot de Telegram, sigue estos pasos:

1. **Crear un bot en Telegram**:
   - Abre Telegram y busca a `@BotFather`
   - Envía el comando `/newbot`
   - Sigue las instrucciones para crear un nuevo bot
   - Al finalizar, recibirás un token de acceso (API token)

2. **Configurar el token en el archivo de configuración**:
   - Crea una copia del archivo `config.example.py` y nómbrala `config.py`:
     ```bash
     cp config.example.py config.py
     ```
   - Edita el archivo `config.py` y reemplaza `TU_TOKEN_AQUI` con el token que recibiste de BotFather:
     ```python
     TELEGRAM_TOKEN = "123456789:ABCdefGhIJKlmnOPQrstUVwxYZ"  # Reemplaza con tu token
     ```
   - Este archivo no se subirá a GitHub ya que está incluido en `.gitignore`

3. **Instalar las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## Uso del bot

1. **Iniciar el bot y la API**:
   ```bash
   python start_telegram_services.py
   ```
   Este script iniciará tanto la API de marca de agua como el bot de Telegram.

2. **Interactuar con el bot**:
   - Busca tu bot en Telegram por el nombre que le diste
   - Inicia una conversación con el comando `/start`
   - Envía una imagen al bot (como foto o como archivo)
   - El bot procesará la imagen y te devolverá la versión con marca de agua

## Comandos disponibles

- `/start` - Inicia el bot y muestra un mensaje de bienvenida
- `/help` - Muestra información de ayuda sobre cómo usar el bot

## Despliegue en producción

Para desplegar el bot en producción, necesitarás:

1. **Desplegar la API de marca de agua** en fly.io u otro servicio similar
2. **Actualizar la URL de la API** en el archivo `config.py`:
   ```python
   API_URL = "https://tu-app.fly.dev/watermark"  # URL de la API en producción
   ```

3. **Ejecutar el bot en un servidor** que esté siempre activo

## Notas

- El bot guarda temporalmente las imágenes procesadas y realiza una limpieza automática
- Para un uso en producción, considera implementar un sistema de almacenamiento más robusto
- El bot está configurado para usar recursos mínimos, lo que lo hace económico para uso personal
