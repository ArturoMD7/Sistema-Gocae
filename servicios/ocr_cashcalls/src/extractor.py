import re
from statistics import mean

from src.concept_aliases import get_cash_call_concepts
from src.validators import clean_amount, detect_currency


# Catalog used by this contractual area. Keeping explicit labels prevents a
# broad category (for example, overhead) from consuming a different concept.
CASH_CALL_CONCEPTS = {
    "Mano de Obra Administrativa y Supervisión Técnica": [
        r"^(?!.*\bajuste\s+(?:de\s+)?mano\s+de\s+obra\b).*\bmano\s+de\s+obra(?:\s+administrativa(?:\s+y\s+supervision\s+tecnica)?)?",
        r"labor\s+costs?",
        r"costos?\s+laborales",
        r"gastos?\s+laborales",
    ],
    "Plan de Gestión Social": [
        r"plan\s+de\s+gestion\s+social",
        r"social\s+management\s+plan",
    ],
    "Transferencia de Tecnología": [
        r"transferencia\s+de\s+tecnologia",
        r"transferencia\s+tecnologica",
        r"technology\s+transfer(?:\s+program)?",
    ],
    "Programa de Capacitación": [
        r"programa\s+de\s+capacitacion",
        r"training\s+program",
        r"capacity\s+building\s+program",
    ],
    "Procura de Pozo": [
        r"procura\s+de\s+pozo",
        r"well\s+procurement",
        r"procurement\s+of\s+(?:the\s+)?well",
    ],
    "Perforación (Renta de Plataforma)": [
        r"perforacion\s*\(?\s*renta\s+de\s+plataforma\s*\)?",
        r"drilling\s*\(?\s*(?:rig|platform)\s+rental\s*\)?",
        r"(?:rig|platform)\s+rental",
    ],
    "Terminación": [
        r"terminacion",
        r"\bcompletion\b",
        r"well\s+completion",
    ],
    "Logística": [
        r"^(?!.*\bajuste\s+(?:de\s+)?(?:servicios?\s+de\s+)?logistica\b).*\blogistica\b",
        r"^(?!.*\badjustment\s+(?:of\s+)?(?:logistics?\s+services?)\b).*\blogistics?\b",
    ],
    "Materiales": [r"materiales", r"\bmaterials?\b"],
    "Gestión de Estudios ARP, PRE, PCA y Certificación del Diseño": [
        r"gestion\s+(?:de\s+estudios?|del\s+diseno)\s+arp.*pre.*pca.*certificacion\s+del\s+diseno",
        r"management\s+of\s+(?:arp|pre|pca).*design\s+certification",
        r"arp.*pre.*pca.*design\s+certification\s+management",
    ],
    "Estudios ARP, PRE, PCA y Certificación del Diseño": [
        r"^(?!.*\bgestion\b).*estudios?\s+arp.*pre.*pca.*certificacion\s+del\s+diseno",
        r"^(?!.*\bmanagement\b).*arp.*pre.*pca.*design\s+certification",
    ],
    "Estudio VCD (Amistli-1EXP)": [r"estudio\s+vcd", r"vcd\s+study"],
    "Estudio de Análisis de Velocidades": [
        r"estudio\s+de\s+analisis\s+de\s+velocidades",
        r"velocity\s+analysis\s+study",
        r"study\s+of\s+velocity\s+analysis",
    ],
    "Gestión de Estudios Geofísicos-Geotécnicos": [
        r"gestion\s+de\s+estudios?\s+geofisicos?\s*-?\s*geotecnicos?",
        r"management\s+of\s+geophysical\s*-?\s*geotechnical\s+stud(?:y|ies)",
        r"geophysical\s*-?\s*geotechnical\s+stud(?:y|ies)\s+management",
    ],
    "Estudios Geofísicos-Geotécnicos": [
        r"^(?!.*\bgestion\b).*estudios?\s+geofisicos?\s*-?\s*geotecnicos?",
        r"^(?!.*\bmanagement\b).*geophysical\s*-?\s*geotechnical\s+stud(?:y|ies)",
        r"^(?!.*\bmanagement\b).*geotechnical\s+stud(?:y|ies)",
        r"^(?!.*\bmanagement\b).*geophysical\s+stud(?:y|ies)",
    ],
    "Seguridad, Salud y Medio Ambiente (SASISOPA)": [
        r"seguridad\s*,?\s*salud\s+y\s+medio\s+ambiente",
        r"sasisopa",
        r"(?:health|safety|environment).*(?:health|safety|environment)",
        r"\bhse\b",
        r"\bhsse\b",
    ],
    "Evaluación de Impacto Social": [
        r"evaluacion\s+de\s+impacto\s+social",
        r"social\s+impact\s+(?:assessment|evaluation)",
    ],
    "Estudio de Línea Base Ambiental": [
        r"estudio\s+de\s+linea\s+base\s+ambiental",
        r"environmental\s+baseline\s+stud(?:y|ies)",
        r"baseline\s+environmental\s+stud(?:y|ies)",
    ],
    "IAEEH": [
        r"^(?!.*\bajuste\s+(?:de\s+)?iaeeh\b).*\biaeeh\b",
        r"^(?!.*\bajuste\s+(?:de\s+)?iaeh\b).*\biaeh\b",
        r"hydrocarbon\s+exploration\s+and\s+extraction\s+activit(?:y|i)\s+tax",
        r"hydrocarbon.*exploration.*extraction.*tax",
        r"actividad\s+de\s+exploracion\s+y\s+extraccion\s+de\s+hidrocarburos",
        r"impuesto.*exploracion.*extraccion.*hidrocarburos",
    ],
    "CUOTA CONTRACTUAL": [
        r"contractual\s+fee",
        r"contrr?actual\s+fee",
        r"^(?!.*\bajuste\s+(?:de\s+)?cuota\b).*\bcuota\s+del\s+area\s+contractual\b",
        r"^(?!.*\bajuste\s+(?:de\s+)?cuota\b).*\bcuota\s+contractual\b",
        r"^(?!.*\bajuste\s+(?:de\s+)?cuota\b).*\bcuotas?\s+contractuales\b",
    ],
    "OVERHEAD": [
        r"^(?!.*\biva\s*[- ]\s*over(?:h|f)ead\b).*\bover(?:h|f)ead\b",
        r"gastos?\s+generales",
        r"costos?\s+indirectos",
        r"gastos?\s+indirectos",
    ],
    "IVA OVERHEAD": [r"iva\s*[- ]\s*over(?:h|f)ead", r"over(?:h|f)ead\s+vat", r"vat\s+over(?:h|f)ead"],
    "DPA-PE": [r"\bdpa\s*(?:-|\s)\s*pe\b"],
    "DPA": [
        r"\bdpa\b(?!\s*(?:-|\s)\s*pe\b)",
        r"derecho\s+por\s+la\s+adm\.?\s*y\s+seg\.?\s*tec\.?\s+anual.*(?:contrato|e&e|hidrocarburos)",
        r"derecho\s+por\s+la\s+administracion\s+y\s+seguridad\s+tecnica\s+anual.*(?:contrato|hidrocarburos)",
        r"annual\s+(?:right|fee)\s+for\s+(?:administration|adm\.?).*(?:technical|tech\.?)\s+(?:supervision|safety|security)",
    ],
    "Intereses acumulados del mes": [
        r"intereses?\s+acumulados?\s+del\s+mes",
        r"intereses?\s+moratorios?(?:\s+de\b.*)?",
        r"interest\s+accrued",
        r"accrued\s+interest",
        r"intereses?\s+devengados?",
    ],
    "Análisis de velocidades": [
        r"^(?!.*\bestudio\s+de\s+analisis\s+de\s+velocidades\b).*\banalisis\s+de\s+velocidades\b",
        r"^(?!.*\bstud(?:y|ies)\b).*velocity\s+analysis",
    ],
    "Ajuste IAEEH": [r"ajuste\s+(?:de\s+)?iaeeh", r"ajuste\s+(?:de\s+)?iaeh", r"iaeeh\s+adjustment"],
    "Ajuste Cuota": [r"ajuste\s+(?:de\s+)?cuota", r"(?:contractual\s+)?fee\s+adjustment"],
    "Ajuste Mano de obra": [r"ajuste\s+(?:de\s+)?mano\s+de\s+obra", r"labor\s+(?:costs?\s+)?adjustment"],
    "Ajuste de Servicios de Logística": [
        r"ajuste\s+(?:de\s+)?servicios?\s+de\s+logistica",
        r"logistics?\s+services?\s+adjustment",
    ],
    "Ajuste Transferencia de Tecnología": [
        r"ajuste\s+(?:de\s+)?transferencia\s+de\s+tecnologia",
        r"technology\s+transfer\s+adjustment",
    ],
}

