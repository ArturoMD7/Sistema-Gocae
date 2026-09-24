import math
import re
from functools import lru_cache
from pathlib import Path

from PIL import Image

from src.validators import clean_amount


MODEL_NAME = "impira/layoutlm-document-qa"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_CACHE_DIR = PROJECT_ROOT / "models" / "huggingface"
MAX_ANSWER_TOKENS = 24

FIELD_QUESTIONS = {
    "Emisor": [
        "Who issued this cash call?",
        "What company issued this document?",
    ],
    "Partner Receptor": [
        "Who is the partner or recipient of the cash call?",
        "Who should pay this cash call?",
    ],
    "Contrato": [
        "What is the contract number?",
        "What is the contractual area or contract name?",
    ],
    "Date": [
        "What is the date?",
    ],
    "Accounting Period": [
        "What is the accounting period?",
    ],
    "Reference": [
        "What is the reference number?",
    ],
    "Payment Due Date": [
        "What is the payment due date?",
        "When is the payment due?",
    ],
    "Total Current Period": [
        "What is the total cash call amount for the current period?",
    ],
    "PEMEX Participation %": [
        "What is the PEMEX participation percentage?",
        "What percentage corresponds to PEP?",
    ],
    "Partner Participation %": [
        "What is the partner participation percentage?",
    ],
    "Amount Due by PEMEX": [
        "What is the amount due by PEMEX or PEP?",
    ],
    "Amount Due by Partner": [
        "What is the amount due by the partner?",
    ],
}

AMOUNT_FIELDS = {
    "Total Current Period",
    "Amount Due by PEMEX",
    "Amount Due by Partner",
}
PERCENT_FIELDS = {"PEMEX Participation %", "Partner Participation %"}


def answer_cash_call_fields(image_path: str, ocr_data: list, min_score: float = 0.15) -> dict:
    """
    Runs local LayoutLM document QA using PaddleOCR words and boxes.

    First run downloads the Hugging Face model to local cache. Later runs are local.
    """
    words, boxes = _ocr_to_words_and_boxes(ocr_data, image_path)
    if not words:
        return {"_error": "DocQA no recibio palabras OCR."}

    try:
        tokenizer, model, torch = _load_docqa_model()
    except Exception as exc:
        return {"_error": f"No se pudo cargar LayoutLM DocQA: {exc}"}

    answers = {}
    for field, questions in FIELD_QUESTIONS.items():
        best = None
        for question in questions:
            try:
                candidate = _answer_question(tokenizer, model, torch, question, words, boxes)
            except Exception as exc:
                candidate = {"answer": "", "score": 0.0, "error": str(exc)}
            if best is None or candidate["score"] > best["score"]:
                best = candidate

        if best and best["answer"] and best["score"] >= min_score:
            answers[field] = {
                "value": _coerce_answer(field, best["answer"]),
                "raw_answer": best["answer"],
                "score": round(best["score"], 4),
            }
    return answers


def apply_docqa_answers(record: dict, answers: dict, overwrite: bool = True) -> dict:
    if not answers or "_error" in answers:
        if answers and "_error" in answers:
            record["DocQA"] = answers["_error"]
        return record

    applied = []
    for field, answer in answers.items():
        value = answer["value"]
        if value in (None, ""):
            continue
        if overwrite or record.get(field) in (None, ""):
            record[field] = value
            applied.append(f"{field}={answer['raw_answer']} ({answer['score']:.2f})")

    if applied:
        record["DocQA"] = "Aplicado: " + "; ".join(applied)
    else:
        record["DocQA"] = "Sin cambios"
    return record


