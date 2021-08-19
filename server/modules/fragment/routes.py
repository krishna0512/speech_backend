import os
from os.path import join
from tempfile import TemporaryDirectory

import requests
from fastapi import APIRouter
from pydub import AudioSegment
from server.utils.minio import Minio

router = APIRouter()

@router.post('')
async def fragment_raw_files():
	"""
	This Endpoint handles the processing of all remaining raw audio files into
	multiple fragments
	"""
	return {'detail': f'{update_all()} audio files updated'}


def update_all():
	ret = update('campaign_source/ozonetel_webapp')
	ret += update('campaign_source/ozonetel_whatsapp')
	return ret

def update(prefix='campaign_source/ozonetel_webapp') -> int:
	a = [i.object_name for i in Minio().list_objects('speech-data-prod', prefix=prefix, recursive=True)]
	a = [i for i in a if i.endswith('wav')]
	if not a:
		return 0
	print(f'{len(a)} new audiofiles detected')
	return len(list(map(split, a)))


def split(key: str) -> str:
	"""
	function that takes the minio key of the wav file and
	splits and saves the file to fragments folder in minio.
	and also moves the concerned audio file to fragmented_source folder

	@returns the new key of the audiofile that is saved in fragmented_source
	"""
	key = key.strip(' /')
	audiofilename = key.split('/')[-1].strip()
	mc = Minio()
	folderpath = TemporaryDirectory(prefix='frags')
	source_audio = join(folderpath.name, audiofilename)
	print(f'Downloading the audiofile to {source_audio}')
	with open(source_audio, 'wb') as f:
		f.write(requests.get(mc.get_fileurl(key)).content)
	splitfolder = join(folderpath.name, 'splits')
	os.makedirs(splitfolder)

	# splitting the audio now.
	a = AudioSegment.from_wav(source_audio)
	print(f'duration of audio = {len(a)}ms')
	b = [i for i in range(2500,3500) if len(a)%i<i*.01]
	lenseg = b[(len(b)-1)//2]
	print(f'Splitting the audio into segments of {lenseg}ms')
	nseg = len(a)//lenseg
	print(f'Total number of segments = {nseg}')
	print(f'splitting and saving the audio to {splitfolder} location...')
	ret = []
	for i in range(nseg):
		e = a[i*lenseg:] if i==nseg-1 else a[i*lenseg:(i+1)*lenseg]
		newfilename = '{}_{}.{}'.format(
			audiofilename.split('.')[0],
			i+1,
			audiofilename.split('.')[-1],
		)
		ret.append(join(splitfolder, newfilename))
		e.export(ret[-1], format='wav')
		print('.', end='', flush=True)
	print('done')
	print(f'saving {len(ret)} frag audio files to minio...')
	for i in ret:
		with open(i, 'rb') as f:
			mc.upload_fileobj(f, f'fragments/{os.path.basename(i)}')
			print('.', end='', flush=True)
	print('done')
	print('moving the wav file from campaign source to fragmented source')
	with open(source_audio, 'rb') as f:
		mc.upload_fileobj(f, f'fragmented_source/{audiofilename}')
	mc.delete(key)
	print('done')
	return f'fragmented_source/{audiofilename}'
