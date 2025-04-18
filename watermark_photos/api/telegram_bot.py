import os
import logging
import tempfile
import requests
import sys
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Intentar importar la configuración
try:
    from config import TELEGRAM_TOKEN, API_URL
    logger.info("Configuración cargada correctamente desde config.py")
except ImportError:
    logger.error("Error: No se pudo cargar el archivo config.py")
    logger.error("Por favor, crea el archivo config.py basado en config.example.py")
    logger.error("Ejemplo: cp config.example.py config.py y edita el archivo con tu token")
    sys.exit(1)

# Directorio temporal para archivos
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un mensaje cuando se emite el comando /start."""
    user = update.effective_user
    await update.message.reply_html(
        f"¡Hola {user.mention_html()}! Soy el bot de marca de agua.\n\n"
        f"Envíame una imagen y te devolveré la misma imagen con una marca de agua.\n\n"
        f"También puedes usar el comando /help para obtener más información."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un mensaje cuando se emite el comando /help."""
    await update.message.reply_text(
        "Este bot aplica una marca de agua a las imágenes que le envíes.\n\n"
        "Simplemente envía una imagen como foto o como archivo, y el bot te devolverá "
        "la misma imagen con una marca de agua.\n\n"
        "Comandos disponibles:\n"
        "/start - Inicia el bot\n"
        "/help - Muestra este mensaje de ayuda"
    )

async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Procesa una imagen y devuelve la versión con marca de agua."""
    # Informar al usuario que estamos procesando la imagen
    processing_message = await update.message.reply_text("Procesando imagen... ⏳")

    try:
        # Obtener el archivo de imagen
        photo = update.message.photo[-1] if update.message.photo else update.message.document
        file = await context.bot.get_file(photo.file_id)

        # Generar un nombre de archivo único
        file_extension = os.path.splitext(file.file_path)[1] or ".jpg"
        if not file_extension.startswith("."):
            file_extension = "." + file_extension

        temp_input_path = os.path.join(TEMP_DIR, f"input_{photo.file_id}{file_extension}")
        temp_output_path = os.path.join(TEMP_DIR, f"output_{photo.file_id}{file_extension}")

        # Descargar la imagen
        await file.download_to_drive(temp_input_path)

        # Enviar la imagen a la API para procesarla
        with open(temp_input_path, 'rb') as img_file:
            files = {'image': (f"telegram_image{file_extension}", img_file, f'image/{file_extension[1:]}')}
            data = {'code': photo.file_id[:8]}  # Usar parte del file_id como código

            response = requests.post(API_URL, files=files, data=data)

            if response.status_code == 200:
                # Guardar la imagen procesada
                with open(temp_output_path, 'wb') as f:
                    f.write(response.content)

                # Enviar la imagen procesada al usuario
                await update.message.reply_photo(
                    photo=open(temp_output_path, 'rb'),
                    caption="Aquí tienes tu imagen con marca de agua 🖼️"
                )

                # Eliminar el mensaje de procesamiento
                await processing_message.delete()
            else:
                # Informar del error
                await processing_message.edit_text(
                    f"❌ Error al procesar la imagen: {response.status_code} - {response.text}"
                )

        # Limpiar archivos temporales
        try:
            os.remove(temp_input_path)
            os.remove(temp_output_path)
        except:
            pass

    except Exception as e:
        logger.error(f"Error al procesar imagen: {str(e)}")
        await processing_message.edit_text(f"❌ Error al procesar la imagen: {str(e)}")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja documentos (archivos) enviados al bot."""
    # Verificar si el documento es una imagen
    mime_type = update.message.document.mime_type
    if mime_type and mime_type.startswith('image/'):
        await process_image(update, context)
    else:
        await update.message.reply_text(
            "❌ Solo puedo procesar imágenes. Por favor, envía una imagen."
        )

def main() -> None:
    """Inicia el bot."""
    # Crear la aplicación
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Registrar manejadores de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Registrar manejadores de mensajes
    application.add_handler(MessageHandler(filters.PHOTO, process_image))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Iniciar el bot
    application.run_polling()

    logger.info("Bot iniciado")

if __name__ == '__main__':
    main()
