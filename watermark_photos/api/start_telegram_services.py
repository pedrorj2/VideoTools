import subprocess
import sys
import os
import time
import signal
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("telegram_services.log"),
        logging.StreamHandler()
    ]
)

def start_services():
    """
    Inicia la API y el bot de Telegram como procesos separados.
    """
    try:
        # Obtener la ruta del directorio actual
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Verificar si existe el archivo de configuración
        config_file = os.path.join(current_dir, 'config.py')
        if not os.path.exists(config_file):
            logging.error("Error: No se encontró el archivo config.py")
            logging.error("Por favor, crea el archivo config.py basado en config.example.py")
            logging.error("Ejemplo: cp config.example.py config.py y edita el archivo con tu token")
            return

        # Comando para iniciar la API
        api_cmd = [sys.executable, os.path.join(current_dir, 'app.py')]

        # Comando para iniciar el bot de Telegram
        telegram_cmd = [sys.executable, os.path.join(current_dir, 'telegram_bot.py')]

        # Iniciar la API
        logging.info("Iniciando la API...")
        api_process = subprocess.Popen(api_cmd)

        # Esperar a que la API esté lista
        logging.info("Esperando a que la API esté lista...")
        time.sleep(5)

        # Iniciar el bot de Telegram
        logging.info("Iniciando el bot de Telegram...")
        telegram_process = subprocess.Popen(telegram_cmd)

        logging.info("Todos los servicios iniciados correctamente")

        # Manejar la terminación de los procesos
        def signal_handler(sig, frame):
            logging.info("Deteniendo servicios...")
            api_process.terminate()
            telegram_process.terminate()
            sys.exit(0)

        # Registrar el manejador de señales
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Mantener el script en ejecución
        while True:
            # Verificar si alguno de los procesos ha terminado
            if api_process.poll() is not None:
                logging.error("La API se ha detenido inesperadamente. Reiniciando...")
                api_process = subprocess.Popen(api_cmd)

            if telegram_process.poll() is not None:
                logging.error("El bot de Telegram se ha detenido inesperadamente. Reiniciando...")
                telegram_process = subprocess.Popen(telegram_cmd)

            time.sleep(10)

    except KeyboardInterrupt:
        logging.info("Deteniendo servicios...")
        if 'api_process' in locals():
            api_process.terminate()
        if 'telegram_process' in locals():
            telegram_process.terminate()

    except Exception as e:
        logging.error(f"Error al iniciar servicios: {str(e)}")
        if 'api_process' in locals():
            api_process.terminate()
        if 'telegram_process' in locals():
            telegram_process.terminate()

if __name__ == "__main__":
    start_services()
