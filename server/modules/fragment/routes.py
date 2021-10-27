from typing import List

from fastapi import APIRouter, Depends
from server.modules.auth.dependencies import *

from ..block.models import Block
from .models import *

router = APIRouter(
	prefix='/speech_backend/fragments',
	tags=['Fragment'],
	# default campaign admin dependency
	dependencies=[Depends(get_campaign_admin)]
)

async def get_fragment_by_id(id: str) -> Fragment:
	return await Fragment.get(id)


@router.get('', response_model=List[Fragment])
async def get_all_fragments():
	return await Fragment.all()


@router.get('/{id}', response_model=Fragment)
async def get_single_fragment(
	fragment: Fragment = Depends(get_fragment_by_id)
):
	return fragment


@router.get('/{id}/review', response_model=Fragment)
async def review_single_fragment(
	correct: bool,
	fragment: Fragment = Depends(get_fragment_by_id)
):
	await fragment.update(review=correct, status='reviewed')
	return await Fragment.get(fragment.id)


@router.post('/{id}/reject', response_model=Fragment)
async def reject_fragment(
	fragment: Fragment = Depends(get_fragment_by_id)
):
	return await fragment.reject()


@router.post('/{id}/approve', response_model=Fragment)
async def reject_fragment(
	fragment: Fragment = Depends(get_fragment_by_id)
):
	return await fragment.approve()


@router.post('/{id}/jobs')
async def create_jobs_for_fragment(
	fragment: Fragment = Depends(get_fragment_by_id)
):
	return {'detail': f'{await fragment.create_jobs()} jobs created'}
