from snowboy import snowboydetect
import pyaudio
import os
import sys
import logging
import collections
import time

import wave

class RingBuffer(object):

    def __init__(self, size=4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):
        self._buf.extend(data)

    def get(self):
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
model = os.path.join(ROOT_DIR, "resources/xiaobaozi.umdl")
resource = os.path.join(ROOT_DIR, "resources/common.res")

sleep_time = 0.03
silent_count_threshold = 5
recording_timeout = 10000

detector = snowboydetect.SnowboyDetect(resource_filename=resource, model_str=model)
ring_buffer = RingBuffer(detector.NumChannels() * detector.SampleRate() * 5)
recorded_data = []

def audio_callback(in_data, frame_count, time_info, status):

    ring_buffer.extend(in_data)
    play_data = chr(0) * len(in_data)

    return play_data, pyaudio.paContinue

audio = pyaudio.PyAudio()

try:
    stream_in = audio.open(
	input=True, output=False,
	format=audio.get_format_from_width(
	    detector.BitsPerSample() / 8),
	channels=detector.NumChannels(),
	rate=detector.SampleRate(),
	frames_per_buffer=2048,
	stream_callback=audio_callback)
except Exception as e:
    logging.critical(e)

silent_start = False
silent_count = 0
recording_count = 0
first_data = b'';

while True:
    data = ring_buffer.get()
    if len(data) == 0:
        time.sleep(sleep_time)
        continue

    status = detector.RunDetection(data)
                
    stop_recording = False

    if recording_count > recording_timeout:
        stop_recording = True
    elif status == -2:
        if silent_count > silent_count_threshold:
            stop_recording = True
        elif silent_start:
            silent_count += 1
            print silent_count
    elif status == 0:
        silent_count = 0
        silent_start = True

    if stop_recording == True:
        break

    recording_count += 1
    if silent_start:
        recorded_data.append(data)
    else:
	first_data = data

res_data = first_data + b''.join(recorded_data)

wf = wave.open('/tmp/1.wav', 'wb')
wf.setnchannels(detector.NumChannels())
wf.setsampwidth(audio.get_sample_size(audio.get_format_from_width(detector.BitsPerSample() / 8)))
wf.setframerate(detector.SampleRate())
wf.writeframes(res_data)
wf.close()

stream_in.stop_stream()
stream_in.close()
audio.terminate()
