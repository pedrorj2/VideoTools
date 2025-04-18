from flask import Flask, request, send_file, jsonify, render_template_string
from PIL import Image, ImageDraw, ImageFont
import os
import io
import uuid
import time
import datetime
import json
from math import sqrt

app = Flask(__name__)

# Crear directorio temporal para archivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Archivo para almacenar estadísticas
STATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stats.json')

# Inicializar estadísticas
def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        'total_images': 0,
        'last_processed': None,
        'processing_history': []
    }

def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f)

def update_stats(filename, code):
    stats = load_stats()
    stats['total_images'] += 1
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    stats['last_processed'] = now

    # Limitar el historial a los últimos 10 elementos
    if len(stats['processing_history']) >= 10:
        stats['processing_history'] = stats['processing_history'][-9:]

    stats['processing_history'].append({
        'filename': filename,
        'code': code,
        'timestamp': now
    })

    save_stats(stats)

def create_watermark(input_image, output_path, file_code):
    """
    Aplica una marca de agua a una imagen.

    Args:
        input_image: Objeto de imagen PIL
        output_path: Ruta donde guardar la imagen con marca de agua
        file_code: Código único para incluir en la marca de agua

    Returns:
        bool: True si el proceso fue exitoso
    """
    watermark_text = f"@pedro.rj2 #{file_code}"

    # Usar la imagen proporcionada
    img = input_image

    # Convertir a RGB si es necesario
    if img.mode != 'RGB':
        img = img.convert('RGB')

    width, height = img.size

    # Crear una nueva imagen para la marca de agua
    txt = Image.new('RGBA', img.size, (255, 255, 255, 0))

    # Calcular tamaño de fuente basado en la diagonal de la imagen
    diagonal = sqrt(width**2 + height**2)
    font_size = int(diagonal * 0.025)  # 2.5% de la diagonal

    try:
        # Intentar usar Arial
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            # Intentar usar Times New Roman
            font = ImageFont.truetype("times.ttf", font_size)
        except:
            # Si no hay fuentes TrueType, usar la fuente por defecto
            font = ImageFont.load_default()

    # Crear objeto para dibujar
    d = ImageDraw.Draw(txt)

    # Calcular dimensiones del texto usando textbbox
    bbox = d.textbbox((0, 0), watermark_text, font=font)
    textwidth = bbox[2] - bbox[0]
    textheight = bbox[3] - bbox[1]

    # Calcular espaciado para el patrón diagonal
    x_spacing = textwidth + 50
    y_spacing = textheight + 50

    # Calcular punto de inicio para que el texto comience desde el borde
    start_x = 0
    start_y = 0

    # Dibujar marca de agua en patrón diagonal
    y = start_y
    while y < height:
        x = start_x
        while x < width:
            # Dibujar texto semi-transparente
            d.text((x, y), watermark_text, font=font, fill=(128, 128, 128, 30))
            # Dibujar texto sólido
            d.text((x+2, y+2), watermark_text, font=font, fill=(64, 64, 64, 30))
            x += x_spacing
        y += y_spacing

    # Combinar imagen original con marca de agua
    watermarked = Image.alpha_composite(img.convert('RGBA'), txt)

    # Guardar resultado
    watermarked.convert('RGB').save(output_path, 'JPEG', quality=95)
    return True

