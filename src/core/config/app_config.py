import os
from typing import Optional

from dotenv import load_dotenv

from core.logger.logger import Logger


class AppConfig:
    _instance: Optional["AppConfig"] = None

    log_level: Optional[str]
    fastapi_host: Optional[str]
    fastapi_port: Optional[int]
    device: Optional[str]
    marker_model_name: Optional[str]
    file_upload_path: Optional[str]
    delete_files_after_processing: Optional[bool]
    marker_model_download_path: Optional[str]

    def __new__(cls) -> "AppConfig":
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)

        return cls._instance

    def _str_to_bool(self, value: str) -> bool:
        return value.lower() in ("true", "1", "yes")

    def _load_env_variables(self) -> None:
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.fastapi_host = os.getenv("FASTAPI_HOST", "127.0.0.1")
        try:
            self.fastapi_port = int(os.getenv("FASTAPI_PORT", "8000"))
        except ValueError:
            self.fastapi_port = 8000

        self.device = os.getenv("DEVICE", "cpu")
        self.marker_model_name = os.getenv("MARKER_MODEL_NAME", "vikp/marker")
        self.file_upload_path = os.getenv("FILE_UPLOAD_PATH", "uploaded_files")
        self.delete_files_after_processing = self._str_to_bool(os.getenv("DELETE_FILES_AFTER_PROCESSING", "true"))
        self.marker_model_download_path = os.getenv("MARKER_MODEL_DOWNLOAD_PATH", "downloaded_marker_models")

    def initialize(
        self,
        logger: Logger,
    ) -> None:
        logger.info("Initializing configuration...")
        load_dotenv()
        self._load_env_variables()
        config_message = (
            f"Configuration loaded:\n"
            f"LOG_LEVEL: {self.log_level}\n"
            f"FASTAPI_HOST: {self.fastapi_host}\n"
            f"FASTAPI_PORT: {self.fastapi_port}\n"
            f"DEVICE: {self.device}\n"
            f"MARKER_MODEL_NAME: {self.marker_model_name}\n"
            f"FILE_UPLOAD_PATH: {self.file_upload_path}\n"
            f"DELETE_FILES_AFTER_PROCESSING: {self.delete_files_after_processing}\n"
            f"MARKER_MODEL_DOWNLOAD_PATH: {self.marker_model_download_path}"
        )
        logger.info(config_message)
        logger.info("Configuration initialized successfully.")
