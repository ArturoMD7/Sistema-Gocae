import fitz  # PyMuPDF
import re

def extract_sat_data(pdf_path: str, file_name: str, rel_path: str) -> dict | None:
    """
    Extracts data from a SAT PDF file.
    Returns None if it's not a valid SAT document.
    """
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            return None
            
        page = doc[0]
        text = page.get_text("text")
        doc.close()
    except Exception as e:
        return None
        
    text_upper = text.upper()
    
    # Exclude normal transfer receipts
    if "IMPORTE A TRANSFERIR" in text_upper:
        return None
        
    # Check for SAT indicators
    if "INFORMACIÓN REGISTRADA DE PAGOS DE CONTRIBUCIONES FEDERALES" not in text_upper and "SERVICIO DE ADMINISTRACIÓN TRIBUTARIA" not in text_upper and "LÍNEA DE CAPTURA" not in text_upper:
        return None

    # Base dictionary
    data = {
        "Emisor": "SAT",
        "RFC EMISOR": "",
        "Fecha de emisión": "",
        "Concepto de pago 1": "",
        "Cantidad a pagar": "",
        "Línea de Captura": "",
        "Vigente hasta": "",
        "Archivo": file_name,
        "Ruta": rel_path,
        "Estado": "Validado",
        "Alertas": ""
    }

    # Helper function for regex search
    def extract_field(pattern, text_target, default=""):
        match = re.search(pattern, text_target, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
        return default

    # RFC: sometimes comes right after "RFC:"
    data["RFC EMISOR"] = extract_field(r"RFC:\s*([A-Z0-9]+)", text)
    
    # Fecha de emisión:
    fecha = extract_field(r"Fecha y [Hh]ora de emisi[oó]n:\s*(\d{2}/\d{2}/\d{4})", text)
    if not fecha:
        fecha = extract_field(r"Fecha y [Hh]ora de presentaci[oó]n:\s*(\d{2}/\d{2}/\d{4})", text)
    data["Fecha de emisión"] = fecha
    
    # Concepto de pago: puede ser 1, 2, etc.
    data["Concepto de pago 1"] = extract_field(r"Concepto de pago \d+:\s*(.*)", text)
    
    # Cantidad a pagar (can be next to 'Cantidad a pagar:' or 'Importe total a pagar:')
    cantidad = extract_field(r"Cantidad a pagar:\s*([\d,\.]+)", text)
    if not cantidad:
        cantidad = extract_field(r"Importe total a pagar:\s*\$?\s*([\d,\.]+)", text)
    data["Cantidad a pagar"] = cantidad
    
    # Línea de captura
    captura_match = re.search(r"L[ií]nea de[ \n]*Captura:?\s*([\w\s]{20,28})(?=\s*Importe|\s*Vigente|\n|$)", text, re.IGNORECASE)
    if captura_match:
        data["Línea de Captura"] = captura_match.group(1).strip()
    else:
        # Fallback: buscar el patrón clásico de 20 caracteres (5 bloques de 4)
        captura_match = re.search(r"\b([A-Z0-9]{4}\s+[A-Z0-9]{4}\s+[A-Z0-9]{4}\s+[A-Z0-9]{4}\s+[A-Z0-9]{4})\b", text, re.IGNORECASE)
        if captura_match:
            data["Línea de Captura"] = captura_match.group(1).strip()
            
    if data["Línea de Captura"]:
        # Clean up line breaks or extra spaces
        data["Línea de Captura"] = re.sub(r'\s+', ' ', data["Línea de Captura"]).strip()
        
    # Vigente hasta
    data["Vigente hasta"] = extract_field(r"Vigente hasta:\s*(\d{2}/\d{2}/\d{4})", text)

    # Some validation if fields are missing
    missing = []
    for k, v in data.items():
        if k not in ["Alertas", "Archivo", "Ruta", "Estado", "Emisor"] and not v:
            missing.append(k)
            
    if missing:
        data["Alertas"] = f"Faltan campos: {', '.join(missing)}"
        data["Estado"] = "Requiere revision"
        
    data["Texto Extraido"] = text

    return data
