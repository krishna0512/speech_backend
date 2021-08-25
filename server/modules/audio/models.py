import os
from datetime import datetime
from os.path import join
from tempfile import TemporaryDirectory
from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field
from server.config import *
from server.database import get_db
from server.modules.fragment.models import Fragment
from server.utils.minio import Minio
from tqdm import trange

from . import helpers


class AudioMixin:

	@staticmethod
	async def all() -> List:
		ret = get_db()['audio'].find()
		return [Audio(**i) async for i in ret]

	@staticmethod
	async def filter(**kwargs) -> List:
		if not kwargs:
			return await Audio.all()
		ret = get_db()['audio'].find(kwargs)
		return [Audio(**i) async for i in ret]

	@staticmethod
	async def get(id):
		ret = await get_db()['audio'].find_one({'id': id})
		return Audio(**ret)

	async def save(self):
		await get_db()['audio'].insert_one(self.dict())

	async def update(self, **kwargs):
		kwargs.update({'modified': datetime.now()})
		await get_db()['audio'].update_one(
			{'id': self.id},
			{'$set': kwargs},
		)

	async def delete(self) -> None:
		if self.status == 'fragmented':
			await self.delete_fragments()
		Minio().delete(self.minio_key)
		Minio().delete(f'app/audio/{self.id}')
		await get_db()['audio'].delete_one({'id': self.id})

	async def move(self, to: str) -> None:
		mk = Minio().move(self.minio_key, to)
		await self.update(minio_key=mk)


class Audio(BaseModel, AudioMixin):
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
	async def refresh() -> int:
		"""
		This method handles all the logic to update the Audiofiles from
		minio that are not already present in the mongodb

		@returns: int, the number of new files added to the mongodb
		"""
		files = []
		for prefix in MINIO_CAMPAIGN_SOURCES:
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

	async def generate_fragments(self) -> List[Fragment]:
		mc = Minio()
		t = TemporaryDirectory(prefix='frags')
		input_file = join(t.name, self.minio_key.split('/')[-1])
		print(f'Downloading audio file to: {input_file}')
		mc.download(self.minio_key, input_file)
		output_dir = helpers.generate_fragments(t.name)
		frag_files = [join(output_dir, f) for f in os.listdir(output_dir)]
		frag_files = sorted(frag_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
		frags = []
		for i in trange(len(frag_files), desc='Creating Fragments '):
			frags.append(
				await Fragment.create(self.id, frag_files[i])
			)

		await self.update(status='fragmented')
		return frags

	async def get_fragments(self) -> List[Fragment]:
		if self.status == 'raw':
			return []
		return await Fragment.filter(audio_id=self.id)

	async def delete_fragments(self):
		if self.status == 'raw':
			return 0
		ret = await self.get_fragments()
		for i in trange(len(ret), desc='Deleting Fragments '):
			await ret[i].delete()
		Minio().delete(f'app/audio/{self.id}/fragments')
		await self.update(status='raw')
		return len(ret)
