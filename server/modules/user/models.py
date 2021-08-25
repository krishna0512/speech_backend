from typing import List, Optional
from uuid import uuid4

from passlib.context import CryptContext
from pydantic import BaseModel, Field
from server.database import get_db


class Token(BaseModel):
	access_token: str
	token_type: str


class UserOut(BaseModel):
	id: str = Field(default_factory=lambda: str(uuid4()))
	username: str
	name: Optional[str] = ''
	mobile: Optional[str] = ''
	email: Optional[str] = ''
	active: Optional[bool] = True
	superuser: Optional[bool] = False

class UserIn(BaseModel):
	username: str
	password: str
	name: Optional[str] = ''
	mobile: Optional[str] = ''
	email: Optional[str] = ''


class User(UserOut):
	# this stores the hashed password
	password: str

	@staticmethod
	async def get(username):
		ret = await get_db()['users'].find_one({'username': username})
		return User(**ret)

	@staticmethod
	async def all():
		ret = get_db()['users'].find()
		return [User(**i) async for i in ret]

	@staticmethod
	async def create(user: UserIn):
		userdict = user.dict().copy()
		# TODO: check if the username already exists
		userdict['password'] = CryptContext(
			schemes=['bcrypt'],
			deprecated='auto',
		).hash(userdict['password'])
		ret = User(
			**userdict,
		)
		await ret.save()
		return ret

	@staticmethod
	async def login(username: str, password: str):
		user = await User.get(username)
		if not user:
			return False
		if not user.authenticate(password):
			return False
		return user

	async def save(self):
		await get_db()['users'].insert_one(self.dict())

	async def authenticate(self, password):
		return CryptContext(
			schemes=['bcrypt'],
			deprecated='auto',
		).verify(password, self.password)
