class Digest:
    def __init__(self, algorithm: str, content: str):
        self.algorithm = algorithm
        self.content = content

    def __eq__(self, other):
        return other and self.algorithm == other.algorithm and self.content == other.content

    def __hash__(self):
        return hash((self.algorithm, self.content))

    def __str__(self):
        return self.algorithm + ':' + self.content

    def __repr__(self):
        return str(self)

    @staticmethod
    def parse(s: str):
        algorithm, content = s.split(':', 1)
        return Digest(algorithm, content)
