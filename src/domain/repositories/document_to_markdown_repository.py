from abc import ABC, abstractmethod


class DocumentToMarkdownRepository(ABC):
    @abstractmethod
    def convert_to_markdown(self, file_path: str) -> str:
        pass
