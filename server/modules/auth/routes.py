from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from server.config import *
from server.modules.user.models import User

from .models import *

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(data: OAuth2PasswordRequestForm = Depends()):

	def create_access_token(data: dict):
		to_encode = data.copy()
		expire = datetime.utcnow() + timedelta(days=AUTH_ACCESS_TOKEN_EXPIRE_DAYS)
		to_encode.update({"exp": expire})
		encoded_jwt = jwt.encode(to_encode, AUTH_SECRET_KEY, algorithm=AUTH_ALGORITHM)
		return encoded_jwt

	user = await User.login(data.username, data.password)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"},
		)
	access_token = create_access_token(
		data={"sub": user.username}
	)
	return {"access_token": access_token, "token_type": "bearer"}
