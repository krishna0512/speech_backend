from motor.motor_asyncio import AsyncIOMotorClient


class Database:
	client: AsyncIOMotorClient = None

db = Database()

def get_db() -> AsyncIOMotorClient:
	return db.client['speech']

async def connect_to_mongo():
	print('Connecting to database...')
	db.client = AsyncIOMotorClient(
		'mongodb://speech_user:iiit123@10.2.8.15/speech'
	)
	print('Connected!')

async def close_mongo_connection():
	print('Disconnecting from database...')
	db.client.close()
	print('Disconnected!')
