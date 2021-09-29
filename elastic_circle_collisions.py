# Created 09.09.2019
import pygame as pg
import numpy as np
from numpy.linalg import norm as Abs
import time
from random import uniform as r
from random import randint as rint
from scipy.constants import g

pg.init()

# Circle Properties
circle_r_min, circle_r_max = 0.025, 0.06  # m, m
circle_v_min, circle_v_max = 0.01, 0.2  # m/s, m/s
circle_height, circle_density = 0.5, 480  # m, kg/m^3
px_per_m = 750  # Pixel per meter
circle_quantity = 10
seizure = False
tracking = False

# Window
win_width, win_height = 750, 750
win_width_temp, win_height_temp = win_width, win_height
win_width_min, win_height_min = 200, 200
info = pg.display.Info()
win = pg.display.set_mode([win_width, win_height], pg.RESIZABLE)
full = False  # Fullscreen

# Time
time_0 = time.time()
time_d = time.time() - time_0

# Mouse
mouse_pos = np.array(pg.mouse.get_pos())
mouse_f_abs = 1

# Gravity
g_toggle = False
g_amp = 1

# Aesthetic
hud = True
font = pg.font.SysFont('trebuchetms', 25)

# Tracker
class Tracker(object):
    def __init__(self, pos, color):
        self.pos = list(pos)
        self.color = color
        self.time_kill = time.time() + 3

    def update(self):
        if time_new < self.time_kill:
            color = self.color if seizure else (255, 0, 0)
            win.set_at(self.pos, color)
        else:
            trackers.remove(self)

# Circle
class Circle(object):
    def __init__(self, pos, rad, v):
        # Physical Properties
        self.pos = np.array(pos)
        self.r = rad * px_per_m
        self.v = np.array(v) * px_per_m
        self.m = np.pi * rad**2 * circle_height * circle_density

        # Logic
        self.prev_collision = None

        # Aesthetics
        self.color = (rint(10, 255), rint(10, 255), rint(10, 255)) if seizure else (255, 0, 0)

    def circle_collide(self, circle, circle_v):
        # Physics
        c = circle.pos - self.pos
        v_c = (c[0]*self.v[0]+c[1]*self.v[1]) / (c[0]**2 + c[1]**2) * c  # Velocity component in direction of collision
        v_t = self.v - v_c  # Velocity component tangent to direction of collision

        circle_c = self.pos - circle.pos
        circle_v_c = (circle_c[0]*circle_v[0]+circle_c[1]*circle_v[1])/(circle_c[0]**2 + circle_c[1]**2) * circle_c

        # Calculate new velocity in direction of collision while tangent velocity is preserved:
        v_c_new = ((self.m - circle.m)/(self.m + circle.m)) * v_c + (2 * circle.m / (self.m + circle.m)) * circle_v_c
        self.v = v_c_new + v_t

        # Logic
        self.color = (rint(10, 255), rint(10, 255), rint(10, 255)) if seizure else (255, 0, 0)
        self.prev_collision = circle

    def wall_collide(self):
        # Physics
        if self.r > self.pos[0] or self.pos[0] > win_width - self.r:
            self.pos[0] = self.r if self.r > self.pos[0] else win_width - self.r
            self.v[0] = -self.v[0]
            # Logic
            self.prev_collision = None

        if self.r > self.pos[1] or self.pos[1] > win_height - self.r:
            self.pos[1] = self.r if self.r > self.pos[1] else win_height - self.r
            self.v[1] = -self.v[1]
            # Logic
            self.prev_collision = None

    def vortex(self):
        # Physics
        mouse_dir = mouse_pos - self.pos
        mouse_f = mouse_dir * (mouse_f_abs / Abs(mouse_dir)) * px_per_m
        mouse_a = mouse_f / self.m
        self.v = self.v + mouse_a * time_d
        # Logic
        self.prev_collision = None
    
    def gravity(self):
        self.v = self.v + np.array([0, g_amp * g]) * time_d * px_per_m

    def move(self):
        self.pos = self.pos + self.v * time_d
        if tracking:
            if list(np.around(self.pos).astype(int)) not in [e.pos for e in trackers]:
                trackers.append(Tracker(np.around(self.pos).astype(int), self.color))

    def draw(self):
        draw_pos = np.around(self.pos).astype(int)
        pg.draw.circle(win, self.color, draw_pos, round(self.r))

def rPos():
    return rint(1, win_width), rint(1, win_height)
def rRad():
    return r(circle_r_min, circle_r_max)
def rVel():
    return r(circle_v_min, circle_v_max), r(circle_v_min, circle_v_max)


# Setup
circles = [Circle(rPos(), rRad(), rVel()) for i in range(circle_quantity)]
clock = pg.time.Clock()
trackers = []
u = 0  # Fps updater
mouse_text = font.render("Mouse Vortex: " + str(mouse_f_abs) + " N", False, (255, 255, 255))
circle_text = font.render(
    "A_UP and A_DOWN: Change number of circles: " + str(circle_quantity),
    False, (255, 255, 255))
gravity_text = font.render(
                    "G: Toggle Gravity: " + ("On" if g_toggle else "Off") + " | T and B: Amplify G: " + str(g_amp),
                    False, (255, 255, 255))
color_text = font.render("C: Toggle Color Change: " + ("On" if seizure else "Off"), False,
                                         (255, 255, 255))
tracking_text = font.render("I: Circle Tracking: " + ("On" if tracking else "Off"), False,
                                            (255, 255, 255))
restart_text = font.render("R: Restart", False, (255, 255, 255))
full_text = font.render("F11: Toggle Fullscren: " + ("On" if full else "Off"), False, (255, 255, 255))
hud_text = font.render("H: Toggle HUD", False, (255, 255, 255))

