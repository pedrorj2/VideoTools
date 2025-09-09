from PIL import Image
import os

def crop_to_aspect_ratio(image_path, target_ratio):
    with Image.open(image_path) as img:
        width, height = img.size
        current_ratio = width / height
        
        target_width, target_height = map(int, target_ratio.split(':'))
        target_ratio_num = target_width / target_height
        
        if current_ratio > target_ratio_num:
            # Crop sides
            new_width = int(height * target_ratio_num)
            left = (width - new_width) // 2
            right = left + new_width
            cropped = img.crop((left, 0, right, height))
        else:
            # Crop top/bottom
            new_height = int(width / target_ratio_num)
            top = (height - new_height) // 2
            bottom = top + new_height
            cropped = img.crop((0, top, width, bottom))
        
        return cropped

def process_images(input_dir, output_dir, target_ratio):
    os.makedirs(output_dir, exist_ok=True)
    supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp')

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_extensions):
            input_path = os.path.join(input_dir, filename)
            name, _ = os.path.splitext(filename)  # Remove original extension
            output_filename = f"{name}.png"  # Always use .png
            output_path = os.path.join(output_dir, output_filename)
            
            try:
                cropped_img = crop_to_aspect_ratio(input_path, target_ratio)
                cropped_img.save(output_path, 'PNG')  # Save as PNG format
                print(f"Procesado y convertido a PNG: {filename} -> {output_filename}")
            except Exception as e:
                print(f"Error con {filename}: {e}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(script_dir, "input")
    output_directory = os.path.join(script_dir, "output")
    
    target_ratio = input("Ingrese el factor de forma deseado (ej: 16:9): ").strip()
    
    process_images(input_directory, output_directory, target_ratio)