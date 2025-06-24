"""Utilities for semantic retrieval using pgvector."""
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_embedding
from app.db.models.content_version import ContentVersion

def _split_text(text: str, chunk_size: int = 500) -> List[str]:
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

async def index_content_version_chunks(
    db: AsyncSession, version: ContentVersion, chunk_size: int = 500
) -> None:
    """Split a document into chunks and store embeddings."""
    chunks = _split_text(version.markdown_content, chunk_size)
    for idx, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk)
        db.add(
            DocumentChunk(
                version_id=version.version_id,
                chunk_index=idx,
                chunk_text=chunk,
                embedding=embedding,
            )
        )
    await db.flush()

async def retrieve_top_k_chunks(
    db: AsyncSession, query_embedding: List[float], top_k: int = 5
) -> List[Tuple[str, float]]:
    """Return top-k text chunks ordered by cosine similarity."""
    stmt = (
        select(DocumentChunk.chunk_text, DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"))
        .order_by("distance")
        .limit(top_k)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [(row[0], row[1]) for row in rows]


async def get_relevant_snippets(db: AsyncSession, query_text: str, top_k: int = 5) -> List[str]:
    """Generate embedding for query_text and return relevant snippets."""
    embedding = generate_embedding(query_text)
    rows = await retrieve_top_k_chunks(db, embedding, top_k)
    return [text for text, _ in rows]


