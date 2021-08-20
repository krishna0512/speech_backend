from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field
from server.database import get_db
from server.utils.minio import Minio


class Fragment(BaseModel):
	id: str = Field(default_factory=lambda: str(uuid4()))
	minio_key: str = ''
	created: datetime = Field(default_factory=datetime.now)
	modified: datetime = Field(default_factory=datetime.now)

	@staticmethod
	async def all():
		ret = get_db()['fragments'].find()
		return [Fragment(**i) async for i in ret]

	@staticmethod
	async def filter(**kwargs):
		if not kwargs:
			return await Fragment.all()
		return await get_db()['fragments'].filter(kwargs)

	async def save(self):
		await get_db()['fragments'].insert_one(self.dict())

	async def delete(self):
		await get_db()['fragments'].delete_one({'id': self.id})
