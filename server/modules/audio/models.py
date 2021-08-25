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
	minio_key: str = ''
	created: datetime = Field(default_factory=datetime.now)
	modified: datetime = Field(default_factory=datetime.now)
	# status can be ["raw", "fragmented"]
	status: str = 'raw'

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
		mc = Minio()
		files = []
		for prefix in paths:
			files += [i.object_name for i in mc.list_objects(
				'speech-data-prod',
				prefix=prefix,
				recursive=True
			)]
		files = [i for i in files if i.endswith('wav')]
		print(f'{len(files)} audio files found in the minio')
		audio_present = await Audio.all()
		audio_present = [i.minio_key for i in audio_present]
		print(f'{len(audio_present)} records found in the mongodb')
		files = [i for i in files if i not in audio_present]
		ret = len(files)
		print(f'{ret} unique audio files found minio that are missing in mongodb')
		if ret == 0:
			return ret
		for i in files:
			a = Audio(minio_key=i)
			await a.save()
		print(f'{ret} records added to mongodb')
		return ret

	async def save(self):
		await get_db()['audio'].insert_one(self.dict())

	async def update(self, **kwargs):
		await get_db()['audio'].update_one(
			{'id': self.id},
			{'$set': kwargs},
		)

	async def delete(self):
		Minio().delete(self.minio_key)
		await get_db()['audio'].delete_one({'id': self.id})

	async def generate_fragments(self) -> List[Fragment]:
		mc = Minio()
		t = TemporaryDirectory(prefix='frags')
		input_file = join(t.name, self.minio_key.split('/')[-1])
		mc.download(self.minio_key, input_file)
		output_dir = helpers.generate_fragments(t.name)
		frag_files = [join(output_dir, f) for f in os.listdir(output_dir)]
		frags = [await Fragment.create(self.id, i) for i in frag_files]

		# moving the minio audio file to fragmented_source folder
		await self.update(
			status='fragmented',
			modified=datetime.now(),
			minio_key=mc.move(
				self.minio_key,
				f'fragmented_source/{self.id}.wav',
			),
		)
		return frags
