import collections
import math

from fdm.equation import Stencil, Number
from fdm.geometry import Point

__all__ = ['Settings', 'create_left_caputo_stencil', 'create_right_caputo_stencil', 'create_riesz_caputo_stencil',
           'create_left_rectangle_rule_stencil', 'create_right_rectangle_rule_stencil',
           'create_riesz_rectangle_rule_stencil', 'create_left_trapezoidal_rule_stencil',
           'create_right_trapezoidal_rule_stencil', 'create_riesz_trapezoidal_rule_stencil']


Settings = collections.namedtuple('CaputoSettings', ('alpha', 'lf', 'resolution'))


def create_parametrized_stencil(start, end, points_number, multiplier, weight):

    def _weight(node_number, relative_address):
        return multiplier * weight(node_number)

    return Stencil.uniform(Point(start), Point(end), points_number, _weight)


def create_side_caputo_stencil(alpha, p, start, end,  multiplier, weights):
    n = math.floor(alpha) + 1.
    h = (end - start)/p
    _multiplier = multiplier * ((h**(n - alpha)) / math.gamma(n - alpha + 2.))

    return create_parametrized_stencil(start, end, p, _multiplier, weights)


def create_left_caputo_stencil(alpha, lf, p):
    n = math.floor(alpha) + 1.
    index = (n - alpha + 1.)

    def weights(number):
        if number == 0:
            return (p - 1.) ** index - (p - n + alpha - 1.) * p ** (n - alpha)
        elif number == p:
            return 1.
        else:
            j = number
            return (p - j + 1.) ** index - 2. * (p - j) ** index + (p - j - 1.) ** index

    return create_side_caputo_stencil(
        alpha, p, -lf, 0., 1., weights,
    )


def create_right_caputo_stencil(alpha, lf, p):
    n = math.floor(alpha) + 1.
    index = (n - alpha + 1.)

    def weights(number):
        if number == 0:
            return 1.
        elif number == p:
            return (p - 1.) ** index - (p - n + alpha - 1.) * p ** (n - alpha)
        else:
            j = number
            return (j + 1.) ** index - 2. * j ** index + (j - 1.) ** index

    return create_side_caputo_stencil(
        alpha, p, 0., lf, (-1.) ** n, weights
    )


def create_riesz_stencil(settings, left, right):
    alpha, lf, resolution = settings
    n = math.floor(alpha) + 1.
    return Number(1. / 2. * math.gamma(2. - alpha) / math.gamma(2.)) * \
           (left + Number((-1.) ** n) * right)


def create_riesz_caputo_stencil(settings):
    return create_riesz_stencil(
        settings,
        create_left_caputo_stencil(*settings),
        create_right_caputo_stencil(*settings)
    )


def create_side_rectangle_rule_stencil(alpha, lf, p, start, end, weight):
    return create_parametrized_stencil(
        start, end, p - 1,
        (lf / float(p)) ** (1. - alpha) / math.gamma(2. - alpha),
        weight)


def create_left_rectangle_rule_stencil(settings):
    alpha, lf, resolution = settings
    dx = lf / float(resolution)

    def weight(i):
        k = -resolution + i
        return (-k)**(1. - alpha) - (-k - 1) ** (1. - alpha)

    return create_side_rectangle_rule_stencil(
        alpha, lf, resolution, -lf + dx, 0., weight
    )


def create_right_rectangle_rule_stencil(settings):
    alpha, lf, resolution = settings
    dx = lf / float(resolution)

    return create_side_rectangle_rule_stencil(
        alpha, lf, resolution, 0., lf - dx,
        lambda k: -((k + 1.)**(1. - alpha) - k**(1. - alpha))
    )


def create_riesz_rectangle_rule_stencil(settings):
    return create_riesz_stencil(
        settings,
        create_left_rectangle_rule_stencil(settings),
        create_right_rectangle_rule_stencil(settings)
    )


def create_side_trapezoidal_rule_stencil(alpha, lf, p, start, end, multiplier, weight):
    return create_parametrized_stencil(
        start, end, p,
        multiplier*(lf / float(p)) ** (1. - alpha) / math.gamma(3. - alpha),
        weight)


def create_left_trapezoidal_rule_stencil(settings):
    alpha, lf, p = settings

    def weight(number):

        if number == 0:
            return (p - 1.)**(2 - alpha) + (2. - alpha - p)*p**(1 - alpha)
        elif number == p:
            return 1.
        else:
            k = -p + number
            return (-k + 1.)**(2 - alpha) - 2*(-k)**(2 - alpha) + (-k - 1.)**(2 - alpha)

    return create_side_trapezoidal_rule_stencil(
        alpha, lf, p, -lf, 0., 1., weight
    )


def create_right_trapezoidal_rule_stencil(settings):
    alpha, lf, p = settings

    def weight(number):

        if number == 0:
            return 1.
        elif number == p:
            return (p - 1.)**(2 - alpha) + (2. - alpha - p)*p**(1 - alpha)
        else:
            k = number
            return (k + 1.)**(2 - alpha) - 2*k**(2 - alpha) + (k - 1.)**(2 - alpha)

    return create_side_trapezoidal_rule_stencil(
        alpha, lf, p, 0., lf, -1., weight
    )


def create_riesz_trapezoidal_rule_stencil(settings):
    return create_riesz_stencil(
        settings,
        create_left_trapezoidal_rule_stencil(settings),
        create_right_trapezoidal_rule_stencil(settings)
    )
