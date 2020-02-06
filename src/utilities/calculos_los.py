from math import sqrt
import numpy as np
import matplotlib.pyplot as plt
# import src.utilities.calculos as calc

LOS_SAMPLE = 200    # 200 points = 8 seconds
CENTER = (0., 0.)     # Center of the screen
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
    return sqrt(((p2[X]-p1[X]) ** 2) + ((p2[Y]-p1[Y]) ** 2))

def belongs_to_ellipsis(cop_x, cop_y, a, b, r, x0 = 0., y0 = 0.):
    if cop_y > 0.:
        if ((cop_x - x0)**2 / r**2) + ((cop_y - y0)**2 / a**2) > 1.0:
            return False
    elif ((cop_x - x0)**2 / r**2) + ((cop_y - y0)**2 / b**2) > 1.0:
        return False

    return True

def reaction_time(cop_x: np.array, cop_y: np.array, amplitude):
    """This method calculates the reaction time

    Parameters
    ----------
    cop_x : numpy.array
        The center of pressure on x-axis
    cop_y : numpy.array
        The center of pressure on y-axis
    Returns
    -------
    float
        The reaction time
    """

    # i = 0
    # print('\n\nIN REACTION TIME')
    # print(f'distance: {distance_points(CENTER, (cop_x[i], cop_y[i]))}')
    # while (i < LOS_SAMPLE) and (distance_points(CENTER, (cop_x[i], cop_y[i])) < amplitude):
    #     print(f'distance: {distance_points(CENTER, (cop_x[i], cop_y[i]))}')
    #     i += 1
    a, b, r = amplitude
    for i in range(LOS_SAMPLE):
        if not belongs_to_ellipsis(cop_x[i], cop_y[i], r, a, b, cop_x[0], cop_y[0]):
            break

    return i, i * DT

