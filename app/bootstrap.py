"""Optional runtime refresh after editing ``config.yaml`` (bonus: reload without full process restart)."""

from __future__ import annotations

from app.config.settings import get_settings, reload_settings
from app.utils.logger import configure_logging


def reload_runtime_configuration() -> None:
    """
    Reload YAML and reset embedding, vector store, and LLM singletons.

    Note: The vector store singleton is reset; on next use Chroma reopens
    ``vector_store.persist_directory`` (data on disk remains unless you delete that folder).
    """
    reload_settings()
    from app.services.embedding import reset_embeddings_for_tests
    from app.services.rag_pipeline import reset_llm_for_tests
    from app.services.vector_store import reset_vector_store_for_tests

    reset_embeddings_for_tests()
    reset_vector_store_for_tests()
    reset_llm_for_tests()
    configure_logging(get_settings())
