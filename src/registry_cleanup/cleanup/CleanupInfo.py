class CleanupInfo:
    def __init__(self, num_removed=0, space_freed=0):
        self.num_removed = num_removed
        self.space_freed = space_freed

    def __add__(self, other):
        if isinstance(other, CleanupInfo):
            return CleanupInfo(self.num_removed + other.num_removed,
                               self.space_freed + other.space_freed)
        else:
            return NotImplemented

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return NotImplemented
