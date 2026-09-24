import re


def _normalize_text(text: str) -> str:
    text = (text or "").lower()
    replacements = {
        "\u00e1": "a",
        "\u00e9": "e",
        "\u00ed": "i",
        "\u00f3": "o",
        "\u00fa": "u",
        "\u00fc": "u",
        "\u00f1": "n",
        "\u00c3\u00a1": "a",
        "\u00c3\u00a9": "e",
        "\u00c3\u00ad": "i",
        "\u00c3\u00b3": "o",
        "\u00c3\u00ba": "u",
        "\u00c3\u00bc": "u",
        "\u00c3\u00b1": "n",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return re.sub(r"\s+", " ", text).strip()


def detect_currency(text: str) -> str:
    """
    Detecta la moneda en un texto basado en palabras clave.
    Retorna 'USD', 'MXN', 'INCIERTO' o 'DESCONOCIDO'.
    """
    text_lower = _normalize_text(text)

    usd_keywords = ["usd", "us$", "dolares", "dollars", "u.s. dollars", "dls", "dlls"]
    mxn_keywords = ["mxn", "m.n.", "mn", "pesos", "moneda nacional"]

    if any(keyword in text_lower for keyword in usd_keywords):
        return "USD"
    if any(keyword in text_lower for keyword in mxn_keywords):
        return "MXN"
    if "$" in (text or ""):
        return "INCIERTO"
    return "DESCONOCIDO"


def clean_amount(amount_str: str) -> float:
    """
    Limpia un monto y lo convierte a float.
    Soporta 410,588.18 y, cuando aplica, 410.588,18.
    """
    if not amount_str:
        return None

    text = str(amount_str).strip()
    negative = text.startswith("-") or (text.startswith("(") and text.endswith(")"))
    clean_str = re.sub(r"[^0-9,.\-]", "", text).replace("-", "")
    if not clean_str:
        return None

    last_dot = clean_str.rfind(".")
    last_comma = clean_str.rfind(",")
    if last_dot >= 0 and last_comma >= 0:
        decimal_separator = "." if last_dot > last_comma else ","
        thousands_separator = "," if decimal_separator == "." else "."
        clean_str = clean_str.replace(thousands_separator, "")
        clean_str = clean_str.replace(decimal_separator, ".")
    elif last_comma >= 0:
        parts = clean_str.split(",")
        clean_str = "".join(parts[:-1]) + "." + parts[-1] if len(parts[-1]) == 2 else clean_str.replace(",", "")
    elif clean_str.count(".") > 1:
        parts = clean_str.split(".")
        clean_str = "".join(parts[:-1]) + "." + parts[-1]

    match = re.search(r"\d+(?:\.\d+)?", clean_str)
    if not match:
        return None
    try:
        amount = float(match.group())
        return -amount if negative else amount
    except ValueError:
        return None


def validate_amounts(subtotal: float, tax: float, total: float, tolerance: float = 0.05) -> bool:
    if subtotal is None or total is None:
        return False
    if tax is None:
        tax = 0.0
    calculated_total = subtotal + tax
    return abs(calculated_total - total) <= tolerance


def validate_extraction_confidence(confidence: float, threshold: float = 0.85) -> str:
    if confidence >= threshold:
        return "Validado"
    if confidence > 0.5:
        return "Requiere revision"
    return "Error"
