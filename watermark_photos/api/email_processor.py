import os
import time
import imaplib
import email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import tempfile
import requests
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("email_processor.log"),
        logging.StreamHandler()
    ]
)

# Configuración de correo electrónico
EMAIL_ADDRESS = "tu_correo@gmail.com"  # Reemplaza con tu dirección de correo
EMAIL_PASSWORD = "tu_contraseña"  # Reemplaza con tu contraseña o contraseña de aplicación
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Configuración de la API
API_URL = "http://localhost:8080/watermark"  # Cambia a la URL de tu API en producción

def check_emails():
    """
    Verifica los correos electrónicos no leídos, procesa las imágenes adjuntas
    y envía las versiones con marca de agua como respuesta.
    """
    try:
        # Conectar al servidor IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select('inbox')
        
        # Buscar correos no leídos
        status, messages = mail.search(None, 'UNSEEN')
        
        if status != 'OK':
            logging.error("Error al buscar correos no leídos")
            return
        
        # Obtener IDs de mensajes
        message_ids = messages[0].split()
        
        if not message_ids:
            logging.info("No hay correos nuevos para procesar")
            return
        
        logging.info(f"Encontrados {len(message_ids)} correos nuevos")
        
        # Procesar cada correo
        for msg_id in message_ids:
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            
            if status != 'OK':
                logging.error(f"Error al obtener el correo {msg_id}")
                continue
            
            # Parsear el mensaje
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Obtener información del remitente
            from_address = email.utils.parseaddr(email_message['From'])[1]
            subject = email_message['Subject'] or "Sin asunto"
            
            logging.info(f"Procesando correo de {from_address} con asunto: {subject}")
            
            # Buscar adjuntos
            attachments = []
            processed_images = []
            
            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                
                filename = part.get_filename()
                if not filename:
                    continue
                
                # Verificar si es una imagen
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                    logging.info(f"Encontrado adjunto: {filename}")
                    
                    # Guardar el adjunto temporalmente
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp:
                        temp.write(part.get_payload(decode=True))
                        temp_path = temp.name
                    
                    attachments.append((filename, temp_path))
            
            # Si no hay adjuntos, enviar un mensaje informativo
            if not attachments:
                send_email(
                    to_address=from_address,
                    subject=f"Re: {subject} - No se encontraron imágenes",
                    body="No se encontraron imágenes adjuntas en tu correo. Por favor, adjunta al menos una imagen para aplicar la marca de agua.",
                    attachments=[]
                )
                logging.info(f"No se encontraron imágenes en el correo de {from_address}")
                continue
            
            # Procesar cada imagen
            for filename, temp_path in attachments:
                try:
                    # Enviar la imagen a la API
                    with open(temp_path, 'rb') as img_file:
                        files = {'image': (filename, img_file, f'image/{os.path.splitext(filename)[1][1:]}')}
                        data = {'code': os.path.splitext(filename)[0]}
                        
                        response = requests.post(API_URL, files=files, data=data)
                        
                        if response.status_code == 200:
                            # Guardar la imagen procesada temporalmente
                            output_filename = f"{os.path.splitext(filename)[0]}_watermarked{os.path.splitext(filename)[1]}"
                            output_path = os.path.join(tempfile.gettempdir(), output_filename)
                            
                            with open(output_path, 'wb') as f:
                                f.write(response.content)
                            
                            processed_images.append((output_filename, output_path))
                            logging.info(f"Imagen {filename} procesada correctamente")
                        else:
                            logging.error(f"Error al procesar la imagen {filename}: {response.status_code} - {response.text}")
                except Exception as e:
                    logging.error(f"Error al procesar la imagen {filename}: {str(e)}")
            
            # Eliminar archivos temporales de entrada
            for _, temp_path in attachments:
                try:
                    os.unlink(temp_path)
                except:
                    pass
            
            # Enviar correo con las imágenes procesadas
            if processed_images:
                send_email(
                    to_address=from_address,
                    subject=f"Re: {subject} - Imágenes con marca de agua",
                    body=f"Hola,\n\nAdjunto encontrarás {len(processed_images)} imagen(es) con marca de agua.\n\nGracias por usar nuestro servicio.",
                    attachments=processed_images
                )
                logging.info(f"Enviado correo con {len(processed_images)} imágenes procesadas a {from_address}")
            else:
                send_email(
                    to_address=from_address,
                    subject=f"Re: {subject} - Error al procesar imágenes",
                    body="Lo sentimos, hubo un error al procesar tus imágenes. Por favor, intenta nuevamente más tarde.",
                    attachments=[]
                )
                logging.info(f"Enviado correo de error a {from_address}")
            
            # Eliminar archivos temporales de salida
            for _, temp_path in processed_images:
                try:
                    os.unlink(temp_path)
                except:
                    pass
        
        # Cerrar conexión
        mail.close()
        mail.logout()
        
    except Exception as e:
        logging.error(f"Error al procesar correos: {str(e)}")

def send_email(to_address, subject, body, attachments):
    """
    Envía un correo electrónico con archivos adjuntos.
    
    Args:
        to_address: Dirección de correo del destinatario
        subject: Asunto del correo
        body: Cuerpo del mensaje
        attachments: Lista de tuplas (nombre_archivo, ruta_archivo)
    """
    try:
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_address
        msg['Subject'] = subject
        
        # Agregar cuerpo del mensaje
        msg.attach(MIMEText(body, 'plain'))
        
        # Agregar adjuntos
        for filename, filepath in attachments:
            attachment = open(filepath, "rb")
            
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {filename}")
            
            msg.attach(part)
            attachment.close()
        
        # Conectar al servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        # Enviar correo
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_address, text)
        
        # Cerrar conexión
        server.quit()
        
        return True
    except Exception as e:
        logging.error(f"Error al enviar correo a {to_address}: {str(e)}")
        return False

def run_email_processor():
    """
    Ejecuta el procesador de correos en un bucle infinito.
    """
    logging.info("Iniciando procesador de correos electrónicos")
    
    while True:
        try:
            check_emails()
        except Exception as e:
            logging.error(f"Error en el ciclo principal: {str(e)}")
        
        # Esperar antes de verificar nuevamente
        logging.info("Esperando 60 segundos antes de verificar nuevamente...")
        time.sleep(60)

if __name__ == "__main__":
    run_email_processor()
