from math import cos, radians, sin
from random import uniform


class LineThreshold:
    def __init__(self, image, gcode, threshold=0.5, angle=45, noise=0, step_size=3):
        self.image = image
        self.gcode = gcode
        self.threshold = threshold
        self.step_size = step_size
        self.angle = angle
        self.noise = noise

        if angle is None:
            angle = uniform(0, 360)

    def paint(self, bounds=None):
        if bounds is None:
            bounds = (0, 0, self.image.width, self.image.height)

        self.line_threshold(bounds=bounds)

    def line_threshold(self, bounds):
        xmin, ymin, xmax, ymax = bounds
        cx = (xmin + xmax) / 2
        cy = (ymin + ymax) / 2
        i = 0

        while True:
            x = cx + i * self.step_size * sin(radians(self.angle + 90))
            y = cy + i * self.step_size * cos(radians(self.angle + 90))

            if x < xmin or x >= xmax or y < ymin or y >= ymax:
                break

            self._line_threshold(
                x,
                y,
                bounds,
            )
            self._line_threshold(
                x,
                y,
                bounds,
                angle_hack=180
            )

            i += 1

        i = 1
        while True:
            x = cx - i * self.step_size * sin(radians(self.angle + 90))
            y = cy - i * self.step_size * cos(radians(self.angle + 90))

            if x < xmin or x >= xmax or y < ymin or y >= ymax:
                break

            self._line_threshold(
                x,
                y,
                bounds,
            )
            self._line_threshold(
                x,
                y,
                bounds,
                angle_hack=180
            )

            i += 1

    def _line_threshold(self, x, y, bounds, angle_hack=0):
        angle = self.angle + angle_hack
        gcode = self.gcode
        image = self.image
        noise = self.noise
        step_size = 0.5
        threshold = self.threshold
        xmin, ymin, xmax, ymax = bounds

        # Dumb way to find where the line intercepts any border
        # Could be done by solving a simple affine equation, but it is too late
        # in the night to think
        while x < xmin or x >= xmax or y < ymin or y >= ymax:
            x += step_size * sin(-radians(angle))
            y += step_size * cos(-radians(angle))

        writing = False
        while True:
            try:
                r, g, b = image.getpixel((x, y))
            except IndexError:
                return

            intensity = ((255 - r) + (255 - g) + (255 - b)) / (255 * 3.0)

            if not writing and intensity > threshold:
                writing = True
                gcode.move_to(
                    (x + uniform(-noise, noise)),
                    (y + uniform(-noise, noise)),
                )
                gcode.pen_down()
            elif writing and intensity < threshold:
                writing = False
                gcode.move_to(
                    (x + uniform(-noise, noise)),
                    (y + uniform(-noise, noise)),
                )
                gcode.pen_up()

            x += step_size * sin(radians(angle))
            y += step_size * cos(radians(angle))
            if x < xmin + 1 or x >= xmax - 1 or y < ymin + 1 or y >= ymax - 1:
                break

        # Ensure we finish any last line that might end in the border
        if writing:
            gcode.move_to(
                (x + uniform(-noise, noise)),
                (y + uniform(-noise, noise)),
            )
            gcode.pen_up()
