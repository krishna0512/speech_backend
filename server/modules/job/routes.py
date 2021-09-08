from typing import List

from fastapi import APIRouter, Depends
from server.modules.auth.dependencies import *

from .models import *

router = APIRouter(
	prefix='/jobs',
	tags=['Job'],
	# default campaign admin dependency
	# dependencies=[Depends(get_campaign_admin)]
)

async def get_job_by_id(id: str) -> Job:
	return await Job.get(id)


@router.get('', response_model=List[JobOut])
async def get_all_jobs(current_user: User = Depends(get_campaign_admin)):
	"""
	get all the jobs of the loggedin user.
	"""
	return await Job.all()


@router.get('/me', response_model=List[JobOut])
async def get_my_jobs(
	current_user: User = Depends(get_active_user)
):
	return await Job.filter(assigned_to=current_user.id)


@router.get('/{id}', response_model=Job)
async def assign_user_to_job(
	current_user: User = Depends(get_active_user),
	job: Job = Depends(get_job_by_id),
):
	return job


@router.post('/{id}/assign', response_model=Job)
async def assign_user_to_job(
	user_id: str,
	current_user: User = Depends(get_campaign_admin),
	job: Job = Depends(get_job_by_id),
):
	return await job.assign(user_id)


@router.patch('/{id}', response_model=Job)
async def update_job(
	data: JobUpdate,
	current_user: User = Depends(get_active_user),
	job: Job = Depends(get_job_by_id),
):
	if job.status == 'assigned':
		await job.update(status='completed', transcript=data.transcript)
	elif job.status == 'completed':
		await job.update(status='reviewed', correct=job.correct)
	return await Job.get(job.id)
