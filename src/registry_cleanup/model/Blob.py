import os.path
from io import TextIOBase

from .Digest import Digest
from .Element import Element


class Blob(Element):
    def __init__(self, registry, digest: Digest):
        self.registry = registry
        self.digest = digest

    def get_path(self):
        return os.path.join(self.registry.get_path(), 'blobs', self.digest.algorithm,
                            self.digest.content[:2], self.digest.content)

    def get_data_as_text(self) -> TextIOBase:
        data_path = os.path.join(self.get_path(), 'data')
        return open(data_path, 'r')

    def __eq__(self, other):
        return other and self.registry == other.registry and self.digest == other.digest

    def __hash__(self):
        return hash((self.registry, self.digest))

    def __str__(self):
        return 'Blob %s' % self.digest

    def __repr__(self):
        return str(self)
