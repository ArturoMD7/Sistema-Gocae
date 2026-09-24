import json
import re
import urllib.error
import urllib.request
from statistics import mean

from src.validators import clean_amount, detect_currency


OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_LLM_MODEL = "qwen2.5:7b-instruct"
MONEY_RE = re.compile(
    r"(?:US\$|\$|USD)\s*-?\(?(?:\d+(?:[,.]\d{3})+|\d+)(?:[,.]\d{1,2})?\)?|"
    r"(?<![\w.])-?\(?\d+(?:[,.]\d{3})+(?:[,.]\d{1,2})?\)?|"
    r"(?<![\w.])-?\(?\d+\.\d{2}\)?"
)

GENERAL_FIELDS = [
    "Emisor",
    "Partner Receptor",
    "Contrato",
    "Date",
    "Accounting Period",
    "Reference",
    "Payment Due Date",
    "Currency",
    "Total Current Period",
    "PEMEX Participation %",
    "Partner Participation %",
    "Amount Due by PEMEX",
    "Amount Due by Partner",
]
MONETARY_GENERAL_FIELDS = {
    "Total Current Period",
    "Amount Due by PEMEX",
    "Amount Due by Partner",
}
PERCENT_FIELDS = {"PEMEX Participation %", "Partner Participation %"}


def parse_cash_call_text_with_llm(
    ocr_text: str,
    file_name: str,
    ocr_data: list[dict],
    concept_fields: list[str],
    model: str = DEFAULT_LLM_MODEL,
    ollama_url: str = OLLAMA_URL,
) -> dict:
    ocr_text = ocr_text or ""
    raw_response = ""
    try:
        raw_response = _ask_ollama(
            _build_prompt(ocr_text, concept_fields),
            model=model,
            ollama_url=ollama_url,
        )
        payload = _extract_json(raw_response)
        record = _record_from_llm_payload(payload, ocr_text, file_name, ocr_data, concept_fields, raw_response)
    except Exception as exc:
        record = _empty_record(ocr_text, file_name, ocr_data, concept_fields)
        record["Alertas"] = f"Error LLM: {exc}"
        record["Estado"] = "Error"
        record["Fuente Extraccion"] = "LLM"
        record["Respuesta LLM"] = raw_response
        return record

    record["Fuente Extraccion"] = "LLM"
    return record


def _ask_ollama(prompt: str, model: str, ollama_url: str) -> str:
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        ollama_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError("No se pudo conectar con Ollama. Verifica que 'ollama serve' este activo.") from exc
    return str(data.get("response") or "")


def _build_prompt(ocr_text: str, concept_fields: list[str]) -> str:
    concepts = "\n".join(f"- {field}" for field in concept_fields)
    amounts = ", ".join(_amount_tokens_from_text(ocr_text))
    return f"""
Eres un parser contable para Cash Calls. Vas a recibir texto OCR que puede tener montos desplazados una linea arriba o abajo.

Tarea:
- Devuelve SOLO un JSON valido, sin markdown.
- Usa exactamente estas llaves de salida: {json.dumps(GENERAL_FIELDS + concept_fields, ensure_ascii=False)}.
- Si un campo no aparece, usa null.
- Para conceptos, usa SOLO estos nombres oficiales:
{concepts}
- No inventes conceptos ni montos.
- Los montos deben salir exactamente de los montos vistos en el OCR. Puedes normalizar separadores, pero no cambiar digitos.
- Si una cantidad esta antes/despues del concepto por error del OCR, alineala como lo haria un humano.
- "Total Current Period" debe ser el total del periodo actual, no subtotales ni montos a pagar por socio.
- Devuelve numeros como numero JSON, no como texto.

Montos detectados en OCR:
{amounts}

Texto OCR:
{ocr_text[:12000]}
""".strip()


def _extract_json(raw_response: str) -> dict:
    text = raw_response.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise RuntimeError("El LLM no devolvio JSON valido.")
        data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise RuntimeError("El JSON del LLM no es un objeto.")
    return data