def _answer_question(tokenizer, model, torch, question: str, words: list[str], boxes: list[list[int]]) -> dict:
    encoding = tokenizer(
        question,
        words,
        boxes=boxes,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )
    with torch.no_grad():
        outputs = model(**encoding)

    start_logits = outputs.start_logits[0]
    end_logits = outputs.end_logits[0]
    candidate_indices = _document_token_indices(encoding)
    if not candidate_indices:
        return {"answer": "", "score": 0.0}

    start_probs = torch.softmax(start_logits, dim=-1)
    end_probs = torch.softmax(end_logits, dim=-1)
    best_score = -math.inf
    best_span = None
    for start in candidate_indices:
        max_end = min(start + MAX_ANSWER_TOKENS, candidate_indices[-1])
        for end in candidate_indices:
            if end < start or end > max_end:
                continue
            score = float(start_probs[start] * end_probs[end])
            if score > best_score:
                best_score = score
                best_span = (start, end)

    if best_span is None:
        return {"answer": "", "score": 0.0}

    input_ids = encoding["input_ids"][0][best_span[0] : best_span[1] + 1]
    answer = tokenizer.decode(input_ids, skip_special_tokens=True).strip()
    answer = _clean_answer(answer)
    return {"answer": answer, "score": max(best_score, 0.0)}


def _document_token_indices(encoding) -> list[int]:
    attention = encoding.get("attention_mask")
    token_types = encoding.get("token_type_ids")
    input_ids = encoding.get("input_ids")
    if attention is None or input_ids is None:
        return []

    indices = []
    for index, active in enumerate(attention[0].tolist()):
        if not active:
            continue
        if token_types is not None and int(token_types[0][index]) != 1:
            continue
        token_id = int(input_ids[0][index])
        if token_id in (0, 1, 2, 3):
            continue
        indices.append(index)
    return indices


def _ocr_to_words_and_boxes(ocr_data: list, image_path: str) -> tuple[list[str], list[list[int]]]:
    width, height = Image.open(image_path).size
    words = []
    boxes = []
    for item in ocr_data or []:
        text = str(item.get("text", "") or "").strip()
        if not text:
            continue
        box = _normalize_box(item.get("box") or [], width, height)
        split_words = text.split()
        for word_box in _split_box_for_words(box, split_words):
            word, sub_box = word_box
            words.append(word)
            boxes.append(sub_box)
    return words[:480], boxes[:480]


def _normalize_box(box: list, width: int, height: int) -> list[int]:
    if not box:
        return [0, 0, 1000, 1000]
    try:
        xs = [point[0] for point in box]
        ys = [point[1] for point in box]
        left, top, right, bottom = min(xs), min(ys), max(xs), max(ys)
        return [
            _clip_1000(left / width * 1000),
            _clip_1000(top / height * 1000),
            _clip_1000(right / width * 1000),
            _clip_1000(bottom / height * 1000),
        ]
    except Exception:
        return [0, 0, 1000, 1000]


def _split_box_for_words(box: list[int], words: list[str]):
    if not words:
        return []
    left, top, right, bottom = box
    total_chars = sum(max(len(word), 1) for word in words)
    cursor = left
    result = []
    for word in words:
        width = max(1, int((right - left) * max(len(word), 1) / max(total_chars, 1)))
        word_box = [cursor, top, min(right, cursor + width), bottom]
        result.append((word, word_box))
        cursor += width
    return result


def _clip_1000(value: float) -> int:
    return max(0, min(1000, int(round(value))))


def _coerce_answer(field: str, answer: str):
    if field in AMOUNT_FIELDS:
        return clean_amount(answer)
    if field in PERCENT_FIELDS:
        match = re.search(r"\d{1,3}(?:\.\d+)?", answer or "")
        return float(match.group(0)) if match else None
    return answer


def _clean_answer(answer: str) -> str:
    answer = re.sub(r"\s+", " ", answer or "").strip()
    answer = answer.replace(" ##", "")
    return answer


@lru_cache(maxsize=1)
def _load_docqa_model():
    import torch
    from transformers import AutoModelForDocumentQuestionAnswering, AutoTokenizer

    MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        cache_dir=MODEL_CACHE_DIR,
        clean_up_tokenization_spaces=True,
    )
    model = AutoModelForDocumentQuestionAnswering.from_pretrained(MODEL_NAME, cache_dir=MODEL_CACHE_DIR)
    model.eval()
    return tokenizer, model, torch
