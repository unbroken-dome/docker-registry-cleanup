import json
import os.path
from typing import Iterable

from .BlobLink import BlobLink
from .Digest import Digest
from .Layer import Layer
from .Signature import Signature


class ManifestSchemaNotSupported(Exception):
    def __init__(self, version):
        self.version = version

    def __str__(self):
        return "Manifest version %s is not supported" % self.version


class Manifest(BlobLink):
    def __init__(self, repository, digest: Digest):
        super().__init__(repository.registry)
        self.repository = repository
        self.digest = digest

    def get_path(self):
        return os.path.join(self.repository.get_path(), '_manifests/revisions',
                            self.digest.algorithm, self.digest.content)

    def _get_manifest_data(self) -> dict:
        manifest_blob = self.get_blob()
        with manifest_blob.get_data_as_text() as manifest_data_stream:
            return json.load(manifest_data_stream)

    def get_layers(self) -> Iterable[Layer]:
        manifest_data = self._get_manifest_data()
        schema_version = manifest_data['schemaVersion']
        if schema_version == 1:
            return self._get_layers_v1(manifest_data)
        elif schema_version == 2:
            return self._get_layers_v2(manifest_data)
        else:
            raise ManifestSchemaNotSupported(schema_version)

    def _get_layers_v1(self, manifest_data) -> Iterable[Layer]:
        for fs_layer in manifest_data['fsLayers']:
            blob_sum = Digest.parse(fs_layer['blobSum'])
            yield Layer(self.repository, blob_sum)

    def _get_layers_v2(self, manifest_data) -> Iterable[Layer]:
        for layer in manifest_data['layers']:
            digest = Digest.parse(layer['digest'])
            yield Layer(self.repository, digest)

    def get_all_signatures(self) -> Iterable[Signature]:
        signatures_path = os.path.join(self.get_path(), 'signatures')
        if os.path.isdir(signatures_path):
            for algorithm_path_entry in os.scandir(signatures_path):
                if algorithm_path_entry.is_dir():
                    for signature_path_entry in os.scandir(algorithm_path_entry.path):
                        if signature_path_entry.is_dir():
                            digest = Digest(algorithm_path_entry.name, signature_path_entry.name)
                            yield Signature(self, digest)

    def __eq__(self, other):
        return other and self.repository == other.repository and self.digest == other.digest

    def __hash__(self):
        return hash((self.repository, self.digest))

    def __str__(self):
        return 'Manifest %s [%s]' % (self.digest, self.repository.name)

    def __repr__(self):
        return str(self)
