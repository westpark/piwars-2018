#
# From the Pygame site:
# https://www.pygame.org/docs/ref/joystick.html
#
import os, sys
import pygame
os.environ["SDL_VIDEODRIVER"] = "dummy" # Removes the need to have a GUI window
pygame.init()

 
#Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()

class TextPrint(object):
    
    def __init__(self):
        self._indent = 0
    
    def print(self, *args, **kwargs):
        return print(" " * self._indent, *args, **kwargs)
        
    def indent(self):
        self._indent += 4
    
    def unindent(self):
        self._indent -= 4

textPrint = TextPrint()

# -------- Main Program Loop -----------
            
 
# Get count of joysticks
joystick_count = pygame.joystick.get_count()

textPrint.print("Number of joysticks: {}".format(joystick_count) )
textPrint.indent()

# For each joystick:
for i in range(joystick_count):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()

    textPrint.print("Joystick {}".format(i) )
    textPrint.indent()

    # Get the name from the OS for the controller/joystick
    name = joystick.get_name()
    textPrint.print("Joystick name: {}".format(name) )
    
    # Usually axis run in pairs, up/down for one, and left/right for
    # the other.
    axes = joystick.get_numaxes()
    textPrint.print("Number of axes: {}".format(axes) )
    textPrint.indent()
    
    for i in range( axes ):
        axis = joystick.get_axis( i )
        textPrint.print("Axis {} value: {:>6.3f}".format(i, axis) )
    textPrint.unindent()
        
    buttons = joystick.get_numbuttons()
    textPrint.print("Number of buttons: {}".format(buttons) )
    textPrint.indent()

    for i in range( buttons ):
        button = joystick.get_button( i )
        textPrint.print("Button {:>2} value: {}".format(i,button) )
    textPrint.unindent()
        
    # Hat switch. All or nothing for direction, not like joysticks.
    # Value comes back in an array.
    hats = joystick.get_numhats()
    textPrint.print("Number of hats: {}".format(hats) )
    textPrint.indent()

    for i in range( hats ):
        hat = joystick.get_hat( i )
        textPrint.print("Hat {} value: {}".format(i, str(hat)) )
    textPrint.unindent()
    
    textPrint.unindent()

while True:
    for event in pygame.event.get(): # User did something
        if event.type == pygame.JOYAXISMOTION:
            if abs(event.value) < 0.01:
                continue
        print("Event:", event)
        #~ # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        #~ if event.type == pygame.JOYBUTTONDOWN:
            #~ print("Joystick button pressed:", event)
        #~ if event.type == pygame.JOYBUTTONUP:
            #~ print("Joystick button released", event)
        
#
# On PS3 controller:
#
# Left joystick
# - Axis 0 - horizontal
# - Axis 1 - vertical
# Right joystick
# - Axis 2 - horizontal
# - Axis 3 - vertical
# Left button set:
# - LRUD - 7,5,4,6
# - (also registers as axes)
# Right button set:
# - LRUD - 15,13,12,14
# - (also registers as axes)
# Top buttons:
# - Left - Upper 10, Lower 8
# - Right - Upper 11, Lower 9
# (joystick, also has accelerometer which registers as axes)
# [Select] - button 0
# [Start] - button 3
#
    
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()
