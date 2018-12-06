import os
import fnmatch
import numpy as np
from pydub import AudioSegment
from pydub.utils import audioop
import wavio
from hashlib import sha1

def unique_hash(filepath, blocksize=2**20):
    """ Small function to generate a hash to uniquely generate
    a file. Inspired by MD5 version here:
    http://stackoverflow.com/a/1131255/712997

    Works with large files. 
    """
    s = sha1()
    with open(filepath , "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            s.update(buf)
    return s.hexdigest().upper()

def find_files(path, extensions):
    # Allow both with ".mp3" and without "mp3" to be used for extensions
    extensions = [e.replace(".", "") for e in extensions]

    for dirpath, dirnames, files in os.walk(path):
        for extension in extensions:
            for f in fnmatch.filter(files, "*.%s" % extension):
                p = os.path.join(dirpath, f)
                yield (p, extension)

def path_to_songname(path):
    """
    Extracts song name from a filepath. Used to identify which songs
    have already been fingerprinted on disk.
    """
    return os.path.splitext(os.path.basename(path))[0]

"""
Following are modified funtions
"""

def read(filename, limit=None):
'''
returns: (channels, samplerate)
'''
	#load data
	data = load_xdf(filename, dejitter_timestamps=False)

	n_channels = 4  # how many expected channels of the MUSE
	participant_idx = np.array([0, 2])  # other channels are about movement / blinks / data quality
	# which frequency bands to use to compute the envelope
	freq_bands = {'delta': (1, 4),
	              'theta': (4, 8),
	              'alpha': (8, 14),
	              'beta': (14, 20)}

	# pasrse data structure
	signal, fs = get_data(data, participant_idx)

	return signal, fs


def get_data(xdf_file, ptp_idx):
'''
extract data and return a single signal and sampling rate
TODO: dimension reduction to reduce channels
TODO: artefacts removal using ICP?
'''
    # figure out the length of shortest recording
    shortest_recording = 1e12
    for ptp_i in ptp_idx:
        if len(data[0][ptp_i]['time_series']) < shortest_recording:
            shortest_recording = len(data[0][ptp_i]['time_series'])

    # put all data into one matrix
    data_matrix = list()
    for ptp_i in ptp_idx:
        this_data = data[0][ptp_i]['time_series']
        data_matrix.append(this_data[0:shortest_recording-1, :])

    # get time stamps and sample freq
    fs = round(data[0][ptp_idx[0]]['info']['effective_srate'] * 1000)

    return np.array(data_matrix), fs