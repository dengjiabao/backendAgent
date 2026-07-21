from io import BytesIO
from pathlib import Path
from typing import Any


class FileObjectStore:
    """独立模式对象存储；生产环境可替换为 MinIO/S3 适配器。"""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, content: bytes) -> str:
        target = (self.root / key).resolve()
        if self.root not in target.parents:
            raise ValueError("对象键超出存储根目录")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target.relative_to(self.root).as_posix()

    def get(self, uri: str) -> bytes:
        target = (self.root / uri).resolve()
        if self.root not in target.parents:
            raise ValueError("对象 URI 超出存储根目录")
        return target.read_bytes()


class MinioObjectStore:
    """MinIO Python 客户端适配器，核心只依赖 ObjectStorePort。"""

    def __init__(self, client: Any, bucket: str) -> None:
        self.client = client
        self.bucket = bucket

    def put(self, key: str, content: bytes) -> str:
        self.client.put_object(self.bucket, key, BytesIO(content), len(content), content_type="application/octet-stream")
        return f"minio://{self.bucket}/{key}"

    def get(self, uri: str) -> bytes:
        prefix = f"minio://{self.bucket}/"
        if not uri.startswith(prefix):
            raise ValueError("对象 URI 不属于当前 MinIO Bucket")
        response = self.client.get_object(self.bucket, uri[len(prefix) :])
        try:
            return bytes(response.read())
        finally:
            close = getattr(response, "close", None)
            if close is not None:
                close()