SUMMED_CONCEPT_FIELDS = {
    "Mano de Obra Administrativa y Supervisión Técnica",
    "OVERHEAD",
}

HEADER_LABELS = {
    "Date": [r"\bdate\b", r"\bfecha\b"],
    "Accounting Period": [r"accounting\s+period", r"periodo\s+contable"],
    "Reference": [r"reference\s*#?", r"\bref\.?\b", r"referencia"],
    "Payment Due Date": [
        r"payment\s+due\s+date",
        r"due\s+date",
        r"fecha\s+de\s+pago",
        r"fecha\s+limite\s+de\s+pago",
        r"fecha\s+limite",
        r"fecha\s+de\s+vencimiento",
        r"vencimiento",
    ],
}
MINI_TABLE_LABEL_STARTS = {
    "Date": [
        r"^date\b",
        r"^fecha\b(?!\s+(?:de\s+)?pago)",
        r"\bfecha\b(?!\s+(?:de\s+)?pago)\s*$",
    ],
    "Accounting Period": [
        r"^accounting\s+period\b",
        r"\bperiodo\s+con(?:t|l)ab(?:l|i|1)e\b",
    ],
    "Reference": [r"^reference\s*#?", r"^#\s*de\s+referencia\b", r"^de\s+referencia\b", r"^referencia\b", r"^ref\.?\b"],
    "Payment Due Date": [
        r"^payment\s+due\s+date\b",
        r"^due\s+date\b",
        r"^fecha\s+(?:de\s+)?pago\b",
        r"^fecha\s+limite\b",
        r"^fecha\s+de\s+vencimiento\b",
        r"^vencimiento\b",
    ],
}

DATE_RE = re.compile(
    r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b",
    re.IGNORECASE,
)
SPANISH_TEXT_DATE_RE = re.compile(
    r"\b(?:el\s+)?\d{1,2}\s+de\s+"
    r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
    r"\s+de\s+\d{4}\b",
    re.IGNORECASE,
)
PERIOD_RE = re.compile(
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december|"
    r"jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec|"
    r"enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
    r"\.?\s+\d{4}\b",
    re.IGNORECASE,
)
PERIOD_MONTH_RE = re.compile(
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december|"
    r"jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec|"
    r"enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b",
    re.IGNORECASE,
)
PERCENT_RE = re.compile(r"(?<![.\d])(\d{1,3}(?:\.\d+)?)\s*%")
AMOUNT_RE = re.compile(
    r"(?:US\$|\$|USD)\s*-?\(?(?:\d+(?:[,.]\d{3})+|\d+)(?:[,.]\d{1,2})?\)?|"
    r"(?<![\w.])-?\(?\d+(?:[,.]\d{3})+(?:[,.]\d{1,2})?\)?|"
    r"(?<![\w.])-?\(?\d+\.\d{2}\)?"
)


