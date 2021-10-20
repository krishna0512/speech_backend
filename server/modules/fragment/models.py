import os
from datetime import datetime
from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field
from server.database import get_db
from server.utils import asr as ASR
from server.utils.minio import Minio
from tqdm import trange

from ..core.mixins import DBModelMixin
from ..job.models import Job


class Fragment(BaseModel, DBModelMixin):
	id: str = Field(default_factory=lambda: str(uuid4()))
	name: str
	index: int
	block_id: str
	status: str = 'new'
	minio_key: str = ''
	url: str = ''
	review: bool = None
	created: datetime = Field(default_factory=datetime.now)
	modified: datetime = Field(default_factory=datetime.now)
	transcript: str = ''

	class Meta:
		collection_name = 'fragments'

	async def delete(self):
		Minio().delete(self.minio_key)
		await get_db()['jobs'].delete_many({'fragment_id': self.id})
		await get_db()['fragments'].delete_one({'id': self.id})

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
	async def create(block_id, camp_name, filepath):
		"""
		Creates a new fragment record given the audio and filepath of 
		fragment audio file in the local machine
		"""
		name = os.path.basename(filepath)
		index = int(name.strip().split('_')[-1].split('.')[0])
		ret = Fragment(
			name=name,
			index=index,
			block_id=block_id,
		)
		key = f'App/Campaigns/{camp_name}/Blocks/{block_id}/Fragments/{name}'
		Minio().upload_fileobj(open(filepath, 'rb'), key)
		ret.minio_key = key
		ret.url = Minio().get_fileurl(key)
		await ret.save()

		# perform the asr on the newly created fragment
		await ret.perform_asr()
		await ret.create_jobs()
		return ret

	async def perform_asr(self) -> str:
		url = Minio().get_fileurl(self.minio_key)
		ret = ASR.telugu(url)
		await self.update(transcript=ret, status='asr_done')
		return ret

	async def create_jobs(self) -> int:
		a = await get_db()['blocks'].find_one({'id': self.block_id})
		a = await get_db()['campaigns'].find_one({'id': a['campaign_id']})
		njobs = a['jobs_per_fragment']
		for _ in trange(njobs):
			# create the new jobs as it is.
			# dont assign the new jobs to anyone i.e. jobs status is pending
			a = await Job.create(self.id)
			# await a.assign("admin")
		return njobs

	async def reject(self):
		await self.update(status='rejected')
		return await self.refresh()

	async def approve(self):
		await self.update(status='approved')
		return await self.refresh()


class FragmentOut(Fragment):
	pass
