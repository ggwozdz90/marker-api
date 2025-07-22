from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import UploadFile

from api.dtos.markdown_response_dto import MarkdownResponseDTO
from api.routers.markdown_router import MarkdownRouter
from application.usecases.convert_document_usecase import ConvertDocumentUseCase


@pytest.fixture
def mock_convert_document_to_markdown_usecase() -> ConvertDocumentUseCase:
    mock_usecase = Mock(ConvertDocumentUseCase)
    mock_usecase.execute = AsyncMock(return_value="# Test Markdown Content")
    return mock_usecase


@pytest.fixture
def markdown_router() -> MarkdownRouter:
    return MarkdownRouter()


@pytest.mark.asyncio
async def test_markdown(
    markdown_router: MarkdownRouter,
    mock_convert_document_to_markdown_usecase: ConvertDocumentUseCase,
) -> None:
    # Given
    mock_file = Mock(UploadFile)
    mock_file.filename = "test.pdf"

    # When
    result = await markdown_router.markdown(
        convert_document_usecase=mock_convert_document_to_markdown_usecase,
        file=mock_file,
    )

    # Then
    mock_convert_document_to_markdown_usecase.execute.assert_called_once_with(mock_file)
    assert isinstance(result, MarkdownResponseDTO)
    assert result.content == "# Test Markdown Content"
