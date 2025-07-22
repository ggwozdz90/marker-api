from unittest.mock import AsyncMock, Mock, mock_open, patch

import pytest
from fastapi import UploadFile

from core.config.app_config import AppConfig
from core.logger.logger import Logger
from data.repositories.file_repository_impl import FileRepositoryImpl
from domain.exceptions.invalid_file_name_error import InvalidFileNameError
from domain.exceptions.invalid_file_path_error import InvalidFilePathError
from domain.repositories.directory_repository import DirectoryRepository


@pytest.fixture
def mock_logger() -> Logger:
    return Mock(Logger)


@pytest.fixture
def mock_config() -> AppConfig:
    mock_config = Mock(AppConfig)
    mock_config.file_upload_path = "/tmp/uploads"
    return mock_config


@pytest.fixture
def mock_directory_repository() -> DirectoryRepository:
    return Mock(DirectoryRepository)


@pytest.fixture
def file_repository(
    mock_config: AppConfig,
    mock_logger: Logger,
    mock_directory_repository: DirectoryRepository,
) -> FileRepositoryImpl:
    return FileRepositoryImpl(
        config=mock_config,
        logger=mock_logger,
        directory_repository=mock_directory_repository,
    )


@pytest.mark.asyncio
async def test_save_file(
    file_repository: FileRepositoryImpl,
    mock_config: AppConfig,
    mock_directory_repository: DirectoryRepository,
) -> None:
    # Given
    mock_file = Mock(UploadFile)
    mock_file.filename = "test_file.txt"
    mock_file.read = AsyncMock(side_effect=[b"file content", b""])

    # When
    with patch("builtins.open", mock_open()) as mock_file_open, patch("os.path.abspath") as mock_abspath:
        mock_abspath.return_value = "/tmp/uploads/test_file.txt"
        result = await file_repository.save_file(mock_file)

    # Then
    mock_directory_repository.create_directory.assert_called_once_with(mock_config.file_upload_path)
    mock_file_open.assert_called_once_with("/tmp/uploads/test_file.txt", "wb")
    assert result == "/tmp/uploads/test_file.txt"


@pytest.mark.asyncio
async def test_save_file_invalid_filename_raises_error(
    file_repository: FileRepositoryImpl,
    mock_config: AppConfig,
) -> None:
    # Given
    mock_file = Mock(UploadFile)
    mock_file.filename = "../../../etc/passwd"
    mock_file.read = AsyncMock(return_value=b"content")

    # When & Then
    with pytest.raises(InvalidFileNameError):
        await file_repository.save_file(mock_file)


def test_delete_file(
    file_repository: FileRepositoryImpl,
    mock_config: AppConfig,
    mock_directory_repository: DirectoryRepository,
) -> None:
    # Given
    file_path = "/tmp/uploads/test_file.txt"

    # When
    with (
        patch("os.remove") as mock_remove,
        patch("os.path.abspath") as mock_abspath,
        patch("os.path.normpath") as mock_normpath,
    ):
        mock_abspath.return_value = "/tmp/uploads/test_file.txt"
        mock_normpath.side_effect = lambda x: x
        file_repository.delete_file(file_path)

    # Then
    mock_directory_repository.create_directory.assert_called_once_with(mock_config.file_upload_path)
    mock_remove.assert_called_once_with("/tmp/uploads/test_file.txt")


def test_delete_file_invalid_path_raises_error(
    file_repository: FileRepositoryImpl,
) -> None:
    # Given
    file_path = "/etc/passwd"

    # When & Then
    with pytest.raises(InvalidFilePathError):
        file_repository.delete_file(file_path)
