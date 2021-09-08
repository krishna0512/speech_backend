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

class Job(BaseModel, JobMixin):
	id: str = Field(default_factory=lambda: str(uuid4()))
	assigned_to: str = ''
	reviewed_by: str = ''
	fragment_id: str
	# pending, assigned, completed, reviewed
	status: str = 'pending'
	correct: bool = False
	transcript: str = ''
	created: datetime = Field(default_factory=datetime.now)
	modified: datetime = Field(default_factory=datetime.now)

	# def validate_assigned_to():
	# 	pass

	@staticmethod
	async def create(fid: str):
		a = Job(fragment_id=fid)
		await a.save()

	async def assign(self, to: str):
		await self.update(status='assigned', assigned_to=to)
		return await Job.get(self.id)

class JobUpdate(BaseModel):
	correct: Optional[bool] = False
	transcript: Optional[str] = ''


class JobOut(Job):
	pass
