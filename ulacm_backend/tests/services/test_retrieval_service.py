import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.sql import Select

from app.services.retrieval_service import retrieve_top_k_chunks, get_relevant_snippets

pytestmark = pytest.mark.asyncio


async def test_retrieve_top_k_chunks_builds_query(mock_db_session):
    query_embedding = [0.1, 0.2]
    mock_result = MagicMock()
    mock_result.all.return_value = [("chunk", 0.05)]
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await retrieve_top_k_chunks(mock_db_session, query_embedding, top_k=1)

    mock_db_session.execute.assert_awaited_once()
    stmt = mock_db_session.execute.call_args[0][0]
    assert isinstance(stmt, Select)
    compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
    assert "document_chunks" in compiled
    assert "<=>" in compiled
    assert "LIMIT 1" in compiled
    assert result == [("chunk", 0.05)]


async def test_get_relevant_snippets_uses_embedding(mock_db_session):
    with patch(
        "app.services.retrieval_service.generate_embedding",
        return_value=[0.3, 0.4],
    ) as mock_gen, patch(
        "app.services.retrieval_service.retrieve_top_k_chunks",
        AsyncMock(return_value=[("txt", 0.1)]),
    ) as mock_retrieve:
        snippets = await get_relevant_snippets(mock_db_session, "query", top_k=1)

    mock_gen.assert_called_once_with("query")
    mock_retrieve.assert_awaited_once_with(mock_db_session, [0.3, 0.4], 1)
    assert snippets == ["txt"]

