"""Config-driven text splitting for RAG chunks."""

from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

from app.config.settings import get_settings


def split_documents(documents: list[Document], markdown: bool = False) -> list[Document]:
    """``markdown``: the text is Markdown (uploads, converted by MarkItDown), so prefer
    breaking at headings, then paragraphs and list items, before lines and words."""
    s = get_settings()
    size, overlap = s.chunking.chunk_size, s.chunking.chunk_overlap
    if markdown:
        splitter = RecursiveCharacterTextSplitter.from_language(
            Language.MARKDOWN, chunk_size=size, chunk_overlap=overlap
        )
    else:
        splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
    chunks = splitter.split_documents(documents)
    for i, doc in enumerate(chunks):
        doc.metadata = {**doc.metadata, "chunk_index": i}
    return chunks
