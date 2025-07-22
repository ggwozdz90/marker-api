import multiprocessing
import multiprocessing.connection
import multiprocessing.synchronize
import os
from dataclasses import dataclass
from multiprocessing.sharedctypes import Synchronized
from typing import Tuple

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

from core.logger.logger import Logger
from data.workers.base_worker import BaseWorker


@dataclass
class MarkdownWorkerConfig:
    device: str
    marker_model_name: str
    marker_model_download_path: str
    log_level: str


class MarkdownWorker(
    BaseWorker[  # type: ignore
        str,
        str,
        MarkdownWorkerConfig,
        PdfConverter,
    ],
):
    def __init__(self, config: MarkdownWorkerConfig, logger: Logger) -> None:
        super().__init__(config, logger)

    def convert(self, file_path: str) -> str:
        if not self.is_alive():
            raise RuntimeError("Worker is not running")

        self._pipe_parent.send(("convert", file_path))
        result = self._pipe_parent.recv()

        if isinstance(result, Exception):
            raise result

        return str(result)

    def convert_to_markdown(self, file_path: str) -> str:
        self._logger.info(f"Starting PDF to Markdown conversion: {file_path}")

        try:
            os.environ["HF_HUB_CACHE"] = self._config.marker_model_download_path
            os.environ["TORCH_DEVICE"] = self._config.device

            marker_config = {
                "torch_device": self._config.device,
                "pdftext_workers": 1,
            }

            artifact_dict = create_model_dict()
            converter = PdfConverter(
                artifact_dict=artifact_dict,
                config=marker_config,
            )

            rendered = converter(file_path)
            markdown_content, _, _ = text_from_rendered(rendered)

            self._logger.info(f"Finished PDF to Markdown conversion: {file_path}")
            return str(markdown_content)

        except Exception as e:
            self._logger.error(f"Error converting {file_path}: {str(e)}")
            raise RuntimeError(f"Error processing PDF to Markdown: {str(e)}") from e

    def initialize_shared_object(
        self,
        config: MarkdownWorkerConfig,
    ) -> PdfConverter:
        os.environ["HF_HUB_CACHE"] = config.marker_model_download_path
        os.environ["TORCH_DEVICE"] = config.device

        marker_config = {
            "torch_device": config.device,
            "pdftext_workers": 1,
        }

        converter = PdfConverter(
            artifact_dict=create_model_dict(),
            config=marker_config,
        )

        return converter

    def handle_command(
        self,
        command: str,
        args: str,
        shared_object: PdfConverter,
        config: MarkdownWorkerConfig,
        pipe: multiprocessing.connection.Connection,
        is_processing: Synchronized,  # type: ignore
        processing_lock: multiprocessing.synchronize.Lock,
    ) -> None:
        if command == "convert":
            try:
                with processing_lock:
                    is_processing.value = True

                file_path = args

                rendered = shared_object(file_path)
                markdown_content, _, _ = text_from_rendered(rendered)

                pipe.send(str(markdown_content))

            except Exception as e:
                pipe.send(e)

            finally:
                with processing_lock:
                    is_processing.value = False

    def get_worker_name(self) -> str:
        return type(self).__name__
