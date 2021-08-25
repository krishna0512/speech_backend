import os
from os.path import join

import numpy as np
from scipy.io import wavfile
from tqdm import tqdm


def generate_fragments(folder):
	def windows(signal, window_size, step_size):
		if type(window_size) is not int:
			raise AttributeError("Window size must be an integer.")
		if type(step_size) is not int:
			raise AttributeError("Step size must be an integer.")
		for i_start in range(0, len(signal), step_size):
			i_end = i_start + window_size
			if i_end >= len(signal):
				break
			yield signal[i_start:i_end]

	def energy(samples):
		return np.sum(np.power(samples, 2.)) / float(len(samples))

	def rising_edges(binary_signal):
		previous_value = 0
		index = 0
		for x in binary_signal:
			if x and not previous_value:
				yield index
			previous_value = x
			index += 1

	window_duration = 0.75
	step_duration = window_duration / 10
	silence_threshold = 0.01
	input_file = [i for i in os.listdir(folder) if i.endswith('.wav')][0]
	input_file = join(folder, input_file)
	print(f'Generating fragments for: {input_file}')
	output_dir = join(folder, 'frags')
	os.makedirs(output_dir)
	output_filename_prefix = os.path.splitext(os.path.basename(input_file))[0]
	sr, samples = input_data = wavfile.read(filename=input_file, mmap=True)
	max_amplitude = np.iinfo(samples.dtype).max
	max_energy = energy([max_amplitude])
	window_size = int(window_duration * sr)
	step_size = int(step_duration * sr)

	signal_windows = windows(
		signal=samples,
		window_size=window_size,
		step_size=step_size
	)

	window_energy = (energy(w) / max_energy for w in tqdm(
		signal_windows,
		total=int(len(samples) / float(step_size))
	))

	window_silence = (e > silence_threshold for e in window_energy)
	cut_times = (r * step_duration for r in rising_edges(window_silence))
	print("Finding silences...")
	cut_samples = [int(t * sr) for t in cut_times]
	cut_samples.append(-1)
	cut_ranges = [(i, cut_samples[i], cut_samples[i+1]) for i in range(len(cut_samples) - 1)]

	for i, start, stop in tqdm(cut_ranges):
		output_file_path = "{}_{:03d}.wav".format(
			os.path.join(output_dir, output_filename_prefix),
			i+1
		)
		print("Writing file ", output_file_path)
		wavfile.write(
			filename=output_file_path,
			rate=sr,
			data=samples[start:stop]
		)
	return output_dir
