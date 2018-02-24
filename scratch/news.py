import os, sys
import io
import queue
import random
import threading
import time

import picamera
from PIL import Image
import networkzero as nw0

def as_code(name):
    return "-".join(name.lower().split())

class NewsThread(threading.Thread):
    
    topic = "piwars"
    
    def __init__(self, name, queue, finish_event, *args, **kwargs):
        super(NewsThread, self).__init__(name=name, *args, **kwargs)
        self.news = nw0.advertise("piwars/%s" % as_code(name))
        self.queue = queue
        self._finish_event = finish_event
    
    def finished(self):
        return self._finish_event.is_set()
    
    def queue_result(self, t, value):
        self.queue.put((self.name, t, value))
    
    def send_news(self, value):
        nw0.send_news_to(self.news, self.topic, value)
    
    def run(self):
        values = self.values()
        while not self.finished():
            try:
                value = next(values)
            except StopIteration:
                break
            t = time.time()
            self.queue_result(t, value)
            self.send_news(value)
    
    def values(self):
        """The values method will be, typically, a generator, yielding
        one value in whatever way seems sensible
        """
        raise NotImplementedError

class DistanceThread(NewsThread):
    
    topic = "distance"
    
    def values(self):
        while not self.finished():
            yield random.random()
            time.sleep(0.1 * random.randint(0, 3))

class LineThread(NewsThread):
    
    topic = "line"
    
    def values(self):
        while not self.finished():
            yield random.choice(["light", "dark"])
            time.sleep(0.1 * random.randint(0, 3))

class CameraThread(NewsThread):
    
    topic = "camera"

    def queue_result(self, t, value):
        self.queue.put((self.name, t, repr(value[:20])))
        
    def send_news(self, value):
        with io.BytesIO(value) as data:
            image = Image.open(data)
            image.thumbnail((320, 240))
        with io.BytesIO() as data:
            image.save(data, "jpeg")
            nw0.send_news_to(self.news, self.topic, data.getvalue())

    def values(self):
        with picamera.PiCamera() as camera:
            camera.resolution = 1024, 768
            with io.BytesIO() as buffer:
                while not self.finished():
                    buffer.seek(0)
                    camera.capture(buffer, "jpeg")
                    yield buffer.getvalue()
                    time.sleep(random.randint(5, 10))

class LoggingThread(NewsThread):
    
    topic = "logs"
    levels = "debug", "info", "warning", "error"
    
    def values(self):
        while not self.finished():
            yield random.choice(self.levels), time.asctime()
            time.sleep(random.randint(2, 5))

def watch_queues(queues):
    print("Watching queues...")
    while True:
        for q in queues:
            try:
                name, t, value = q.get(timeout=0.1)
                print("%s: %s => %s" % (time.ctime(t), name, value))
            except queue.Empty:
                pass

def main():
    threads = []
    finish_event = threading.Event()
    threads.append(DistanceThread("Distance A", queue.Queue(), finish_event))
    threads.append(DistanceThread("Distance B", queue.Queue(), finish_event))
    threads.append(LineThread("Line", queue.Queue(), finish_event))
    threads.append(CameraThread("Camera", queue.Queue(), finish_event))
    threads.append(LoggingThread("Logs", queue.Queue(), finish_event))

    print("Firing up threads..")
    for thread in threads:
        print("Starting", thread.name)
        thread.start()
    
    try:
        watch_queues([t.queue for t in threads])
    except KeyboardInterrupt:
        finish_event.set()
        print("Waiting for threads to complete...")
        for thread in threads:
            print("Waiting for", thread.name)
            thread.join()

if __name__ == '__main__':
    main(*sys.argv[1:])
