import os
from unittest.mock import Mock, patch

import pytest

from core.logger.logger import Logger
from data.workers.markdown_worker import MarkdownWorker, MarkdownWorkerConfig


@pytest.fixture
def mock_logger() -> Logger:
    return Mock(Logger)


@pytest.fixture
def worker_config() -> MarkdownWorkerConfig:
    return MarkdownWorkerConfig(
        device="cpu",
        marker_model_name="vikp/marker",
        marker_model_download_path="/tmp/models",
        log_level="DEBUG",
    )


@pytest.fixture
def markdown_worker(
    worker_config: MarkdownWorkerConfig,
    mock_logger: Logger,
) -> MarkdownWorker:
    return MarkdownWorker(worker_config, mock_logger)


def test_convert_success(
    markdown_worker: MarkdownWorker,
) -> None:
    # Given
    file_path = "/test/file.pdf"
    expected_result = "# Test Markdown Content"

    with patch.object(markdown_worker, "is_alive", return_value=True):
        with patch.object(markdown_worker, "_pipe_parent") as mock_pipe:
            mock_pipe.recv.return_value = expected_result

            # When
            result = markdown_worker.convert(file_path)

            # Then
            assert result == expected_result
            mock_pipe.send.assert_called_once_with(("convert", file_path))
            mock_pipe.recv.assert_called_once()


def test_convert_worker_not_running(
    markdown_worker: MarkdownWorker,
) -> None:
    # Given
    file_path = "/test/file.pdf"

    with patch.object(markdown_worker, "is_alive", return_value=False):
        # When & Then
        with pytest.raises(RuntimeError, match="Worker is not running"):
            markdown_worker.convert(file_path)


def test_convert_error_handling(
    markdown_worker: MarkdownWorker,
) -> None:
    # Given
    file_path = "/test/file.pdf"
    error_message = "Conversion failed"
    test_exception = RuntimeError(error_message)

    with patch.object(markdown_worker, "is_alive", return_value=True):
        with patch.object(markdown_worker, "_pipe_parent") as mock_pipe:
            mock_pipe.recv.return_value = test_exception

            # When & Then
            with pytest.raises(RuntimeError, match=error_message):
                markdown_worker.convert(file_path)


@patch("data.workers.markdown_worker.text_from_rendered")
@patch("data.workers.markdown_worker.PdfConverter")
@patch("data.workers.markdown_worker.create_model_dict")
@patch("data.workers.markdown_worker.os.environ", {})
def test_initialize_shared_object_success(
    mock_create_model_dict: Mock,
    mock_pdf_converter_class: Mock,
    mock_text_from_rendered: Mock,
    worker_config: MarkdownWorkerConfig,
    mock_logger: Logger,
) -> None:
    # Given
    mock_create_model_dict.return_value = {"model": "dict"}
    mock_converter = Mock()
    mock_pdf_converter_class.return_value = mock_converter

    markdown_worker = MarkdownWorker(worker_config, mock_logger)

    # When
    result = markdown_worker.initialize_shared_object(worker_config)

    # Then
    assert result == mock_converter
    mock_create_model_dict.assert_called_once()
    mock_pdf_converter_class.assert_called_once_with(
        artifact_dict={"model": "dict"},
        config={"torch_device": "cpu", "pdftext_workers": 1},
    )

    assert os.environ.get("HF_HUB_CACHE") == worker_config.marker_model_download_path
    assert os.environ.get("TORCH_DEVICE") == worker_config.device


@patch("data.workers.markdown_worker.text_from_rendered")
def test_handle_command_convert_success(
    mock_text_from_rendered: Mock,
    worker_config: MarkdownWorkerConfig,
    mock_logger: Logger,
) -> None:
    # Given
    file_path = "/test/file.pdf"
    mock_converter = Mock()
    mock_converter.return_value = {"rendered": "content"}
    mock_text_from_rendered.return_value = ("# Test Markdown", {}, [])

    mock_pipe = Mock()
    mock_is_processing = Mock()
    mock_is_processing.value = False
    mock_processing_lock = Mock()
    mock_processing_lock.__enter__ = Mock(return_value=mock_processing_lock)
    mock_processing_lock.__exit__ = Mock(return_value=False)

    markdown_worker = MarkdownWorker(worker_config, mock_logger)

    # When
    markdown_worker.handle_command(
        "convert",
        file_path,
        mock_converter,
        worker_config,
        mock_pipe,
        mock_is_processing,
        mock_processing_lock,
    )

    # Then
    mock_converter.assert_called_once_with(file_path)
    mock_text_from_rendered.assert_called_once_with({"rendered": "content"})
    mock_pipe.send.assert_called_once_with("# Test Markdown")


def test_handle_command_convert_error_handling(
    worker_config: MarkdownWorkerConfig,
    mock_logger: Logger,
) -> None:
    # Given
    file_path = "/test/file.pdf"
    error_message = "Conversion failed"
    mock_converter = Mock()
    mock_converter.side_effect = Exception(error_message)

    mock_pipe = Mock()
    mock_is_processing = Mock()
    mock_is_processing.value = False
    mock_processing_lock = Mock()
    mock_processing_lock.__enter__ = Mock(return_value=mock_processing_lock)
    mock_processing_lock.__exit__ = Mock(return_value=False)

    markdown_worker = MarkdownWorker(worker_config, mock_logger)

    # When
    markdown_worker.handle_command(
        "convert",
        file_path,
        mock_converter,
        worker_config,
        mock_pipe,
        mock_is_processing,
        mock_processing_lock,
    )

    # Then
    assert mock_pipe.send.call_count == 1
    sent_exception = mock_pipe.send.call_args[0][0]
    assert isinstance(sent_exception, Exception)
    assert str(sent_exception) == error_message
