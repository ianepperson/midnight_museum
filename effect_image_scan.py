import logging
import random
from os import listdir

from PIL import Image

from effect_base import Effect


log = logging.getLogger(__name__)


class ImageScan(Effect):
    def __init__(self, image_filename):
        super().__init__()
        self.transition_length = [[0.4] * 5 for _ in range(5)]

        log.info(f'Loading image {image_filename}')
        self.image = Image.open(image_filename)
        self.image.load()
        self.image = self.image.convert(mode='RGB')

        # distance from pixel to pixel
        self.spread = 5

        # How much to step each pixel each time
        self.speed = [4, 1]

        self.origin = [0, 0]
        self.step = self.origin

    def update_origin(self):
        diameter = len(self.pattern) * self.spread
        new_origin = [spd + org for spd, org in zip(self.speed, self.origin)]
        # Reached the left edge
        if new_origin[0] < 0:
            log.info('at left edge')
            self.speed[0] *= -1
            new_origin[0] = 0

        # Reached the top edge
        if new_origin[1] < 0:
            log.info('at top edge')
            self.speed[1] *= -1
            new_origin[0] = 0

        # Reached the right edge
        if new_origin[0] + diameter >= self.image.size[0]:
            log.info('at right edge')
            self.speed[0] *= -1
            new_origin[0] = self.image.size[0] - diameter - 1

        # Reached the bottom edge
        if new_origin[1] + diameter >= self.image.size[1]:
            log.info('at bottom edge')
            self.speed[1] *= -1
            new_origin[1] = self.image.size[1] - diameter - 1

        self.origin = new_origin
        self.step = new_origin  # for debugging

    def getpixel(self, x, y):
        red, green, blue = self.image.getpixel((x, y))
        return (red / 255, green / 255, blue / 255)

    def next_frame(self):
        # called every 0.4 seconds
        self.update_origin()

        for row_num, row in enumerate(self.pattern):
            for col_num in range(len(self.pattern)):
                x = row_num * self.spread + self.origin[0]
                y = col_num * self.spread + self.origin[1]
                row[col_num] = self.getpixel(x, y)


class RandomImageScan(ImageScan):
    def __init__(self):
        images = []
        for filename in listdir('static'):
            if filename.startswith('effect') and filename.endswith('.png'):
                images.append(filename)

        super().__init__('static/' + random.choice(images))


class LightHouseImageScan(ImageScan):
    def __init__(self):
        super().__init__('static/panel-black_rock_lighthouse.png')