# Main
run = True
while run:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        # Keyboard
        elif event.type == pg.KEYDOWN:
            # Circle
            if event.key == pg.K_r:
                circles = [Circle(rPos(), rRad(), rVel()) for i in range(circle_quantity)]
            elif event.key == pg.K_UP:
                circle_quantity += 1
                circle_text = font.render(
                    "A_UP and A_DOWN: Change number of circles: " + str(circle_quantity),
                    False, (255, 255, 255))
            elif event.key == pg.K_DOWN:
                circle_quantity -= 1
                circle_text = font.render(
                    "A_UP and A_DOWN: Change number of circles: " + str(circle_quantity),
                    False, (255, 255, 255))
            # Gravity
            elif event.key == pg.K_g:
                g_toggle = not g_toggle
                gravity_text = font.render(
                    "G: Toggle Gravity: " + ("On" if g_toggle else "Off") + " | T and B: Amplify G: " + str(g_amp),
                    False, (255, 255, 255))
            elif event.key == pg.K_t:
                g_amp = round(g_amp + 0.1, 1)
                gravity_text = font.render(
                    "G: Toggle Gravity: " + ("On" if g_toggle else "Off") + " | T and B: Amplify G: " + str(g_amp),
                    False, (255, 255, 255))
            elif event.key == pg.K_b:
                g_amp = round(g_amp - 0.1, 1)
                gravity_text = font.render(
                    "G: Toggle Gravity: " + ("On" if g_toggle else "Off") + " | T and B: Amplify G: " + str(g_amp),
                    False, (255, 255, 255))
            # Aesthetic
            elif event.key == pg.K_c:
                seizure = not seizure
                color_text = font.render("C: Toggle Color Change: " + ("On" if seizure else "Off"), False,
                                         (255, 255, 255))
            elif event.key == pg.K_i:
                tracking = not tracking
                if not tracking:
                    trackers = []
                tracking_text = font.render("I: Circle Tracking: " + ("On" if tracking else "Off"), False,
                                            (255, 255, 255))
            elif event.key == pg.K_h:
                hud = not hud
                hud_text = font.render("H: Toggle HUD", False, (255, 255, 255))

            elif event.key == pg.K_F11:
                full = not full
                if full:
                    win_width_temp, win_height_temp = win_width, win_height
                    win_width, win_height = info.current_w, info.current_h
                    pg.display.set_mode((info.current_w, info.current_h), pg.FULLSCREEN)
                else:
                    win_width, win_height = win_width_temp, win_height_temp
                    pg.display.set_mode([win_width, win_height], pg.RESIZABLE)
                full_text = font.render("F11: Toggle Fullscren: " + ("On" if full else "Off"), False, (255, 255, 255))
        # Mouse
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 2:
                mouse_f_abs = -mouse_f_abs
            elif event.button == 4:
                mouse_f_abs = round(mouse_f_abs + 0.1, 1)
            elif event.button == 5:
                mouse_f_abs = round(mouse_f_abs - 0.1, 1)
            mouse_text = font.render("Mouse Vortex: " + str(mouse_f_abs) + " N", False, (255, 255, 255))

        # Window
        elif event.type == pg.VIDEORESIZE and not full:
            win_width, win_height = event.size
            if win_width < win_width_min:
                win_width = win_width_min
            if win_height < win_height_min:
                win_height = win_height_min
            win = pg.display.set_mode([win_width, win_height], pg.RESIZABLE)
            time_d, time_0 = time.time() - time_0, time.time()

    # Time
    time_d, time_0 = time.time() - time_0, time.time()
    clock.tick()

    # Action
    for i, circle_1 in enumerate(circles[:-1]):
        for circle_2 in circles[i+1:]:
            circle_dist = circle_2.pos - circle_1.pos
            if Abs(circle_dist) <= circle_1.r + circle_2.r:
                if circle_1.prev_collision != circle_2 or circle_2.prev_collision != circle_1:
                    circle_v_1 = circle_1.v
                    circle_1.circle_collide(circle_2, circle_2.v)
                    circle_2.circle_collide(circle_1, circle_v_1)

                circle_dist_new = circle_dist * (circle_1.r + circle_2.r) / Abs(circle_dist)
                circle_1.pos = circle_1.pos - (circle_dist_new - circle_dist)/2
                circle_2.pos = circle_2.pos + (circle_dist_new - circle_dist)/2

    for circle in circles:
        circle.wall_collide()
        if g_toggle:
            circle.gravity()

    if pg.mouse.get_pressed()[0]:
        mouse_pos = np.array(pg.mouse.get_pos())
        for circle in circles:
            circle.vortex()

    for circle in circles:
        circle.move()

    # Drawing
    win.fill((0, 0, 0))

    time_new = time.time()
    for tracker in trackers:
        tracker.update()

    for circle in circles:
        circle.draw()

    # HUD
    if hud:
        if pg.time.get_ticks() >= 250 * u:
            fps_text = font.render("Fps: " + str(int(clock.get_fps())), False, (255, 255, 255))
            u += 1
        win.blit(fps_text, (win_width - fps_text.get_rect()[2], 0))

        win.blit(mouse_text, (0, 0))

        for i, text in enumerate([restart_text, tracking_text, color_text, gravity_text, circle_text], 1):
            win.blit(text, (0, win_height - font.size("a")[1] * i))

        win.blit(full_text, (win_width - full_text.get_rect()[2], win_height - font.size("a")[1] * 2))

        win.blit(hud_text, (win_width - full_text.get_rect()[2], win_height - font.size("a")[1]))

    pg.display.update()

pg.quit()
