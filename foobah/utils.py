from io import BytesIO

import cairo
import IPython.display
import PIL
import PIL.Image

from .constants import START_X, START_Y, XMAX, XMIN, YMAX, YMIN


def clamp(value, min_value, max_value):
    return min(max(value, min_value), max_value)


def preview(basename):
    filename = f"{basename}.gcode"
    writing = False

    last_x = (START_X - XMIN) / (XMAX - XMIN)
    last_y = (START_Y - YMIN) / (YMAX - YMIN)

    width = 210 * 2
    height = 297 * 2

    with cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height) as surface, open(
        filename
    ) as f:
        context = cairo.Context(surface)
        context.scale(width, height)
        context.set_line_width(0.00125)
        context.set_source_rgba(0, 0, 0, 1)

        for line in f.readlines():
            if "G0" in line:

                tokens = line.strip().split(" ")[1:]
                x = (float(tokens[0][1:]) - XMIN) / (XMAX - XMIN)
                y = (float(tokens[1][1:]) - YMIN) / (YMAX - YMIN)

                if writing:
                    context.move_to(last_x, last_y)
                    context.line_to(x, y)
                    context.stroke()

                last_x = x
                last_y = y

            if "M280 P0" in line:
                tokens = line.strip().split(" ")[1:]
                if tokens[1] == "S0":
                    writing = False
                elif tokens[1] == "S90":
                    writing = True

        surface.write_to_png("preview.png")


def preview_png(basename):
    preview(basename)

    image = PIL.Image.open("preview.png")
    return IPython.display.display(data=image)


def preview_svg(basename):
    filename = f"{basename}.gcode"
    svgio = BytesIO()

    writing = False
    last_x = (START_X - XMIN) / (XMAX - XMIN)
    last_y = (START_Y - YMIN) / (YMAX - YMIN)

    width = 210 * 2
    height = 297 * 2

    with cairo.SVGSurface(svgio, width, height) as surface, open(filename) as f:
        context = cairo.Context(surface)
        context.scale(width, height)
        context.set_line_width(0.00125)
        context.set_source_rgba(0, 0, 0, 1)

        for line in f.readlines():
            if "G0" in line:

                tokens = line.strip().split(" ")[1:]
                x = (float(tokens[0][1:]) - XMIN) / (XMAX - XMIN)
                y = (float(tokens[1][1:]) - YMIN) / (YMAX - YMIN)

                if writing:
                    context.move_to(last_x, last_y)
                    context.line_to(x, y)
                    context.stroke()

                last_x = x
                last_y = y

            if "M280 P0" in line:
                tokens = line.strip().split(" ")[1:]
                if tokens[1] == "S0":
                    writing = False
                elif tokens[1] == "S90":
                    writing = True

    return IPython.display.SVG(data=svgio.getvalue())
