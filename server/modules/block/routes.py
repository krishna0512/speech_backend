from typing import List

from fastapi import APIRouter, Depends
from server.modules.auth.dependencies import *

from ..campaign.models import *
from ..fragment.models import Fragment
from .models import *

router = APIRouter(
	prefix='/blocks',
	tags=['Block'],
	# default campaign admin dependency
	dependencies=[Depends(get_campaign_admin)]
)

async def get_block_by_id(id: str) -> Block:
	return await Block.get(id)


@router.get('', response_model=List[BlockOut])
async def get_all_raw_block_files():
	"""
	Get all raw block files from the DB without refreshing from MINIO

	Idea is that minio to mongodb refresh will happen via another endpoint
	through a cron job just like fragmentation cron.
	"""
	return await Block.all()


# @router.post('', response_model=BlockOut)
# async def create_new_block(
# 	data: BlockIn = Body(...),
# 	file: UploadFile = File(...)
# ):
# 	print(data, file)


@router.get('/{id}', response_model=BlockOut)
async def get_single_block(
	block: Block = Depends(get_block_by_id)
):
	return block


@router.delete('/{id}')
async def get_single_block(
	block: Block = Depends(get_block_by_id)
):
	await block.delete()
	return {'detail': f'1 block record deleted'}


@router.post('/update')
async def update_blocks_for_campaign(
	campaign_id: str
):
	"""
	This endpoint will handle all the logic for checking in the Minio server
	and updating any new files to the mongodb.
	"""
	ret = await Block.update_block_from_minio(campaign_id)
	return {'detail': f'{ret} new raw files updated'}


@router.post('/{id}/fragments', response_model=List[Fragment])
async def get_single_block(
	block: Block = Depends(get_block_by_id)
):
	return await block.generate_fragments()