@app.route('/watermark', methods=['POST'])
def watermark_image():
    """
    Endpoint para aplicar marca de agua a una imagen.

    Espera un archivo de imagen en el campo 'image' del formulario.
    Opcionalmente puede recibir un 'code' personalizado para la marca de agua.

    Returns:
        La imagen con marca de agua o un mensaje de error.
    """
    # Verificar si se recibió un archivo
    if 'image' not in request.files:
        return jsonify({'error': 'No se envió ninguna imagen'}), 400

    file = request.files['image']

    # Verificar si el archivo tiene nombre
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ninguna imagen'}), 400

    # Obtener el código personalizado o generar uno
    file_code = request.form.get('code', str(uuid.uuid4())[:8])

    try:
        # Abrir la imagen con PIL
        img = Image.open(file.stream)

        # Generar un nombre de archivo único para la salida
        output_filename = f"{file_code}_watermarked.jpg"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)

        # Aplicar marca de agua
        create_watermark(img, output_path, file_code)

        # Actualizar estadísticas
        update_stats(file.filename, file_code)

        # Devolver la imagen procesada
        return send_file(output_path, mimetype='image/jpeg', as_attachment=True,
                         download_name=output_filename)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    """Página de inicio con instrucciones básicas y estadísticas."""
    stats = load_stats()

    # Formatear el historial para mostrarlo
    history_html = ""
    if stats['processing_history']:
        history_html = "<table border='1' cellpadding='5' cellspacing='0'>\n"
        history_html += "<tr><th>Fecha y Hora</th><th>Nombre de archivo</th><th>Código</th></tr>\n"
        for item in reversed(stats['processing_history']):
            history_html += f"<tr><td>{item['timestamp']}</td><td>{item['filename']}</td><td>{item['code']}</td></tr>\n"
        history_html += "</table>"
    else:
        history_html = "<p>Aún no se han procesado imágenes.</p>"

    return f"""
    <html>
        <head>
            <title>API de Marca de Agua</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                code {{ background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
                pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                .stats {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ text-align: left; padding: 8px; }}
                th {{ background-color: #f2f2f2; }}
            </style>
            <meta http-equiv="refresh" content="30">
        </head>
        <body>
            <h1>API de Marca de Agua</h1>
            <p>Esta API permite aplicar marcas de agua a imágenes.</p>

            <div class="stats">
                <h2>Estadísticas de Uso</h2>
                <p>Total de imágenes procesadas: <strong>{stats['total_images']}</strong></p>
                <p>Última imagen procesada: <strong>{stats['last_processed'] if stats['last_processed'] else 'Ninguna'}</strong></p>

                <h3>Últimas imágenes procesadas:</h3>
                {history_html}
            </div>

            <h2>Cómo usar:</h2>
            <h3>Usando curl:</h3>
            <pre>curl -X POST -F "image=@ruta/a/tu/imagen.jpg" -F "code=codigo_opcional" https://tu-app.fly.dev/watermark -o imagen_con_marca.jpg</pre>

            <h3>Usando Python:</h3>
            <pre>
import requests

url = "https://tu-app.fly.dev/watermark"
files = {{"image": open("ruta/a/tu/imagen.jpg", "rb")}}
data = {{"code": "codigo_opcional"}}  # El código es opcional

response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    with open("imagen_con_marca.jpg", "wb") as f:
        f.write(response.content)
    print("Imagen guardada correctamente")
else:
    print(f"Error: {{response.json()}}")
            </pre>

            <h3>Usando Telegram:</h3>
            <p>Envía una imagen a nuestro bot de Telegram <code>@TuBotDeWatermark</code> y recibirás la imagen con marca de agua como respuesta.</p>

            <h3>Parámetros:</h3>
            <ul>
                <li><code>image</code>: La imagen a la que se aplicará la marca de agua (obligatorio)</li>
                <li><code>code</code>: Código personalizado para la marca de agua (opcional)</li>
            </ul>
        </body>
    </html>
    """

# Limpiar archivos temporales periódicamente (en una aplicación real deberías usar un job programado)
@app.after_request
def cleanup_old_files(response):
    """Elimina archivos temporales antiguos después de cada solicitud."""
    try:
        # En una aplicación real, deberías usar un criterio más sofisticado
        # como eliminar archivos más antiguos que cierto tiempo
        files = os.listdir(UPLOAD_FOLDER)
        if len(files) > 100:  # Mantener un máximo de 100 archivos
            for file in sorted(files)[:-100]:
                os.remove(os.path.join(UPLOAD_FOLDER, file))
    except Exception:
        pass  # No interrumpir la respuesta si hay un error en la limpieza
    return response

if __name__ == '__main__':
    # Usar el puerto proporcionado por el entorno o 8080 por defecto
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
