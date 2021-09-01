from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from server.config import *
from server.modules.user.models import User

from .models import *

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

async def get_user(token: str = Depends(oauth2_scheme)):
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		payload = jwt.decode(token, AUTH_SECRET_KEY, algorithms=[AUTH_ALGORITHM])
		username: str = payload.get("sub")
		if username is None:
			raise credentials_exception
	except JWTError:
		raise credentials_exception
	user = await User.get(username)
	if user is None:
		raise credentials_exception
	return user


async def get_active_user(user: User = Depends(get_user)):
	if not user.active:
		raise HTTPException(
			status_code=400,
			detail="User Inactive. Please contact admin"
		)
	return user

async def get_superuser(user: User = Depends(get_user)):
	if not user.superuser:
		raise HTTPException(
			status_code=400,
			detail="Endpoint only accessible to superuser"
		)
	return user

async def get_campaign_admin(user: User = Depends(get_active_user)):
	# if not 'campaign_admin' in user.roles and not user.superuser:
	# 	raise HTTPException(
	# 		status_code=400,
	# 		detail='Endpoint only accessible to campaign admin or Superuser'
	# 	)
	return user