def extract_cash_call_data(ocr_data: list, file_name: str) -> dict:
    rows = _group_rows(ocr_data)
    full_text = "\n".join(row["text"] for row in rows)
    overall_confidence = _overall_confidence(ocr_data)
    concept_patterns = get_cash_call_concepts(CASH_CALL_CONCEPTS)

    result = {
        "Archivo": file_name,
        "Emisor": _extract_issuer(rows),
        "Partner Receptor": _extract_receiver_partner(rows),
        "Contrato": _extract_contract(rows),
        "Date": _extract_header_value(rows, "Date"),
        "Accounting Period": _extract_header_value(rows, "Accounting Period"),
        "Reference": _extract_header_value(rows, "Reference"),
        "Payment Due Date": _extract_header_value(rows, "Payment Due Date"),
        "Currency": detect_currency(full_text),
        **{field: None for field in CASH_CALL_CONCEPTS},
        "Total Current Period": None,
        "Total Conceptos": None,
        "PEMEX Participation %": None,
        "Partner Participation %": None,
        "Amount Due by PEMEX": None,
        "Amount Due by Partner": None,
        "Overall Confidence": round(overall_confidence, 4),
        "OCR Lines": len(rows),
        "Alertas": "",
        "Estado": "Requiere revision",
        "Texto OCR": full_text,
    }

    current_rows = _current_period_rows(rows)
    for field, patterns in concept_patterns.items():
        result[field] = _extract_concept_amount(
            current_rows,
            patterns,
            sum_matches=field in SUMMED_CONCEPT_FIELDS,
            concept_field=field,
            all_concepts=concept_patterns,
        )


    result["Total Current Period"] = _extract_current_total(current_rows)
    result.update(_extract_participation_rows(rows))

    alerts = _build_alerts(result, ocr_data)
    result["Alertas"] = "; ".join(alerts)
    result["Estado"] = _status_from_alerts(result, alerts)
    return result


def _group_rows(ocr_data: list, y_tolerance: float | None = None) -> list[dict]:
    items = []
    for item in ocr_data or []:
        box = item.get("box") or []
        x, y = _box_center(box)
        x_min, y_min, x_max, y_max = _box_bounds(box)
        text = str(item.get("text", "") or "").strip()
        if not text:
            continue
        items.append(
            {
                "text": text,
                "box": box,
                "confidence": float(item.get("confidence") or 0),
                "x": x,
                "y": y,
                "x_min": x_min,
                "y_min": y_min,
                "x_max": x_max,
                "y_max": y_max,
                "height": max(1.0, y_max - y_min),
            }
        )

    if y_tolerance is None:
        y_tolerance = _compute_row_tolerance(items)

    items.sort(key=lambda item: (item["y"], item.get("x_min", item["x"])))
    rows = []
    for item in items:
        if not rows or abs(rows[-1]["y"] - item["y"]) > y_tolerance:
            rows.append({"items": [item], "y": item["y"]})
        else:
            rows[-1]["items"].append(item)
            rows[-1]["y"] = mean([row_item["y"] for row_item in rows[-1]["items"]])

    for row in rows:
        _refresh_row(row)
    rows = _attach_nearby_amount_rows(rows)
    return rows


