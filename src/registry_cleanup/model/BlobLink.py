from abc import ABCMeta

from .Blob import Blob
from .LinkElement import LinkElement


class BlobLink(LinkElement, metaclass=ABCMeta):

    def __init__(self, registry):
        self.registry = registry

    def get_blob(self) -> Blob:
        digest = self.get_link_as_digest()
        return self.registry.get_blob(digest)
