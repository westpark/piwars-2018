import os, sys
import io
import time

import PIL
import pygame
from pygame.locals import *
pygame.init()

import networkzero as nw0

CAMERA_RECT = pygame.Rect(0, 0, 320, 240)
DISTANCE_A_RECT = pygame.Rect(0, 250, 320, 30)
DISTANCE_B_RECT = pygame.Rect(0, 290, 320, 30)
LINE_RECT = pygame.Rect(0, 330, 320, 30)

FONT = pygame.font.Font("piwars.ttf", 18) # copied from arial.ttf
TEXT_FOREGROUND = pygame.Color(0xff, 0xff, 0xff, 0xff)
TEXT_BACKGROUND = pygame.Color(0x00, 0x00, 0xff, 0xff)

def update_from_camera(news, rects_to_update):
    topic, info = nw0.wait_for_news_from(news, wait_for_s=0)
    if topic is None: 
        return
    
    t, image_data = info
    image_bytes = nw0.string_to_bytes(image_data)
    with io.BytesIO(image_bytes) as buffer:
        image_surface = pygame.image.load(buffer, "camera.jpg")
        rects_to_update.append((image_surface, CAMERA_RECT.topleft))

def update_from_distance_a(news, rects_to_update):
    topic, info = nw0.wait_for_news_from(news, wait_for_s=0)
    if topic is None:
        return
    
    t, distance = info
    rendered = FONT.render("Distance A: %3.2fcm" % distance, True, TEXT_FOREGROUND, TEXT_BACKGROUND)
    rects_to_update.append((rendered, DISTANCE_A_RECT.topleft))
    
def update_from_distance_b(news, rects_to_update):
    topic, info = nw0.wait_for_news_from(news, wait_for_s=0)
    if topic is None:
        return
    
    t, distance = info
    rendered = FONT.render("Distance B: %3.2fcm" % distance, True, TEXT_FOREGROUND, TEXT_BACKGROUND)
    rects_to_update.append((rendered, DISTANCE_B_RECT.topleft))

def update_from_line(news, rects_to_update):
    topic, info = nw0.wait_for_news_from(news, wait_for_s=0)
    if topic is None:
        return
    
    t, light_or_dark = info
    rendered = FONT.render("Line? %s" % light_or_dark, True, TEXT_FOREGROUND, TEXT_BACKGROUND)
    rects_to_update.append((rendered, LINE_RECT.topleft))

def main():
    print("About to discover...")
    camera_news = nw0.discover("piwars/camera")
    distance_a_news = nw0.discover("piwars/distance-a")
    distance_b_news = nw0.discover("piwars/distance-b")
    line_news = nw0.discover("piwars/line")

    size = width, height = 640, 480
    black = 0, 0, 0

    screen = pygame.display.set_mode(size)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
        
        rects_to_update = []
        update_from_camera(camera_news, rects_to_update)
        update_from_distance_a(distance_a_news, rects_to_update)
        update_from_distance_b(distance_b_news, rects_to_update)
        update_from_line(line_news, rects_to_update)

        for surface, rect in rects_to_update:
            screen.blit(surface, rect)
        pygame.display.flip()

if __name__ == '__main__':
    main(*sys.argv[1:])
