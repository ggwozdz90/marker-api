from typing import Annotated

from fastapi import Depends, UploadFile

from core.config.app_config import AppConfig
from core.logger.logger import Logger
from domain.services.document_processing_service import DocumentProcessingService


class ConvertDocumentUseCase:
    def __init__(
        self,
        config: Annotated[AppConfig, Depends()],
        logger: Annotated[Logger, Depends()],
        document_processing_service: Annotated[DocumentProcessingService, Depends()],
    ) -> None:
        self.config = config
        self.logger = logger
        self.document_processing_service = document_processing_service

    async def execute(self, file: UploadFile) -> str:
        self.logger.info(f"Executing document conversion for file '{file.filename}'")

        result: str = await self.document_processing_service.process_document(file)

        self.logger.info(f"Returning conversion result for file '{file.filename}'")

        return result
