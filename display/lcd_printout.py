class Printout:
    def __init__(self, id: str, firstLine : str, secondLine : str, duration : int):
        self.firstLine = firstLine
        self.secondLine = secondLine
        self.duration = duration
        self.id = id
    def __eq__(self, other): 
        if not isinstance(other, Printout):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.firstLine == other.firstLine and self.secondLine == other.secondLine and self.duration == other.duration