from effect_base import Effect
from random import choices, choice
from colorsys import hsv_to_rgb

off = (0, 0, 0)


colors = 20
RGB_tuples = [hsv_to_rgb(x * 1.0 / colors, 0.9, 1.0) for x in range(colors)]

class PartyPattern(Effect):
    def __init__(self):
        super().__init__()
        self.step = 0
        self.pool = set(range(25))
        self.lifetime = dict.fromkeys(self.pool, 0)
        self.all_off()

    def setLantern(self, index, color):
        self.pattern[index // 5][index % 5] = color

    def setTransition(self, index, time):
        self.transition_length[index // 5][index % 5] = time

    def all_off(self):
        for i in range(25):
            self.setLantern(i, off)

    def next_frame(self):
        # called every 0.4 seconds
        self.step += 1

        newLights = 5
        fade = 1.0

        for i in range(25):
            if self.lifetime[i] <= 0:
                self.setTransition(i, 0)
                self.pool.add(i)
            else:
                self.setTransition(i, 1.0)
                self.lifetime[i] -= 0.4
                self.setLantern(i, off)

        newLight = set(choices(list(self.pool), k=newLights))
        self.pool -= newLight

        for light in newLight:
            self.lifetime[light] = fade
            self.setLantern(light, choice(RGB_tuples))
