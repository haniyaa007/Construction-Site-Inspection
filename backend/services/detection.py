from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Protocol

from fastapi import HTTPException

from backend import config


class ModelNotAvailableError(RuntimeError):
    pass


@dataclass(frozen=True)
class RawDetection:
    object_class: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float


class Detector(Protocol):
    def detect(self, image_path: Path) -> list[RawDetection]: ...


class YoloDetector:
    def __init__(self, model_path: Path, min_confidence: float):
        if not model_path.exists():
            raise ModelNotAvailableError(f"Detection model not found at {model_path}")
        from ultralytics import YOLO  # imported here: slow, and only needed in production

        self._model = YOLO(str(model_path))
        self._min_confidence = min_confidence

    def detect(self, image_path: Path) -> list[RawDetection]:
        result = self._model(str(image_path), conf=self._min_confidence, verbose=False)[0]
        detections = []
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append(
                RawDetection(
                    object_class=result.names[int(box.cls)],  # names come from the weights file
                    confidence=float(box.conf),
                    x1=x1, y1=y1, x2=x2, y2=y2,
                )
            )
        return detections


@lru_cache(maxsize=1)
def _load_detector() -> YoloDetector:
    return YoloDetector(config.MODEL_PATH, config.DETECTION_MIN_CONFIDENCE)


def get_detector() -> Detector:
    """FastAPI dependency. Loads the model once; 503 if the weights are missing."""
    try:
        return _load_detector()
    except ModelNotAvailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


def is_flagged(object_class: str, confidence: float) -> bool:
    return object_class in config.FLAGGED_CLASSES and confidence >= config.FLAG_MIN_CONFIDENCE