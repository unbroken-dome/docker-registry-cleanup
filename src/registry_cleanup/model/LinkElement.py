import os.path
from abc import ABCMeta

from .Digest import Digest
from .Element import Element


class LinkElement(Element, metaclass=ABCMeta):

    def get_link_path(self) -> str:
        return os.path.join(self.get_path(), 'link')

    def exists(self):
        return super().exists() and os.path.exists(self.get_link_path())

    def get_link_as_string(self) -> str:
        link_path = self.get_link_path()
        with open(link_path, 'r') as link_file:
            return link_file.read()

    def get_link_as_digest(self) -> Digest:
        return Digest.parse(self.get_link_as_string())
