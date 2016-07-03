import logging

from typing import Iterable, Set

from .CleanupInfo import CleanupInfo
from ..model import Registry, Repository, Manifest, Layer, Blob, Element


logger = logging.getLogger(__name__)


class RegistryCleanup:
    def __init__(self, registry: Registry):
        self.registry = registry
        if not self.registry.exists():
            raise ValueError("Registry storage path does not exist")

    def find_empty_repositories(self) -> Iterable[Repository]:
        return (repository for repository in self.registry.get_all_repositories()
                if not repository.has_tags())

    def find_broken_manifests(self) -> Iterable[Manifest]:
        for repository in self.registry.get_all_repositories():
            for manifest in repository.get_all_manifests():
                manifest_blob = manifest.get_blob()
                if not manifest_blob.exists():
                    yield manifest

    def find_used_manifests(self) -> Set[Manifest]:
        manifests = set()
        for repository in self.registry.get_all_repositories():
            for tag in repository.get_all_tags():
                logger.debug('%s is used by %s', tag.get_manifest(), tag)
                manifests.add(tag.get_manifest())
        return manifests

    def find_orphaned_manifests(self) -> Iterable[Manifest]:
        used_manifests = self.find_used_manifests()
        for repository in self.registry.get_all_repositories():
            for manifest in repository.get_all_manifests():
                if manifest not in used_manifests:
                    logger.debug('%s is orphaned', manifest)
                    yield manifest

    def find_used_layers(self, repository: Repository) -> Set[Layer]:
        layers = set()
        for manifest in repository.get_all_manifests():
            for layer in manifest.get_layers():
                logger.debug('%s is used by %s', layer, manifest)
                layers.add(layer)
        return layers

    def find_orphaned_layers(self, repository: Repository) -> Iterable[Layer]:
        used_layers = self.find_used_layers(repository)
        return (layer
                for layer in repository.get_all_layers()
                if layer not in used_layers)

    def find_all_orphaned_layers(self) -> Iterable[Layer]:
        for repository in self.registry.get_all_repositories():
            for layer in self.find_orphaned_layers(repository):
                logger.debug('%s is orphaned', layer)
                yield layer

    def find_used_blobs(self) -> Set[Blob]:
        blobs = set()
        for repository in self.registry.get_all_repositories():
            for layer in repository.get_all_layers():
                blob = layer.get_blob()
                logger.debug('%s is used by %s', blob, layer)
                blobs.add(blob)
            for manifest in repository.get_all_manifests():
                blob = manifest.get_blob()
                logger.debug('%s is used by %s', blob, manifest)
                blobs.add(blob)
                for signature in manifest.get_all_signatures():
                    blob = signature.get_blob()
                    logger.debug('%s is used by %s', blob, signature)
                    blobs.add(blob)
        return blobs

    def find_orphaned_blobs(self) -> Iterable[Blob]:
        used_blobs = self.find_used_blobs()
        for blob in self.registry.get_all_blobs():
            if blob not in used_blobs:
                logger.debug('%s is orphaned', blob)
                yield blob

    def _delete_elements(self, elements: Iterable[Element]) -> CleanupInfo:
        num_removed = 0
        space_freed = 0
        for element in set(elements):
            if element.exists():
                space_freed += element.get_size()
                num_removed += 1
                logger.info('Deleted: %s')
                element.delete()
        return CleanupInfo(num_removed, space_freed)

    def delete_empty_repositories(self) -> CleanupInfo:
        return self._delete_elements(self.find_empty_repositories())

    def delete_broken_manifests(self) -> CleanupInfo:
        return self._delete_elements(self.find_broken_manifests())

    def delete_orphaned_manifests(self) -> CleanupInfo:
        return self._delete_elements(self.find_orphaned_manifests())

    def delete_orphaned_layers(self) -> CleanupInfo:
        return self._delete_elements(self.find_all_orphaned_layers())

    def delete_orphaned_blobs(self) -> CleanupInfo:
        return self._delete_elements(self.find_orphaned_blobs())
