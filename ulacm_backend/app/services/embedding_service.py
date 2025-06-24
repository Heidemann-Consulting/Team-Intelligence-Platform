from typing import List
import logging

try:
    from sentence_transformers import SentenceTransformer
except Exception as e:  # catch ImportError
    SentenceTransformer = None  # type: ignore
    logging.getLogger(__name__).warning("sentence-transformers not available: %s", e)


_logger = logging.getLogger(__name__)
_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers package is not installed")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        _logger.info("Loaded embedding model all-MiniLM-L6-v2")
    return _model


def generate_embedding(text: str) -> List[float]:
    """Generate an embedding vector for the given text."""
    model = _get_model()
    embedding = model.encode(text)
    return embedding.tolist()
