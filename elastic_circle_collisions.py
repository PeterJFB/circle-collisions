# Created 09.09.2019
import pygame as pg
import numpy as np
from numpy.linalg import norm as Abs
import time
from random import randint as r
import math as m

pg.init()

# Circle Properties
circle_r_min, circle_r_max = 20, 50
circle_v_min, circle_v_max = 25, 50
circle_height, circle_density = 30, 0.001
circle_quantity = 10
seizure = True

# Window
win_width = 1000
win_height = 1000
win_width_min = 200
win_height_min = 200
win = pg.display.set_mode([win_width, win_height], pg.RESIZABLE)

# Time
time_0 = time.time()
time_d = time.time() - time_0

# Mouse
mouse_pos = np.array(pg.mouse.get_pos())
mouse_f_abs = 100000

# Aesthetic
font = pg.font.SysFont("calibri", 25)

# Circle
class Circle(object):
    def __init__(self, pos, rad, v):
        # Physical Properties
        self.pos = np.array(pos)
        self.r = rad
        self.v = np.array(v)
        self.m = np.pi * rad**2 * circle_height * circle_density

        # Logic
        self.prev_collision = None

        # Aesthetics
        self.color = (r(10, 255), r(10, 255), r(10, 255)) if seizure else (255, 0, 0)

    def circle_collide(self, circle, circle_v):
        # Physics
        c = circle.pos - self.pos
        v_c = (c[0]*self.v[0]+c[1]*self.v[1])/(c[0]**2 + c[1]**2) * c # Velocity component in direction of collision
        v_t = self.v - v_c # Velocity component tangent to direction of collision

        circle_c = self.pos - circle.pos
        circle_v_c = (circle_c[0]*circle_v[0]+circle_c[1]*circle_v[1])/(circle_c[0]**2 + circle_c[1]**2) * circle_c

        # Calculate new velocity in direction of collision while velocity tangent is preserved:
        v_c_new = ((self.m - circle.m)/(self.m + circle.m)) * v_c + (2 * circle.m / (self.m + circle.m)) * circle_v_c
        self.v = v_c_new + v_t

        # Logic
        self.color = (r(10, 255), r(10, 255), r(10, 255)) if seizure else (255, 0, 0)
        self.prev_collision = circle

    def wall_collide(self):
        # Physics
        if 0 > self.pos[0] or self.pos[0] > win_width:
            self.pos[0] = 0 if 0 > self.pos[0] else win_width
            self.v[0] = -self.v[0]
            # Logic
            self.prev_collision = None

        if 0 > self.pos[1] or self.pos[1] > win_height:
            self.pos[1] = 0 if 0 > self.pos[1] else win_height
            self.v[1] = -self.v[1]
            # Logic
            self.prev_collision = None

    def vortex(self):
        # Physics
        mouse_dir = mouse_pos - self.pos
        mouse_f = mouse_dir * (mouse_f_abs / Abs(mouse_dir))
        mouse_a = mouse_f / self.m
        self.v = self.v + mouse_a * time_d
        # Logic
        self.prev_collision = None

    def move(self):
        self.pos = self.pos + self.v * time_d

    def draw(self):
        draw_pos = np.around(self.pos).astype(int)
        pg.draw.circle(win, self.color, draw_pos, self.r)

def rPos():
    return r(1, win_width), r(1, win_height)
def rRad():
    return r(circle_r_min, circle_r_max)
def rVel():
    return r(circle_v_min, circle_v_max), r(circle_v_min, circle_v_max)


# Setup
circles = [Circle(rPos(), rRad(), rVel()) for i in range(circle_quantity)]
# Main
run = True
while run:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        # Keyboard
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_r:
                circles = [Circle(rPos(), rRad(), rVel()) for i in range(circle_quantity)]
            elif event.key == pg.K_UP:
                circle_quantity += 1
            elif event.key == pg.K_DOWN:
                circle_quantity -= 1
        # Mouse
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 2:
                mouse_f_abs = -mouse_f_abs
            elif event.button == 4:
                mouse_f_abs += 10000
            elif event.button == 5:
                mouse_f_abs = round(mouse_f_abs - 10000)

        # Window
        elif event.type == pg.VIDEORESIZE:
            win_width, win_height = event.size
            if win_width < win_width_min:
                win_width = win_width_min
            if win_height < win_height_min:
                win_height = win_height_min
            win = pg.display.set_mode([win_width, win_height], pg.RESIZABLE)
            time_d, time_0 = time.time() - time_0, time.time()

    # Time
    time_d, time_0 = time.time() - time_0, time.time()

    # Action
    for i, circle_1 in enumerate(circles[:-1]):
        for circle_2 in circles[i+1:]:
            if Abs(circle_2.pos - circle_1.pos) <= circle_1.r + circle_2.r:
                if circle_1.prev_collision != circle_2 or circle_2.prev_collision != circle_1:
                    circle_v_1 = circle_1.v
                    circle_1.circle_collide(circle_2, circle_2.v)
                    circle_2.circle_collide(circle_1, circle_v_1)

                circle_dist = (circle_2.pos - circle_1.pos) * (circle_1.r + circle_2.r) / Abs(circle_2.pos - circle_1.pos)
                circle_1.pos = circle_1.pos - (circle_dist - (circle_2.pos - circle_1.pos))/2
                circle_2.pos = circle_2.pos + (circle_dist - (circle_2.pos - circle_1.pos))/2

    for circle in circles:
        circle.wall_collide()

    if pg.mouse.get_pressed()[0]:
        mouse_pos = np.array(pg.mouse.get_pos())
        for circle in circles:
            circle.vortex()

    for circle in circles:
        circle.move()

    # Drawing
    win.fill((0, 0, 0))

    mouse_text = font.render("mouse_force: " + str(mouse_f_abs / 1000) + " kN", False, (255, 255, 255))
    win.blit(mouse_text, (0, 0))
    info_text = font.render("A_UP and A_DOWN: Change number of circles: " + str(circle_quantity), False, (255, 255, 255))
    win.blit(info_text, (0, win_height - font.size("a")[1] * 2))
    info_text = font.render("R: Restart", False, (255, 255, 255))
    win.blit(info_text, (0, win_height - font.size("a")[1]))

    for circle in circles:
        circle.draw()
    pg.display.update()

pg.quit()
