#!/usr/bin/env python

import numpy as np

from .constants import PEN_DELAY, START_X, START_Y, XMAX, XMIN, YMAX, YMIN
from .utils import clamp


class GCODE:
    def __init__(self, name="foobar", feedrate=1000):
        self.start_pos = np.array([START_X, START_Y])
        self.pos = np.array([START_X, START_Y])
        self.f = open(f"{name}.gcode", "wt")
        self.feedrate = feedrate

        self.servo = "P0"
        self.pen_up_pos = "S0"
        self.pen_down_pos = "S90"

        self.f.write("M17\n")  # Ensure steppers are enabled
        self.f.write("M121\n")  # Disable endstops, just in case
        self.f.write("G90\n")  # Set absolute positioning
        self.f.write("; potatolangelo\n")
        self.pen_up()
        self.move_to_starting_position()

    def pen_up(self):
        self.finish_moves()
        self.f.write(f"M280 {self.servo} {self.pen_up_pos} T{PEN_DELAY}\n")

    def pen_down(self):
        self.finish_moves()
        self.f.write(f"M280 {self.servo} {self.pen_down_pos} T{PEN_DELAY}\n")

    def finish_moves(self):
        self.f.write("M400\n")

    def move_to(self, x, y, feedrate=None):
        feedrate = feedrate or self.feedrate

        x = clamp(x, XMIN, XMAX)
        y = clamp(y, YMIN, YMAX)

        self.pos[0] = x
        self.pos[1] = y

        self.f.write(f"G0 X{x} Y{y} F{feedrate}\n")

    def move_to_mid_point(self, feedrate=None):
        self.move_to(XMID, YMID, feedrate=feedrate)

    def move_to_starting_position(self, feedrate=None):
        self.move_to(START_X, START_Y, feedrate=feedrate)

    def step(self, dx, dy, feedrate=None):
        feedrate = feedrate or self.feedrate
        self.pos[0] += dx
        self.pos[1] += dy

        x = self.pos[0]
        y = self.pos[1]
        x = clamp(x, XMIN, XMAX)
        y = clamp(y, YMIN, YMAX)
        self.pos[0] = x
        self.pos[1] = y

        self.f.write(f"G0 X{x} Y{y} F{feedrate}\n")

    def square_filled(self, xmin, ymin, xmax, ymax, dy=1, zigzag=True):
        #         print(f"square filled centered on {(xmin + xmax) / 2.0:.2f} {(ymin + ymax) / 2.0:.2f}")

        self.pen_up()
        self.move_to((xmin + xmax) / 2.0, (ymin + ymax) / 2.0)

        self.square(xmin, ymin, xmax, ymax)

        self.pen_up()
        self.move_to(xmin, ymin)
        self.pen_down()

        x = xmin
        y = ymin
        while y < ymax:
            y += dy

            # When zigzag is true the pen moves in a saw tooth pattern,
            # otherwise it goes in a square wave form.
            # Zigzag looks good with ballpoint pens, while the square pattern
            # works best on thicker points.
            if not zigzag:
                self.move_to(x, y)

            if x == xmin:
                x = xmax
            else:
                x = xmin

            self.move_to(x, y)

        self.pen_up()

    def square(self, xmin, ymin, xmax, ymax):
        return
        self.move_to(xmin, ymin)
        self.pen_down()
        self.move_to(xmax, ymin)
        self.move_to(xmax, ymax)
        self.move_to(xmin, ymax)
        self.move_to(xmin, ymin)
        self.pen_up()

    def line(self, x1, y1, x2, y2):
        self.pen_up()
        self.move_to(x1, y1)
        self.pen_down()
        self.move_to(x2, y2)
        self.pen_up()

    def draw_boundaries(self):
        self.square(XMIN, YMIN, XMAX, YMAX)

    def flush(self):
        self.f.flush()
