import cv2
import numpy as np
from pathlib import Path

MAX_OCR_SIDE = 3800


def prepare_ocr_image_variants(image_path: str, output_dir: str = None) -> list[str]:
    """
    Creates OCR candidates from the same rendered page. Some clean PDFs read
    better without aggressive preprocessing, while scans often benefit from it.
    """
    if output_dir is None:
        output_dir = str(Path(image_path).parent)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    variants = []
    limited_original = _save_limited_original(image_path, output_dir)
    if limited_original:
        variants.append(limited_original)
    variants.append(preprocess_image(image_path, output_dir))
    return _unique_paths(variants)


def preprocess_image(image_path: str, output_dir: str = None) -> str:
    """
    Aplica técnicas de preprocesamiento a una imagen para mejorar la lectura OCR.
    Incluye:
    - Conversión a escala de grises.
    - Aumento de contraste (CLAHE).
    - Reducción de ruido.
    - (Opcional) Corrección de sesgo/inclinación.
    
    Retorna la ruta de la imagen procesada.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"No se pudo cargar la imagen: {image_path}")
    img = _limit_image_side(img)

    # 1. Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Corrección de inclinación (Deskew) simplificada
    # Calculamos las coordenadas de los píxeles no blancos
    coords = np.column_stack(np.where(gray < 250))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        # Ajuste de ángulo para cv2.minAreaRect
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        # Si el ángulo es muy pequeño, lo ignoramos para no distorsionar
        if abs(angle) > 0.5 and abs(angle) < 15:
            (h, w) = gray.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # 3. Mejora de contraste usando CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # 4. Reducción de ruido (filtro bilateral preserva bordes)
    denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # Binarización adaptativa opcional (se puede activar si PaddleOCR batalla con fondos)
    # thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Guardar imagen procesada
    if output_dir is None:
        output_dir = str(Path(image_path).parent)
    else:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
    base_name = Path(image_path).name
    processed_path = str(Path(output_dir) / f"processed_{base_name}")
    
    cv2.imwrite(processed_path, denoised)
    return processed_path


def _save_limited_original(image_path: str, output_dir: str) -> str | None:
    img = cv2.imread(image_path)
    if img is None:
        return None
    img = _limit_image_side(img)
    output_path = str(Path(output_dir) / f"ocr_original_{Path(image_path).name}")
    cv2.imwrite(output_path, img)
    return output_path


def _unique_paths(paths: list[str]) -> list[str]:
    unique = []
    seen = set()
    for path in paths:
        if not path or path in seen:
            continue
        seen.add(path)
        unique.append(path)
    return unique


def _limit_image_side(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    longest_side = max(height, width)
    if longest_side <= MAX_OCR_SIDE:
        return image

    scale = MAX_OCR_SIDE / longest_side
    resized_width = max(1, round(width * scale))
    resized_height = max(1, round(height * scale))
    return cv2.resize(image, (resized_width, resized_height), interpolation=cv2.INTER_AREA)
