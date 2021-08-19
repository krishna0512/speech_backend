from fastapi import FastAPI

from server.config import *
from server.modules.audio.routes import router as audio_router
from server.modules.fragment.routes import router as fragment_router

app = FastAPI(
	title='Speech Data API',
	description='Comprehensive API for all the speech data related backend tasks',
)

app.include_router(
	audio_router,
	prefix='/audio',
	tags=['Audio'],
)

app.include_router(
	fragment_router,
	prefix='/fragment',
	tags=['Fragmentation'],
)


@app.post('/', tags=['Main'])
async def index():
	return {'detail': 'Hello World!'}
