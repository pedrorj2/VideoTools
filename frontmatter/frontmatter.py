from PIL import Image, ImageDraw
import os

def add_translucent_center_stripe(image_path, output_path, rgb_color, stripe_height_ratio, opacity):
    """
    Superpone una franja translúcida horizontal centrada de lado a lado en una imagen.
    """
    with Image.open(image_path) as img:
        width, height = img.size
        stripe_height = int(height * stripe_height_ratio)
        stripe_top = (height - stripe_height) // 2
        stripe_bottom = stripe_top + stripe_height

        # Crear una capa RGBA para superposición
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Dibujar la franja translúcida centrada
        draw.rectangle([(0, stripe_top), (width, stripe_bottom)], fill=(*rgb_color, opacity))

        # Combinar la imagen original con la franja
        combined = Image.alpha_composite(img.convert('RGBA'), overlay)
        combined.save(output_path, 'PNG')
        print(f"Procesado: {os.path.basename(image_path)} -> {os.path.basename(output_path)}")

def process_images_with_stripe(input_dir, output_dir, rgb_color, stripe_height_ratio, opacity):
    """
    Procesa todas las imágenes de un directorio agregando la franja translúcida.
    """
    # Verificar que existe el directorio input
    if not os.path.exists(input_dir):
        print(f"Creando directorio: {input_dir}")
        os.makedirs(input_dir)
        print("Coloca tus imágenes en la carpeta 'input' y ejecuta el script nuevamente.")
        return

    os.makedirs(output_dir, exist_ok=True)
    supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp')
    
    # Verificar que hay imágenes
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(supported_extensions)]
    if not image_files:
        print("No se encontraron imágenes en la carpeta 'input'.")
        print("Formatos soportados: JPG, PNG, BMP, TIFF, GIF, WebP")
        return

    processed_count = 0
    
    for filename in image_files:
        input_path = os.path.join(input_dir, filename)
        name, _ = os.path.splitext(filename)
        output_filename = f"{name}.png"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            add_translucent_center_stripe(input_path, output_path, rgb_color, stripe_height_ratio, opacity)
            processed_count += 1
        except Exception as e:
            print(f"Error procesando {filename}: {e}")
    
    print(f"\nProcesadas {processed_count} imágenes con éxito.")

if __name__ == "__main__":
    # ===== CONFIGURACIÓN - MODIFICA ESTOS VALORES =====
    
    # Color de la franja (RGB: 0-255)
    # RGB_COLOR = (52, 177, 201)  # MNP       
    RGB_COLOR = (52,177,32)   # MP
    RGB_COLOR = (30,30,180)   # EDPs
    RGB_COLOR = (178, 238, 248)
    # RGB_COLOR = (0, 128, 255)     # Azul
    # RGB_COLOR = (50, 50, 80)      # Azul oscuro espacial
    
    # Altura de la franja como porcentaje de la imagen (0.1 = 10%, 0.2 = 20%, etc.)
    STRIPE_HEIGHT_RATIO = 0.3      # 60% del alto de la imagen

    # Opacidad de la franja (0 = transparente, 255 = opaco)
    OPACITY = 200                 # Semitransparente (recomendado: 80-150)
    
    # ===== FIN DE CONFIGURACIÓN =====
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(script_dir, "input")
    output_directory = os.path.join(script_dir, "output")
    
    print("=== Generador de Franjas Translúcidas ===")
    print(f"Configuración actual:")
    print(f"  - Color: RGB{RGB_COLOR}")
    print(f"  - Altura: {STRIPE_HEIGHT_RATIO*100:.1f}% de la imagen")
    print(f"  - Opacidad: {OPACITY}/255")
    print()
    
    process_images_with_stripe(input_directory, output_directory, RGB_COLOR, STRIPE_HEIGHT_RATIO, OPACITY)
    
    if os.path.exists(output_directory):
        print(f"Imágenes guardadas en: {output_directory}")
    
    input("\nPresiona Enter para salir...")
