from typing import Annotated

from fastapi import Depends, UploadFile

from core.config.app_config import AppConfig
from core.logger.logger import Logger
from data.repositories.document_to_markdown_repository_impl import (
    DocumentToMarkdownRepositoryImpl,
)
from data.repositories.file_repository_impl import FileRepositoryImpl
from domain.repositories.document_to_markdown_repository import (
    DocumentToMarkdownRepository,
)
from domain.repositories.file_repository import FileRepository


class DocumentProcessingService:
    def __init__(
        self,
        config: Annotated[AppConfig, Depends()],
        file_repository: Annotated[FileRepository, Depends(FileRepositoryImpl)],
        document_to_markdown_repository: Annotated[
            DocumentToMarkdownRepository,
            Depends(DocumentToMarkdownRepositoryImpl),
        ],
        logger: Annotated[Logger, Depends()],
    ) -> None:
        self.config = config
        self.file_repository = file_repository
        self.document_to_markdown_repository = document_to_markdown_repository
        self.logger = logger

    async def process_document(self, file: UploadFile) -> str:
        file_path = await self.file_repository.save_file(file)

        self.logger.debug(f"Starting document processing for file '{file.filename}'")

        result: str = self.document_to_markdown_repository.convert_to_markdown(file_path)

        self.logger.debug(f"Completed document processing for file '{file.filename}'")

        if self.config.delete_files_after_processing:
            self.file_repository.delete_file(file_path)

        return result
