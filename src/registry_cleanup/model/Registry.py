import os
from typing import Iterable

from .Blob import Blob
from .Digest import Digest
from .Element import Element
from .Repository import Repository


class Registry(Element):
    def __init__(self, path: str):
        self.path = os.path.join(path, 'docker/registry/v2')

    def get_path(self) -> str:
        return self.path

    def get_blob(self, digest) -> Blob:
        return Blob(self, digest)

    def get_all_repositories(self) -> Iterable[Repository]:
        repositories_path = os.path.join(self.get_path(), 'repositories')
        if not os.path.isdir(repositories_path):
            return []
        # Scan through all of the directories in the "repositories" root. The tricky bit
        # is that repositories can either be one or two levels deep (e.g. "foo/bar" or just "bar")
        for entry in os.scandir(repositories_path):
            # if the directory is a repository dir, return it
            if Registry._is_repository_dir(entry.path):
                yield Repository(self, entry.name)
            # otherwise, it's just a namespace, so continue scanning one level below
            else:
                for entry2 in os.scandir(entry.path):
                    if Registry._is_repository_dir(entry2.path):
                        yield Repository(self, entry.name + '/' + entry2.name)

    @staticmethod
    def _is_repository_dir(path) -> bool:
        return os.path.exists(os.path.join(path, '_manifests'))

    def get_all_blob_digests(self) -> Iterable[Digest]:
        blobs_path = os.path.join(self.get_path(), 'blobs')
        if os.path.isdir(blobs_path):
            for algorithm_path_entry in os.scandir(blobs_path):
                if algorithm_path_entry.is_dir():
                    for prefix_path_entry in os.scandir(algorithm_path_entry.path):
                        if prefix_path_entry.is_dir():
                            for blob_path_entry in os.scandir(prefix_path_entry.path):
                                if blob_path_entry.is_dir():
                                    yield Digest(algorithm_path_entry.name, blob_path_entry.name)
        else:
            return []

    def get_all_blobs(self) -> Iterable[Blob]:
        return (Blob(self, digest) for digest in self.get_all_blob_digests())

    def __eq__(self, other):
        return other and self.path == other.path

    def __hash__(self):
        return hash(self.path)

    def __str__(self):
        return 'Registry at %s', self.path

    def __repr__(self):
        return str(self)
