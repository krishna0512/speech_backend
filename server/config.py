import os

MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', '10.2.8.15:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'Minio@0710')
MINIO_BUCKET_NAME = 'speech-data-prod'

MINIO_CAMPAIGN_SOURCES = [
	'campaign_source/ozonetel_webapp',
	'campaign_source/ozonetel_whatsapp',
]
