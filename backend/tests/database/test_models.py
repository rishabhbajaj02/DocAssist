from pgvector.sqlalchemy import Vector
from sqlalchemy import Computed
from sqlalchemy.dialects.postgresql import TSVECTOR

from app.database.models import Base


def test_phase_one_tables_and_foreign_keys() -> None:
    tables = Base.metadata.tables

    assert set(tables) == {
        "users",
        "source_documents",
        "document_chunks",
        "chat_threads",
        "chat_messages",
        "message_citations",
    }
    assert {str(fk.column) for fk in tables["document_chunks"].c.document_id.foreign_keys} == {
        "source_documents.id"
    }
    assert {str(fk.column) for fk in tables["chat_threads"].c.user_id.foreign_keys} == {
        "users.id"
    }
    assert {str(fk.column) for fk in tables["chat_messages"].c.thread_id.foreign_keys} == {
        "chat_threads.id"
    }
    assert {str(fk.column) for fk in tables["message_citations"].c.message_id.foreign_keys} == {
        "chat_messages.id"
    }
    assert {str(fk.column) for fk in tables["message_citations"].c.chunk_id.foreign_keys} == {
        "document_chunks.id"
    }


def test_chunks_have_vector_and_generated_search_column() -> None:
    chunks = Base.metadata.tables["document_chunks"]

    assert isinstance(chunks.c.embedding.type, Vector)
    assert chunks.c.embedding.type.dim == 1536
    assert isinstance(chunks.c.search_vector.type, TSVECTOR)
    assert isinstance(chunks.c.search_vector.computed, Computed)
