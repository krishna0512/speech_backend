import os
from datetime import datetime
from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field
from server.database import get_db
from server.utils import asr as ASR
from server.utils.minio import Minio


class FragmentMixin:

	@staticmethod
	async def all() -> List:
		ret = get_db()['fragments'].find().sort('index')
		return [Fragment(**i) async for i in ret]

	@staticmethod
	async def filter(**kwargs) -> List:
		if not kwargs:
			return await Fragment.all()
		ret = get_db()['fragments'].find(kwargs).sort('index')
		return [Fragment(**i) async for i in ret]

	@staticmethod
	async def get(id):
		ret = await get_db()['fragments'].find_one({'id': id})
		return Fragment(**ret)

	async def save(self):
		await get_db()['fragments'].insert_one(self.dict())

	async def update(self, **kwargs):
		kwargs.update({'modified': datetime.now()})
		await get_db()['fragments'].update_one(
			{'id': self.id},
			{'$set': kwargs},
		)

	async def delete(self):
		Minio().delete(self.minio_key)
		await get_db()['fragments'].delete_one({'id': self.id})



class Fragment(FragmentMixin, BaseModel):
	id: str = Field(default_factory=lambda: str(uuid4()))
	name: str
	index: int
	audio_id: str
	minio_key: str = ''
	created: datetime = Field(default_factory=datetime.now)
	modified: datetime = Field(default_factory=datetime.now)
	text: str = ''

	@staticmethod
	async def create(audio_id, filepath):
		"""
		Creates a new fragment record given the audio and filepath of 
		fragment audio file in the local machine
		"""
		name = os.path.basename(filepath)
		index = int(name.strip().split('_')[-1].split('.')[0])
		ret = Fragment(
			name=name,
			index=index,
			audio_id=audio_id,
		)
		key = f'app/audio/{audio_id}/fragments/{name}'
		Minio().upload_fileobj(open(filepath, 'rb'), key)
		ret.minio_key = key
		await ret.save()

		# perform the asr on the newly created fragment
		await ret.perform_asr()
		return ret

	async def perform_asr(self) -> str:
		url = Minio().get_fileurl(self.minio_key)
		ret = ASR.telugu(url)
		await self.update(text=ret)
		return ret
