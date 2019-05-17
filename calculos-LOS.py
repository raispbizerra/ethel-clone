from math import sqrt
import numpy as np
import math

LOS_SAMPLE = 200    # 200 points = 8 seconds
DIST = 1            # Distance
CENTER = (384, 384)  # Center of the screen
DT = 0.04           # Period


def distance_points(p1: tuple, p2: tuple):
    """This method calculates the distance between two points

    Parameters
    ----------
    p1 : tuple
        A point
    p2 : tuple
        Another point
    -------
    float
      The distance between 'p1' and 'p2'
    """
    X = 0
    Y = 1
    return math.sqrt(((p2[X]-p1[X]) ** 2) + ((p2[Y]-p1[Y]) ** 2))


def reaction_time(cop: np.array, r):
    """This method calculates the reaction time

    Parameters
    ----------
    cop : numpy.ndarray
        The center of pressure array
    Returns
    -------
    float
        The reaction time
    """

    i = 0
    while (i < LOS_SAMPLE) and (distance_points(CENTER, cop[i]) < r):
        i += 1
    return i * DT


def maximum_excursions(cop: np.array, target_point: tuple):
    """This method calculates the maximum excursion in a direction

    Parameters
    ----------
    cop : np.array
        The center of pressure array
    target_point : tuple
        The point to calculate distance

    Returns
    -------
    float
        The distance between 'p' and the line defined by 'a' and 'b'
    """
    lower_dist = distance_points(cop[0], target_point)
    index = 0
    i = 0
    while i < LOS_SAMPLE:
        dist = distance_points(cop[i], target_point)
        if dist < lower_dist:
            lower_dist = dist
            index = i
        i += 1
    return (index, cop[index])


LOS_SAMPLE = 10


def distance_point_line(a: tuple, b: tuple, p: tuple):
    """This method calculates the distance between a point and a line

    Parameters
    ----------
    a : tuple
        A point belonging to the line
    b : tuple
        Another point belonging to the line
    p : tuple
        The point to calculate distance

    Returns
    -------
    int
        The distance between 'p' and the line defined by 'a' and 'b'
    """
    X = 0
    Y = 1

    numerator = abs((a[Y] - b[Y]) * p[X] + (b[X] - a[X])
                    * p[Y] + (a[X] * b[Y] - b[X] * a[Y]))
    denominator = sqrt((a[Y] - b[Y])**2 + (b[X] - a[X])**2)

    return numerator // denominator


def directional_control(r: float, a: tuple, b: tuple, cop: np.array):
    l = len(cop)

    on_target = 0
    for i, c in enumerate(cop):
        if (distance_point_line(a, b, c) < r):
            on_target += 1

    off_target = l - on_target
    dc = (on_target / l) * 100

    return dc


cop = np.random.uniform(low=384, high=384, size=(8, LOS_SAMPLE, 2))

print("\nRection Time", reaction_time(cop[0], 3))

cop = np.random.uniform(low=384, high=384, size=(8, LOS_SAMPLE, 2))
print("\nMaximum Excursions", maximum_excursions(cop[0], (384, 390)))

# Consider a square screen of 768x768
a = (0, 0)     # center point
b = (-15, 0)   # superior center point
r = 3          # trust radius

cop = np.random.uniform(low=-5., high=0., size=(1, LOS_SAMPLE, 2))
print("\nControle Direcional {}%".format(
    directional_control(r, a, b, cop[0])))
