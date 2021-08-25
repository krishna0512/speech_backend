from fastapi import APIRouter, Body, Depends
from server.modules.auth.dependencies import *

from .models import *

router = APIRouter()

@router.get('', response_model=List[UserOut])
async def get_all_users(user: User = Depends(get_superuser)):
	return await User.all()

@router.get("/me", response_model=UserOut)
async def read_users_me(user: User = Depends(get_active_user)):
	return user


@router.post('/register', response_model=UserOut)
async def register_new_user(
	data: UserIn = Body(...),
	user: User = Depends(get_superuser)
):
	return await User.create(data)
