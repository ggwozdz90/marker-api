from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from api.dtos.markdown_response_dto import MarkdownResponseDTO
from application.usecases.convert_document_usecase import ConvertDocumentUseCase


class MarkdownRouter:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.post("/markdown")(self.markdown)

    async def markdown(
        self,
        convert_document_usecase: Annotated[ConvertDocumentUseCase, Depends()],
        file: UploadFile = File(...),
    ) -> MarkdownResponseDTO:
        markdown_content = await convert_document_usecase.execute(file)

        return MarkdownResponseDTO(
            content=markdown_content,
        )
