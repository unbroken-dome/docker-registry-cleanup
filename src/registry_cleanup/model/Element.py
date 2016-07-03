import os.path
import shutil
from datetime import datetime
from abc import ABCMeta, abstractmethod


class Element(object, metaclass=ABCMeta):

    @abstractmethod
    def get_path(self) -> str:
        return None

    def exists(self) -> bool:
        path = self.get_path()
        return os.path.exists(path)

    @staticmethod
    def _get_tree_size(path) -> int:
        total = 0
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                total += Element._get_tree_size(entry.path)
            else:
                total += entry.stat(follow_symlinks=False).st_size
        return total

    def get_size(self) -> int:
        path = self.get_path()
        return self._get_tree_size(path)

    def get_last_modified(self) -> datetime:
        path = self.get_path()
        return datetime.fromtimestamp(os.path.getmtime(path))

    def delete(self):
        path = self.get_path()
        shutil.rmtree(path)
