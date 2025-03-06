import os
import shutil
from pymediainfo import MediaInfo

def es_video_vertical(video_path):
    media_info = MediaInfo.parse(video_path)
    rotation = 0
    width = height = None

    for track in media_info.tracks:
        if track.track_type == 'Video':
            width = track.width
            height = track.height
            rotation_str = getattr(track, 'rotation', '0').strip()

            # Manejo robusto de decimales en la rotación
            try:
                rotation = int(float(rotation_str))
            except (ValueError, TypeError):
                rotation = 0

            if rotation in [90, 270]:
                width, height = height, width
            break

    if width is None or height is None:
        raise ValueError("No se pudieron obtener dimensiones")

    return height > width

def separar_videos_por_orientacion(input_carpeta, output_carpeta):
    vertical_dir = os.path.join(output_carpeta, 'vertical')
    horizontal_dir = os.path.join(output_carpeta, 'horizontal')

    os.makedirs(vertical_dir, exist_ok=True)
    os.makedirs(horizontal_dir, exist_ok=True)

    for archivo in os.listdir(input_carpeta):
        ruta_archivo = os.path.join(input_carpeta, archivo)
        if archivo.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            try:
                if es_video_vertical(ruta_archivo):
                    destino = os.path.join(vertical_dir, archivo)
                    orientacion = "vertical"
                else:
                    destino = os.path.join(horizontal_dir, archivo)
                    orientacion = "horizontal"

                shutil.move(ruta_archivo, destino)
                print(f"Movido {archivo} a {orientacion}")
            except Exception as e:
                print(f"Error con {archivo}: {e}")

if __name__ == '__main__':
    input_carpeta = r'C:\Users\Pedro\Desktop\VideoTools\video_orientation\input\Hangzhou'
    output_carpeta = r'C:\Users\Pedro\Desktop\VideoTools\video_orientation\output\Hangzhou'

    separar_videos_por_orientacion(input_carpeta, output_carpeta)
