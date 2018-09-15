from PIL import Image
from PIL import ImageColor
from PIL import ImageFilter

from numpy import random
from numpy import cumsum

from collections import defaultdict

SUNSET_ORANGE = (255, 162, 0)
SUNSET_BLUE = (131, 187, 206)
RANGE_COLOR = (210, 231, 210)
BLACK = (0, 0, 0)

PRINT_OUTLINES = False
FILTER_FNS = {
    "GAUSSIAN": ImageFilter.GaussianBlur(0.5),
    "MEDIAN": ImageFilter.MedianFilter(7),
}
FILTER_FN = "GAUSSIAN"

WIDTH = 2000
HEIGHT = 1000
GROUND = HEIGHT

COLOR_FNS = {
    "GREENIFY": lambda rgb: (rgb[0], int(rgb[1] * 1.2), rgb[2]),
    "DARKEN": lambda rgb: tuple([int(float(x) * 0.98) for x in rgb]),
}
COLOR_FN = "DARKEN"


def generateWalk(n):
    return cumsum(2 * random.randint(0, 2, (1, n)) - 1)


def generateRidges(start, end, increment):
    walk = range(HEIGHT) + 10 * generateWalk(HEIGHT)
    return [walk[x] for x in range(start, end, increment)]


def printRidges(img, ridges, rgb):
    skyline = defaultdict(lambda: HEIGHT)
    for ridge in ridges:
        rgb = COLOR_FNS[COLOR_FN](rgb)
        img = printRidgeline(img, skyline, ridge + generateWalk(WIDTH), rgb)
    return img, skyline


def printRidgeline(img, skyline, walk, rgb):
    for x in range(len(walk)):
        skyline[x] = min(skyline[x], walk[x])
        for y in range(max(0, walk[x]), GROUND):
            img.putpixel((x, y), rgb)
        if PRINT_OUTLINES:
            img.putpixel((x, walk[x]), BLACK)
    return img.filter(FILTER_FNS[FILTER_FN])


def generateSky(img, skyline, startColor, endColor):
    lowestRidge = max(skyline.values())
    for x, y in skyline.items():
        for pos in range(0, y + 5):
            # linearly weighted transition
            weighting = 1.0 * pos / lowestRidge
            weightedStart = [weighting * t for t in startColor]
            weightedEnd = [(1 - weighting) * t for t in endColor]
            weightedColor = tuple([int(t[0] + t[1])
                                   for t in zip(weightedStart, weightedEnd)])
            img.putpixel((x, pos), weightedColor)
    return img


img = Image.new("RGB", (WIDTH, HEIGHT))
img, skyline = printRidges(img, generateRidges(350, GROUND, 20), RANGE_COLOR)
generateSky(img, skyline, SUNSET_ORANGE, SUNSET_BLUE)
img.filter(FILTER_FNS[FILTER_FN])
img.convert("RGB").save('out.png')
