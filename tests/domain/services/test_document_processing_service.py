from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import UploadFile

from core.config.app_config import AppConfig
from core.logger.logger import Logger
from domain.repositories.document_to_markdown_repository import (
    DocumentToMarkdownRepository,
)
from domain.repositories.file_repository import FileRepository
from domain.services.document_processing_service import DocumentProcessingService


@pytest.fixture
def mock_logger() -> Logger:
    return Mock(Logger)


@pytest.fixture
def mock_config() -> AppConfig:
    mock_config = Mock(AppConfig)
    mock_config.delete_files_after_processing = True
    return mock_config


@pytest.fixture
def mock_file_repository() -> FileRepository:
    mock_repo = Mock(FileRepository)
    mock_repo.save_file = AsyncMock(return_value="/tmp/test.pdf")
    mock_repo.delete_file = Mock()
    return mock_repo


@pytest.fixture
def mock_document_to_markdown_repository() -> DocumentToMarkdownRepository:
    mock_repo = Mock(DocumentToMarkdownRepository)
    mock_repo.convert_to_markdown = Mock(return_value="# Test Markdown")
    return mock_repo


@pytest.fixture
def document_processing_service(
    mock_config: AppConfig,
    mock_file_repository: FileRepository,
    mock_document_to_markdown_repository: DocumentToMarkdownRepository,
    mock_logger: Logger,
) -> DocumentProcessingService:
    return DocumentProcessingService(
        config=mock_config,
        file_repository=mock_file_repository,
        document_to_markdown_repository=mock_document_to_markdown_repository,
        logger=mock_logger,
    )


@pytest.mark.asyncio
async def test_process_document_with_file_deletion(
    document_processing_service: DocumentProcessingService,
    mock_file_repository: FileRepository,
    mock_document_to_markdown_repository: DocumentToMarkdownRepository,
    mock_logger: Logger,
) -> None:
    # Given
    mock_file = Mock(UploadFile)
    mock_file.filename = "test.pdf"

    # When
    result = await document_processing_service.process_document(mock_file)

    # Then
    mock_file_repository.save_file.assert_called_once_with(mock_file)
    mock_document_to_markdown_repository.convert_to_markdown.assert_called_once_with("/tmp/test.pdf")
    mock_file_repository.delete_file.assert_called_once_with("/tmp/test.pdf")
    assert result == "# Test Markdown"
    mock_logger.debug.assert_any_call("Starting document processing for file 'test.pdf'")
    mock_logger.debug.assert_any_call("Completed document processing for file 'test.pdf'")


@pytest.mark.asyncio
async def test_process_document_without_file_deletion(
    mock_config: AppConfig,
    mock_file_repository: FileRepository,
    mock_document_to_markdown_repository: DocumentToMarkdownRepository,
    mock_logger: Logger,
) -> None:
    # Given
    mock_config.delete_files_after_processing = False
    service = DocumentProcessingService(
        config=mock_config,
        file_repository=mock_file_repository,
        document_to_markdown_repository=mock_document_to_markdown_repository,
        logger=mock_logger,
    )
    mock_file = Mock(UploadFile)
    mock_file.filename = "test.pdf"

    # When
    result = await service.process_document(mock_file)

    # Then
    mock_file_repository.save_file.assert_called_once_with(mock_file)
    mock_document_to_markdown_repository.convert_to_markdown.assert_called_once_with("/tmp/test.pdf")
    mock_file_repository.delete_file.assert_not_called()
    assert result == "# Test Markdown"
