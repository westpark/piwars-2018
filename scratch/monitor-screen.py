import os, sys
import collections
import io
import threading
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

    size = width, height = 800, 600
    font = pygame.font.Font("piwars.ttf", 18) # copied from arial.ttf
    font_h = font.get_height()
    log_font = pygame.font.Font("piwars.ttf", 14)
    log_font_h = log_font.get_height()
    bg = pygame.Color(0, 0, 0, 0xff)
    text_h = 30
    text_fg = pygame.Color(0xff, 0xff, 0xff, 0xff)
    text_bg = pygame.Color(0x00, 0x00, 0xff, 0xff)
    border_w = 4

    channel_names = ["camera", "distance-a", "distance-b", "line", "logs"]
    rects = {}
    rects["camera"] = camera_rect = pygame.Rect(0, 0, width / 3, height / 2)
    rects["distance-a"] = distance_a_rect = pygame.Rect(camera_rect.left, camera_rect.top + camera_rect.height + border_w, camera_rect.width, text_h)
    rects["distance-b"] = distance_b_rect = pygame.Rect(distance_a_rect.left, distance_a_rect.top + distance_a_rect.height + border_w, distance_a_rect.width, text_h)
    rects["line"] = line_rect = pygame.Rect(distance_b_rect.left, distance_b_rect.top + distance_b_rect.height + border_w, distance_b_rect.width, text_h)
    rects["logs"] = logs_rect = pygame.Rect(camera_rect.left + camera_rect.width + (3 * border_w), camera_rect.top, width - (camera_rect.left + camera_rect.width + (3 * border_w)), height)
    
    def __init__(self):
        self.log_queue = collections.deque(maxlen=self.height // self.log_font_h)
        self.channels = {}
        for name in self.channel_names:
            address = nw0.discover("piwars/%s" % name, wait_for_s=3)
            if address:
                self.channels[name] = address
            else:
                print("WARNING: No channel found for", name)

    def rendered_text(self, text, rect):
        surface = pygame.Surface(rect.size)
        surface.fill(self.text_fg)
        surface.fill(self.text_bg, surface.get_rect().inflate(-self.border_w, -self.border_w))
        rendered_text = self.font.render(text, True, self.text_fg, self.text_bg)
        surface.blit(rendered_text, (2 + self.border_w, 2 + self.border_w))
        return surface
    
    def update_from_news_distance(self, name, info):
        distance = nw0.sockets._unserialise(info)
        return self.rendered_text("%s: %3.2fcm" % (name_from_code(name), distance), self.rects[name])
    
    def update_from_news_line(self, name, info):
        light_or_dark = nw0.sockets._unserialise(info)
        return self.rendered_text("Line? %s" % light_or_dark, self.rects[name])
    
    def update_from_news_camera(self, name, info):
        with io.BytesIO(info) as buffer:
            return pygame.image.load(buffer, "camera.jpg").convert()
    
    def update_from_news_logs(self, name, info):
        levels_fg = {
            "debug" : pygame.Color(0x66, 0x66, 0x66, 0xff),
            "info" : pygame.Color(0xff, 0xff, 0xff, 0xff),
            "warning" : pygame.Color(0xff, 0xa5, 0x00, 0xff),
            "error" : pygame.Color(0xff, 0x00, 0x00, 0xff)
        }
        self.log_queue.append(nw0.sockets._unserialise(info))
        logs_rect = self.rects["logs"]
        surface = pygame.Surface(logs_rect.size)
        for n, (level, text) in enumerate(self.log_queue):
            line = "%s: %s" % (level.upper(), text)
            rendered = self.log_font.render(line, True, levels_fg[level], self.bg)
            surface.blit(rendered, (0, n * self.log_font_h))
        return surface
    
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
                screen.blit(surface, rect)
            updated_rects = [rect for _, rect in rects_to_update]
            pygame.display.update(updated_rects)
    
def main():
    monitor = Monitor()
    monitor.run()

if __name__ == '__main__':
    main(*sys.argv[1:])
