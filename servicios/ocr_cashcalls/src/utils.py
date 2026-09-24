import fitz  # PyMuPDF
import cv2
import numpy as np
from pathlib import Path

def pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 300) -> list[str]:
    """
    Convierte un archivo PDF a una lista de imágenes (una por página).
    Retorna la lista de rutas de las imágenes generadas.
    """
    pdf_document = fitz.open(pdf_path)
    image_paths = []
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    base_name = Path(pdf_path).stem
    
    # Zoom para aumentar la resolución basada en DPI (DPI base de PDF es usualmente 72)
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        output_path = str(Path(output_dir) / f"{base_name}_page_{page_num + 1}.png")
        pix.save(output_path)
        image_paths.append(output_path)
        
    pdf_document.close()
    return image_paths
