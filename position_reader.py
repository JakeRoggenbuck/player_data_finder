import nbtlib


class PositionReader:
    def __init__(self, filename):
        self.filename = filename

    def load_file(self):
        nbt_file = nbtlib.load(self.filename)
        return nbt_file

    def get_pos(self):
        _file = self.load_file()
        coords = _file.root["Pos"]
        return [pos.real for pos in coords]
