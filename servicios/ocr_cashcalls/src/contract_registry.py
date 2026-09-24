import re
import unicodedata

import pandas as pd

from src.database import get_connection


CONTRACT_COLUMNS = [
    "id",
    "contract_number",
    "contract_name",
    "operator_name",
    "operator_alias",
    "operator_participation",
    "partner_name",
    "partner_alias",
    "partner_participation",
    "active",
    "notes",
]


def list_contracts(active_only: bool = False) -> list[dict]:
    conn = get_connection()
    query = "SELECT * FROM active_contracts"
    params = []
    if active_only:
        query += " WHERE active = ?"
        params.append(1)
    query += " ORDER BY active DESC, contract_number"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_contracts_df(active_only: bool = False) -> pd.DataFrame:
    rows = list_contracts(active_only=active_only)
    if not rows:
        return pd.DataFrame(columns=CONTRACT_COLUMNS)
    return pd.DataFrame(rows)[CONTRACT_COLUMNS]


def upsert_contract(contract: dict) -> None:
    contract_number = str(contract.get("contract_number") or "").strip()
    operator_name = str(contract.get("operator_name") or "").strip()
    partner_name = str(contract.get("partner_name") or "").strip()
    
    if not contract_number or not operator_name:
        return

    contract_id = _none_if_blank(contract.get("id"))
    conn = get_connection()
    try:
        if contract_id is not None:
            conn.execute(
                """
                UPDATE active_contracts SET
                    contract_number = ?,
                    contract_name = ?,
                    operator_name = ?,
                    operator_alias = ?,
                    operator_participation = ?,
                    partner_name = ?,
                    partner_alias = ?,
                    partner_participation = ?,
                    active = ?,
                    notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    contract_number,
                    _none_if_blank(contract.get("contract_name")),
                    operator_name,
                    _none_if_blank(contract.get("operator_alias")),
                    _float_or_none(contract.get("operator_participation")),
                    partner_name,
                    _none_if_blank(contract.get("partner_alias")),
                    _float_or_none(contract.get("partner_participation")),
                    1 if bool(contract.get("active", True)) else 0,
                    _none_if_blank(contract.get("notes")),
                    contract_id
                )
            )
        else:
            conn.execute(
                """
                INSERT INTO active_contracts (
                    contract_number,
                    contract_name,
                    operator_name,
                    operator_alias,
                    operator_participation,
                    partner_name,
                    partner_alias,
                    partner_participation,
                    active,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    contract_number,
                    _none_if_blank(contract.get("contract_name")),
                    operator_name,
                    _none_if_blank(contract.get("operator_alias")),
                    _float_or_none(contract.get("operator_participation")),
                    partner_name,
                    _none_if_blank(contract.get("partner_alias")),
                    _float_or_none(contract.get("partner_participation")),
                    1 if bool(contract.get("active", True)) else 0,
                    _none_if_blank(contract.get("notes")),
                )
            )
        conn.commit()
    except Exception as e:
        print(f"Error saving contract {contract_number}: {e}")
    finally:
        conn.close()


def save_contracts_from_df(df: pd.DataFrame) -> int:
    saved = 0
    for record in df.to_dict("records"):
        if not str(record.get("contract_number") or "").strip():
            continue
        upsert_contract(record)
        saved += 1
    return saved


def apply_contract_catalog(record: dict) -> dict:
    contract = match_contract(record)
    if not contract:
        reconcile_participation_amounts(record)
        return _refresh_record_status(record)
    return apply_selected_contract(record, contract, source="Catalogo")


def apply_selected_contract(record: dict, contract: dict, source: str = "Seleccion manual") -> dict:
    """Apply a contract explicitly selected by the user or matched in the catalog."""
    if not contract:
        reconcile_participation_amounts(record)
        return _refresh_record_status(record)

    record["Contrato"] = contract["contract_number"]
    record["Contrato Nombre"] = contract.get("contract_name")
    record["Operador"] = contract["operator_name"]
    record["Socio"] = contract["partner_name"]
    record["Emisor"] = contract["operator_name"]
    record["Partner Receptor"] = contract["partner_name"]
    record["PEMEX Participation %"] = contract.get("operator_participation")
    record["Partner Participation %"] = contract.get("partner_participation")
    record["Participacion Operador %"] = contract.get("operator_participation")
    record["Participacion Socio %"] = contract.get("partner_participation")
    record["Fuente Contrato"] = source

    record["Alertas"] = _remove_missing_catalog_fields(str(record.get("Alertas") or ""))
    reconcile_participation_amounts(record)
    return _refresh_record_status(record)


def match_contract(record: dict) -> dict | None:
    haystack = " ".join(
        str(record.get(key) or "")
        for key in ("Contrato", "Texto OCR", "Reference", "Archivo")
    )
    normalized_haystack = _normalize_contract_text(haystack)
    if not normalized_haystack:
        return None

    for contract in list_contracts(active_only=True):
        candidates = [
            contract.get("contract_number"),
            contract.get("contract_name"),
        ]
        if any(_contract_candidate_matches(candidate, normalized_haystack) for candidate in candidates):
            return contract
    return None


