import snowboydecoder
import sys
import os
import time
import signal
#from pixels.pixels import Pixels

interrupted = False
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
model = os.path.join(ROOT_DIR, "resources/xiaobaozi.umdl")
#pixel = Pixels()

def signal_handler(signal, frame):
    global interrupted
    interrupted = True
    #pixel.off()

def interrupt_callback():
    global interrupted
    return interrupted

def detected_callback_func():
    interrupted = True
    #pixel.wakeup()
    print('wakeup')
    snowboydecoder.play_audio_file()
    print('listen')
    #time.sleep(5)
    #pixel.listen()
    #time.sleep(5)
    ##pixel.request()
    print('request')
    print('response')
    print('speak')
    interrupted = False
    

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.4)
#pixel.wait()
print('wait')

# main loop
detector.start(detected_callback=detected_callback_func,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()
