import threading
from typing import Annotated, Optional

from fastapi import Depends

from core.config.app_config import AppConfig
from core.logger.logger import Logger
from data.repositories.directory_repository_impl import DirectoryRepositoryImpl
from data.workers.markdown_worker import MarkdownWorker, MarkdownWorkerConfig
from domain.repositories.directory_repository import DirectoryRepository
from domain.repositories.document_to_markdown_repository import (
    DocumentToMarkdownRepository,
)


class DocumentToMarkdownRepositoryImpl(DocumentToMarkdownRepository):  # type: ignore
    _instance: Optional["DocumentToMarkdownRepositoryImpl"] = None
    _lock = threading.Lock()

    def __new__(
        cls,
        config: Annotated[AppConfig, Depends()],
        directory_repository: Annotated[DirectoryRepository, Depends(DirectoryRepositoryImpl)],
        logger: Annotated[Logger, Depends()],
    ) -> "DocumentToMarkdownRepositoryImpl":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DocumentToMarkdownRepositoryImpl, cls).__new__(cls)
                    cls._instance._initialize(config, directory_repository, logger)

        return cls._instance

    def _initialize(
        self,
        config: AppConfig,
        directory_repository: DirectoryRepository,
        logger: Logger,
    ) -> None:
        directory_repository.create_directory(config.marker_model_download_path)
        self.config = config
        self.logger = logger

    def convert_to_markdown(self, file_path: str) -> str:
        self.logger.debug(f"Converting file to markdown: {file_path}")

        worker_config = MarkdownWorkerConfig(
            device=self.config.device,
            marker_model_name=self.config.marker_model_name,
            marker_model_download_path=self.config.marker_model_download_path,
            log_level=self.config.log_level,
        )

        worker = MarkdownWorker(worker_config, self.logger)

        try:
            self.logger.info("Starting markdown worker process")
            worker.start()

            self.logger.debug(f"Sending conversion request for file: {file_path}")
            result = worker.convert(file_path)

            self.logger.debug(f"Markdown conversion completed for file: {file_path}")

            return str(result)

        except Exception as e:
            self.logger.error(f"Error converting file {file_path} to markdown: {str(e)}")
            raise

        finally:
            if worker.is_alive():
                self.logger.info("Stopping markdown worker process")
                worker.stop()
