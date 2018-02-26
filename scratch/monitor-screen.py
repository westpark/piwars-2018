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
    return " ".join(w.title() for w in code.split("/"))

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

    channel_names = ["camera", "distance/a", "distance/b", "line", "logs"]
    rects = {}
    rects["camera"] = camera_rect = pygame.Rect(0, 0, width / 3, height / 2)
    rects["distance/a"] = distance_a_rect = pygame.Rect(camera_rect.left, camera_rect.top + camera_rect.height + border_w, camera_rect.width, text_h)
    rects["distance/b"] = distance_b_rect = pygame.Rect(distance_a_rect.left, distance_a_rect.top + distance_a_rect.height + border_w, distance_a_rect.width, text_h)
    rects["line"] = line_rect = pygame.Rect(distance_b_rect.left, distance_b_rect.top + distance_b_rect.height + border_w, distance_b_rect.width, text_h)
    rects["logs"] = logs_rect = pygame.Rect(camera_rect.left + camera_rect.width + (3 * border_w), camera_rect.top, width - (camera_rect.left + camera_rect.width + (3 * border_w)), height)
    levels_fg = {
        "debug" : pygame.Color(0x66, 0x66, 0x66, 0xff),
        "info" : pygame.Color(0xff, 0xff, 0xff, 0xff),
        "warning" : pygame.Color(0xff, 0xa5, 0x00, 0xff),
        "error" : pygame.Color(0xff, 0x00, 0x00, 0xff)
    }
    
    def __init__(self):
        self.log_queue = collections.deque(maxlen=self.height // self.log_font_h)
        self.channels = {}
        for name in self.channel_names:
            address = nw0.discover("piwars/%s" % name, wait_for_s=3)
            if address:
                self.channels[name] = address
            else:
                print("WARNING: No channel found for", name)
        
        self.channel_locks = {}
        for name in self.channel_names:
            self.channel_locks[name] = threading.Lock()
        self.channel_values = {}

    def get_channel_value(self, name, default=None):
        with self.channel_locks[name]:
            return self.channel_values.get(name, default)
    
    def set_channel_value(self, name, value):
        with self.channel_locks[name]:
            self.channel_values[name] = value
    
    def rendered_text(self, text, rect):
        surface = pygame.Surface(rect.size)
        surface.fill(self.text_fg)
        surface.fill(self.text_bg, surface.get_rect().inflate(-self.border_w, -self.border_w))
        rendered_text = self.font.render(text, True, self.text_fg, self.text_bg)
        surface.blit(rendered_text, (2 + self.border_w, 2 + self.border_w))
        return surface
    
    def render_from_distance(self, name):
        value = self.get_channel_value(name)
        if value:
            return self.rendered_text("%s: %3.2fcm" % (name_from_code(name), value), self.rects[name])
    
    def render_from_line(self, name):
        value = self.get_channel_value(name)
        if value:
            return self.rendered_text("Line? %s" % value, self.rects[name])
    
    def render_from_camera(self, name):
        value = self.get_channel_value(name)
        if value:
            with io.BytesIO(value) as buffer:
                return pygame.image.load(buffer, "camera.jpg").convert()
    
    def render_from_logs(self, name):
        queue = self.get_channel_value(name)
        if queue:
            logs_rect = self.rects["logs"]
            surface = pygame.Surface(logs_rect.size)
            for n, (level, text) in enumerate(queue):
                rendered = self.log_font.render(text, True, self.levels_fg[level], self.bg)
                surface.blit(rendered, (0, n * self.log_font_h))
            return surface
    
    def render_from(self):
        prefix = "render_from_"
        for name in self.channels:
            base, _, suffix = name.partition("/")
            function_name = prefix + base
            function = getattr(self, function_name)
            surface = function(name)
            if surface:
                yield surface, self.rects[name]
    
    def update_from_distance(self, name, info):
        self.set_channel_value(name, nw0.sockets._unserialise(info))
    
    def update_from_line(self, name, info):
        self.set_channel_value(name, nw0.sockets._unserialise(info))
    
    def update_from_camera(self, name, info):
        self.set_channel_value(name, info)
    
    def update_from_logs(self, name, info):
        with self.channel_locks[name]:
            queue = self.channel_values.setdefault(name, collections.deque(maxlen=self.height // self.log_font_h))
            queue.append(nw0.sockets._unserialise(info))

    def update_from(self, name, topic, info):
        function = getattr(self, "update_from_%s" % topic.lower())
        function(name, info)
    
    def run(self):
        screen = pygame.display.set_mode(self.size)
        clock = pygame.time.Clock()
        
        updated_rects = []
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()
            
            for name, channel in self.channels.items():
                topic, info = nw0.wait_for_news_from(channel, wait_for_s=0, is_raw=True)
                if topic is None:
                    continue
                self.update_from(name, topic, info)

            clock.tick(30)
            updated_rects.clear()
            for surface, rect in self.render_from():
                screen.blit(surface, rect)
                updated_rects.append(rect)
            pygame.display.update(updated_rects)

if __name__ == '__main__':
    Monitor().run()
