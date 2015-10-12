#!/usr/bin/env python2

# Trying to make it easier to insert handwritten signatures in a digital age.
# Cause I don't have a scanner.
# by moosd 2015

# This version reads raw touchpad events rather than using mouse relative movements
# Linux specific!

import sys, pygame, os
import operator
from itertools import islice
import tkFileDialog
import Tkinter as tk
import struct
import time
import threading

# OPTIONS TO CHANGE
line_thickness = 6
antialiasing = False
window_size = (640, 480)
resize_on_save = False
events_location = "/dev/input/by-path/platform-i8042-serio-1-event-mouse"
ww = 4500
hh = 3500

# REST OF CODE FOLLOWS:
def draw_instructions(instructions):
    font = pygame.font.Font(None, 24)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    n = 0
    for t in instructions:
        text = font.render(t, 1, (10, 10, 10))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        n += 24
        background.blit(text, (textpos.left, n))
    return background

def window(seq, n=2):
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result

def scaler(p):
    return ((int(float(p[0]) / (ww) * window_size[0])), (int(float(p[1]) / (hh) * window_size[1])))

def reinit_vars():
    global points
    points = []

timeout = 0
touch = 0

def listener():
    global timeout, points, stage, events_location
    FORMAT = 'llHHI'
    EVENT_SIZE = struct.calcsize(FORMAT)
    in_file = open(events_location, "rb")
    event = in_file.read(EVENT_SIZE)
    x = 0
    y = 0
    while event:
        (tv_sec, tv_usec, type, code, value) = struct.unpack(FORMAT, event)
        if type != 0 or code != 0 or value != 0:
            if code == 1:
                if not timeout > time.time():
                    touch = 1
                    del points
                    reinit_vars()
                    stage = 1
                timeout = time.time() + 0.2
            if code == 53:
                x = value - 1210
            if code == 54:
                y = value - 1250
                points.append([x,y])
        event = in_file.read(EVENT_SIZE)
    in_file.close()

lthread = threading.Thread(target=listener)
lthread.start()

pygame.init()

screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("TouchSigner")

pygame.mouse.set_visible(0)
pygame.event.set_grab(1)

instructions = ["Use your touchpad to draw a signature and hit enter when done.", "Esc = reset", "q = quit"]
stage = 0

background = draw_instructions(instructions)
blank = 255, 255, 255

reinit_vars()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            os._exit(0)
        elif event.type == pygame.KEYUP:
            kmap = pygame.key.get_pressed()
            if event.key == pygame.K_q:
                os._exit(0)
            if event.key == pygame.K_ESCAPE:
                del points
                reinit_vars()
                stage = 0
            if event.key == pygame.K_F4 and (kmap[pygame.K_LALT] or kmap[pygame.K_RALT]):
                os._exit(0)
            if event.key == pygame.K_RETURN:
                pygame.event.set_grab(0)
                pygame.mouse.set_visible(1)
                root = tk.Tk()
                root.withdraw()
                f = tkFileDialog.asksaveasfilename(defaultextension=".png")
                root.destroy()
                if f == ():
                   pygame.mouse.set_visible(0)
                   pygame.event.set_grab(1)
                   continue
                if resize_on_save:
                    tosave = pygame.Surface(window_size, pygame.SRCALPHA, 32)
                else:
                    tosave = pygame.Surface((ww, hh), pygame.SRCALPHA, 32)
                tosave = tosave.convert_alpha()
                for pos1, pos2 in window(points, 2):
                    if resize_on_save:
                        p1 = scaler(pos1)
                        p2 = scaler(pos2)
                    else:
                        p1 = ((pos1[0]), (pos1[1]))
                        p2 = ((pos2[0]), (pos2[1]))
                    if antialiasing:
                        pygame.draw.aaline(tosave, (0,0,0), p1, p2)
                    else:
                        pygame.draw.line(tosave, (0,0,0), p1, p2, line_thickness)
                pygame.image.save(tosave, f)
                del tosave
                print "Saved!"
                os._exit(0)

    if stage == 0:
        screen.blit(background, (0,0))
    elif stage == 1:
        screen.fill(blank)
        for pos1, pos2 in window(points, 2):
            p1 = scaler(pos1)
            p2 = scaler(pos2)
            if antialiasing:
                pygame.draw.aaline(screen, (0,0,0), p1, p2)
            else:
                pygame.draw.line(screen, (0,0,0), p1, p2, line_thickness)
    pygame.display.flip()