def _record_from_llm_payload(
    payload: dict,
    ocr_text: str,
    file_name: str,
    ocr_data: list[dict],
    concept_fields: list[str],
    raw_response: str,
) -> dict:
    record = _empty_record(ocr_text, file_name, ocr_data, concept_fields)
    available_amounts = _amount_values_from_text(ocr_text)
    ignored = []

    for field in GENERAL_FIELDS:
        value = payload.get(field)
        if field in PERCENT_FIELDS:
            record[field] = _coerce_float(value, allow_percent=True)
        elif field in MONETARY_GENERAL_FIELDS:
            record[field] = _validated_amount(value, available_amounts, field, ignored)
        elif field == "Currency":
            record[field] = str(value).strip() if value not in (None, "") else detect_currency(ocr_text)
        else:
            record[field] = str(value).strip() if value not in (None, "") else None

    concepts_payload = payload.get("concepts") if isinstance(payload.get("concepts"), dict) else {}
    for field in concept_fields:
        value = payload.get(field, concepts_payload.get(field))
        record[field] = _validated_amount(value, available_amounts, field, ignored)

    record["Respuesta LLM"] = raw_response
    alerts = _build_alerts(record, concept_fields, ignored)
    record["Alertas"] = "; ".join(alerts)
    record["Estado"] = "Requiere revision" if alerts else "Validado"
    return record


def _empty_record(ocr_text: str, file_name: str, ocr_data: list[dict], concept_fields: list[str]) -> dict:
    return {
        "Archivo": file_name,
        "Emisor": None,
        "Partner Receptor": None,
        "Contrato": None,
        "Date": None,
        "Accounting Period": None,
        "Reference": None,
        "Payment Due Date": None,
        "Currency": detect_currency(ocr_text),
        **{field: None for field in concept_fields},
        "Total Current Period": None,
        "PEMEX Participation %": None,
        "Partner Participation %": None,
        "Amount Due by PEMEX": None,
        "Amount Due by Partner": None,
        "Overall Confidence": round(_overall_confidence(ocr_data), 4),
        "OCR Lines": len([line for line in ocr_text.splitlines() if line.strip()]),
        "Alertas": "",
        "Estado": "Requiere revision",
        "Texto OCR": ocr_text,
        "Fuente Extraccion": "LLM",
        "Respuesta LLM": "",
    }


def _build_alerts(record: dict, concept_fields: list[str], ignored: list[str]) -> list[str]:
    required = [
        "Emisor",
        "Partner Receptor",
        "Contrato",
        "Date",
        "Payment Due Date",
        "Total Current Period",
        "PEMEX Participation %",
        "Partner Participation %",
    ]
    alerts = []
    missing = [field for field in required if record.get(field) in (None, "")]
    if missing:
        alerts.append("Campos faltantes: " + ", ".join(missing))

    concept_amounts = [record.get(field) for field in concept_fields if record.get(field) is not None]
    total = record.get("Total Current Period")
    if total is not None and concept_amounts:
        concepts_sum = round(sum(concept_amounts), 2)
        if abs(concepts_sum - total) > 0.05:
            alerts.append(f"Total no cuadra con conceptos: conceptos={concepts_sum:,.2f}, total={total:,.2f}")
    if ignored:
        alerts.append("Montos LLM ignorados: " + ", ".join(ignored[:8]))
    return alerts


def _validated_amount(value, available_amounts: list[float], field: str, ignored: list[str]) -> float | None:
    amount = _coerce_float(value)
    if amount is None:
        return None
    if not _amount_exists(amount, available_amounts):
        ignored.append(f"{field}={amount:,.2f}")
        return None
    return amount


def _coerce_float(value, allow_percent: bool = False) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    text = str(value).strip()
    if allow_percent:
        text = text.replace("%", "")
        try:
            return round(float(text), 2)
        except ValueError:
            return None
    return clean_amount(text)


def _amount_exists(amount: float, available_amounts: list[float]) -> bool:
    return any(abs(amount - candidate) <= 0.05 for candidate in available_amounts)


def _amount_values_from_text(text: str) -> list[float]:
    values = []
    for token in _amount_tokens_from_text(text):
        value = clean_amount(token)
        if value is not None:
            values.append(value)
    return values


def _amount_tokens_from_text(text: str) -> list[str]:
    tokens = []
    for match in MONEY_RE.finditer(text or ""):
        token = match.group(0).strip()
        if "%" not in token:
            tokens.append(token)
    return tokens


def _overall_confidence(ocr_data: list[dict]) -> float:
    confidences = [float(item.get("confidence") or 0) for item in ocr_data or []]
    return mean(confidences) if confidences else 0.0
