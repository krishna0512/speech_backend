from typing import List

from fastapi import APIRouter, Depends
from server.modules.auth.dependencies import *
from server.utils.minio import Minio

from .models import *

router = APIRouter()


@router.get('', response_model=List[Job])
async def get_all_jobs(
	user: User = Depends(get_active_user)
):
	"""
	get all the jobs of the loggedin user.
	"""
	return await Job.all()


@router.post('', response_model=Job)
async def create_new_job(
	data: JobIn,
	user: User = Depends(get_active_user),
):
	pass


@router.get('/{id}', response_model=Job)
async def get_job_detail(
	id: str,
	user: User = Depends(get_active_user)
):
	return await Job.get(id)
