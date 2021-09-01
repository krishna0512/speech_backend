from typing import List

from fastapi import APIRouter, Body, Depends
from server.modules.auth.dependencies import *

from .models import *

router = APIRouter(
	prefix='/campaigns',
	tags=['Campaign'],
	dependencies=[Depends(get_campaign_admin)]
)

async def get_campaign_by_id(id: str):
	return await Campaign.get(id)

@router.get('', response_model=List[CampaignOut])
async def get_all_campaigns():
	return await Campaign.all()


@router.post('', response_model=CampaignOut)
async def create_new_campaign(
	data: CampaignIn = Body(...),
):
	return await Campaign.create(data)


@router.get('/{id}', response_model=CampaignOut)
async def get_single_campaign(
	camp: Campaign = Depends(get_campaign_by_id)
):
	return camp


@router.patch('/{id}', response_model=CampaignOut)
async def update_single_campaign(
	camp: Campaign = Depends(get_campaign_by_id),
	data: CampaignUpdate = Body(...),
):
	data = data.dict()
	data = {i:data[i] for i in data if data[i] is not None}
	await camp.update(**data)
	return await camp.refresh()


@router.delete('/{id}')
async def delete_single_campaign(
	camp: Campaign = Depends(get_campaign_by_id)
):
	await camp.delete()
	return {'detail': '1 record deleted'}


@router.post('/{id}/transcribers', response_model=CampaignOut)
async def add_transcriber_to_campaign(
	user_id: str,
	camp: Campaign = Depends(get_campaign_by_id)
):
	await camp.add_transcriber(user_id)
	return await camp.refresh()


@router.post('/{id}/reviewers', response_model=CampaignOut)
async def add_reviewer_to_campaign(
	user_id: str,
	camp: Campaign = Depends(get_campaign_by_id)
):
	await camp.add_reviewer(user_id)
	return await camp.refresh()
