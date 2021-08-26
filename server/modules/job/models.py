from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from server.config import *
from server.database import get_db
from server.utils.minio import Minio


class JobMixin:

	@staticmethod
	async def all() -> List:
		ret = get_db()['jobs'].find()
		return [Job(**i) async for i in ret]

	@staticmethod
	async def filter(**kwargs) -> List:
		if not kwargs:
			return await Job.all()
		ret = get_db()['jobs'].find(kwargs)
		return [Job(**i) async for i in ret]

	@staticmethod
	async def get(id):
		ret = await get_db()['jobs'].find_one({'id': id})
		return Job(**ret)

	async def save(self):
		await get_db()['jobs'].insert_one(self.dict())

	async def update(self, **kwargs):
		kwargs.update({'modified': datetime.now()})
		await get_db()['jobs'].update_one(
			{'id': self.id},
			{'$set': kwargs},
		)

	async def delete(self) -> None:
		await get_db()['jobs'].delete_one({'id': self.id})


class JobIn(BaseModel):
	pass

class Job(BaseModel):
	id: str = Field(default_factory=lambda: str(uuid4()))
	fragment_id: str
	created: datetime = Field(default_factory=datetime.now)
	modified: datetime = Field(default_factory=datetime.now)
	# status can be ['new', 'correct', 'incorrect']
	status: Optional[str] = 'new'
