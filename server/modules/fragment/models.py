from datetime import datetime
from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field
from server.database import get_db
from server.utils.minio import Minio


class Fragment(BaseModel):
	id: str = Field(default_factory=lambda: str(uuid4()))
	audio_id: str
	minio_key: str = ''
	created: datetime = Field(default_factory=datetime.now)
	modified: datetime = Field(default_factory=datetime.now)

	@staticmethod
	async def all() -> List:
		ret = get_db()['fragments'].find()
		return [Fragment(**i) async for i in ret]

	@staticmethod
	async def filter(**kwargs) -> List:
		if not kwargs:
			return await Fragment.all()
		ret = get_db()['fragments'].find(kwargs)
		return [Fragment(**i) async for i in ret]

	@staticmethod
	async def create(audio_id, filepath):
		"""
		Creates a new fragment record given the audio and filepath of 
		fragment audio file in the local machine
		"""
		print(f'Creating fragment from file: {filepath}')
		ret = Fragment(
			audio_id=audio_id
		)
		key = f'fragments/{audio_id}/{ret.id}.wav'
		Minio().upload_fileobj(open(filepath, 'rb'), key)
		ret.minio_key = key
		await ret.save()
		return ret

	async def save(self):
		await get_db()['fragments'].insert_one(self.dict())

	async def delete(self):
		await get_db()['fragments'].delete_one({'id': self.id})
