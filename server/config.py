import os

MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', '10.2.8.15:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'Minio@0710')
MINIO_BUCKET_NAME = 'speech-data-prod'

SUBTL_ENDPOINT = 'http://10.2.8.18:8887'
SUBTL_USERNAME = 'admin%40agastya.com'
SUBTL_PASSWORD = 'Agastya%401234'
# SUBTL_ACCESS_TOKEN_FILE = './.subtl_access_token'
