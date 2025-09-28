import ocrmypdf

def procesar_pdf(input_pdf, output_pdf):
    try:
        ocrmypdf.ocr(input_pdf, output_pdf, use_threads=True)
        print(f"PDF procesado con éxito. Archivo guardado en: {output_pdf}")
    except Exception as e:
        print(f"Error al procesar el PDF: {e}")

if __name__ == "__main__":
    input_pdf = "input.pdf"      # Cambia aquí la ruta de tu archivo PDF de entrada
    output_pdf = "output_ocr.pdf"  # Cambia aquí la ruta del archivo PDF de salida
    procesar_pdf(input_pdf, output_pdf)
