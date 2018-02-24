import os, sys
import io
import time

import pygame
from pygame.locals import *
#
# Need to .init here so that "constant" fonts are available
#
pygame.init()

import networkzero as nw0

def name_from_code(code):
    return " ".join(w.title() for w in code.split("-"))

class Monitor(object):

    size = width, height = 640, 480
    font = pygame.font.Font("piwars.ttf", 18) # copied from arial.ttf
    text_fg = pygame.Color(0xff, 0xff, 0xff, 0xff)
    text_bg = pygame.Color(0x00, 0x00, 0xff, 0xff)

    channel_names = ["camera", "distance-a", "distance-b", "line", "logs"]
    rects = {
        "camera" : pygame.Rect(0, 0, 320, 240),
        "distance-a" : pygame.Rect(0, 250, 320, 30),
        "distance-b" : pygame.Rect(0, 290, 320, 30),
        "line" : pygame.Rect(0, 330, 320, 30),
        "logs" : pygame.Rect(330, 0, 310, 480)
    }
    
    def __init__(self):
        self.channels = {}
        for name in self.channel_names:
            address = nw0.discover("piwars/%s" % name, wait_for_s=3)
            if address:
                self.channels[name] = address
    
    def update_from_news_distance(self, name, info):
        distance = nw0.sockets._unserialise(info)
        return self.font.render("%s: %3.2fcm" % (name_from_code(name), distance), True, self.text_fg, self.text_bg)
    
    def update_from_news_line(self, name, info):
        light_or_dark = nw0.sockets._unserialise(info)
        return self.font.render("Line? %s" % light_or_dark, True, self.text_fg, self.text_bg)
    
    def update_from_news_camera(self, name, info):
        with io.BytesIO(info) as buffer:
            return pygame.image.load(buffer, "camera.jpg")
    
    def update_from_news(self, name, topic, info):
        function = getattr(self, "update_from_news_%s" % topic.lower())
        rendered = function(name, info)
        return rendered, self.rects[name]
    
    def run(self):
        screen = pygame.display.set_mode(self.size)
        
        rects_to_update = []
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()

            rects_to_update.clear()
            for name, channel in self.channels.items():
                topic, info = nw0.wait_for_news_from(channel, wait_for_s=0, is_raw=True)
                if topic is None:
                    continue
                rects_to_update.append(self.update_from_news(name, topic, info))

            for surface, rect in rects_to_update:
                screen.blit(surface, rect.topleft)
            updated_rects = [rect for _, rect in rects_to_update]
            pygame.display.update(updated_rects)
    
def main():
    monitor = Monitor()
    monitor.run()

if __name__ == '__main__':
    main(*sys.argv[1:])
