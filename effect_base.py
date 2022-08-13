'''Used as the base class for any effect driver'''


class Effect:
    def __init__(self):
        self.pattern = [[None] * 5 for _ in range(5)]

    def next_frame(self):
        '''Calculate the next thing.'''
        pass

    def get_diff(self, other):
        '''Yield the row, column and other's value for every difference.
        '''
        for row, (l_row, r_row) in enumerate(zip(self.pattern, other.pattern)):
            for column, (l_pix, r_pix) in enumerate(zip(l_row[:], r_row)):
                if l_pix != r_pix:
                    yield (row, column), r_pix
                    # Update the left with the right
                    self.pattern[row][column] = r_pix
