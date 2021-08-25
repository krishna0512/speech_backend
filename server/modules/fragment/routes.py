from fastapi import APIRouter

from .models import *

router = APIRouter()

@router.post('')
async def fragment_raw_files():
	"""
	This Endpoint handles the processing of all remaining raw audio files into
	multiple fragments
	"""
	pass


@router.get('/{id}', response_model=Fragment)
async def get_fragment(id: str) -> Fragment:
	return await Fragment.get(id)


@router.post('/{id}/asr', response_model=Fragment)
async def perform_asr_on_fragment(id: str) -> Fragment:
	frag = await Fragment.get(id)
	await frag.perform_asr()
	return await Fragment.get(id)
