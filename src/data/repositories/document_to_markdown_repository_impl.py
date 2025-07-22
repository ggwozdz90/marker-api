from domain.repositories.document_to_markdown_repository import (
    DocumentToMarkdownRepository,
)


class DocumentToMarkdownRepositoryImpl(DocumentToMarkdownRepository):  # type: ignore
    def convert_to_markdown(self, file_path: str) -> str:
        return "Markdown"
