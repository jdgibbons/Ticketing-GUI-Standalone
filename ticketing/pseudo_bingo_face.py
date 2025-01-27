class PseudoBingoFace:
    def __init__(self, very: int | str, lines: list[int | str], staggered: bool):
        self.verification = very
        self.lines = lines
        self.staggered = staggered

    def get_verification(self):
        return self.verification

    def set_verification(self, very):
        self.verification = very

    def get_lines(self):
        return self.lines

    def set_lines(self, lines):
        self.lines = lines

    def get_line(self, index):
        return self.lines[index]

    def set_line(self, index, line):
        self.lines[index] = line

    def get_staggered(self):
        return self.staggered

    def set_staggered(self, staggered):
        self.staggered = staggered
