from effect_base import Effect

red = (1.0, 0, 0)
orange = (1.0, 0.65, 0)
yellow = (1.0, 1.0, 0)
green = (0, 1.0, 0)
blue = (0, 0, 1.0)
off = (0, 0, 0)

rainbow = [red, orange, yellow, green, blue]


class TestPattern(Effect):
    '''Show a rainbow, and about every second flick one row off and on again'''
    def __init__(self):
        super().__init__()
        self.step = 0
        self.all_on()

    def all_on(self):
        for idx in range(5):
            self.pattern[idx] = rainbow

    def next_frame(self):
        # caled every 0.4 seconds
        self.step += 1

        # start with all the lights on
        self.all_on()

        if self.step % 5 in (3, 4):
            off_row = int(self.step / 5)
            if off_row >= 5:
                self.step = 0
                return

            self.pattern[off_row] = [off] * 5
