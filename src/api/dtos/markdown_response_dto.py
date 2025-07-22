from pydantic import BaseModel


class MarkdownResponseDTO(BaseModel):
    content: str
