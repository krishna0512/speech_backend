import json

import requests


def telugu(audio_url) -> str:
	print(f'Performing ASR on audio: {audio_url}')
	url = 'http://canvas.iiit.ac.in/iiitASR/runASR'
	headers = {
		'Content-Type': 'application/json',
	}
	payload = {
		'audioURL': audio_url
	}

	r = requests.post(url, headers=headers, data=json.dumps(payload))
	if r.status_code != 200:
		return 'Error in ASR'
	ret = r.json()['scriptedText'].strip()
	print(f'Telugu ASR output: {ret}')
	return ret
