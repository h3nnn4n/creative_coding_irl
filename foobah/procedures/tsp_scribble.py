import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from random import uniform


class TSPScribble:
    def __init__(self, image, gcode, step_size=3, noise=0.5, pow_exp=4):
        self.image = image
        self.gcode = gcode
        self.step_size = step_size
        self.noise = noise
        self.pow_exp = pow_exp

    def paint(self, bounds=None):
        if bounds is None:
            bounds = (0, 0, self.image.width, self.image.height)
        xmin, ymin, xmax, ymax = bounds

        points = self._get_point_cloud(bounds)
        model = self._create_model(points)
        solution = self._solve(model)

        print(solution)

    def _solve(self, model):
        manager = pywrapcp.RoutingIndexManager(
            len(model["locations"]), model["num_vehicles"], model["depot"]
        )

        routing = pywrapcp.RoutingModel(manager)
        distance_matrix = _compute_euclidean_distance_matrix(model["locations"])

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            # Todo, we can probably make this faster and more memory efective
            # by lazily calculating things and memoizing them as we go
            return distance_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )

        solution = routing.SolveWithParameters(search_parameters)

        return solution

    def _create_model(self, points):
        model = {}
        model["locations"] = points
        model["num_vehicles"] = 1
        model["depot"] = 0

        return model

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


def _compute_euclidean_distance_matrix(locations):
    distances = {}
    for from_counter, from_node in enumerate(locations):
        distances[from_counter] = {}
        for to_counter, to_node in enumerate(locations):
            if from_counter == to_counter:
                distances[from_counter][to_counter] = 0
            else:
                distances[from_counter][to_counter] = int(
                    math.hypot((from_node[0] - to_node[0]), (from_node[1] - to_node[1]))
                )
    return distances
