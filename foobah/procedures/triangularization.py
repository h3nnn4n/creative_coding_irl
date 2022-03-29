from random import uniform
from scipy.spatial import Delaunay, KDTree


class Triangularizator:
    def __init__(self, image, gcode, step_size=3, pow_exp=4, noise=0.5):
        self.image = image
        self.gcode = gcode
        self.step_size = step_size
        self.pow_exp = pow_exp
        self.noise = noise

    def paint(self, bounds=None):
        if bounds is None:
            bounds = (0, 0, self.image.width, self.image.height)

        point_cloud = self._get_point_cloud(bounds=bounds)

        if len(point_cloud) < 3:
            return

        triangles = Delaunay(point_cloud)

        for a, b, c in triangles.simplices:
            p1 = point_cloud[a]
            p2 = point_cloud[b]
            p3 = point_cloud[c]

            self.gcode.move_to(*p1)
            self.gcode.line_to(*p2)
            self.gcode.line_to(*p3)
            self.gcode.line_to(*p1)
            self.gcode.pen_up()

    def _get_point_cloud(self, bounds):
        xmin, ymin, xmax, ymax = bounds

        step_size = self.step_size

        point_cloud = []

        for x in range(xmin, xmax + 1, step_size):
            for y in range(ymin, ymax + 1, step_size):
                dx = uniform(-step_size / 2, step_size / 2) * self.noise
                dy = uniform(-step_size / 2, step_size / 2) * self.noise

                if x + dx < xmin or x + dx >= xmax or y + dy < ymin or y + dy >= ymax:
                    continue

                try:
                    r, g, b = self.image.getpixel((x + dx, y + dy))
                except IndexError:
                    continue

                intensity = ((255 - r) + (255 - g) + (255 - b)) / (255 * 3.0)

                if pow(intensity, self.pow_exp) > uniform(0, 1):
                    point_cloud.append((x + dx, y + dy))

        return point_cloud
