class WaveSignal:
    def __init__(
        self,
        image,
        gcode,
        step_size=4,
        min_dy=0.5,
        gamma_ish=1.5,
        intensity_threshold=0.0,
        moving_average_samples=2,
    ):
        self.image = image
        self.gcode = gcode

        self.step_size = step_size
        self.min_dy = min_dy
        self.max_dy = step_size
        self.gamma_ish = gamma_ish
        self.intensity_threshold = intensity_threshold
        self.moving_average_samples = moving_average_samples

    def paint(self, bounds=None):
        if bounds is None:
            bounds = (0, 0, self.image.width, self.image.height)
        xmin, ymin, xmax, ymax = bounds

        step_size = self.step_size
        min_dy = self.min_dy
        max_dy = self.max_dy
        gamma_ish = self.gamma_ish
        intensity_threshold = self.intensity_threshold
        moving_average_samples = self.moving_average_samples
        gcode = self.gcode
        image = self.image

        writing = False

        intensities = []

        for x_center in range(
            xmin + step_size // 2, xmax + step_size // 2, step_size
        ):
            y = ymin
            dy = -1

            gcode.move_to(x_center, y)
            gcode.pen_down()
            writing = True

            counter = 0

            while y < ymax and y >= ymin:
                intensity_ = 0
                sample_count = 0
                for x_ in range(0, step_size):
                    if x_center + x_ >= xmax:
                        continue

                    try:
                        r, g, b = image.getpixel((x_center + x_, y))
                    except IndexError:
                        break

                    intensity_ += ((255 - r) + (255 - g) + (255 - b)) / (255 * 3.0)
                    sample_count += 1

                if sample_count == 0:
                    counter += 1
                    y += dy
                    continue

                intensity_ /= sample_count
                intensities.append(intensity_)

                if len(intensities) > moving_average_samples:
                    intensities.pop(0)

                intensity = sum(intensities) / len(intensities)

                pixel_intensity = max_dy - (
                    (pow(intensity, 1 / gamma_ish) * 1) * max_dy
                )
                dy = pixel_intensity
                dy = max(dy, min_dy)
                dy = min(dy, max_dy)

                if intensity < intensity_threshold and writing:
                    gcode.pen_up()
                    writing = False

                if intensity >= intensity_threshold and not writing:
                    gcode.pen_down()
                    writing = True

                if counter % 2 == 0:
                    x = x_center + (step_size / 2.0) * intensity
                else:
                    x = x_center - (step_size / 2.0) * intensity

                counter += 1
                y += dy

                gcode.move_to(x, y)

            gcode.pen_up()
            writing = False
