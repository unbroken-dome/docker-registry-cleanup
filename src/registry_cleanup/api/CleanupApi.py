from flask import abort, json, request

from .Application import app, registry
from ..cleanup import RegistryCleanup, CleanupInfo, RepositoryPurge
from ..model import Repository


@app.route('/cleanup', methods=['POST'])
def cleanup():
    registry_cleanup = RegistryCleanup(registry)
    cleanup_infos = {
        "broken_manifests": registry_cleanup.delete_broken_manifests(),
        "orphaned_manifests": registry_cleanup.delete_orphaned_manifests(),
        "orphaned_layers": registry_cleanup.delete_orphaned_layers(),
        "orphaned_blobs": registry_cleanup.delete_orphaned_blobs(),
        "empty_repositories": registry_cleanup.delete_empty_repositories()
    }

    total_cleanup_info = sum(cleanup_infos.values(), CleanupInfo())

    return json.jsonify(
        steps={key: vars(cleanup_infos[key]) for key in cleanup_infos.keys()},
        total=vars(total_cleanup_info))


@app.route('/repositories/<path:repository_name>/_purge', methods=['POST'])
def purge_repository(repository_name: str):
    repository = Repository(registry, repository_name)
    if not repository.exists():
        abort(404)
    min_tags = _to_int(request.args.get('min', None))
    max_tags = _to_int(request.args.get('max', None))
    max_age_in_days = _to_int(request.args.get('maxdays', None))
    purge = RepositoryPurge(min_tags, max_tags, max_age_in_days)
    cleanup_info = purge.purge_repository(repository)
    return json.jsonify(result=vars(cleanup_info))


def _to_int(s):
    return int(s) if s is not None else None
