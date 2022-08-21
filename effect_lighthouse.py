from effect_base import Effect


white = (1.0, 1.0, 1.0)
off = (0, 0, 0)
loop = [0, 1, 2, 3, 4, 9, 14, 19, 24, 23, 22, 21, 20, 15, 10, 5]

steps = (
    [[0, 0], [1, 1]],
    [[0, 1]],
    [[0, 2], [1, 2]],
    [[0, 3]],
    [[0, 4], [1, 3]],
    [[1, 4]],
    [[2, 4], [2, 3]],
    [[3, 4]],
    [[4, 4], [3, 3]],
    [[4, 3]],
    [[4, 2], [3, 2]],
    [[4, 1]],
    [[4, 0], [3, 1]],
    [[3, 0]],
    [[2, 0], [2, 1]],
    [[1, 0]]
)


def scaleLightVector(s, v):
    return (max(v[0] * s, 0), max(v[1] * s, 0), max(v[2] * s, 0))


class LighthousePatternOld(Effect):
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
            self.setLantern(
                loop[i],
                scaleLightVector(
                    1 - (((self.step - i) % looplen) / looplen), white
                )
            )


class LighthousePattern(Effect):
    def __init__(self):
        super().__init__()

        self.transition_length = [[0.4] * 5 for _ in range(5)]
        self.step = 1
        self.last_step = 0
        self.all_off()

    def all_off(self):
        for i in range(25):
            self.setLantern(i, off)

    def setLantern(self, index, color):
        self.pattern[index // 5][index % 5] = color

    def set_lantern(self, idx, color, transition):
        self.pattern[idx[0]][idx[1]] = color
        self.transition_length[idx[0]][idx[1]] = transition

    def next_frame(self):
        # called every 0.4 seconds
        self.last_step = self.step
        self.step += 1
        if self.step >= len(steps):
            self.step = 0

        lit = steps[self.step]
        dark = steps[self.last_step]

        for idx in lit:
            self.set_lantern(idx, white, 0.2)

        for idx in dark:
            self.set_lantern(idx, (0.1, 0.1, 0.1), 5)
