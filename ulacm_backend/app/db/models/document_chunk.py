from sqlalchemy import Column, ForeignKey, Integer, TEXT
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid

from app.db.base_class import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id = Column(UUID(as_uuid=True), ForeignKey("content_versions.version_id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(TEXT, nullable=False)
    embedding = Column(Vector(384), nullable=False)

    version = relationship("ContentVersion", back_populates="chunks")

