from math import pow


class SquareWaver:
    def __init__(
        self,
        image,
        gcode,
        gamma_ish=1.0,
        intensity_threshold=0.001,
        step_size=3,
        min_dy=0.5,
    ):
        self.image = image
        self.gcode = gcode
        self.gamma_ish = gamma_ish
        self.intensity_threshold = intensity_threshold
        self.step_size = step_size
        self.min_dy = min_dy
        self.max_dy = self.step_size

    def paint(self, bounds=None):
        if bounds is None:
            bounds = (0, 0, self.image.width, self.image.height)
        xmin, ymin, xmax, ymax = bounds

        step_size = self.step_size
        min_dy = self.min_dy
        max_dy = self.max_dy
        gamma_ish = self.gamma_ish

        writing = False

        for x_center in range(xmin + step_size // 2, xmax + step_size // 2, step_size):
            y_center = ymin + step_size / 2.0

            # This forces the pixel intensity to be evaluated in the first step
            y = y_center - step_size
            y = ymin
            dy = -1

            self.gcode.move_to(x_center, y)
            self.gcode.pen_down()
            writing = True

            counter = 0

            while y < ymax:
                if y - y_center >= step_size or dy < 0:
                    y_center += step_size

                    intensity = 0
                    sample_count = 0

                    for x_ in range(0, step_size - 1):
                        for y_ in range(0, step_size):
                            if x_center + x_ >= xmax or y_center + y_ >= ymax:
                                continue

                            if y_center + y_ >= ymax:
                                continue

                            try:
                                r, g, b = self.image.getpixel(
                                    (x_center + x_, y_center + y_)
                                )
                            except IndexError:
                                continue

                            intensity += ((255 - r) + (255 - g) + (255 - b)) / (
                                255 * 3.0
                            )
                            sample_count += 1

                    if sample_count == 0:
                        break

                    intensity /= sample_count

                    pixel_intensity = max_dy - (
                        (pow(intensity, 1 / gamma_ish) * 1) * max_dy
                    )
                    dy = pixel_intensity
                    dy = max(dy, min_dy)
                    dy = min(dy, max_dy)

                if intensity < self.intensity_threshold and writing:
                    self.gcode.pen_up()
                    writing = False

                if intensity >= self.intensity_threshold and not writing:
                    self.gcode.pen_down()
                    writing = True

                if counter % 2 == 0:
                    x = x_center + step_size / 2.0
                else:
                    x = x_center - step_size / 2.0

                counter += 1

                self.gcode.move_to(x, y)

                y += dy

                self.gcode.move_to(x, y)

            self.gcode.pen_up()
            writing = False
