import os.path

from .LinkElement import LinkElement
from .Manifest import Manifest


class Tag(LinkElement):
    def __init__(self, repository, name: str):
        self.repository = repository
        self.name = name

    def get_path(self) -> str:
        return os.path.join(self.repository.get_path(), '_manifests/tags', self.name)

    def get_link_path(self) -> str:
        return os.path.join(self.get_path(), 'current/link')

    def get_manifest(self) -> Manifest:
        digest = self.get_link_as_digest()
        return self.repository.get_manifest(digest)

    def __eq__(self, other):
        return other and self.repository == other.repository and self.name == other.name

    def __hash__(self):
        return hash((self.repository, self.name))

    def __str__(self):
        return 'Tag %s:%s' % (self.repository.name, self.name)

    def __repr__(self):
        return str(self)
