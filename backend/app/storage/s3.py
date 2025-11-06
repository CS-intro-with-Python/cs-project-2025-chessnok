"""
Модуль для работы с S3-совместимым хранилищем (MinIO).
"""
import io
from typing import Optional, BinaryIO
from contextlib import asynccontextmanager

import aioboto3
from botocore.exceptions import ClientError
from app.core.config import settings
from app.core.logger import logger


class S3Storage:
    """Класс для работы с S3-совместимым хранилищем."""
    
    def __init__(self):
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self.access_key_id = settings.S3_ACCESS_KEY_ID
        self.secret_access_key = settings.S3_SECRET_ACCESS_KEY
        self.region = settings.S3_REGION
        self.bucket_name = settings.S3_BUCKET_NAME
        self.use_ssl = settings.S3_USE_SSL
        
        self.session = aioboto3.Session()
    
    @asynccontextmanager
    async def get_client(self):
        """Получить клиент S3."""
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region,
            use_ssl=self.use_ssl,
        ) as client:
            yield client
    
    async def ensure_bucket_exists(self):
        """Создать bucket, если он не существует."""
        try:
            async with self.get_client() as client:
                await client.head_bucket(Bucket=self.bucket_name)
                logger.debug(f"Bucket {self.bucket_name} already exists")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == '404':
                # Bucket не существует, создаем его
                async with self.get_client() as client:
                    await client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created bucket {self.bucket_name}")
            else:
                logger.error(f"Error checking bucket: {e}")
                raise
    
    async def upload_file(
        self,
        file_obj: BinaryIO,
        object_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Загрузить файл в S3.
        
        Args:
            file_obj: Файловый объект для загрузки
            object_key: Ключ объекта в S3 (путь к файлу)
            content_type: MIME-тип файла
            metadata: Метаданные файла
            
        Returns:
            URL загруженного файла
        """
        await self.ensure_bucket_exists()
        
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        if metadata:
            extra_args['Metadata'] = metadata
        
        async with self.get_client() as client:
            await client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_key,
                ExtraArgs=extra_args
            )
        
        logger.info(f"Uploaded file to s3://{self.bucket_name}/{object_key}")
        return f"{self.endpoint_url}/{self.bucket_name}/{object_key}"
    
    async def upload_bytes(
        self,
        data: bytes,
        object_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Загрузить байты в S3.
        
        Args:
            data: Байты для загрузки
            object_key: Ключ объекта в S3
            content_type: MIME-тип файла
            metadata: Метаданные файла
            
        Returns:
            URL загруженного файла
        """
        file_obj = io.BytesIO(data)
        return await self.upload_file(file_obj, object_key, content_type, metadata)
    
    async def download_file(self, object_key: str) -> bytes:
        """
        Скачать файл из S3.
        
        Args:
            object_key: Ключ объекта в S3
            
        Returns:
            Байты файла
        """
        async with self.get_client() as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=object_key)
            data = await response['Body'].read()
            return data
    
    async def download_file_stream(self, object_key: str):
        """
        Получить поток файла из S3.
        
        Args:
            object_key: Ключ объекта в S3
            
        Yields:
            Чанки данных файла
        """
        async with self.get_client() as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=object_key)
            async for chunk in response['Body']:
                yield chunk
    
    async def delete_file(self, object_key: str) -> bool:
        """
        Удалить файл из S3.
        
        Args:
            object_key: Ключ объекта в S3
            
        Returns:
            True если файл удален, False если не найден
        """
        try:
            async with self.get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_key)
                logger.info(f"Deleted file s3://{self.bucket_name}/{object_key}")
                return True
        except ClientError as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    async def file_exists(self, object_key: str) -> bool:
        """
        Проверить существование файла в S3.
        
        Args:
            object_key: Ключ объекта в S3
            
        Returns:
            True если файл существует, False иначе
        """
        try:
            async with self.get_client() as client:
                await client.head_object(Bucket=self.bucket_name, Key=object_key)
                return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == '404':
                return False
            raise
    
    async def get_file_url(self, object_key: str, expires_in: int = 3600) -> str:
        """
        Получить временную URL для доступа к файлу.
        
        Args:
            object_key: Ключ объекта в S3
            expires_in: Время жизни URL в секундах (по умолчанию 1 час)
            
        Returns:
            Временная URL
        """
        async with self.get_client() as client:
            url = await client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expires_in
            )
            return url
    
    async def list_files(self, prefix: str = "") -> list[dict]:
        """
        Получить список файлов в bucket с опциональным префиксом.
        
        Args:
            prefix: Префикс для фильтрации файлов
            
        Returns:
            Список словарей с информацией о файлах
        """
        files = []
        async with self.get_client() as client:
            paginator = client.get_paginator('list_objects_v2')
            async for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        files.append({
                            'key': obj['Key'],
                            'size': obj['Size'],
                            'last_modified': obj['LastModified'].isoformat(),
                        })
        return files


# Глобальный экземпляр storage
_storage_instance: Optional[S3Storage] = None


async def get_s3_client() -> S3Storage:
    """Получить экземпляр S3Storage (dependency для FastAPI)."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = S3Storage()
        # Создаем bucket при первой инициализации
        await _storage_instance.ensure_bucket_exists()
    return _storage_instance

