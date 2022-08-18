from effect_base import Effect


white = (1.0, 1.0, 1.0)
off = (0, 0, 0)
loop = [0, 1, 2, 3, 4, 9, 14, 19, 24, 23, 22, 21, 20, 15, 10, 5]

def scaleLightVector(s, v):
    return (max(v[0] * s, 0), max(v[1] * s, 0), max(v[2] * s, 0))


class LighthousePattern(Effect):
    def __init__(self):
        super().__init__()
        self.transition_length = [[0.4] * 5 for _ in range(5)]
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

        looplen = len(loop)

        for i in range(looplen):
            self.setLantern(loop[i], scaleLightVector(1 - (((self.step - i) % looplen) / looplen), white))
            




