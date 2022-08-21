from effect_base import Effect


white = (1.0, 1.0, 1.0)
off = (0, 0, 0)
loop = [0, 1, 2, 3, 4, 9, 14, 19, 24, 23, 22, 21, 20, 15, 10, 5]
loop_pairs = (
    [0, 0],
    [0, 1],
    [0, 2],
    [0, 3],
    [0, 4],
    [1, 4],
    [2, 4],
    [3, 4],
    [4, 4],
    [4, 3],
    [4, 2],
    [4, 1],
    [4, 0],
    [3, 0],
    [2, 0],
    [1, 0]
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

    def next_frame(self):
        # called every 0.4 seconds
        self.last_step = self.step
        self.step += 1
        if self.step >= len(loop_pairs):
            self.step = 0

        lit = loop_pairs[self.step]
        dark = loop_pairs[self.last_step]

        self.pattern[lit[0]][lit[1]] = white
        self.transition_length[lit[0]][lit[1]] = 0.2

        self.pattern[dark[0]][dark[1]] = (0.1, 0.1, 0.1)
        self.transition_length[dark[0]][dark[1]] = 5
