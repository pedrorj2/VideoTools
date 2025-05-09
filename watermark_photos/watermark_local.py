
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from math import sqrt

def create_watermark(input_image_path, output_path, file_code):
    watermark_text = f"@pedro.rj2 #{file_code}"
    
    # Abrir imagen
    with Image.open(input_image_path) as img:
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

def process_directory(input_dir, output_dir):
    if not os.path.exists(input_dir):
        return

    os.makedirs(output_dir, exist_ok=True)
    supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_extensions):
            input_path = os.path.join(input_dir, filename)
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_watermark{ext}"
            output_path = os.path.join(output_dir, output_filename)
            
            try:
                print(f"Procesando: {filename}")
                create_watermark(
                    input_path,
                    output_path,
                    name  # Usando el nombre del archivo como código
                )
                print(f"Completado: {filename}")
            except Exception as e:
                print(f"Error procesando {filename}: {str(e)}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(script_dir, "input")
    output_directory = os.path.join(script_dir, "output")
    
    os.makedirs(input_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)
    
    process_directory(input_directory, output_directory)





