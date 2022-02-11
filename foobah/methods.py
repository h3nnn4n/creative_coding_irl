from math import cos, radians, sin
from random import uniform

from foobah.constants import XMAX, XMIN, YMAX, YMIN


def line_threshold(image, gcode, threshold=0.5, step_size=3, angle=45, noise=0):
    cx = image.width / 2
    cy = image.height / 2
    i = 0

    while True:
        x = cx + i * step_size * sin(radians(angle + 90))
        y = cy + i * step_size * cos(radians(angle + 90))

        if x < 0 or x >= image.width or y < 0 or y >= image.height:
            break

        _line_threshold(
            image,
            gcode,
            x,
            y,
            threshold=threshold,
            step_size=step_size,
            angle=angle,
            noise=noise,
        )
        _line_threshold(
            image,
            gcode,
            x,
            y,
            threshold=threshold,
            step_size=step_size,
            angle=angle + 180,
        )

        i += 1

    i = 0
    while True:
        x = cx - i * step_size * sin(radians(angle + 90))
        y = cy - i * step_size * cos(radians(angle + 90))

        if x < 0 or x >= image.width or y < 0 or y >= image.height:
            break

        _line_threshold(
            image,
            gcode,
            x,
            y,
            threshold=threshold,
            step_size=step_size,
            angle=angle,
            noise=noise,
        )
        _line_threshold(
            image,
            gcode,
            x,
            y,
            threshold=threshold,
            step_size=step_size,
            angle=angle + 180,
            noise=noise,
        )

        i += 1


def _line_threshold(image, gcode, x, y, angle, threshold, step_size, noise=0):
    # Dumb way to find where the line intercepts any border of the image
    # Could be done by solving a simple affine equation, but it is too late in the night to think
    while x < 0 or x >= image.width or y < 0 or y >= image.height:
        x += step_size * sin(-radians(angle))
        y += step_size * cos(-radians(angle))

    writing = False
    while True:
        r, g, b = image.getpixel((x, y))
        intensity = ((255 - r) + (255 - g) + (255 - b)) / (255 * 3.0)

        if not writing and intensity > threshold:
            writing = True
            gcode.move_to(
                ((x + uniform(-noise, noise)) / image.width) * (XMAX - XMIN) + XMIN,
                ((y + uniform(-noise, noise)) / image.height) * (YMAX - YMIN) + YMIN,
            )
            gcode.pen_down()
        elif writing and intensity < threshold:
            writing = False
            gcode.move_to(
                ((x + uniform(-noise, noise)) / image.width) * (XMAX - XMIN) + XMIN,
                ((y + uniform(-noise, noise)) / image.height) * (YMAX - YMIN) + YMIN,
            )
            gcode.pen_up()

        x += step_size * sin(radians(angle))
        y += step_size * cos(radians(angle))
        if x < 0 or x >= image.width or y < 0 or y >= image.height:
            break

    # Ensure we finish any last line that might end in the border
    if writing:
        gcode.move_to(
            ((x + uniform(-noise, noise)) / image.width) * (XMAX - XMIN) + XMIN,
            ((y + uniform(-noise, noise)) / image.height) * (YMAX - YMIN) + YMIN,
        )
        gcode.pen_up()