def _compute_row_tolerance(items: list) -> float:
    """
    Compute a y_tolerance that is:
      - large enough to group items that PaddleOCR assigns to slightly different Y
        within the same visual line (e.g. text label vs right-aligned amount)
      - small enough to keep adjacent document rows separate

    Strategy: sort items by Y centroid, compute consecutive Y gaps, take the
    20th-percentile gap as the threshold (i.e. 80% of inter-item gaps are
    LARGER than this threshold, so only within-line drift is bridged).
    Floor: 6px (never collapse near-identical lines).
    Ceiling: 40% of the median item height (never merge visually distinct rows).
    """
    if len(items) < 2:
        return 12.0
    ys = sorted(item["y"] for item in items)
    gaps = [ys[i + 1] - ys[i] for i in range(len(ys) - 1) if ys[i + 1] - ys[i] > 0]
    if not gaps:
        return 12.0
    gaps.sort()
    # 20th-percentile gap  →  bridges within-line Y drift but not line spacing
    p20_index = max(0, int(len(gaps) * 0.20) - 1)
    p20_gap = gaps[p20_index]
    # Safety ceiling: 40% of median item height
    heights = sorted(item["height"] for item in items)
    median_height = heights[len(heights) // 2]
    ceiling = median_height * 0.40
    return max(6.0, min(p20_gap, ceiling))


def _box_center(box: list) -> tuple[float, float]:
    try:
        xs = [point[0] for point in box]
        ys = [point[1] for point in box]
        return sum(xs) / len(xs), sum(ys) / len(ys)
    except Exception:
        return 0.0, 0.0


def _box_bounds(box: list) -> tuple[float, float, float, float]:
    try:
        xs = [point[0] for point in box]
        ys = [point[1] for point in box]
        return min(xs), min(ys), max(xs), max(ys)
    except Exception:
        return 0.0, 0.0, 0.0, 0.0


def _refresh_row(row: dict) -> dict:
    if not row.get("items"):
        row["text"] = ""
        row["confidence"] = 0.0
        row["height"] = 1.0
        return row
    row["items"].sort(key=lambda item: item.get("x_min", item.get("x", 0.0)))
    row["text"] = " ".join(item["text"] for item in row["items"])
    row["confidence"] = mean(item["confidence"] for item in row["items"])
    row["x_min"] = min(item.get("x_min", item.get("x", 0.0)) for item in row["items"])
    row["x_max"] = max(item.get("x_max", item.get("x", 0.0)) for item in row["items"])
    row["y_min"] = min(item.get("y_min", item.get("y", 0.0)) for item in row["items"])
    row["y_max"] = max(item.get("y_max", item.get("y", 0.0)) for item in row["items"])
    row["y"] = mean(item.get("y", 0.0) for item in row["items"])
    row["height"] = max(1.0, row["y_max"] - row["y_min"])
    return row


def _attach_nearby_amount_rows(rows: list[dict]) -> list[dict]:
    if not rows:
        return rows
    rows = [dict(row, items=list(row.get("items") or [])) for row in rows]
    average_height = mean(row.get("height", 10.0) for row in rows)
    # y_limit: how far (in pixels) we look for a matching text row.
    # 2.5× average height gives enough slack for PaddleOCR Y-drift without
    # accidentally pulling amounts from two rows away.
    y_limit = max(26.0, average_height * 2.5)
    attached_indexes = set()

    for index, row in enumerate(rows):
        if not _is_amount_only_row(row.get("text", "")):
            continue
        target_index = _best_text_row_for_amount(rows, index, y_limit, attached_indexes)
        if target_index is None:
            continue
        rows[target_index]["items"].extend(row.get("items") or [])
        _refresh_row(rows[target_index])
        attached_indexes.add(index)

    _attach_shifted_heading_amounts(rows, y_limit)

    aligned_rows = [
        row
        for index, row in enumerate(rows)
        if index not in attached_indexes
    ]
    aligned_rows.sort(key=lambda row: (row.get("y", 0.0), row.get("x_min", 0.0)))
    return [_refresh_row(row) for row in aligned_rows]


def _y_overlap(a_min: float, a_max: float, b_min: float, b_max: float) -> float:
    """Returns the pixel length of the vertical overlap between two Y ranges."""
    return max(0.0, min(a_max, b_max) - max(a_min, b_min))


def _best_text_row_for_amount(
    rows: list[dict],
    amount_index: int,
    y_limit: float,
    attached_indexes: set[int],
) -> int | None:
    """
    Find the text row that best "owns" this amount box.

    Primary criterion : vertical overlap between the amount box and the
    candidate row.  When PaddleOCR assigns the amount a Y-centroid that
    drifts slightly from the text centroid, the bounding-box extents
    (y_min / y_max) still overlap with the correct row.

    Secondary criterion : Y-center distance, so ties are broken cleanly.

    Only rows whose x_min is to the LEFT of the amount are considered
    (amounts always appear to the right of their label).
    """
    amount_row = rows[amount_index]
    a_ymin = amount_row.get("y_min", amount_row.get("y", 0.0))
    a_ymax = amount_row.get("y_max", amount_row.get("y", 0.0))
    a_yctr = amount_row.get("y", (a_ymin + a_ymax) / 2)
    amount_x = amount_row.get("x_min", amount_row.get("x", 0.0))

    candidates = []
    # Search ±4 rows; wider window catches multi-line heading rows that span
    # a larger Y band.
    for index in range(max(0, amount_index - 4), min(len(rows), amount_index + 5)):
        if index == amount_index or index in attached_indexes:
            continue
        row = rows[index]
        if _is_amount_only_row(row.get("text", "")):
            continue
        if _first_amount_in_row(row) is not None:
            continue
        if not _has_meaningful_text(row.get("text", "")):
            continue
        # The text label must start to the LEFT of the amount.
        if row.get("x_min", row.get("x", 0.0)) >= amount_x:
            continue
        y_distance = abs(row.get("y", 0.0) - a_yctr)
        if y_distance > y_limit:
            continue

        if row.get("items"):
            first_item = row["items"][0]
            r_ymin = first_item.get("y_min", first_item.get("y", 0.0))
            r_ymax = first_item.get("y_max", first_item.get("y", 0.0))
        else:
            r_ymin = row.get("y_min", row.get("y", 0.0))
            r_ymax = row.get("y_max", row.get("y", 0.0))
        r_height = max(1.0, r_ymax - r_ymin)
        overlap = _y_overlap(a_ymin, a_ymax, r_ymin, r_ymax)
        r_yctr = row.get('y', 0.0)
        direction_bonus = 1.5 if r_yctr <= a_yctr else 1.0

        # Score = overlap² / row_height.
        #
        # Why squared?  Neither raw overlap nor simple ratio (overlap/height)
        # alone is robust enough:
        #
        #   • Raw overlap: a tall garbage box (AAAS, 80 px) wins by sheer
        #     Y extent even when the correct short row has better proportional
        #     coverage.
        #
        #   • Simple ratio (overlap/height): when two candidate rows are
        #     close in height the tiny ratio differences (e.g. 0.45 vs 0.44)
        #     flip the result arbitrarily.
        #
        # overlap² / height = overlap × (overlap / height) combines absolute
        # magnitude with proportional fit, giving clearly separated scores:
        #
        #   Cuota (h=25, ov=11):  11²/25  = 4.84  ← correct winner
        #   Mano de Obra (h=20, ov=9): 9²/20 = 4.05
        #   Overhead junio (h=20, ov=11): 11²/20 = 6.05 ← correct winner
        #   AAAS (h=80, ov=18):   18²/80  = 4.05
        r_height = max(1.0, r_ymax - r_ymin)
        overlap_score = ((overlap * overlap) / r_height) * direction_bonus
        # Higher score is better; negate so sort ascending picks winner.
        # y_distance breaks ties.
        candidates.append((-overlap_score, y_distance, index))

    if not candidates:
        return None
    candidates.sort()
    return candidates[0][2]


def _attach_shifted_heading_amounts(rows: list[dict], y_limit: float) -> None:
    for index, row in enumerate(rows[:-1]):
        normalized = _normalize(row.get("text", ""))
        if not _looks_like_cash_call_heading(normalized) or _matches_any_concept(normalized):
            continue

        def _is_amount_item(item: dict) -> bool:
            text = item.get("text", "")
            if "%" in text or _amount_from_text(text) is None:
                return False
            norm = _normalize(text)
            return not (_matches_any_concept(norm) or _looks_like_cash_call_heading(norm))

        amount_items = [item for item in row.get("items") or [] if _is_amount_item(item)]
        if not amount_items:
            continue

        # We found a heading with an amount! This indicates a shift.
        # Find the contiguous block of concept rows below it.
        cascade_block = []
        target_index = index + 1
        found_empty = False
        skipped_rows = 0

        while target_index < len(rows):
            target = rows[target_index]
            target_norm = _normalize(target.get("text", ""))
            
            # Stop if we hit a heading
            if _looks_like_cash_call_heading(target_norm):
                break
                
            # Stop if the vertical distance is too large
            last_y = cascade_block[-1].get("y", 0.0) if cascade_block else row.get("y", 0.0)
            if abs(target.get("y", 0.0) - last_y) > y_limit * 2.0:
                break
                
            # If it's not a concept, skip it (up to 3 times)
            if not _matches_any_concept(target_norm):
                skipped_rows += 1
                if skipped_rows > 3:
                    break
                target_index += 1
                continue
                
            skipped_rows = 0
            cascade_block.append(target)
            
            if _first_amount_in_row(target) is None:
                found_empty = True
                break
                
            target_index += 1

        if found_empty and cascade_block:
            # We can perform the cascade shift!
            amounts_to_shift = [amount_items]
            for block_row in cascade_block[:-1]:
                row_amount_items = [item for item in block_row.get("items") or [] if _is_amount_item(item)]
                amounts_to_shift.append(row_amount_items)
                
            # Apply shifts from top to bottom
            for i, block_row in enumerate(cascade_block):
                items_to_add = amounts_to_shift[i]
                
                # Remove any existing amounts from this row that are being pushed down
                if i < len(cascade_block) - 1:
                    items_to_remove = amounts_to_shift[i+1]
                    for item in items_to_remove:
                        if item in block_row["items"]:
                            block_row["items"].remove(item)
                            
                # Add the new amounts from above
                for item in items_to_add:
                    if item not in block_row["items"]:
                        block_row["items"].append(item)
                        
                block_row["has_shifted_heading_amount"] = True
                _refresh_row(block_row)
                
            # Remove the original amount from the heading
            for item in amount_items:
                if item in row["items"]:
                    row["items"].remove(item)
            _refresh_row(row)


def _looks_like_cash_call_heading(normalized: str) -> bool:
    return (
        "cash call" in normalized
        or "solicitud de efectivo" in normalized
        or "solicitud de fondos" in normalized
        or "llamado" in normalized
    )


def _matches_any_concept(normalized: str) -> bool:
    return any(
        re.search(pattern, normalized, re.IGNORECASE)
        for patterns in CASH_CALL_CONCEPTS.values()
        for pattern in patterns
    )


def _normalize(text: str) -> str:
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


def _extract_issuer(rows: list[dict]) -> str | None:
    for row in rows[:12]:
        text = row["text"]
        normalized = _normalize(text)
        if "pemex" in normalized and ("exploracion" in normalized or "exploration" in normalized):
            return text
    if "pemex" in _normalize(" ".join(row["text"] for row in rows[:12])):
        return "PEMEX"
    return None


def _extract_receiver_partner(rows: list[dict]) -> str | None:
    labels = [r"partners\b", r"socios\b", r"socio\b", r"participantes\b", r"asociados\b"]
    bare_labels = {"partners", "socios", "socio", "participantes", "asociados"}
    for index, row in enumerate(rows):
        normalized = _normalize(row["text"])
        if not any(re.search(pattern, normalized, re.IGNORECASE) for pattern in labels):
            continue
        value = None if normalized in bare_labels else _after_label(row["text"], labels)
        if value and not _looks_like_address(value):
            return value
        for next_row in rows[index + 1 : index + 4]:
            candidate = next_row["text"].strip()
            candidate_normalized = _normalize(candidate)
            if (
                candidate
                and "att:" not in candidate_normalized
                and "atn" not in candidate_normalized
                and not _looks_like_address(candidate)
            ):
                return candidate
    return None


def _extract_contract(rows: list[dict]) -> str | None:
    for row in rows[:20]:
        normalized = _normalize(row["text"])
        if "contract" in normalized or "contrato" in normalized or "area contractual" in normalized:
            value = _after_label(
                row["text"],
                [
                    r"contrato\s*(?:no\.?|numero|#)?",
                    r"numero\s+de\s+contrato",
                    r"\bcontract\b\s*(?:no\.?|number|#)?",
                ],
            )
            return value or row["text"]
    return None


def _extract_header_value(rows: list[dict], field: str) -> str | None:
    return _extract_header_value_from_mini_table(rows, field)


def _extract_header_value_from_mini_table(rows: list[dict], field: str) -> str | None:
    patterns = MINI_TABLE_LABEL_STARTS[field]
    for row_index, row in enumerate(rows):
        items = row.get("items") or []
        for index, item in enumerate(items):
            normalized = _normalize(item.get("text", ""))
            if not any(re.search(pattern, normalized, re.IGNORECASE) for pattern in patterns):
                continue

            inline_value = _after_label(item["text"], patterns)
            cleaned = _coerce_header_value(field, inline_value)
            if cleaned:
                return cleaned

            for next_item in items[index + 1 :]:
                if next_item.get("x", 0) <= item.get("x", 0):
                    continue
                if _is_mini_table_label(_normalize(next_item.get("text", ""))):
                    break
                cleaned = _coerce_header_value(field, next_item.get("text"))
                if cleaned:
                    return cleaned

            for previous_row in reversed(rows[:row_index]):
                if row.get("y", 0) - previous_row.get("y", 0) > 36:
                    break
                for previous_item in reversed(previous_row.get("items") or []):
                    if previous_item.get("x", 0) <= item.get("x", 0):
                        continue
                    if _is_mini_table_label(_normalize(previous_item.get("text", ""))):
                        continue
                    cleaned = _coerce_header_value(field, previous_item.get("text"))
                    if cleaned:
                        return cleaned

            for next_row in rows[row_index + 1 :]:
                if next_row.get("y", 0) - row.get("y", 0) > 36:
                    break
                for next_item in next_row.get("items") or []:
                    if next_item.get("x", 0) <= item.get("x", 0):
                        continue
                    if _is_mini_table_label(_normalize(next_item.get("text", ""))):
                        continue
                    cleaned = _coerce_header_value(field, next_item.get("text"))
                    if cleaned:
                        return cleaned
    return None


def _is_mini_table_label(normalized: str) -> bool:
    return any(
        re.search(pattern, normalized, re.IGNORECASE)
        for patterns in MINI_TABLE_LABEL_STARTS.values()
        for pattern in patterns
    )


def _coerce_header_value(field: str, value: str | None) -> str | None:
    if not value:
        return None
    if field in ("Date", "Payment Due Date"):
        match = DATE_RE.search(value) or SPANISH_TEXT_DATE_RE.search(value)
        return match.group(0) if match else None
    if field == "Accounting Period":
        match = PERIOD_RE.search(value)
        if match:
            return match.group(0)
        month_match = PERIOD_MONTH_RE.search(value)
        return _clean_value(month_match.group(0)) if month_match else None
    if field == "Reference":
        if DATE_RE.search(value) or PERIOD_MONTH_RE.search(value):
            return None
    return _clean_value(value)


def _page_max_x(rows: list[dict]) -> float:
    max_x = 0.0
    for row in rows:
        for item in row.get("items") or []:
            box = item.get("box") or []
            try:
                max_x = max(max_x, max(point[0] for point in box))
            except Exception:
                max_x = max(max_x, float(item.get("x") or 0))
    return max_x or 1.0


def _after_label(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(rf"{pattern}\s*[:#-]?\s*(.+)$", text, re.IGNORECASE)
        if match:
            return _clean_value(match.group(1))
    return None


def _clean_value(value: str) -> str | None:
    value = re.sub(r"\s+", " ", value or "").strip(" :#-|")
    return value or None


def _current_period_rows(rows: list[dict]) -> list[dict]:
    start = 0
    end = len(rows)
    for index, row in enumerate(rows):
        normalized = _normalize(row["text"])
        is_current_start = (
            "cash call" in normalized
            or "llamado" in normalized
            or "solicitud de fondos" in normalized
            or "solicitud de efectivo" in normalized
        )
        is_estimate = "estimate" in normalized or "estimado" in normalized or "estimacion" in normalized
        is_budget = "approved budget" in normalized or "presupuesto aprobado" in normalized
        if is_current_start and not is_estimate and not is_budget:
            start = index
            break

    for index in range(start + 1, len(rows)):
        normalized = _normalize(rows[index]["text"])
        if _is_current_total_row(normalized):
            end = index + 1
            if (
                _first_amount_in_row(rows[index]) is None
                and index + 1 < len(rows)
                and _is_amount_only_row(rows[index + 1]["text"])
            ):
                end = index + 2
            break
        if (
            normalized.startswith("estimate of")
            or "estimate of" in normalized
            or normalized.startswith("estimado de")
            or "estimado de" in normalized
            or normalized.startswith("estimacion de")
            or "estimacion de" in normalized
        ):
            end = index
            break
    return rows[start:end]


def _extract_concept_amount(
    rows: list[dict],
    patterns: list[str],
    sum_matches: bool = False,
    concept_field: str | None = None,
    all_concepts: dict[str, list[str]] | None = None,
) -> float | None:
    if sum_matches and concept_field in {
        "Labor Costs",
        "Mano de Obra Administrativa y Supervisión Técnica",
    }:
        return _extract_labor_costs_amount(rows, patterns, all_concepts)

    matches = []
    use_previous_amount = _uses_previous_amount_alignment(rows)
    for index, row in enumerate(rows):
        normalized = _normalize(row["text"])
        if not any(re.search(pattern, normalized, re.IGNORECASE) for pattern in patterns):
            continue
        amount = _aligned_row_amount(rows, index, use_previous_amount)
        if amount is None:
            amount = _continuation_amount(rows, index, concept_field)
        if amount is None:
            continue
        if not sum_matches:
            return amount
        matches.append((row, amount, False))

    if not matches:
        return None
    if not sum_matches:
        return None

    if concept_field == "OVERHEAD":
        amounts = _overhead_amounts_from_matches(matches)
    else:
        detail_amounts = [
            amount
            for row, amount, is_continuation in matches
            if is_continuation or _looks_like_summed_concept_detail(row["text"], concept_field)
        ]
        amounts = detail_amounts or [amount for _, amount, _ in matches]
    return round(sum(amounts), 2) if amounts else None


def _extract_labor_costs_amount(
    rows: list[dict],
    patterns: list[str],
    all_concepts: dict[str, list[str]] | None = None,
) -> float | None:
    for index, row in enumerate(rows):
        normalized = _normalize(row["text"])
        if any(re.search(pattern, normalized, re.IGNORECASE) for pattern in patterns):
            return _sum_labor_costs_block(rows, index, patterns, all_concepts)
    return None


def _sum_labor_costs_block(
    rows: list[dict],
    start_index: int,
    patterns: list[str],
    all_concepts: dict[str, list[str]] | None = None,
) -> float | None:
    amounts = []
    waiting_for_continuation_amount = False
    use_previous_amount = _uses_previous_amount_alignment(rows)

    for index in range(start_index, len(rows)):
        row = rows[index]
        normalized = _normalize(row["text"])
        if normalized.startswith("total") or "estimate" in normalized or "estimado" in normalized:
            break

        is_labor_row = any(re.search(pattern, normalized, re.IGNORECASE) for pattern in patterns)
        amount = _labor_row_amount(rows, index, patterns, use_previous_amount)
        if is_labor_row:
            if amount is not None:
                amounts.append(amount)
            waiting_for_continuation_amount = False
            continue

        if _matches_other_concept(normalized, patterns, all_concepts):
            break

        if _looks_like_section_continuation(row["text"]):
            if amount is not None:
                amounts.append(amount)
                waiting_for_continuation_amount = False
            else:
                waiting_for_continuation_amount = True
            continue

        if waiting_for_continuation_amount and amount is not None and _is_amount_only_row(row["text"]):
            amounts.append(amount)
            waiting_for_continuation_amount = False
            continue

        if amount is None and not _has_meaningful_text(row["text"]):
            continue
        break

    return round(sum(amounts), 2) if amounts else None


def _labor_row_amount(
    rows: list[dict],
    index: int,
    patterns: list[str],
    use_previous_amount: bool,
) -> float | None:
    amount = _first_amount_in_row(rows[index])
    if amount is not None:
        return amount
    if not use_previous_amount or index == 0:
        return None

    previous_normalized = _normalize(rows[index - 1]["text"])
    if any(re.search(pattern, previous_normalized, re.IGNORECASE) for pattern in patterns):
        return None
    return _first_amount_in_row(rows[index - 1])


def _uses_previous_amount_alignment(rows: list[dict]) -> bool:
    if any(row.get("has_shifted_heading_amount") for row in rows):
        return False

    total_index = None
    for index, row in enumerate(rows):
        if _is_current_total_row(_normalize(row["text"])):
            total_index = index
            break
    if (
        total_index is None
        or total_index == 0
        or _first_amount_in_row(rows[total_index]) is not None
        or _first_amount_in_row(rows[total_index - 1]) is None
    ):
        return False

    for index, row in enumerate(rows[:total_index]):
        normalized = _normalize(row["text"])
        if not _matches_any_concept(normalized):
            continue
        return (
            index > 0
            and _looks_like_cash_call_heading(_normalize(rows[index - 1]["text"]))
            and _first_amount_in_row(rows[index - 1]) is not None
            and _first_amount_in_row(row) is not None
        )
    return False


def _aligned_row_amount(rows: list[dict], index: int, use_previous_amount: bool) -> float | None:
    if use_previous_amount and index > 0:
        previous_amount = _first_amount_in_row(rows[index - 1])
        if previous_amount is not None:
            return previous_amount
    return _first_amount_in_row(rows[index])


def _matches_other_concept(
    normalized: str,
    current_patterns: list[str],
    all_concepts: dict[str, list[str]] | None = None,
) -> bool:
    for patterns in (all_concepts or CASH_CALL_CONCEPTS).values():
        if patterns is current_patterns:
            continue
        if any(re.search(pattern, normalized, re.IGNORECASE) for pattern in patterns):
            return True
    return False


def _overhead_amounts_from_matches(matches: list[tuple[dict, float, bool]]) -> list[float]:
    detail_matches = [
        (row, amount)
        for row, amount, is_continuation in matches
        if is_continuation or _looks_like_summed_concept_detail(row["text"], "OVERHEAD")
    ]
    if not detail_matches:
        return [amount for _, amount, _ in matches]

    detail_amounts = [amount for _, amount in detail_matches]
    plain_amounts = [
        amount
        for row, amount, _ in matches
        if _is_plain_summed_concept_label(row["text"], "OVERHEAD")
    ]
    if any(_looks_like_time_based_summed_detail(row["text"]) for row, _ in detail_matches):
        return plain_amounts + detail_amounts
    return detail_amounts


def _is_plain_summed_concept_label(text: str, concept_field: str | None) -> bool:
    normalized = _normalize(text)
    if "ajustes" in normalized or "adjustments" in normalized:
        return False
    if concept_field == "OVERHEAD":
        label_pattern = r"\b(?:over(?:h|f)ead|gastos generales|costos indirectos|gastos indirectos)\b"
    else:
        label_pattern = r"\b(?:labor costs?|labou?r|costos laborales|gastos laborales|mano de obra)\b"
    text_without_amounts = AMOUNT_RE.sub("", normalized)
    text_without_label = re.sub(label_pattern, "", text_without_amounts, flags=re.IGNORECASE)
    text_without_label = re.sub(r"[\s$.,()-]+", "", text_without_label)
    return not text_without_label


def _looks_like_time_based_summed_detail(text: str) -> bool:
    normalized = _normalize(text)
    return bool(PERIOD_MONTH_RE.search(normalized) or re.search(r"\b20\d{2}\b", normalized))

def _looks_like_section_continuation(text: str) -> bool:
    normalized = _normalize(text)
    return "ajustes" in normalized or "adjustments for the period" in normalized


def _is_amount_only_row(text: str) -> bool:
    return _amount_from_text(text) is not None and not _has_meaningful_text(text)


def _has_meaningful_text(text: str) -> bool:
    text_without_amounts = AMOUNT_RE.sub("", text or "")
    
    # Reject noise rows consisting only of disconnected single characters (e.g. "U A A", "s")
    words = [w for w in re.split(r"[\s$.,()-]+", text_without_amounts) if w]
    if not words or all(len(w) == 1 for w in words):
        return False
        
    text_stripped = re.sub(r"[\s$.,()-]+", "", text_without_amounts)
    return sum(c.isalpha() for c in text_stripped) >= 2


def _looks_like_summed_concept_detail(text: str, concept_field: str | None) -> bool:
    normalized = _normalize(text)
    if (
        "ajustes" in normalized
        or "adjustments for the period" in normalized
        or "subtotal" in normalized
        or "total" in normalized
    ):
        return False
    if concept_field == "Labor Costs":
        label_pattern = r"\b(?:labor costs?|labou?r|costos laborales|gastos laborales|mano de obra)\b"
    else:
        label_pattern = r"\b(?:over(?:h|f)ead|gastos generales|costos indirectos|gastos indirectos)\b"
    text_without_amounts = AMOUNT_RE.sub("", normalized)
    text_without_label = re.sub(
        label_pattern,
        "",
        text_without_amounts,
        flags=re.IGNORECASE,
    )
    text_without_label = re.sub(r"[\s$.,()-]+", "", text_without_label)
    return bool(text_without_label)


def _continuation_amount(
    rows: list[dict],
    index: int,
    concept_field: str | None = None,
) -> float | None:
    """
    Only use the next row as a continuation when it looks like an amount-only
    fragment. This avoids stealing the amount from the next concept row.
    """
    if index + 1 >= len(rows):
        return None
    next_row = rows[index + 1]
    normalized = _normalize(next_row["text"])
    known_labels = [
        pattern
        for patterns in CASH_CALL_CONCEPTS.values()
        for pattern in patterns
    ]
    if any(re.search(pattern, normalized, re.IGNORECASE) for pattern in known_labels):
        return None
    if normalized.startswith("total") or "estimate" in normalized or "estimado" in normalized:
        return None
    if concept_field == "IAEEH" and PERIOD_MONTH_RE.search(normalized):
        return _first_amount_in_row(next_row)
    text_without_amounts = AMOUNT_RE.sub("", next_row["text"] or "")
    text_without_amounts = re.sub(r"[\s$.,()-]+", "", text_without_amounts)
    if len(text_without_amounts) > 6:
        return None
    return _first_amount_in_row(next_row)


def _extract_current_total(rows: list[dict]) -> float | None:
    for index, row in enumerate(rows):
        normalized = _normalize(row["text"])
        if _is_current_total_row(normalized):
            amount = _first_amount_in_row(row)
            if amount is not None:
                return amount
            if index + 1 < len(rows) and _is_amount_only_row(rows[index + 1]["text"]):
                return _first_amount_in_row(rows[index + 1])
            for previous_row in reversed(rows[max(0, index - 2) : index]):
                if not _is_amount_only_row(previous_row["text"]):
                    continue
                amount = _first_amount_in_row(previous_row)
                if amount is not None:
                    return amount
            if index > 0 and _uses_previous_amount_alignment(rows):
                return _first_amount_in_row(rows[index - 1])
    return None


def _is_current_total_row(normalized: str) -> bool:
    has_total = bool(re.search(r"\bt[o0]ta[l1i]\b", normalized))
    return (
        has_total
        and "subtotal" not in normalized
        and "sub total" not in normalized
        and "sub-total" not in normalized
    )


def _extract_participation_rows(rows: list[dict]) -> dict:
    result = {
        "PEMEX Participation %": None,
        "Partner Participation %": None,
        "Amount Due by PEMEX": None,
        "Amount Due by Partner": None,
    }
    labels = [
        "amount due by",
        "suma a pagar por",
        "monto a pagar por",
        "importe a pagar por",
        "cantidad a pagar por",
        "monto adeudado por",
        "importe adeudado por",
        "a cargo de",
    ]
    for row in rows:
        normalized = _normalize(row["text"])
        if not any(label in normalized for label in labels):
            continue
        percent = _first_percent(row["text"])
        amount = _first_amount_in_row(row)
        if "pep" in normalized or "pemex" in normalized:
            result["PEMEX Participation %"] = percent
            result["Amount Due by PEMEX"] = amount
        elif "wsd" in normalized or "wintershall" in normalized or "winter" in normalized:
            result["Partner Participation %"] = percent
            result["Amount Due by Partner"] = amount
        else:
            result["Partner Participation %"] = percent
            result["Amount Due by Partner"] = amount
    return result


def _looks_like_address(value: str) -> bool:
    normalized = _normalize(value)
    address_tokens = [
        "cp.",
        " c.p.",
        "col.",
        "avenida",
        "av.",
        "calle",
        "miguel hidalgo",
        "cdmx",
        "codigo postal",
    ]
    return any(token in normalized for token in address_tokens)


def _first_amount_in_row(row: dict) -> float | None:
    items = sorted(row["items"], key=lambda item: item["x"], reverse=True)
    for item in items:
        text = item["text"]
        if "%" in text or DATE_RE.search(text):
            continue
        amount = _amount_from_text(text)
        if amount is not None:
            return amount
    return _amount_from_text(row["text"])


def _amount_from_text(text: str) -> float | None:
    for match in AMOUNT_RE.finditer(text or ""):
        token = match.group(0)
        if "%" in token:
            continue
        
        # OCR garbage filter: valid cash call amounts either have decimals (e.g., .00) 
        # or are large numbers. If a matched token has no decimal and fewer than 3 digits,
        # it is almost certainly OCR garbage (like $$6$).
        if "." not in token and sum(c.isdigit() for c in token) < 3:
            continue
            
        amount = clean_amount(token)
        if amount is not None:
            return amount
    return None


def _first_percent(text: str) -> float | None:
    match = PERCENT_RE.search(text or "")
    return float(match.group(1)) if match else None


def _overall_confidence(ocr_data: list) -> float:
    confidences = [float(item.get("confidence") or 0) for item in ocr_data or []]
    return sum(confidences) / len(confidences) if confidences else 0.0


def _build_alerts(result: dict, ocr_data: list) -> list[str]:
    alerts = []
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
    missing = [field for field in required if result.get(field) in (None, "")]
    if missing:
        alerts.append("Campos faltantes: " + ", ".join(missing))

    concept_fields = list(CASH_CALL_CONCEPTS.keys())
    concept_amounts = [
        result.get(field) 
        for field in concept_fields 
        if result.get(field) is not None and field != "Intereses acumulados del mes"
    ]
    
    concepts_sum = round(sum(concept_amounts), 2) if concept_amounts else None
    if concepts_sum is not None:
        result["Total Conceptos"] = concepts_sum
        
    total = result.get("Total Current Period")
    if total is not None and concepts_sum is not None:
        if abs(concepts_sum - total) > 0.05:
            mandatory_concepts = ["IAEEH", "CUOTA CONTRACTUAL", "Mano de Obra Administrativa y Supervisión Técnica", "OVERHEAD"]
            missing_mandatory = [field for field in mandatory_concepts if result.get(field) in (None, "")]
            prefix = f"(Falta campo \"{', '.join(missing_mandatory)}\") " if missing_mandatory else ""
            alerts.append(
                f"{prefix}Total no cuadra con conceptos: "
                f"conceptos={concepts_sum:,.2f}, total={total:,.2f}"
            )

    if not ocr_data:
        alerts.append("OCR no devolvio texto")
    elif result["Overall Confidence"] < 0.85:
        alerts.append(f"Confianza OCR promedio baja: {result['Overall Confidence']:.2f}")

    return alerts


def _status_from_alerts(result: dict, alerts: list[str]) -> str:
    if not result["OCR Lines"]:
        return "Error"
    if alerts:
        return "Requiere revision"
    return "Validado"




