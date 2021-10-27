from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.config import *
from server.database import close_mongo_connection, connect_to_mongo
from server.modules.auth.routes import router as auth_router
from server.modules.block.routes import router as block_router
from server.modules.campaign.routes import router as campaign_router
from server.modules.fragment.routes import router as fragment_router
from server.modules.job.routes import router as job_router
from server.modules.user.routes import router as user_router

app = FastAPI(
	title='Speech Data API',
	description='Comprehensive API for all the speech data related backend tasks',
	docs_url='/speech_backend/docs',
	openapi_url='/speech_backend/openapi.json',
)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler('startup', connect_to_mongo)
app.add_event_handler('shutdown', close_mongo_connection)

app.include_router(
	auth_router,
	prefix='/speech_backend/auth',
	tags=['Auth'],
)

# app.include_router(
# 	user_router,
# 	prefix='/users',
# 	tags=['User'],
# )

app.include_router(campaign_router)
app.include_router(block_router)
app.include_router(fragment_router)
app.include_router(job_router)


@app.post('/speech_backend', tags=['Main'])
async def index():
	return {'detail': 'Hello World!'}
