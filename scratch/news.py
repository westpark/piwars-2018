import os, sys
import io
import queue
import random
import threading
import time

import picamera
import networkzero as nw0

class NewsThread(threading.Thread):
    
    def __init__(self, name, queue, finish_event, *args, **kwargs):
        super(NewsThread, self).__init__(name=name, *args, **kwargs)
        self.news = nw0.advertise("piwars/%s" % name)
        self.queue = queue
        self.finish_event = finish_event
        self.daemon = True
    
    def run(self):
        values = self.values()
        while not self.finish_event.is_set():
            value = next(values)
            t = time.time()
            self.queue.put((self.name, t, value))
            nw0.send_news_to(self.news, self.name, (t, value))
    
    def values(self):
        """The values method will be, typically, a generator, yielding
        one value in whatever way seems sensible
        """
        raise NotImplementedError

class DistanceThread(NewsThread):
    
    def values(self):
        while not self.finish_event.is_set():
            yield random.random()
            time.sleep(0.5 + (0.1 * random.randint(0, 3)))

class LineThread(NewsThread):
    
    def values(self):
        while not self.finish_event.is_set():
            yield random.choice(["light", "dark"])
            time.sleep(0.5 + (0.1 * random.randint(0, 3)))

class CameraThread(NewsThread):
    
    def values(self):
        with picamera.PiCamera() as camera:
            camera.resolution = 1024, 768
            with io.BytesIO() as buffer:
                while not self.finish_event.is_set():
                    buffer.seek(0)
                    camera.capture(buffer, "jpeg")
                    image = buffer.getvalue()
                    yield nw0.bytes_to_string(image)
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
    distance_a_queue = queue.Queue()
    distance_b_queue = queue.Queue()
    line_queue = queue.Queue()
    camera_queue = queue.Queue()
    finish_event = threading.Event()

    threads = []
    threads.append(DistanceThread("Distance A", distance_a_queue, finish_event))
    threads.append(DistanceThread("Distance B", distance_b_queue, finish_event))
    threads.append(LineThread("Line", line_queue, finish_event))
    threads.append(CameraThread("Camera", camera_queue, finish_event))

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
