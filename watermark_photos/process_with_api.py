import os
import requests
import time
from pathlib import Path

def process_images_with_api(input_dir, output_dir, api_url="http://localhost:8080/watermark"):
    """
    Procesa todas las imágenes en la carpeta de entrada usando la API de marca de agua
    y guarda los resultados en la carpeta de salida.
    
    Args:
        input_dir: Directorio donde se encuentran las imágenes originales
        output_dir: Directorio donde se guardarán las imágenes con marca de agua
        api_url: URL de la API de marca de agua
    """
    # Crear la carpeta de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Extensiones de archivo soportadas
    supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    
    # Contador para estadísticas
    total_images = 0
    successful_images = 0
    failed_images = 0
    
    print(f"Procesando imágenes de {input_dir}...")
    
    # Procesar cada imagen en la carpeta de entrada
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_extensions):
            input_path = os.path.join(input_dir, filename)
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_watermarked{ext}"
            output_path = os.path.join(output_dir, output_filename)
            
            total_images += 1
            
            try:
                print(f"Procesando: {filename}")
                
                # Abrir el archivo de imagen
                with open(input_path, 'rb') as img_file:
                    # Preparar los datos para la solicitud
                    files = {'image': (filename, img_file, f'image/{ext[1:]}')}
                    data = {'code': name}  # Usar el nombre del archivo como código
                    
                    # Enviar la solicitud a la API
                    response = requests.post(api_url, files=files, data=data)
                    
                    # Verificar si la solicitud fue exitosa
                    if response.status_code == 200:
                        # Guardar la imagen procesada
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        
                        print(f"✓ Completado: {filename} -> {output_filename}")
                        successful_images += 1
                    else:
                        print(f"✗ Error en la API: {response.status_code} - {response.text}")
                        failed_images += 1
                
                # Pequeña pausa para no sobrecargar la API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"✗ Error procesando {filename}: {str(e)}")
                failed_images += 1
    
    # Mostrar estadísticas
    print("\n--- Resumen ---")
    print(f"Total de imágenes encontradas: {total_images}")
    print(f"Imágenes procesadas exitosamente: {successful_images}")
    print(f"Imágenes con errores: {failed_images}")
    
    if successful_images > 0:
        print(f"\nLas imágenes procesadas se guardaron en: {output_dir}")

if __name__ == "__main__":
    # Obtener la ruta del script
    script_dir = Path(__file__).parent.absolute()
    
    # Definir las carpetas de entrada y salida
    input_directory = os.path.join(script_dir, "input")
    output_directory = os.path.join(script_dir, "output")
    
    # URL de la API (ajustar si es necesario)
    api_url = "http://localhost:8080/watermark"
    
    # Procesar las imágenes
    process_images_with_api(input_directory, output_directory, api_url)
