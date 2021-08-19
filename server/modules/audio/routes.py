from typing import List

from fastapi import APIRouter
from server.utils.minio import Minio

router = APIRouter()


@router.get('')
async def get_all_raw_audio_files():
	"""
	Get all raw audio files from the DB without refreshing from MINIO

	Idea is that minio to mongodb refresh will happen via another endpoint
	through a cron job just like fragmentation cron.
	"""
	pass


@router.post('/refresh')
async def update_db_from_minio():
	"""
	This endpoint will handle all the logic for checking in the Minio server
	and updating any new files to the mongodb.
	"""
	return {'detail': '0 new raw files updated'}
