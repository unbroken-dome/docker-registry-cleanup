import os.path
from typing import Iterable

from .Digest import Digest
from .Element import Element
from .Layer import Layer
from .Manifest import Manifest
from .Tag import Tag


class Repository(Element):
    def __init__(self, registry, name: str):
        self.registry = registry
        self.name = name

    def get_path(self) -> str:
        return os.path.join(self.registry.get_path(), 'repositories', self.name)

    def get_tag(self, name: str) -> Tag:
        return Tag(self, name)

    def get_all_tags(self) -> Iterable[Tag]:
        tags_path = os.path.join(self.get_path(), '_manifests/tags')
        if os.path.isdir(tags_path):
            return (Tag(self, entry.name)
                    for entry in os.scandir(tags_path)
                    if entry.is_dir())
        else:
            return []

    def has_tags(self) -> bool:
        tags_path = os.path.join(self.get_path(), '_manifests/tags')
        return os.path.isdir(tags_path) and len(os.listdir(tags_path)) > 0

    def get_manifest(self, digest: Digest) -> Manifest:
        return Manifest(self, digest)

    def get_all_manifests(self) -> Iterable[Manifest]:
        revisions_path = os.path.join(self.get_path(), '_manifests/revisions')
        if os.path.isdir(revisions_path):
            for algorithm_path_entry in os.scandir(revisions_path):
                if algorithm_path_entry.is_dir():
                    for manifest_path_entry in os.scandir(algorithm_path_entry.path):
                        digest = Digest(algorithm_path_entry.name, manifest_path_entry.name)
                        manifest = Manifest(self, digest)
                        if manifest.exists():
                            yield manifest

    def get_all_layers(self) -> Iterable[Layer]:
        layers_path = os.path.join(self.get_path(), '_layers')
        if os.path.isdir(layers_path):
            for algorithm_path_entry in os.scandir(layers_path):
                if algorithm_path_entry.is_dir():
                    for layer_path_entry in os.scandir(algorithm_path_entry.path):
                        digest = Digest(algorithm_path_entry.name, layer_path_entry.name)
                        layer = Layer(self, digest)
                        if layer.exists():
                            yield layer

    def __eq__(self, other):
        return other and self.registry == other.registry and self.name == other.name

    def __hash__(self):
        return hash((self.registry, self.name))

    def __str__(self):
        return 'Repository %s' % self.name

    def __repr__(self):
        return str(self)
