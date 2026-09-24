from src.database import get_connection

def save_correction(original_text: str, corrected_text: str):
    """
    Guarda una corrección hecha por el usuario en la base de datos.
    Si la corrección ya existe (basado en original_text), se actualiza.
    """
    if not original_text or not corrected_text or original_text == corrected_text:
        return
        
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO ocr_corrections (original_text, corrected_text)
            VALUES (?, ?)
            ON CONFLICT(original_text) DO UPDATE SET corrected_text=excluded.corrected_text
        ''', (original_text, corrected_text))
        conn.commit()
    except Exception as e:
        print(f"Error al guardar corrección: {e}")
    finally:
        conn.close()

def get_all_corrections() -> dict:
    """
    Obtiene todas las correcciones como un diccionario {original: corrected}.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT original_text, corrected_text FROM ocr_corrections')
    rows = cursor.fetchall()
    conn.close()
    
    return {row['original_text']: row['corrected_text'] for row in rows}

def apply_corrections(text: str, corrections: dict | None = None) -> str:
    """
    Aplica las correcciones conocidas a un texto dado.
    """
    if not text:
        return text
        
    corrections = corrections if corrections is not None else get_all_corrections()
    
    # Primero buscamos coincidencias exactas para reemplazar toda la palabra
    if text in corrections:
        return corrections[text]
        
    # Luego podríamos implementar reemplazos parciales si se considera necesario,
    # aunque para valores financieros es mejor reemplazos exactos para evitar
    # falsos positivos. De momento, retornamos el texto si no hay coincidencia exacta.
    return text

def save_field_alias(alias_name: str, canonical_name: str):
    """
    Guarda un alias para un campo, ej. "Total Amount" -> "Total"
    """
    if not alias_name or not canonical_name:
        return
        
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO field_aliases (alias_name, canonical_name)
            VALUES (?, ?)
            ON CONFLICT(alias_name) DO UPDATE SET canonical_name=excluded.canonical_name
        ''', (alias_name, canonical_name))
        conn.commit()
    except Exception as e:
        print(f"Error al guardar alias: {e}")
    finally:
        conn.close()
