from __future__ import annotations

import json
import math
import re
from pathlib import Path


ALIAS_FILE = Path(__file__).resolve().parents[1] / "data" / "concept_aliases.json"
ALIAS_COLUMNS = ["concept", "alias", "match_type", "active", "notes"]
MATCH_TYPES = ["texto", "regex"]


def load_concept_aliases() -> list[dict]:
    if not ALIAS_FILE.exists():
        return []
    try:
        data = json.loads(ALIAS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    return [_normalize_alias_record(record) for record in data if isinstance(record, dict)]


def list_concept_aliases_df() -> pd.DataFrame:
    import pandas as pd

    aliases = load_concept_aliases()
    if not aliases:
        return pd.DataFrame(columns=ALIAS_COLUMNS)
    dataframe = pd.DataFrame(aliases)
    for column in ALIAS_COLUMNS:
        if column not in dataframe.columns:
            dataframe[column] = "" if column != "active" else True
    dataframe["active"] = dataframe["active"].astype(bool)
    return dataframe[ALIAS_COLUMNS]


def save_concept_aliases_from_df(dataframe: pd.DataFrame, valid_concepts: list[str]) -> int:
    if dataframe is None:
        return 0
    valid_concepts_set = set(valid_concepts)
    records = []
    seen = set()
    for raw_record in dataframe.to_dict("records"):
        record = _normalize_alias_record(raw_record)
        if not record["concept"] or not record["alias"]:
            continue
        if record["concept"] not in valid_concepts_set:
            continue
        key = (record["concept"], record["alias"].casefold(), record["match_type"])
        if key in seen:
            continue
        seen.add(key)
        records.append(record)

    ALIAS_FILE.parent.mkdir(parents=True, exist_ok=True)
    ALIAS_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return len(records)


def get_cash_call_concepts(base_concepts: dict[str, list[str]]) -> dict[str, list[str]]:
    concepts = {concept: list(patterns) for concept, patterns in base_concepts.items()}
    for record in load_concept_aliases():
        if not record["active"] or record["concept"] not in concepts:
            continue
        pattern = _alias_to_pattern(record["alias"], record["match_type"])
        if not pattern:
            continue
        if pattern not in concepts[record["concept"]]:
            concepts[record["concept"]].append(pattern)
    return concepts


def build_alias_pattern(alias: str, match_type: str = "texto") -> str | None:
    return _alias_to_pattern(alias, match_type)


def _normalize_alias_record(record: dict) -> dict:
    match_type = _clean_text_value(record.get("match_type")) or "texto"
    match_type = match_type.strip().lower()
    if match_type not in MATCH_TYPES:
        match_type = "texto"
    active_value = record.get("active", True)
    active = True if _is_blank(active_value) else bool(active_value)
    return {
        "concept": _clean_text_value(record.get("concept")).strip(),
        "alias": _clean_text_value(record.get("alias")).strip(),
        "match_type": match_type,
        "active": active,
        "notes": _clean_text_value(record.get("notes")).strip(),
    }


def _alias_to_pattern(alias: str, match_type: str) -> str | None:
    alias = str(alias or "").strip()
    if not alias:
        return None
    if match_type == "regex":
        try:
            re.compile(alias)
        except re.error:
            return None
        return alias

    normalized = _normalize_text(alias)
    if not normalized:
        return None
    escaped = re.escape(normalized)
    return re.sub(r"\\\s+", r"\\s+", escaped)


def _normalize_text(text: str) -> str:
    text = (text or "").lower()
    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u",
        "ñ": "n",
        "Ã¡": "a",
        "Ã©": "e",
        "Ã­": "i",
        "Ã³": "o",
        "Ãº": "u",
        "Ã¼": "u",
        "Ã±": "n",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return re.sub(r"\s+", " ", text).strip()


def _clean_text_value(value) -> str:
    if _is_blank(value):
        return ""
    return str(value)


def _is_blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False
