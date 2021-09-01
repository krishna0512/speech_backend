from fastapi import APIRouter, Body, Depends
from server.modules.auth.dependencies import *

from .models import *

router = APIRouter()

@router.get('', response_model=List[UserOut])
async def get_all_users(user: User = Depends(get_superuser)):
	return await User.all()

@router.get("/me", response_model=UserOut)
async def get_my_user_details(user: User = Depends(get_active_user)):
	return user

@router.patch("/me", response_model=UserOut)
async def update_my_user_details(
	data: UserUpdate = Body(...),
	user: User = Depends(get_active_user)
):
	data = data.dict()
	# ignore the empty data keys
	data = {i:data[i] for i in data if data[i]}
	await user.update(**data)
	return await User.get(user.username)


@router.post('/register', response_model=UserOut)
async def register_new_user(
	data: UserIn = Body(...),
	user: User = Depends(get_superuser)
):
	return await User.create(data)
