from typing import List

from fastapi import APIRouter
from server.utils.minio import Minio

from .models import *

router = APIRouter()


@router.get('', response_model=List[Audio])
async def get_all_raw_audio_files():
	"""
	Get all raw audio files from the DB without refreshing from MINIO

	Idea is that minio to mongodb refresh will happen via another endpoint
	through a cron job just like fragmentation cron.
	"""
	return await Audio.all()

@router.delete('/{id}')
async def delete_audio(id: str) -> str:
	ret = await Audio.filter(id=id)
	await ret.delete()
	return {'detail': f'1 audio record deleted'}

@router.delete('/all')
async def delete_all_audio():
	ret = await Audio.all()
	[await i.delete() for i in ret]
	return {'detail': f'{len(ret)} audio records deleted'}

@router.post('')
async def upload_new_raw_audio():
	"""
	This endpoint allows upload and creation of new audio files
	not sure, if this endpoint is applicable or not
	"""
	pass


@router.post('/refresh')
async def update_db_from_minio():
	"""
	This endpoint will handle all the logic for checking in the Minio server
	and updating any new files to the mongodb.
	"""
	ret = await Audio.refresh()
	return {'detail': f'{ret} new raw files updated'}