def _contract_candidate_matches(candidate: str | None, normalized_haystack: str) -> bool:
    for part in _split_aliases(candidate):
        normalized_candidate = _normalize_contract_text(part)
        if len(normalized_candidate) >= 6 and normalized_candidate in normalized_haystack:
            return True
    return False


def _split_aliases(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in re.split(r"[;|,]", str(value)) if part.strip()]


def _normalize_contract_text(value: str | None) -> str:
    text = str(value or "").upper()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^A-Z0-9]+", "", text)


def _remove_missing_catalog_fields(alerts: str) -> str:
    if not alerts:
        return ""
    removable = {
        "Emisor",
        "Partner Receptor",
        "Contrato",
        "Partner Participation %",
        "PEMEX Participation %",
        "Amount Due by PEMEX",
        "Amount Due by Partner",
    }
    parts = []
    for alert in [part.strip() for part in alerts.split(";") if part.strip()]:
        if not alert.startswith("Campos faltantes:"):
            parts.append(alert)
            continue
        fields = [field.strip() for field in alert.replace("Campos faltantes:", "").split(",")]
        remaining = [field for field in fields if field not in removable]
        if remaining:
            parts.append("Campos faltantes: " + ", ".join(remaining))
    return "; ".join(parts)


def _join_alert(existing: str, new_alert: str) -> str:
    return f"{existing}; {new_alert}" if existing else new_alert


def reconcile_participation_amounts(record: dict) -> dict:
    """Correct participation amounts when the total and percentage are reliable."""
    total = _float_or_none(record.get("Total Current Period"))
    operator_pct = _float_or_none(record.get("PEMEX Participation %"))
    partner_pct = _float_or_none(record.get("Partner Participation %"))
    if total is None:
        return record

    if operator_pct is not None:
        expected = round(total * operator_pct / 100, 2)
        record["Monto Esperado Operador"] = expected
        _correct_amount(record, "Amount Due by PEMEX", expected)
    if partner_pct is not None:
        expected = round(total * partner_pct / 100, 2)
        record["Monto Esperado Socio"] = expected
        _correct_amount(record, "Amount Due by Partner", expected)
    return record


def _refresh_record_status(record: dict) -> dict:
    alerts = [part.strip() for part in str(record.get("Alertas") or "").split(";") if part.strip()]
    record["Alertas"] = "; ".join(
        alert
        for alert in alerts
        if alert not in {"Contrato reconocido en catalogo", "Contrato seleccionado manualmente"}
    )

    numeric_alerts = _participation_validation_alerts(record)
    if numeric_alerts:
        record["Alertas"] = _join_alert(record["Alertas"], "; ".join(numeric_alerts))

    if not record.get("OCR Lines"):
        record["Estado"] = "Error"
    elif _has_actionable_alert(record["Alertas"]):
        record["Estado"] = "Requiere revision"
    else:
        record["Estado"] = "Validado"
    return record


def _participation_validation_alerts(record: dict) -> list[str]:
    total = _float_or_none(record.get("Total Current Period"))
    operator_pct = _float_or_none(record.get("PEMEX Participation %"))
    partner_pct = _float_or_none(record.get("Partner Participation %"))
    operator_amount = _float_or_none(record.get("Amount Due by PEMEX"))
    partner_amount = _float_or_none(record.get("Amount Due by Partner"))
    alerts = []

    if operator_pct is not None and partner_pct is not None and abs(operator_pct + partner_pct - 100) > 0.10:
        alerts.append("Porcentajes de participacion no suman 100%")
    if total is not None and operator_pct is not None and operator_amount is not None:
        if abs(operator_amount - round(total * operator_pct / 100, 2)) > 0.10:
            alerts.append("Monto de PEMEX no cuadra con total y porcentaje")
    if total is not None and partner_pct is not None and partner_amount is not None:
        if abs(partner_amount - round(total * partner_pct / 100, 2)) > 0.10:
            alerts.append("Monto del socio no cuadra con total y porcentaje")
    return alerts


def _has_actionable_alert(alerts: str) -> bool:
    for alert in [part.strip() for part in str(alerts or "").split(";") if part.strip()]:
        if alert.startswith("Confianza OCR promedio baja:"):
            continue
        return True
    return False


def _correct_amount(record: dict, field: str, expected: float) -> None:
    current = _float_or_none(record.get(field))
    if current is None:
        record[field] = expected
        _append_automatic_correction(record, f"{field}: completado={expected:,.2f}")
        return
    if abs(current - expected) > 0.10:
        record[field] = expected
        _append_automatic_correction(record, f"{field}: OCR={current:,.2f}, calculado={expected:,.2f}")


def _append_automatic_correction(record: dict, detail: str) -> None:
    key = "Correcciones automaticas"
    existing = str(record.get(key) or "")
    record[key] = f"{existing}; {detail}" if existing else detail


def _float_or_none(value):
    if value in (None, "") or pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _none_if_blank(value):
    if value in (None, "") or pd.isna(value):
        return None
    return value
