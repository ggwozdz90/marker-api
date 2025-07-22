from unittest.mock import Mock, patch

import pytest

from core.config.app_config import AppConfig
from core.logger.logger import Logger
from data.repositories.document_to_markdown_repository_impl import (
    DocumentToMarkdownRepositoryImpl,
)
from data.workers.markdown_worker import MarkdownWorker
from domain.repositories.directory_repository import DirectoryRepository


@pytest.fixture
def mock_logger() -> Logger:
    return Mock(Logger)


@pytest.fixture
def mock_config() -> AppConfig:
    mock_config = Mock(AppConfig)
    mock_config.marker_model_download_path = "/tmp/models"
    mock_config.device = "cpu"
    mock_config.marker_model_name = "vikp/marker"
    mock_config.log_level = "DEBUG"
    return mock_config


@pytest.fixture
def mock_directory_repository() -> DirectoryRepository:
    return Mock(DirectoryRepository)


@patch("data.repositories.document_to_markdown_repository_impl.MarkdownWorker")
def test_convert_to_markdown(
    mock_markdown_worker_class: Mock,
    mock_config: AppConfig,
    mock_directory_repository: DirectoryRepository,
    mock_logger: Logger,
) -> None:
    # Given
    DocumentToMarkdownRepositoryImpl._instance = None

    mock_worker = Mock(MarkdownWorker)
    mock_worker.convert.return_value = "# Test Markdown"
    mock_worker.is_alive.return_value = True
    mock_markdown_worker_class.return_value = mock_worker

    repository = DocumentToMarkdownRepositoryImpl(
        config=mock_config,
        directory_repository=mock_directory_repository,
        logger=mock_logger,
    )
    file_path = "/test/file.pdf"

    # When
    result = repository.convert_to_markdown(file_path)

    # Then
    assert result == "# Test Markdown"
    mock_directory_repository.create_directory.assert_called_once_with("/tmp/models")

    mock_markdown_worker_class.assert_called_once()
    call_args = mock_markdown_worker_class.call_args
    worker_config = call_args[0][0]  # pierwszy argument
    assert worker_config.device == "cpu"
    assert worker_config.marker_model_name == "vikp/marker"
    assert worker_config.marker_model_download_path == "/tmp/models"
    assert worker_config.log_level == "DEBUG"

    mock_worker.start.assert_called_once()
    mock_worker.convert.assert_called_once_with(file_path)
    mock_worker.is_alive.assert_called_once()
    mock_worker.stop.assert_called_once()


def test_singleton_pattern(
    mock_config: AppConfig,
    mock_directory_repository: DirectoryRepository,
    mock_logger: Logger,
) -> None:
    # Given
    DocumentToMarkdownRepositoryImpl._instance = None

    # When
    instance1 = DocumentToMarkdownRepositoryImpl(
        config=mock_config,
        directory_repository=mock_directory_repository,
        logger=mock_logger,
    )
    instance2 = DocumentToMarkdownRepositoryImpl(
        config=mock_config,
        directory_repository=mock_directory_repository,
        logger=mock_logger,
    )

    # Then
    assert instance1 is instance2


@patch("data.repositories.document_to_markdown_repository_impl.MarkdownWorker")
def test_convert_to_markdown_error_handling(
    mock_markdown_worker_class: Mock,
    mock_config: AppConfig,
    mock_directory_repository: DirectoryRepository,
    mock_logger: Logger,
) -> None:
    # Given
    DocumentToMarkdownRepositoryImpl._instance = None

    mock_worker = Mock(MarkdownWorker)
    mock_worker.convert.side_effect = RuntimeError("Conversion failed")
    mock_worker.is_alive.return_value = True
    mock_markdown_worker_class.return_value = mock_worker

    repository = DocumentToMarkdownRepositoryImpl(
        config=mock_config,
        directory_repository=mock_directory_repository,
        logger=mock_logger,
    )
    file_path = "/test/file.pdf"

    # When & Then
    with pytest.raises(RuntimeError, match="Conversion failed"):
        repository.convert_to_markdown(file_path)

    mock_worker.start.assert_called_once()
    mock_worker.convert.assert_called_once_with(file_path)
    mock_worker.is_alive.assert_called_once()
    mock_worker.stop.assert_called_once()
