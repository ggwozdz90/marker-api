from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import UploadFile

from application.usecases.convert_document_usecase import ConvertDocumentUseCase
from core.config.app_config import AppConfig
from core.logger.logger import Logger
from domain.services.document_processing_service import DocumentProcessingService


@pytest.fixture
def mock_logger() -> Logger:
    return Mock(Logger)


@pytest.fixture
def mock_config() -> AppConfig:
    return Mock(AppConfig)


@pytest.fixture
def mock_document_processing_service() -> DocumentProcessingService:
    mock_service = Mock(DocumentProcessingService)
    mock_service.process_document = AsyncMock(return_value="# Converted Markdown")
    return mock_service


@pytest.fixture
def use_case(
    mock_config: AppConfig,
    mock_logger: Logger,
    mock_document_processing_service: DocumentProcessingService,
) -> ConvertDocumentUseCase:
    return ConvertDocumentUseCase(
        config=mock_config,
        logger=mock_logger,
        document_processing_service=mock_document_processing_service,
    )


@pytest.mark.asyncio
async def test_execute(
    use_case: ConvertDocumentUseCase,
    mock_document_processing_service: DocumentProcessingService,
    mock_logger: Logger,
) -> None:
    # Given
    mock_file = Mock(UploadFile)
    mock_file.filename = "test.pdf"

    # When
    result = await use_case.execute(mock_file)

    # Then
    mock_document_processing_service.process_document.assert_called_once_with(mock_file)
    assert result == "# Converted Markdown"
    mock_logger.info.assert_any_call("Executing document conversion for file 'test.pdf'")
    mock_logger.info.assert_any_call("Returning conversion result for file 'test.pdf'")
