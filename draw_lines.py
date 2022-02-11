import PIL
import PIL.Image
import PIL.ImageFilter

from foobah.constants import START_X, START_Y, XMAX, XMIN, YMAX, YMIN
from foobah.gcode import GCODE

from math import sin, cos, radians

from random import uniform


noise = 0


def main():
    basename = "david-bowie"
    scale = 1
    image_name = "images/david-bowie.jpg"
    image = PIL.Image.open(image_name)

    width = image.width
    height = image.height

    image = image.resize((int(width / scale), int(height / scale)), PIL.Image.ANTIALIAS)
    # image = image.filter(PIL.ImageFilter.EDGE_ENHANCE_MORE)
    # image = image.filter(PIL.ImageFilter.SMOOTH_MORE)
    # image = image.filter(PIL.ImageFilter.CONTOUR)
    image = image.filter(PIL.ImageFilter.DETAIL)
    # image = image.filter(PIL.ImageFilter.EDGE_ENHANCE)
    # image = image.filter(PIL.ImageFilter.EDGE_ENHANCE_MORE)

    # image = image.rotate(-90, expand=True)

    image = image.convert("RGB")

    gcode = GCODE(basename, feedrate=3500)
    gcode.move_to_starting_position()
    gcode.pen_down()
    gcode.draw_boundaries()
    gcode.pen_up()

    width = image.width
    height = image.height


def build_layer(image, threshold, step_size, angle):
    cx = image.width / 2
    cy = image.height / 2
    i = 0

    while True:
        x = cx + i * step_size * sin(radians(angle + 90))
        y = cy + i * step_size * cos(radians(angle + 90))

        if x < 0 or x >= image.width or y < 0 or y >= image.height:
            break

        draw_lines(image, x, y, threshold=threshold, step_size=step_size, angle=angle)
        draw_lines(image, x, y, threshold=threshold, step_size=step_size, angle=angle + 180)

        i += 1

    i = 0
    while True:
        x = cx - i * step_size * sin(radians(angle + 90))
        y = cy - i * step_size * cos(radians(angle + 90))

        if x < 0 or x >= image.width or y < 0 or y >= image.height:
            break

        draw_lines(image, x, y, threshold=threshold, step_size=step_size, angle=angle)
        draw_lines(image, x, y, threshold=threshold, step_size=step_size, angle=angle + 180)

        i += 1


def draw_lines(image, x, y, angle, threshold, step_size):
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


    build_layer(threshold=0.7, angle=uniform(0, 180), step_size=3)
    build_layer(threshold=0.6, angle=uniform(0, 180), step_size=3)
    build_layer(threshold=0.5, angle=uniform(0, 180), step_size=3)

    # n_layers = 10
    # min_threshold = 0.3
    # max_threshold = 0.9
    # min_step_size = 17
    # max_step_size = 2

    # for i in range(n_layers):
    #     threshold = round(min_threshold + (i / (n_layers - 1)) * (max_threshold - min_threshold), 2)
    #     step_size = round(min_step_size + (i / (n_layers - 1)) * (max_step_size - min_step_size))
    #     print(i, threshold, step_size)
    #     build_layer(threshold=threshold, angle=uniform(0, 180), step_size=step_size)


    gcode.pen_up()
    gcode.move_to_starting_position()
    gcode.flush()

if __name__ == '__main__':
    main()
