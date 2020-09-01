
import apa102
import time
import threading
import numpy
from gpiozero import LED
try:
    import queue as Queue
except ImportError:
    import Queue as Queue


class Pixels:
    PIXELS_N = 12
    LOW_MULTIPLE = 5
    MIDDLE_MULTIPLE = 15
    HIGH_MULTIPLE = 35
    HIGHLIGHT_MULTIPLE = 50

    def __init__(self):

        self.basis = numpy.array([0] * 4 * self.PIXELS_N)
        self.basis[0 * 4 + 1] = 4
        self.basis[1 * 4 + 1] = 3
        self.basis[1 * 4 + 2] = 1
        self.basis[2 * 4 + 1] = 2
        self.basis[2 * 4 + 2] = 2
        self.basis[3 * 4 + 1] = 1
        self.basis[3 * 4 + 2] = 3
        self.basis[4 * 4 + 2] = 4
        self.basis[5 * 4 + 2] = 3
        self.basis[5 * 4 + 3] = 1
        self.basis[6 * 4 + 2] = 2
        self.basis[6 * 4 + 3] = 2
        self.basis[7 * 4 + 2] = 1
        self.basis[7 * 4 + 3] = 3
        self.basis[8 * 4 + 3] = 4
        self.basis[9 * 4 + 3] = 3
        self.basis[9 * 4 + 1] = 1
        self.basis[10 * 4 + 3] = 2
        self.basis[10 * 4 + 1] = 2
        self.basis[11 * 4 + 3] = 1
        self.basis[11 * 4 + 1] = 3

	self.multiple = 1

        self.colors = self.basis
        self.dev = apa102.APA102(num_led=self.PIXELS_N)

        self.power = LED(5)
        self.power.on()

        self.next = threading.Event()
        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def wait(self):
        self.next.set()
        self.queue.put(self._wait)

    def wakeup(self):
        self.next.set()
        self.queue.put(self._wakeup)

    def listen(self):
        self.next.set()
        self.queue.put(self._listen)

    def think(self):
        self.next.set()
        self.queue.put(self._think)

    def speak(self):
        self.next.set()
        self.queue.put(self._speak)

    def off(self):
        self.next.set()
        self.queue.put(self._off)

    def _wait(self):

        step = 0.5

        self.next.clear()
        while not self.next.is_set():

            self.write(self.colors * self.multiple)

            if self.multiple >= self.MIDDLE_MULTIPLE:
                step = -0.5
            elif self.multiple <= self.LOW_MULTIPLE:
                step = 0.5

            self.multiple += step
            time.sleep(0.1)

    def _wakeup(self):

        self.next.clear()
        while self.multiple < self.HIGHLIGHT_MULTIPLE:
	    self.multiple += 5
            self.write(self.colors * self.multiple)
	    time.sleep(0.02)

        while self.multiple > self.MIDDLE_MULTIPLE:
	    self.multiple -= 5
            self.write(self.colors * self.multiple)
	    time.sleep(0.01)

    def _listen(self):

        step = 0.5
        count = (self.HIGH_MULTIPLE - self.MIDDLE_MULTIPLE) / step
        step_time = 1 / count

        self.next.clear()
        while not self.next.is_set():

	    self.write(self.colors * self.multiple)

            if self.multiple >= self.HIGH_MULTIPLE:
                step = -0.5
            elif self.multiple <= self.MIDDLE_MULTIPLE:
                step = 0.5

            self.multiple += step
            time.sleep(step_time)

    def _think(self):

        self.next.clear()

        t = 0.02
        while self.multiple != self.MIDDLE_MULTIPLE:
            if self.multiple > self.MIDDLE_MULTIPLE:
                self.multiple -= 0.5
            else:
                self.multiple += 0.5
            self.write(self.colors * self.multiple)
            time.sleep(t)

        while not self.next.is_set():
            self.colors = numpy.roll(self.colors, 4)
            self.write(self.colors * self.multiple)
            time.sleep(0.5)

    def _speak(self):
        colors = self.colors
        step = -1
        brightness = 24

        self.next.clear()
        while not self.next.is_set():
            brightness += step
            self.write(colors * brightness / 24)

            if brightness == 4 or brightness == 24:
                step = -step
                time.sleep(0.2)
            else:
                time.sleep(0.1)

        while brightness > 0:
            brightness -= 1
            self.write(colors * brightness / 24)
            time.sleep(0.01)

    def _off(self):
        self.write([0] * 4 * self.PIXELS_N)

    def _run(self):
        while True:
            func = self.queue.get()
            func()

    def write(self, colors):
        for i in range(self.PIXELS_N):
            self.dev.set_pixel(i, int(colors[4*i + 1]), int(colors[4*i + 2]), int(colors[4*i + 3]))

        self.dev.show()


if __name__ == '__main__':

    pixels = Pixels()

    while True:

        try:
            #print('wait')
            #pixels.wait()
            #time.sleep(5)
            print('wakeup')
            pixels.wakeup()
            time.sleep(2)
            print('listen')
            pixels.listen()
            time.sleep(5)
            print('think')
            pixels.think()
            time.sleep(5)
        except KeyboardInterrupt:
            break


    pixels.off()
    time.sleep(1)
