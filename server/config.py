import os

MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', '10.2.8.15:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'Minio@0710')
MINIO_BUCKET_NAME = 'speech-data-prod'

MINIO_CAMPAIGN_SOURCES = [
	'campaign_source/ozonetel_webapp',
	'campaign_source/ozonetel_whatsapp',
]

AUTH_SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
AUTH_ALGORITHM = "HS256"
AUTH_ACCESS_TOKEN_EXPIRE_DAYS = 365
