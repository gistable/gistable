#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import librosa
import numpy as np
import os
from progressbar import ProgressBar

parser = argparse.ArgumentParser(
	description='Split audio into multiple files and save analysis.')
parser.add_argument('-i', '--input', type=str)
parser.add_argument('-o', '--output', type=str, default='transients')
parser.add_argument('-s', '--sr', type=int, default=44100)
args = parser.parse_args()

y, sr = librosa.load(args.input, sr=args.sr)
o_env = librosa.onset.onset_strength(y, sr=sr, feature=librosa.cqt)
onset_frames = librosa.onset.onset_detect(onset_envelope=o_env, sr=sr)

def prepare(y, sr=22050):
    y = librosa.to_mono(y)
    y = librosa.util.fix_length(y, sr) # 1 second of audio
    y = librosa.util.normalize(y)
    return y

def get_fingerprint(y, sr=22050):
    y = prepare(y, sr)
    cqt = librosa.cqt(y, sr=sr, hop_length=2048)
    return cqt.flatten('F')

def normalize(x):
    x -= x.min(axis=0)
    x /= x.max(axis=0)
    return x

def basename(file):
    file = os.path.basename(file)
    return os.path.splitext(file)[0]

vectors = []
words = []
filenames = []

onset_samples = list(librosa.frames_to_samples(onset_frames))
onset_samples = np.concatenate(onset_samples, len(y))
starts = onset_samples[0:-1]
stops = onset_samples[1:]
analysis_folder = args.output
samples_folder = os.path.join(args.output, 'samples')
try:
	os.makedirs(samples_folder)
except:
	pass
pbar = ProgressBar()
for i, (start, stop) in enumerate(pbar(zip(starts, stops))):
    audio = y[start:stop]
    filename = os.path.join(samples_folder, str(i) + '.wav')
    librosa.output.write_wav(filename, audio, sr)
    vector = get_fingerprint(audio, sr=sr)
    word = basename(filename)
    vectors.append(vector)
    words.append(word)
    filenames.append(filename)
np.savetxt(os.path.join(analysis_folder, 'vectors'), vectors, fmt='%.5f', delimiter='\t')
np.savetxt(os.path.join(analysis_folder, 'words'), words, fmt='%s')
np.savetxt(os.path.join(analysis_folder, 'filenames.txt'), filenames, fmt='%s')