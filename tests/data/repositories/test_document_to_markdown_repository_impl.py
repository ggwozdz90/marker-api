import pytest

from data.repositories.document_to_markdown_repository_impl import (
    DocumentToMarkdownRepositoryImpl,
)


@pytest.fixture
def repository() -> DocumentToMarkdownRepositoryImpl:
    return DocumentToMarkdownRepositoryImpl()


def test_convert_to_markdown(repository: DocumentToMarkdownRepositoryImpl) -> None:
    # Given
    file_path = "/path/to/test.pdf"

    # When
    result = repository.convert_to_markdown(file_path)

    # Then
    assert result == "Markdown"
