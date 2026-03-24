from __future__ import annotations

from pathlib import Path

from azure.storage.blob import BlobServiceClient, ContainerClient

from bangkok_aqi.config import Settings


class StorageClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._container_client: ContainerClient | None = None

    @property
    def backend_name(self) -> str:
        return "azure-blob" if self.settings.azure_storage_connection_string else "local-filesystem"

    def _get_container_client(self) -> ContainerClient:
        if self._container_client is None:
            if not self.settings.azure_storage_connection_string:
                raise RuntimeError("Azure storage is not configured.")
            service_client = BlobServiceClient.from_connection_string(
                self.settings.azure_storage_connection_string
            )
            container_client = service_client.get_container_client(
                self.settings.azure_storage_container_name
            )
            if not container_client.exists():
                container_client.create_container()
            self._container_client = container_client
        return self._container_client

    def _get_local_path(self, path: str) -> Path:
        local_path = self.settings.data_dir / path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        return local_path

    def save_bytes(self, path: str, content: bytes) -> None:
        if self.settings.azure_storage_connection_string:
            blob_client = self._get_container_client().get_blob_client(path)
            blob_client.upload_blob(content, overwrite=True)
            return

        local_path = self._get_local_path(path)
        local_path.write_bytes(content)

    def read_bytes(self, path: str) -> bytes:
        if self.settings.azure_storage_connection_string:
            blob_client = self._get_container_client().get_blob_client(path)
            return blob_client.download_blob().readall()

        local_path = self._get_local_path(path)
        return local_path.read_bytes()

    def list_files(self, prefix: str = "") -> list[str]:
        if self.settings.azure_storage_connection_string:
            blobs = self._get_container_client().list_blobs(name_starts_with=prefix)
            return sorted(blob.name for blob in blobs)

        target_dir = self.settings.data_dir / prefix
        if not target_dir.exists():
            return []

        return sorted(
            str(file_path.relative_to(self.settings.data_dir))
            for file_path in target_dir.rglob("*")
            if file_path.is_file()
        )
