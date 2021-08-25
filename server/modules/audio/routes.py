from typing import List

from fastapi import APIRouter
from server.modules.fragment.models import *
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


@router.get('/{id}', response_model=Audio)
async def get_single_audio(id: str):
	return await Audio.get(id)


@router.delete('/{id}')
async def delete_audio(id: str) -> str:
	ret = await Audio.filter(id=id)
	await ret.delete()
	return {'detail': f'1 audio record deleted'}


@router.delete('')
async def delete_all_audio() -> str:
	ret = await Audio.all()
	[await i.delete() for i in ret]
	return {'detail': f'{len(ret)} audio records deleted'}


@router.post('/refresh')
async def update_db_from_minio():
	"""
	This endpoint will handle all the logic for checking in the Minio server
	and updating any new files to the mongodb.
	"""
	ret = await Audio.refresh()
	return {'detail': f'{ret} new raw files updated'}


@router.post('/{id}/fragments', response_model=List[Fragment])
async def fragment_raw_audio(id: str) -> List[Fragment]:
	audio = await Audio.get(id)
	return await audio.generate_fragments()


@router.get('/{id}/fragments', response_model=List[Fragment])
async def get_fragments_for_audio(id: str) -> List[Fragment]:
	audio = await Audio.get(id)
	return await audio.get_fragments()


@router.delete('/{id}/fragments')
async def delete_fragments_for_audio(id: str) -> str:
	audio = await Audio.get(id)
	ret = await audio.delete_fragments()
	return {'detail': f'{ret} fragments deleted'}
