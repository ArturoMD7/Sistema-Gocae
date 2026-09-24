from pathlib import Path
import tempfile

from src.contract_registry import apply_contract_catalog
from src.extractor import extract_cash_call_data
from src.learning_memory import apply_corrections, get_all_corrections
from src.ocr import get_ocr_instance
from src.preprocessing import preprocess_image
from src.utils import pdf_to_images


def process_cash_call_document(
    file_name: str,
    file_bytes: bytes,
    use_docqa: bool = False,
    docqa_min_score: float = 0.15,
    docqa_overwrite: bool = True,
    ocr_device: str = "cpu",
) -> dict:
    """Process one PDF without depending on Streamlit state."""
    with tempfile.TemporaryDirectory(prefix="cashcall_") as temp_dir:
        temp_path = Path(temp_dir)
        pdf_path = temp_path / "document.pdf"
        pdf_path.write_bytes(file_bytes)

        image_paths = pdf_to_images(str(pdf_path), str(temp_path))
        if not image_paths:
            return _error_record(file_name, "No se pudo convertir el PDF a imagen.")

        processed_image = preprocess_image(image_paths[0], str(temp_path))
        ocr_result = get_ocr_instance(device=ocr_device).extract_text_with_boxes(processed_image)
        corrections = get_all_corrections()
        for item in ocr_result:
            item["text"] = apply_corrections(item.get("text", ""), corrections)

        extracted = extract_cash_call_data(ocr_result, file_name)
        if use_docqa:
            from src.docqa_model import answer_cash_call_fields, apply_docqa_answers

            docqa_answers = answer_cash_call_fields(
                processed_image,
                ocr_result,
                min_score=docqa_min_score,
            )
            extracted = apply_docqa_answers(
                extracted,
                docqa_answers,
                overwrite=docqa_overwrite,
            )

        return apply_contract_catalog(extracted)


def error_record(file_name: str, error: Exception | str) -> dict:
    return _error_record(file_name, str(error))


def _error_record(file_name: str, message: str) -> dict:
    return {
        "Archivo": file_name,
        "Alertas": f"Error al procesar documento: {message}",
        "Estado": "Error",
    }
