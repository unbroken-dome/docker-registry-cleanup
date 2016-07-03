import os.path

from .BlobLink import BlobLink
from .Digest import Digest


class Layer(BlobLink):
    def __init__(self, repository, digest: Digest):
        super().__init__(repository.registry)
        self.repository = repository
        self.digest = digest

    def get_path(self) -> str:
        return os.path.join(self.repository.get_path(), '_layers', self.digest.algorithm,
                            self.digest.content)

    def __eq__(self, other):
        return other and self.repository == other.repository and self.digest == other.digest

    def __hash__(self):
        return hash((self.repository, self.digest))

    def __str__(self):
        return 'Layer %s [%s]' % (self.digest, self.repository.name)

    def __repr__(self):
        return str(self)