def maximum_excursions(cop_x: np.array, cop_y: np.array, target_point: tuple):
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
    # lower_dist = distance_points((cop_x[0],cop_y[0]), target_point)
    # index = 0
    # i = 0
    # for i in range(1, len(cop_x)):
    #     dist = distance_points((cop_x[i],cop_y[i]), target_point)
    #     if dist < lower_dist:
    #         lower_dist = dist
    #         index = i
    # # return distance_points((cop_x[index], cop_y[index]), CENTER) * .1
    # return distance_points((cop_x[index], cop_y[index]), CENTER)
    dist = cop_x**2 + cop_y**2
    
    return sqrt(dist.max()) * .1

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
    float
        The distance between 'p' and the line defined by 'a' and 'b'
    """
    X = 0
    Y = 1

    numerator = abs((a[Y] - b[Y]) * p[X] + (b[X] - a[X]) * p[Y] + (a[X] * b[Y] - b[X] * a[Y]))
    denominator = sqrt((a[Y] - b[Y])**2 + (b[X] - a[X])**2)

    return numerator / denominator


#def directional_control(center: tuple, target: tuple, cop_x: np.array, cop_y: np.array):
def directional_control(sp, cop_x: np.array, cop_y: np.array):

    # l = len(cop_x)
    #
    # on_target = 0
    # for i in range(l):
    #     if (distance_point_line(a, b, (cop_x[i], cop_y[i])) < r):
    #         on_target += 1
    #
    # # off_target = l - on_target
    # dc = (on_target / l) * 100
    #
    # return dc
    #sp = distance_points(center, target)
    atp = np.sqrt(((cop_y[1:] - cop_y[:-1]) ** 2) + ((cop_x[1:] - cop_x[:-1]) ** 2))
    atp = atp.sum()
    # atp = calc.totex(cop_x, cop_y)

    return sp/atp * 100

def center_of_gravity(height : float):
    """This method calculates the center of gravity height

    Parameters
    ----------
    height : float
        Height

    Returns
    -------
    float
        The center of gravity height
    """
    return 0.55*height

def get_zeros(cop_x, cop_y):
    zero = [LOS_SAMPLE] * 8
    for i in range(8):
        for j in range(LOS_SAMPLE):
            if cop_x[i][j] == 0. and cop_y[i][j] == 0.:
                zero[i] = j
                break
    return zero

def computes_metrics(cop_x, cop_y, height, amplitude):
    # Metrics dict


    metrics = dict()
    # metrics['i'] = np.zeros(8, dtype=int)
    metrics['reaction_time'] = np.zeros(8)
    metrics['maximum_excursion'] = np.zeros(8)
    metrics['directional_control'] = np.zeros(8)

    # LOS_DIRECTIONS
    FRONT_L, FRONT, FRONT_R, RIGHT, REAR_R, REAR, REAR_L, LEFT = range(8)

    # TARGET_POSITIONS
    positions = np.zeros((8), dtype=(float, 2))
    cog = center_of_gravity(height*10)
    angle = np.radians(8.)
    Y = cog*np.sin(angle) # radius
    print(f"Y = {Y}")
    # Y = 233 / 2 # radius
    coord_circle = sqrt(Y**2/2)
    coord_ellipsis = sqrt(Y**2 * (Y/2)**2 / (Y**2 + (Y/2)**2))

    positions[FRONT_L]  = (np.negative(coord_circle), coord_circle)
    positions[FRONT]    = (0, Y)
    positions[FRONT_R]  = (coord_circle, coord_circle)
    positions[RIGHT]    = (Y, 0)
    positions[REAR_R]   = (coord_ellipsis, np.negative(coord_ellipsis))
    positions[REAR]     = (0, np.negative(Y/2))
    positions[REAR_L]   = (np.negative(coord_ellipsis), np.negative(coord_ellipsis))
    positions[LEFT]     = (np.negative(Y), 0)

    a, b, r = amplitude
    d1x = r*np.cos(np.radians(45))
    d1y = a*np.sin(np.radians(45))
    d1 = sqrt(d1x**2 + d1y**2)

    d2x = d1x
    d2y = b*np.sin(np.radians(45))
    d2 = sqrt(d2x**2 + d2y**2)


    D315 = sqrt(2*coord_circle**2) - d1
    D00 = Y - a
    D45 = D315
    D90 = Y - r
    D135 = sqrt(2*coord_ellipsis**2) - d2
    D180 = Y/2 - b
    D225 = D135
    D270 = D90

    sp = [D315, D00, D45, D90, D135, D180, D225, D270]
    # max_ex = np.zeros(9)
    # for i, pos in enumerate(positions):
    #     max_ex[i] = distance_points(pos, CENTER)
    # max_ex[8] = distance_points(positions[0], CENTER)

    # angles = np.radians(np.arange(0., 405., 45.))
    # ax = plt.subplot(111, projection='polar')
    # ax.set_title('Máxima Excursão')
    # ax.set_ylim(0, 20)
    # ax.set_aspect('equal', 'box')
    # ax.set_theta_zero_location("N")  # theta=0 at the top
    # ax.set_theta_direction(-1)  # theta increasing clockwise
    # ax.set_rticks([0, 5, 10, 15, 20])
    # ax.plot(angles, max_ex)
    # plt.show()

    # zero = get_zeros(cop_x, cop_y)

    for i in range(8):
        # f = zero[i]
        _, metrics['reaction_time'][i] = reaction_time(cop_x[i], cop_y[i], amplitude)
        # j = metrics['i'][i]
        # metrics['maximum_excursion'][i] = maximum_excursions(cop_x[i][:f], cop_y[i][:f], positions[i])
        metrics['maximum_excursion'][i] = maximum_excursions(cop_x[i], cop_y[i], positions[i])
        # metrics['directional_control'][i] = directional_control(CENTER, positions[i], cop_x[i][:f], cop_y[i][:f])
        metrics['directional_control'][i] = directional_control(sp[i], cop_x[i], cop_y[i])
        print(i, sp[i], metrics['directional_control'][i])

    for key in metrics.keys():
        metrics[key] = np.append(metrics[key][1:], metrics[key][0])

    return metrics