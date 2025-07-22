from typing import Annotated

from fastapi import APIRouter, Depends, File, Response, UploadFile

from application.usecases.convert_document_usecase import ConvertDocumentUseCase


class MarkdownRouter:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.post("/markdown")(self.markdown)

    async def markdown(
        self,
        convert_document_usecase: Annotated[ConvertDocumentUseCase, Depends()],
        file: UploadFile = File(...),
    ) -> Response:
        markdown_content = await convert_document_usecase.execute(file)

        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{file.filename}.md"'},
        )
