import logging
import os
import subprocess
import warnings
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PADDLEX_CACHE_DIR = PROJECT_ROOT / "models" / "paddlex"

# PaddleX reads its cache location while importing, so configure it first.
os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(PADDLEX_CACHE_DIR))
os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")
os.environ.setdefault("GLOG_minloglevel", "2")
os.environ.setdefault("FLAGS_minloglevel", "2")

logging.getLogger("ppocr").setLevel(logging.WARNING)
logging.getLogger("paddlex").setLevel(logging.WARNING)
warnings.filterwarnings("ignore", message=r"No ccache found\..*")


class OCRProcessor:
    def __init__(self, lang="en", device="cpu"):
        """
        Initializes PaddleOCR locally. The adapter supports PaddleOCR 2.x and 3.x.
        """
        PADDLEX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.device = device
        self.ocr = self._create_engine(lang)

    def extract_text_with_boxes(self, image_path: str):
        """
        Returns OCR items with text, box and confidence.
        """
        result = self._run_ocr(image_path)
        extracted_data = []
        for line in self._iter_lines(result):
            extracted_data.append(
                {
                    "text": line["text"],
                    "box": line["box"],
                    "confidence": line["confidence"],
                }
            )
        return extracted_data

    def _create_engine(self, lang):
        try:
            import paddleocr
            from paddleocr import PaddleOCR
        except Exception as exc:
            raise RuntimeError(
                "PaddleOCR/PaddlePaddle no estan instalados en este entorno. "
                "Ejecuta: pip install -r requirements.txt. "
                f"Detalle tecnico: {exc}"
            ) from exc

        if self.device == "gpu" and not _paddle_cuda_available():
            raise RuntimeError(
                "La GPU NVIDIA fue seleccionada, pero PaddlePaddle no tiene soporte CUDA en este entorno. "
                "Instala una compilacion de PaddlePaddle compatible con CUDA y reinicia la aplicacion."
            )

        paddle_version = _package_version("paddlepaddle")
        paddleocr_version = getattr(paddleocr, "__version__", _package_version("paddleocr"))
        base_attempts = [
            {"use_angle_cls": True, "lang": lang, "show_log": False},
            {"use_angle_cls": True, "lang": lang},
            {
                "use_textline_orientation": True,
                "use_doc_orientation_classify": False,
                "use_doc_unwarping": False,
                "lang": lang,
            },
            {"lang": lang},
        ]
        device_attempts = [{"device": "gpu:0"}, {"device": "gpu"}, {"use_gpu": True}] if self.device == "gpu" else [{}]
        last_error = None
        for device_kwargs in device_attempts:
            for base_kwargs in base_attempts:
                try:
                    return PaddleOCR(**device_kwargs, **base_kwargs)
                except Exception as exc:
                    last_error = exc
        raise RuntimeError(
            "No se pudo inicializar PaddleOCR. "
            f"Versiones detectadas: paddlepaddle={paddle_version}, paddleocr={paddleocr_version}. "
            "Si usas PaddleOCR 3.x, instala PaddlePaddle 3.0 o superior. "
            "Comando recomendado: pip install --upgrade paddlepaddle==3.2.0 "
            "paddleocr>=3.0.0,<3.7.0. "
            f"Detalle tecnico: {last_error}"
        )

    def _run_ocr(self, image_path):
        attempts = [
            lambda: self.ocr.ocr(image_path, cls=True),
            lambda: self.ocr.ocr(image_path, use_textline_orientation=True),
            lambda: self.ocr.predict(image_path, use_textline_orientation=True),
            lambda: self.ocr.ocr(image_path),
            lambda: self.ocr.predict(image_path),
        ]
        for attempt in attempts:
            try:
                return attempt()
            except (TypeError, ValueError):
                continue
        return []

    def _iter_lines(self, result):
        # PaddleOCR 2.x: [[[box, (text, confidence)], ...]]
        if isinstance(result, list) and result and isinstance(result[0], list):
            for item in result[0]:
                if item and len(item) >= 2:
                    yield {
                        "box": _box_to_list(item[0]),
                        "text": str(item[1][0]),
                        "confidence": float(item[1][1] or 0),
                    }
            return

        # PaddleOCR/PaddleX 3.x: list of dict-like OCRResult objects.
        pages = result if isinstance(result, list) else [result]
        for page in pages:
            data = dict(page) if hasattr(page, "keys") else page
            if isinstance(data, dict) and "res" in data and isinstance(data["res"], dict):
                data = data["res"]
            if not isinstance(data, dict):
                continue

            texts = data.get("rec_texts") or []
            scores = data.get("rec_scores") or []
            boxes = data.get("rec_polys") or data.get("dt_polys") or []
            for index, text in enumerate(texts):
                box = boxes[index] if index < len(boxes) else []
                score = scores[index] if index < len(scores) else 0
                yield {
                    "box": _box_to_list(box),
                    "text": str(text),
                    "confidence": float(score or 0),
                }


def _box_to_list(box):
    if hasattr(box, "tolist"):
        return box.tolist()
    return box or []


def _package_version(package_name: str) -> str:
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "desconocida"


_ocr_instances = {}


def get_ocr_instance(device: str = "cpu"):
    normalized_device = "gpu" if device == "gpu" else "cpu"
    if normalized_device not in _ocr_instances:
        _ocr_instances[normalized_device] = OCRProcessor(device=normalized_device)
    return _ocr_instances[normalized_device]


def get_nvidia_gpu_name() -> str | None:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            check=True,
            text=True,
            timeout=3,
        )
        return result.stdout.splitlines()[0].strip() or None
    except (OSError, subprocess.SubprocessError, IndexError):
        return None


def _paddle_cuda_available() -> bool:
    try:
        import paddle

        return bool(paddle.is_compiled_with_cuda())
    except Exception:
        return False
