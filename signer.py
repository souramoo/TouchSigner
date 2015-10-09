#!/usr/bin/env python2

# Trying to make it easier to insert handwritten signatures in a digital age.
# Cause I don't have a scanner.
# by moosd 2015

import sys, pygame
import operator
from itertools import islice
import tkFileDialog
import Tkinter as tk

# OPTIONS TO CHANGE
line_thickness = 6
antialiasing = False
window_size = (640, 480)
resize_on_save = True

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

def scaler(p, scalefac):
    return ((int(float(p[0] - minwidth) / (scalefac) * window_size[0])), (int(float(p[1] - minheight) / (scalefac) * window_size[1])))

def reinit_vars():
    global points, minwidth, minheight, maxwidth, maxheight
    points = []
    maxwidth = 1
    maxheight = 1
    minwidth = 0
    minheight = 0

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
            sys.exit()
        elif event.type == pygame.KEYUP:
            kmap = pygame.key.get_pressed()
            if event.key == pygame.K_q:
                sys.exit()
            if event.key == pygame.K_ESCAPE:
                del points
                reinit_vars()
                stage = 0
            if event.key == pygame.K_F4 and (kmap[pygame.K_LALT] or kmap[pygame.K_RALT]):
                sys.exit()
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
                tosave = pygame.Surface((maxwidth-minwidth, maxheight-minheight), pygame.SRCALPHA, 32)
                tosave = tosave.convert_alpha()
                for pos1, pos2 in window(points, 2):
                    if resize_on_save:
                        scalefac = max([maxwidth - minwidth, maxheight - minheight])
                        p1 = scaler(pos1, scalefac)
                        p2 = scaler(pos2, scalefac)
                    else:
                        p1 = ((pos1[0] - minwidth), (pos1[1] - minheight))
                        p2 = ((pos2[0] - minwidth), (pos2[1] - minheight))
                    if antialiasing:
                        pygame.draw.aaline(tosave, (0,0,0), p1, p2)
                    else:
                        pygame.draw.line(tosave, (0,0,0), p1, p2, line_thickness)
                pygame.image.save(tosave, f)
                del tosave
                print "Saved!"
                sys.exit()
        elif event.type == pygame.MOUSEMOTION:
            points.append(pygame.mouse.get_rel())
            if len(points) > 1:
                stage = 1
                points[-1] = tuple(map(operator.add, points[-2], points[-1]))
            maxheight = max([x[1] for x in points])
            maxwidth = max([x[0] for x in points])
            minheight = min([x[1] for x in points])
            minwidth = min([x[0] for x in points])
            if maxwidth == 0: maxwidth = 1
            if maxheight == 0: maxheight = 1

    if stage == 0:
        screen.blit(background, (0,0))
    elif stage == 1:
        screen.fill(blank)
        for pos1, pos2 in window(points, 2):
            scalefac = max([maxwidth - minwidth, maxheight - minheight])
            p1 = scaler(pos1, scalefac)
            p2 = scaler(pos2, scalefac)
            if antialiasing:
                pygame.draw.aaline(screen, (0,0,0), p1, p2)
            else:
                pygame.draw.line(screen, (0,0,0), p1, p2, line_thickness)
    pygame.display.flip()

