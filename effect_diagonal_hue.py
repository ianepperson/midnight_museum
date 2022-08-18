from effect_base import Effect
from random import randint
from colorsys import hsv_to_rgb

off = (0, 0, 0)


class DiagonalHuePattern(Effect):
    def __init__(self):
        super().__init__()
        self.step = 0
        self.transition_length = [[0.4] * 5 for _ in range(5)]
        self.all_off()

    def setLantern(self, index, color):
        self.pattern[index // 5][index % 5] = color

    def all_off(self):
        for i in range(25):
            self.setLantern(i, off)

    def next_frame(self):
        # called every 0.4 seconds
        self.step += 1
        speed = 30  # a full cycle every n seconds

        for y in range(5):
            for x in range(5):
                self.pattern[x][y] = hsv_to_rgb(
                    ((self.step * 0.4 * 9 / speed + x + y) % 9) / 9, 0.9, 1
                )
