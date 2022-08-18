from effect_base import Effect
from colorsys import hsv_to_rgb

off = (0, 0, 0)

colors = 10
RGB_tuples = [hsv_to_rgb(x * 1.0 / colors, 0.9, 1.0) for x in range(colors)]

groups = [
    [12],
    [6, 7, 8, 11, 13, 16, 17, 18],
    [0, 1, 2, 3, 4, 9, 14, 19, 24, 23, 22, 21, 20, 15, 10, 5],
    [],
]
groupMap = [0, 1, 2, 3, 3, 2, 1, 0, 3, 3]


class RipplePattern(Effect):
    def __init__(self):
        super().__init__()
        self.step = 0
        
        self.all_off()

    def setLantern(self, index, color):
        self.pattern[index // 5][index % 5] = color

    def all_off(self):
        for i in range(25):
            self.setLantern(i, off)

    def next_frame(self):
        # called every 0.4 seconds
        self.step += 1

        color = RGB_tuples[(self.step // 10) % 10]

        self.all_off()
        for lantern in groups[groupMap[self.step % 10]]:
            self.setLantern(lantern, color)
