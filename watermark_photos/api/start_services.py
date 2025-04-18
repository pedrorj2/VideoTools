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
        logging.FileHandler("services.log"),
        logging.StreamHandler()
    ]
)

def start_services():
    """
    Inicia la API y el procesador de correos electrónicos como procesos separados.
    """
    try:
        # Obtener la ruta del directorio actual
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Comando para iniciar la API
        api_cmd = [sys.executable, os.path.join(current_dir, 'app.py')]
        
        # Comando para iniciar el procesador de correos
        email_cmd = [sys.executable, os.path.join(current_dir, 'email_processor.py')]
        
        # Iniciar la API
        logging.info("Iniciando la API...")
        api_process = subprocess.Popen(api_cmd)
        
        # Esperar a que la API esté lista
        logging.info("Esperando a que la API esté lista...")
        time.sleep(5)
        
        # Iniciar el procesador de correos
        logging.info("Iniciando el procesador de correos electrónicos...")
        email_process = subprocess.Popen(email_cmd)
        
        logging.info("Todos los servicios iniciados correctamente")
        
        # Manejar la terminación de los procesos
        def signal_handler(sig, frame):
            logging.info("Deteniendo servicios...")
            api_process.terminate()
            email_process.terminate()
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
            
            if email_process.poll() is not None:
                logging.error("El procesador de correos se ha detenido inesperadamente. Reiniciando...")
                email_process = subprocess.Popen(email_cmd)
            
            time.sleep(10)
    
    except KeyboardInterrupt:
        logging.info("Deteniendo servicios...")
        if 'api_process' in locals():
            api_process.terminate()
        if 'email_process' in locals():
            email_process.terminate()
    
    except Exception as e:
        logging.error(f"Error al iniciar servicios: {str(e)}")
        if 'api_process' in locals():
            api_process.terminate()
        if 'email_process' in locals():
            email_process.terminate()

if __name__ == "__main__":
    start_services()
