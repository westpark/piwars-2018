#!/usr/bin/env python
# coding: utf-8
# Load library functions we want
import time
import os
import sys
# import ThunderBorg
import io
import threading
import picamera
import picamera.array
import cv2
import numpy

# Camera settings
imageWidth = 320  # Camera image width
imageHeight = 240  # Camera image height
frameRate = 3  # Camera image capture frame rate

finished = threading.Event()
buffer_empty = threading.Event()
buffer_filled = threading.Event()

class Robot(object):
    
    def __init__(self):
        pass
    
    def reset(self):
        pass
    
    def drive(self, left_speed, right_speed):
        pass

class PiborgRobot(Robot):
    
    def __init__(self):
        self.tb = ThunderBorg.ThunderBorg()
        self.tb.Init()
        if not TB.foundChip:
            raise RuntimeError("ThunderBorg not found")
        self.tb.SetCommsFailsafe(False)
        
        # Auto drive settings
        self.autoMaxPower = 1.0                      # Maximum output in automatic mode
        self.autoMinPower = 0.2                      # Minimum output in automatic mode
        self.autoFullSpeedArea = 300                 # Target size at which we use the maximum allowed output
        
        self.voltageIn = 12.0                        # Total battery voltage to the ThunderBorg
        self.voltageOut = 12.0 * 0.95                # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power
        # Setup the power limits
        if self.voltageOut > self.voltageIn:
            self.maxPower = 1.0
        else:
            self.maxPower = self.voltageOut / float(self.voltageIn)
        self.autoMaxPower *= self.maxPower
    
    def reset(self):
        self.tb.MotorsOff()
    
    def drive(self, left_speed, right_speed):
        self.tb.SetMotor1(left_speed)
        self.tb.SetMotor2(right_speed)


# Image processing function
def ProcessImage(self, image, colour):
    print("Processing image for", colour)
    time.sleep(random.random())
    return 
    
    # View the original image seen by the camera.
    if debug:
        cv2.imshow('original', image)
        cv2.waitKey(0)

    # Blur the image
    image = cv2.medianBlur(image, 5)
    if debug:
        cv2.imshow('blur', image)
        cv2.waitKey(0)

    # Convert the image from 'BGR' to HSV colour space
    image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    if debug:
        cv2.imshow('cvtColour', image)
        cv2.waitKey(0)

    # We want to extract the 'Hue', or colour, from the image. The 'inRange'
    # method will extract the colour we are interested in (between 0 and 180)
    # In testing, the Hue value for red is between 95 and 125
    # Green is between 50 and 75
    # Blue is between 20 and 35
    # Yellow is... to be found!
    if colour == "red":
        imrange = cv2.inRange(image, numpy.array((95, 127, 64)), numpy.array((125, 255, 255)))
    elif colour == "green":
        imrange = cv2.inRange(image, numpy.array((50, 127, 64)), numpy.array((75, 255, 255)))
    elif colour == 'blue':
        imrange = cv2.inRange(image, numpy.array((20, 64, 64)), numpy.array((35, 255, 255)))

    # I used the following code to find the approximate 'hue' of the ball in
    # front of the camera
    #        for crange in range(0,170,10):
    #            imrange = cv2.inRange(image, numpy.array((crange, 64, 64)), numpy.array((crange+10, 255, 255)))
    #            print(crange)
    #            cv2.imshow('range',imrange)
    #            cv2.waitKey(0)
    
    # View the filtered image found by 'imrange'
    if debug:
        cv2.imshow('imrange', imrange)
        cv2.waitKey(0)

    # Find the contours
    contourimage, contours, hierarchy = cv2.findContours(imrange, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if debug:
        cv2.imshow('contour', contourimage)
        cv2.waitKey(0)

    # Go through each contour
    foundArea = -1
    foundX = -1
    foundY = -1
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cx = x + (w / 2)
        cy = y + (h / 2)
        area = w * h
        if foundArea < area:
            foundArea = area
            foundX = cx
            foundY = cy
    if foundArea > 0:
        ball = [foundX, foundY, foundArea]
    else:
        ball = None
    # Set drives or report ball status
    self.SetSpeedFromBall(ball)

# Set the motor speed from the ball position
def SetSpeedFromBall(self, ball):
    global TB
    driveLeft = 0.0
    driveRight = 0.0
    if ball:
        x = ball[0]
        area = ball[2]
        if area < autoMinArea:
            print('Too small / far')
        elif area > autoMaxArea:
            print('Close enough')
        else:
            if area < autoFullSpeedArea:
                speed = 1.0
            else:
                speed = 1.0 / (area / autoFullSpeedArea)
            speed *= autoMaxPower - autoMinPower
            speed += autoMinPower
            direction = (x - imageCentreX) / imageCentreX
            if direction < 0.0:
                # Turn right
                print('Turn Right')
                driveLeft = speed
                driveRight = speed * (1.0 + direction)
            else:
                # Turn left
                print('Turn Left')
                driveLeft = speed * (1.0 - direction)
                driveRight = speed
            print('%.2f, %.2f' % (driveLeft, driveRight))
    else:
        print('No ball')



# Image stream processing thread
class StreamProcessor(threading.Thread):
    def __init__(self, stream, process_image):
        super(StreamProcessor, self).__init__()
        self.stream = stream
        self.process_image = process_image
        self.start()

    def run(self):
        while not finished.is_set():
            buffer_filled.wait()            
            buffer_filled.clear()
            try:
                self.stream.seek(0)
                self.process_image(self.stream.array, colour)
            finally:
                # Reset the stream and event
                self.stream.seek(0)
                self.stream.truncate()
                buffer_empty.set()
    
# Image capture thread
class ImageCapture(threading.Thread):
    def __init__(self, camera, stream):
        super(ImageCapture, self).__init__()
        self.camera = camera
        self.buffer = stream
        self.start()

    def run(self):
        print('Start the stream using the video port')
        self.camera.capture_sequence(self.writeable_buffer(), format='bgr', use_video_port=True)
        print('Terminating camera processing...')
        finished.set()
        print('Processing terminated.')

    def writeable_buffer(self):
        while not finished.is_set():
            buffer_empty.wait()
            yield self.buffer
            buffer_filled.set()

def main():
    # Startup sequence
    print('Setup camera')
    robot = Robot()
    camera = picamera.PiCamera()
    camera.resolution = (imageWidth, imageHeight)
    camera.framerate = frameRate
    imageCentreX = imageWidth / 2.0
    imageCentreY = imageHeight / 2.0

    stream = picamera.array.PiRGBArray(camera)

    print('Setup the stream processing thread')
    processor = StreamProcessor(stream, ProcessImage)

    print('Wait ...')
    time.sleep(2)
    captureThread = ImageCapture(camera, stream)

    try:
        print('Press CTRL+C to quit')
        ##    TB.MotorsOff()
        ##    TB.SetLedShowBattery(True)
        # Loop indefinitely until we are no longer running
        while running:
            # Wait for the interval period
            # You could have the code do other work in here 🙂
            time.sleep(1.0)
            # Disable all drives
    except KeyboardInterrupt:
        # CTRL+C exit, disable all drives
        print('\nUser shutdown')
        break
    finally:
        robot.reset()
        captureThread.join()
        processor.join()

if __name__ == '__main__':
    main(*sys.argv[1:])
