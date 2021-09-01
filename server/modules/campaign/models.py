import os
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from server.config import *
from server.database import get_db
from server.modules.user.models import *


class CampaignMixin:

	@staticmethod
	async def all() -> List:
		ret = get_db()['campaigns'].find()
		return [Campaign(**i) async for i in ret]

	@staticmethod
	async def filter(**kwargs) -> List:
		if not kwargs:
			return await Campaign.all()
		ret = get_db()['campaigns'].find(kwargs)
		return [Campaign(**i) async for i in ret]

	@staticmethod
	async def get(id):
		ret = await get_db()['campaigns'].find_one({'id': id})
		return Campaign(**ret)

	async def save(self):
		await get_db()['campaigns'].insert_one(self.dict())

	async def update(self, **kwargs):
		kwargs.update({'modified': datetime.now()})
		await get_db()['campaigns'].update_one(
			{'id': self.id},
			{'$set': kwargs},
		)

	async def refresh(self):
		return await Campaign.get(self.id)

	async def delete(self) -> None:
		await get_db()['campaigns'].delete_one({'id': self.id})

class CampaignIn(BaseModel):
	name: str
	rate_speaker: Optional[float] = 0.0
	rate_transcriber: Optional[float] = 0.0
	rate_reviewer: Optional[float] = 0.0
	jobs_per_fragment: Optional[int] = 3

class CampaignUpdate(BaseModel):
	name: Optional[str] = None
	rate_speaker: Optional[float] = None
	rate_transcriber: Optional[float] = None
	rate_reviewer: Optional[float] = None
	jobs_per_fragment: Optional[int] = None

class Campaign(BaseModel, CampaignMixin):
	id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
	name: str
	speakers: Optional[List[str]] = []
	transcribers: Optional[List[str]] = []
	reviewers: Optional[List[str]] = []
	rate_speaker: Optional[float] = 0.0
	rate_transcriber: Optional[float] = 0.0
	rate_reviewer: Optional[float] = 0.0
	jobs_per_fragment: Optional[int] = 3
	created: datetime = Field(default_factory=datetime.now)
	modified: datetime = Field(default_factory=datetime.now)

	@staticmethod
	async def create(data: CampaignIn):
		camp = Campaign(
			**data.dict()
		)
		await camp.save()
		return camp

class CampaignOut(Campaign):
	pass
