import os
from datetime import datetime
from os.path import join
from tempfile import TemporaryDirectory
from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field
from server.database import get_db
from server.modules.fragment.models import Fragment
from server.utils.minio import Minio

from . import helpers


class Audio(BaseModel):
	id: str = Field(default_factory=lambda: str(uuid4()))
	# stores the name of the original audio file as referenced from
	# minio campaign_source folder
	name: str
	minio_key: str = ''
	created: datetime = Field(default_factory=datetime.now)
	modified: datetime = Field(default_factory=datetime.now)
	# status can be ["raw", "fragmented"]
	status: str = 'raw'
	# stores the campaign that this audio belongs to
	# campaign can be ["ozonetel_webapp", "ozonetel_whatsapp"]
	campaign: str = ''

	@staticmethod
	async def all():
		ret = get_db()['audio'].find()
		return [Audio(**i) async for i in ret]

	@staticmethod
	async def filter(**kwargs) -> List:
		if not kwargs:
			return await Audio.all()
		return await get_db()['audio'].find(kwargs)

	@staticmethod
	async def get(id):
		ret = await get_db()['audio'].find_one({'id': id})
		return Audio(**ret)

	@staticmethod
	async def refresh() -> int:
		"""
		This method handles all the logic to update the Audiofiles from
		minio that are not already present in the mongodb

		@returns: int, the number of new files added to the mongodb
		"""
		paths = [
			'campaign_source/ozonetel_webapp',
			'campaign_source/ozonetel_whatsapp',
		]
		files = []
		for prefix in paths:
			files += [i.object_name for i in Minio().list_objects(
				'speech-data-prod',
				prefix=prefix,
				recursive=True
			)]
		files = [i.strip(' /') for i in files if i.endswith('wav')]
		print(f'{len(files)} audio files found in the minio')
		ret = len(files)
		if ret == 0:
			return ret
		for i in files:
			a = Audio(
				name=i.split('/')[-1],
				minio_key=i,
				campaign=i.split('/')[1],
			)
			await a.save()
			await a.move(f'app/audio/{a.id}/{a.name}')
		print(f'{ret} records added to mongodb')
		return ret

	async def save(self):
		await get_db()['audio'].insert_one(self.dict())

	async def update(self, **kwargs):
		kwargs.update({'modified': datetime.now()})
		await get_db()['audio'].update_one(
			{'id': self.id},
			{'$set': kwargs},
		)

	async def delete(self) -> None:
		Minio().delete(self.minio_key)
		await get_db()['audio'].delete_one({'id': self.id})

	async def move(self, to: str) -> None:
		mk = Minio().move(self.minio_key, to)
		await self.update(minio_key=mk)

	async def generate_fragments(self) -> List[Fragment]:
		mc = Minio()
		t = TemporaryDirectory(prefix='frags')
		input_file = join(t.name, self.minio_key.split('/')[-1])
		mc.download(self.minio_key, input_file)
		output_dir = helpers.generate_fragments(t.name)
		frag_files = [join(output_dir, f) for f in os.listdir(output_dir)]
		frags = [await Fragment.create(self.id, i) for i in frag_files]

		await self.update(status='fragmented')
		return frags

	async def get_fragments(self) -> List[Fragment]:
		if self.status == 'raw':
			return []
		return await Fragment.filter(audio_id=self.id)
