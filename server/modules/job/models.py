from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from server.config import *
from server.database import get_db
from server.utils.minio import Minio

from ..core.mixins import DBModelMixin


class JobIn(BaseModel):
	pass

class Job(BaseModel, DBModelMixin):
	id: str = Field(default_factory=lambda: str(uuid4()))
	assigned_to: str = ''
	fragment_id: str
	# pending, assigned, completed, reviewed
	status: str = 'pending'
	transcript: str = ''
	created: datetime = Field(default_factory=datetime.now)
	modified: datetime = Field(default_factory=datetime.now)

	class Meta:
		collection_name = 'jobs'

	# def validate_assigned_to():
	# 	pass

	@staticmethod
	async def create(fid: str):
		a = Job(fragment_id=fid)
		await a.save()
		return a

	async def assign(self, to: str):
		await self.update(status='assigned', assigned_to=to)
		return await Job.get(self.id)

class JobUpdate(BaseModel):
	transcript: Optional[str] = ''


class JobOut(Job):
	pass
