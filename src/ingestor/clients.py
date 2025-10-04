"""
GCS and Pub/Sub client wrappers.
"""
from __future__ import annotations

import json
import logging
from typing import Dict, Any

from google.cloud import storage, pubsub_v1

logger = logging.getLogger(__name__)


class GCSClient:
    """Google Cloud Storage client wrapper."""
    
    def __init__(self):
        self.client = storage.Client()
    
    def write_json(
        self,
        bucket_name: str,
        object_path: str,
        data: Dict[str, Any],
        content_type: str = "application/json"
    ) -> str:
        """
        Write JSON data to GCS.
        
        Args:
            bucket_name: GCS bucket name
            object_path: Object path within bucket
            data: Dictionary to write as JSON
            content_type: Content type header
            
        Returns:
            GCS URI of written object
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(object_path)
            
            blob.upload_from_string(
                json.dumps(data, indent=2),
                content_type=content_type
            )
            
            uri = f"gs://{bucket_name}/{object_path}"
            logger.info(f"Successfully wrote to {uri}")
            return uri
            
        except Exception as e:
            logger.error(f"Failed to write to GCS: {str(e)}")
            raise
    
    def read_json(self, bucket_name: str, object_path: str) -> Dict[str, Any]:
        """
        Read JSON data from GCS.
        
        Args:
            bucket_name: GCS bucket name
            object_path: Object path within bucket
            
        Returns:
            Parsed JSON as dictionary
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(object_path)
            
            content = blob.download_as_text()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Failed to read from GCS: {str(e)}")
            raise
    
    def list_objects(
        self,
        bucket_name: str,
        prefix: str = "",
        delimiter: str | None = None
    ) -> list[str]:
        """
        List objects in GCS bucket with optional prefix.
        
        Args:
            bucket_name: GCS bucket name
            prefix: Object prefix to filter
            delimiter: Delimiter for hierarchical listing
            
        Returns:
            List of object names
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=prefix, delimiter=delimiter)
            return [blob.name for blob in blobs]
            
        except Exception as e:
            logger.error(f"Failed to list GCS objects: {str(e)}")
            raise


class PubSubClient:
    """Google Cloud Pub/Sub client wrapper."""
    
    def __init__(self):
        self.publisher = pubsub_v1.PublisherClient()
    
    def publish_message(
        self,
        project_id: str,
        topic_name: str,
        data: Dict[str, Any],
        **attributes
    ) -> str:
        """
        Publish a message to Pub/Sub topic.
        
        Args:
            project_id: GCP project ID
            topic_name: Pub/Sub topic name
            data: Message data as dictionary
            **attributes: Additional message attributes
            
        Returns:
            Published message ID
        """
        try:
            topic_path = self.publisher.topic_path(project_id, topic_name)
            
            # Convert data to JSON bytes
            message_bytes = json.dumps(data).encode("utf-8")
            
            # Publish with retry
            future = self.publisher.publish(
                topic_path,
                message_bytes,
                **attributes
            )
            
            message_id = future.result(timeout=30)
            logger.info(f"Published message {message_id} to {topic_path}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to publish to Pub/Sub: {str(e)}")
            raise
    
    def publish_batch(
        self,
        project_id: str,
        topic_name: str,
        messages: list[Dict[str, Any]]
    ) -> list[str]:
        """
        Publish multiple messages to Pub/Sub topic.
        
        Args:
            project_id: GCP project ID
            topic_name: Pub/Sub topic name
            messages: List of message data dictionaries
            
        Returns:
            List of published message IDs
        """
        try:
            topic_path = self.publisher.topic_path(project_id, topic_name)
            futures = []
            
            for msg_data in messages:
                message_bytes = json.dumps(msg_data).encode("utf-8")
                future = self.publisher.publish(topic_path, message_bytes)
                futures.append(future)
            
            # Wait for all to complete
            message_ids = [f.result(timeout=30) for f in futures]
            logger.info(f"Published {len(message_ids)} messages to {topic_path}")
            return message_ids
            
        except Exception as e:
            logger.error(f"Failed to publish batch to Pub/Sub: {str(e)}")
            raise
