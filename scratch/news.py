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
    
    def __init__(self, name, queue, finish_event, *args, **kwargs):
        super(NewsThread, self).__init__(name=name, *args, **kwargs)
        self.news = nw0.advertise("piwars/%s" % as_code(name))
        self.queue = queue
        self._finish_event = finish_event
    
    def finished(self):
        return self._finish_event.is_set()
    
    def run(self):
        values = self.values()
        while not self.finished():
            try:
                value = next(values)
            except StopIteration:
                break
            t = time.time()
            if self.name == "Camera":
                queue_value = repr(value)[:20]
                with io.BytesIO(value) as data:
                    image = Image.open(data)
                    image.thumbnail((320, 240))
                with io.BytesIO() as data:
                    image.save(data, "jpeg")
                    news_value = nw0.bytes_to_string(data.getvalue())
            else:
                queue_value = news_value = value
            self.queue.put((self.name, t, queue_value))
            nw0.send_news_to(self.news, self.name, (t, news_value))
    
    def values(self):
        """The values method will be, typically, a generator, yielding
        one value in whatever way seems sensible
        """
        raise NotImplementedError

class DistanceThread(NewsThread):
    
    def values(self):
        while not self.finished():
            yield random.random()
            time.sleep(0.5 + (0.1 * random.randint(0, 3)))

class LineThread(NewsThread):
    
    def values(self):
        while not self.finished():
            yield random.choice(["light", "dark"])
            time.sleep(0.5 + (0.1 * random.randint(0, 3)))

class CameraThread(NewsThread):
    
    def values(self):
        with picamera.PiCamera() as camera:
            camera.resolution = 1024, 768
            with io.BytesIO() as buffer:
                while not self.finished():
                    buffer.seek(0)
                    camera.capture(buffer, "jpeg")
                    yield buffer.getvalue()
                    time.sleep(0.5 + (0.1 * random.randint(0, 3)))

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
