"""Config-driven text splitting for RAG chunks."""

from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import get_settings


def split_documents(documents: list[Document]) -> list[Document]:
    s = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=s.chunking.chunk_size,
        chunk_overlap=s.chunking.chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    for i, doc in enumerate(chunks):
        doc.metadata = {**doc.metadata, "chunk_index": i}
    return chunks
