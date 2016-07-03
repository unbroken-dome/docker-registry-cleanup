import os.path

from .BlobLink import BlobLink
from .Digest import Digest


class Signature(BlobLink):

    def __init__(self, manifest, digest: Digest):
        super().__init__(manifest.registry)
        self.manifest = manifest
        self.digest = digest

    def get_path(self) -> str:
        return os.path.join(self.manifest.get_path(), 'signatures', self.digest.algorithm,
                            self.digest.content)

    def __eq__(self, other):
        return other and self.manifest == other.manifest and self.digest == other.digest

    def __hash__(self):
        return hash((self.manifest, self.digest))

    def __str__(self):
        return 'Signature %s' % self.digest

    def __repr__(self):
        return str(self)
