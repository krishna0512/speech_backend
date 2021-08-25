import requests
from server.config import *

from minio import Minio as BaseMinio
from minio.commonconfig import CopySource


class Minio:
	def __init__(self):
		self.bucket_name = MINIO_BUCKET_NAME
		self.client = BaseMinio(
			MINIO_ENDPOINT,
			MINIO_ACCESS_KEY,
			MINIO_SECRET_KEY,
			secure=False,
		)

	def upload_fileobj(self, file, key: str) -> str:
		"""
		uploads a file to the minio server given the file like object.
		"""
		self.client.put_object(
			self.bucket_name,
			key,
			file,
			length=-1,
			part_size=10*1024*1024,
		)
		return key

	def upload_fileurl(self, url: str, key: str) -> str:
		"""
		uploads a file to the minio server given the url.
		"""
		r = requests.get(url, stream=True)
		return self.upload_fileobj(r.raw, key)

	def get_fileurl(self, key: str) -> str:
		"""
		gets the presigned url for the file denoted by the key
		"""
		return self.client.presigned_get_object(self.bucket_name, key)

	def delete(self, key: str) -> None:
		self.client.remove_object(self.bucket_name, key)

	def copy(self, source_key: str, dest_key: str) -> str:
		self.client.copy_object(
			self.bucket_name,
			dest_key,
			CopySource(
				self.bucket_name,
				source_key,
			)
		)
		return dest_key

	def move(self, source_key: str, dest_key: str) -> str:
		self.copy(source_key, dest_key)
		self.delete(source_key)
		return dest_key

	def list_objects(self, *args, **kwargs):
		return self.client.list_objects(*args, **kwargs)

	def download(self, key, path) -> None:
		self.client.fget_object(self.bucket_name, key, path)
