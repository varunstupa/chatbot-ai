"""Single Chroma collection of guide chunks. Content only; no access decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_chroma import Chroma

from app.knowledge.parser import Chunk


class ChunkIndex:
    def __init__(self, persist_directory: Path, collection_name: str, embeddings: Any):
        self._store = Chroma(
            persist_directory=str(persist_directory),
            collection_name=collection_name,
            embedding_function=embeddings,
        )

    @property
    def _collection(self):
        return self._store._collection

    def replace_document(self, doc_id: str, chunks: list[Chunk]) -> None:
        """Swap a document's chunks for new ones (re-embeds them)."""
        self.delete_document(doc_id)
        if chunks:
            self._store.add_texts(
                texts=[c.text for c in chunks],
                metadatas=[c.metadata for c in chunks],
                ids=[c.chunk_id for c in chunks],
            )

    def delete_document(self, doc_id: str) -> None:
        self._collection.delete(where={"doc_id": doc_id})

    def count(self, doc_id: str) -> int:
        return len(self._collection.get(where={"doc_id": doc_id}, include=[])["ids"])

    def set_route(self, doc_id: str, route: str) -> None:
        """Rewrite the informational route on a document's chunks without re-embedding."""
        got = self._collection.get(where={"doc_id": doc_id}, include=["metadatas"])
        ids = got.get("ids") or []
        if not ids:
            return
        metadatas = [{**(m or {}), "route": route} for m in got.get("metadatas") or []]
        self._collection.update(ids=ids, metadatas=metadatas)

    def query(self, text: str, doc_ids: list[str], k: int) -> list[tuple[str, dict, float]]:
        """Closest chunks among the given documents: (text, metadata, distance)."""
        if not doc_ids:
            return []
        results = self._store.similarity_search_with_score(
            text, k=k, filter={"doc_id": {"$in": doc_ids}}
        )
        return [(doc.page_content or "", doc.metadata or {}, float(score)) for doc, score in results]

    def document_chunks(self, doc_id: str) -> list[tuple[str, dict]]:
        """All chunks of one document in reading order."""
        got = self._collection.get(where={"doc_id": doc_id}, include=["documents", "metadatas"])
        rows = list(zip(got.get("documents") or [], got.get("metadatas") or []))
        return sorted(rows, key=lambda row: (row[1] or {}).get("chunk_index", 0))

    def collection_names(self) -> list[str]:
        return [c.name for c in self._store._client.list_collections()]
