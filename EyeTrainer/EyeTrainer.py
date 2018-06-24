#!/usr/bin/python

#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys, os
import time
import pygame
import pygame.mixer
import math
from math import sqrt
from random import choice


for font in pygame.font.get_fonts():
    print font

def signum(int):#{{{
    if(int < 0): return -1;
    elif(int > 0): return 1;
    else: return int;
#}}}
def time2str(timeval):#{{{
    ms = timeval % 1000
    sec = (timeval / 1000) % 60
    min = timeval / (1000 * 60)
    return '%02d:%02d:%03d' % (min, sec, ms)
#}}}

def rand_text(numchars):
    
    #chars = string.letters + string.digits
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    str = ''
    for i in range(numchars):
        str = str + choice(chars)
    return str


#
# Main
#

pygame.init();

# some constants
size = width, height = 800, 600
color_bg = 30, 30, 30
color_font = 230, 230, 240
color_bar_bg = 0, 30, 80
color_bar_fg = 0, 130, 200
color_bar_frame = 120, 120, 120
color_marker_normal = 255, 0, 34
color_marker_active = 100, 200, 50
linespacing = 30
rect_bar = pygame.Rect(10, height - 40, width - 20, 20)

# globals
pygame.display.set_caption('EyeTrainer')
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
clock = pygame.time.Clock()
verdana = pygame.font.match_font('Verdana')
font = pygame.font.Font(verdana, 13) # arialblack dejavusansmono
#font = pygame.font.SysFont(verdana, 24) # arialblack dejavusansmono

# main loop

block_start = time.time()
block_spaces = 3
block_chars = 2
block_duration = 200
block_text = str = rand_text(block_chars) + ' '*block_spaces + 'X' + ' '*block_spaces + rand_text(block_chars)

while 1:
    screen.fill(color_bg)

    mods = pygame.key.get_mods()
    alt_pressed = (mods & pygame.KMOD_LALT) == pygame.KMOD_LALT

    # event handling {{{
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            key = event.dict['key']
            scancode = event.dict['scancode']
            
            if key == pygame.K_SPACE:
                block_start = time.time()
                block_text = str = rand_text(block_chars) + ' '*block_spaces + 'X' + ' '*block_spaces + rand_text(block_chars)
            elif key == pygame.K_RIGHT:
                block_spaces += 1
            elif key == pygame.K_LEFT:
                block_spaces -= 1
            elif key == pygame.K_UP:
                block_duration += 50
            elif key == pygame.K_DOWN:
                block_duration -= 50
            elif key == pygame.K_KP_PLUS:
                block_chars += 1
            elif key == pygame.K_KP_MINUS:
                block_chars -= 1
            
        elif event.type == pygame.KEYUP:
            key = event.dict['key']
            scancode = event.dict['scancode']
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pass
        elif event.type == pygame.VIDEORESIZE:
            size = width, height = event.size
            screen = pygame.display.set_mode(size, pygame.RESIZABLE)

    new_time = time.time()
    
    # print block
    if new_time*1000 < block_start*1000 + block_duration:
        text = font.render(block_text, True, color_font, color_bg)
        textpos = text.get_rect(centerx = width / 2, centery = height / 2)
        screen.blit(text, textpos)
    else:
        text = font.render('X', True, color_font, color_bg)
        textpos = text.get_rect(centerx = width / 2, centery = height / 2)
        screen.blit(text, textpos)

    # fps
    text = font.render("fps: %6.3f    chars = %d    spaces = %d    duration = %d" % (clock.get_fps(), block_chars, block_spaces, block_duration), True, color_font, color_bg)
    textpos = text.get_rect(centerx = width / 2, centery = 20)
    screen.blit(text, textpos)

    clock.tick(100)
    pygame.display.flip()














"""
ballrect = ballrect.move(speed)
if ballrect.left < 0 or ballrect.right > width:
    speed[0] = -speed[0]
if ballrect.top < 0 or ballrect.bottom > height:
    speed[1] = -speed[1]
screen.blit(ball, ballrect)
"""


# ball = pygame.image.load("ball.bmp")
# ballrect = ball.get_rect()

"""
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init();
pygame.mixer.music.load('/home/fabian/Desktop/Black Crowes - Remedy.mp3');
pygame.mixer.music.play();

soundfile = pygame.mixer.Sound('/home/fabian/Desktop/Black Crowes - Remedy.mp3')
length = soundfile.get_length()
channels = soundfile.get_num_channels()
pygame.sndarray.use_arraytype('numeric')
array = pygame.sndarray.array(soundfile)
print length
print array
print type(array)
print array.shape
"""


"""
self.player = gst.Pipeline("player")
source = gst.element_factory_make("filesrc", "file-source")
decoder = gst.element_factory_make("mad", "mp3-decoder")
conv1 = gst.element_factory_make("audioconvert", "converter1")
resam1 = gst.element_factory_make("audioresample", "resample1")
scaletempo = gst.element_factory_make("scaletempo", "scaletempo")
conv2 = gst.element_factory_make("audioconvert", "converter2")
resam2 = gst.element_factory_make("audioresample", "resample2")
sink = gst.element_factory_make("alsasink", "alsa-output")

self.player.add(source, decoder, conv1, resam1, scaletempo, conv2, resam2, sink)
gst.element_link_many(source, decoder, conv1, resam1, scaletempo, conv2, resam2, sink)

bus = self.player.get_bus()
bus.add_signal_watch()
bus.connect("message", self.on_message)

self.player.get_by_name("file-source").set_property("location", '/home/fabian/Desktop/Black Crowes - Remedy.mp3')
self.player.set_state(gst.STATE_PLAYING)

pos_int = self.player.query_position(self.time_format, None)[0]
seek_ns = pos_int + (10 * 1000000000)
print seek_ns
#scaletempo.seek(0.8, self.time_format, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, 0, gst.SEEK_TYPE_SET, seek_ns)
self.player.seek(0.8, self.time_format, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, 0, gst.SEEK_TYPE_SET, seek_ns)
#self.player.seek(0.8, self.time_format, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, seek_ns, gst.SEEK_TYPE_NONE, gst.CLOCK_TIME_NONE)
#self.player.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, seek_ns)

#self.player.seek(0.8, self.time_format, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_NONE, gst.CLOCK_TIME_NONE, gst.SEEK_TYPE_NONE, gst.CLOCK_TIME_NONE)
"""

#error = 0
#plugin = gst.plugin_load_file("/home/fabian/coding/python/soundplayer/gst-scaletempo/src/libgstscaletempoplugin.la")
#print error
#plugin.load()

#pos_int = self.playbin.query_position(self.time_format, None)[0]
#seek_ns = pos_int + (10 * 1000000000)
#print seek_ns
#self.playbin.seek(0.8, self.time_format, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, 0, gst.SEEK_TYPE_SET, seek_ns)

