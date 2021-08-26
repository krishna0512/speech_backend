"""
This file contains all the endpoints that contain the prefix of audio
but are about operations on Fragment model
"""
from typing import List

from fastapi import APIRouter
from server.modules.fragment.models import Fragment

from .models import *

router = APIRouter()

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
