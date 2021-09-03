from typing import List

from fastapi import APIRouter, Depends
from server.modules.auth.dependencies import *

from ..block.models import Block
from .models import *

router = APIRouter(
	prefix='/fragments',
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
