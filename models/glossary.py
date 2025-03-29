from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, VECTOR
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class GlossaryTerm(Base):
    __tablename__ = "glossary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    term = Column(String, unique=True, nullable=False)
    definition = Column(Text, nullable=False)
    simplified_explanation = Column(Text)
    contextual_examples = Column(JSON)
    vector_embedding = Column(VECTOR(1536))  # OpenAI Ada-002 Embeddings
