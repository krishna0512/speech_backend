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
	code: str
	language: Optional[str] = 'Telugu'
	description: Optional[str] = ''
	# can be [free, paid]
	category: Optional[str] = 'free'
	topics: Optional[List[str]] = []
	demourl: Optional[str] = ''
	max_users: Optional[int] = 1
	rate_speaker: Optional[float] = 0.0
	rate_transcriber: Optional[float] = 0.0
	rate_reviewer: Optional[float] = 0.0
	jobs_per_fragment: Optional[int] = 3

class CampaignUpdate(BaseModel):
	name: Optional[str] = None
	code: Optional[str] = None
	language: Optional[str] = None
	description: Optional[str] = None
	# can be [free, paid]
	category: Optional[str] = None
	topics: Optional[List[str]] = None
	demourl: Optional[str] = None
	max_users: Optional[int] = None
	rate_speaker: Optional[float] = None
	rate_transcriber: Optional[float] = None
	rate_reviewer: Optional[float] = None
	jobs_per_fragment: Optional[int] = None
	status: Optional[str] = None

class Campaign(BaseModel, CampaignMixin):
	id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
	name: str
	code: str
	language: Optional[str] = 'Telugu'
	description: Optional[str] = ''
	# can be [free, paid]
	category: Optional[str] = 'free'
	topics: Optional[List[str]] = []
	demourl: Optional[str] = ''
	max_users: Optional[int] = 1
	speakers: Optional[List[str]] = []
	transcribers: Optional[List[str]] = []
	reviewers: Optional[List[str]] = []
	rate_speaker: Optional[float] = 0.0
	rate_transcriber: Optional[float] = 0.0
	rate_reviewer: Optional[float] = 0.0
	jobs_per_fragment: Optional[int] = 3
	created: datetime = Field(default_factory=datetime.now)
	modified: datetime = Field(default_factory=datetime.now)
	status: Optional[str] = 'active'

	@staticmethod
	async def create(data: CampaignIn):
		camp = Campaign(
			**data.dict()
		)
		await camp.save()
		return camp

	async def add_speaker(self, user_id: str):
		"""
		Adds the given user to the speakers list of this camapaign
		"""
		ret = self.speakers
		ret.append(user_id)
		await self.update(speakers=ret)

	async def add_transcriber(self, user_id: str):
		"""
		Adds the given user to the transcribers list of this camapaign
		"""
		ret = self.transcribers
		ret.append(user_id)
		await self.update(transcribers=ret)

	async def add_reviewer(self, user_id: str):
		"""
		Adds the given user to the reviewers list of this camapaign
		"""
		ret = self.reviewers
		ret.append(user_id)
		await self.update(reviewers=ret)

class CampaignOut(Campaign):
	pass
