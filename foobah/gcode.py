#!/usr/bin/env python

import math

import numpy as np

from .constants import PEN_DELAY, START_X, START_Y, XMAX, XMID, XMIN, YMAX, YMID, YMIN
from .utils import clamp, dist


class GCODE:
    def __init__(
        self,
        name="foobar",
        feedrate=1000,
        travel_feedrate=None,
        line_feedrate=None,
        max_line_length=10,
        scale=None,
    ):
        self.start_pos = np.array([START_X, START_Y])
        self.pos = np.array([START_X, START_Y])
        self.f = open(f"{name}.gcode", "wt")
        self.feedrate = feedrate

        self.travel_feedrate = travel_feedrate or feedrate
        self.line_feedrate = line_feedrate or feedrate

        self.servo = "P0"
        self.pen_up_pos = "S0"
        self.pen_down_pos = "S90"

        self.max_line_length = max_line_length
        self.scale = scale

        self._is_pen_up = False

        self._start_routine()

    def _start_routine(self):
        self.f.write("M17\n")  # Ensure steppers are enabled
        self.f.write("M121\n")  # Disable endstops, just in case
        self.f.write("G90\n")  # Set absolute positioning
        self.f.write("; potatolangelo\n")
        self.pen_up()
        self.move_to_starting_position()

    def pen_up(self):
        if self._is_pen_up:
            return

        self._is_pen_up = True

        self.finish_moves()
        self.f.write(f"M280 {self.servo} {self.pen_up_pos} T{PEN_DELAY}\n")

    def pen_down(self):
        if not self._is_pen_up:
            return

        self._is_pen_up = False

        self.finish_moves()
        self.f.write(f"M280 {self.servo} {self.pen_down_pos} T{PEN_DELAY}\n")

    def finish_moves(self):
        self.f.write("M400\n")

    def scale_coordinate(self, x, y):
        if not self.scale:
            return x, y

        xmin, xmax, ymin, ymax = self.scale

        return (
            ((x - xmin) / (xmax - xmin)) * (XMAX - XMIN) + XMIN,
            ((y - ymin) / (ymax - ymin)) * (YMAX - YMIN) + YMIN,
        )

    def move_to(self, x, y, feedrate=None, scale=True):
        line_length = dist(self.pos, (x, y))

        if line_length <= self.max_line_length:
            self._move_to(x, y, feedrate=feedrate or self.line_feedrate, scale=scale)
            return

        n_steps = int(math.ceil(line_length / self.max_line_length))

        x0 = self.pos[0]
        y0 = self.pos[1]

        dx = (x - x0) / n_steps
        dy = (y - y0) / n_steps

        for i in range(n_steps + 1):
            self._move_to(
                x0 + dx * i,
                y0 + dy * i,
                feedrate=feedrate or self.line_feedrate,
                scale=scale,
            )

    def _move_to(self, x, y, feedrate=None, scale=True):
        feedrate = feedrate or self.feedrate

        if scale:
            x, y = self.scale(x, y)

        x = clamp(x, XMIN, XMAX)
        y = clamp(y, YMIN, YMAX)

        self.pos[0] = x
        self.pos[1] = y

        self.f.write(f"G0 X{x} Y{y} F{feedrate}\n")

    def line_to(self, x, y, feedrate=None):
        self.pen_down()

        line_length = dist(self.pos, (x, y))

        if line_length <= self.max_line_length:
            self.move_to(x, y, feedrate=feedrate or self.line_feedrate)
            return

        n_steps = int(math.ceil(line_length / self.max_line_length))

        x0 = self.pos[0]
        y0 = self.pos[1]

        dx = (x - x0) / n_steps
        dy = (y - y0) / n_steps

        for i in range(n_steps + 1):
            self.move_to(
                x0 + dx * i,
                y0 + dy * i,
                feedrate=feedrate or self.line_feedrate,
            )

    def travel_to(self, x, y, feedrate=None):
        self.pen_up()
        self.move_to(x, y, feedrate=feedrate or self.travel_feedrate)

    def move_to_mid_point(self, feedrate=None):
        self.move_to(XMID, YMID, feedrate=feedrate, scale=False)

    def move_to_starting_position(self, feedrate=None):
        self.move_to(START_X, START_Y, feedrate=feedrate, scale=False)

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
        self.travel_to(xmin, ymin)
        self.line_to(xmax, ymin)
        self.line_to(xmax, ymax)
        self.line_to(xmin, ymax)
        self.line_to(xmin, ymin)
        self.pen_up()

    def line(self, x1, y1, x2, y2):
        self.pen_up()
        self.move_to(x1, y1)
        self.pen_down()
        self.move_to(x2, y2)
        self.pen_up()

    def draw_boundaries(self):
        self.pen_down()

        # Ugly hack to not scale the boundaries
        _scale = self.scale
        self.scale = None

        self.square(XMIN, YMIN, XMAX, YMAX)

        self.scale = _scale
        self.pen_up()

    def flush(self):
        self.f.flush()
