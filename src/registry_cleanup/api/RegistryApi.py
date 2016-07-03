from flask import abort, json, url_for

from .Application import app, registry
from ..model import Repository, Tag


@app.route('/', methods=['GET'])
def get_registry():
    return json.jsonify(
            _links={
                "self": {"href": url_for(get_registry.__name__)},
                "repositories": {"href": url_for(list_repositories.__name__)}
            }
    )


@app.route('/repositories', methods=['GET'])
def list_repositories():
    return json.jsonify(
            _links={
                "self": {"href": url_for(list_repositories.__name__)},
            },
            _embedded={
                "item": [{
                             "name": repository.name,
                             "_links": {
                                 "self": {"href": url_for(get_repository.__name__, repository_name=repository.name)}
                             }
                         } for repository in registry.get_all_repositories()
                         if repository.exists()]
            }
    )


@app.route('/repositories/<path:repository_name>', methods=['GET'])
def get_repository(repository_name: str):
    repository = Repository(registry, repository_name)
    if not repository.exists():
        abort(404)
    return json.jsonify(
            name=repository.name,
            _links={
                "self": {"href": url_for(get_repository.__name__, repository_name=repository_name)},
                "tags": {"href": url_for(list_tags.__name__, repository_name=repository_name)}
            }
    )


@app.route('/repositories/<path:repository_name>/tags', methods=['GET'])
def list_tags(repository_name: str):
    repository = Repository(registry, repository_name)
    if not repository.exists():
        abort(404)
    return json.jsonify({
        "name": repository.name,
        "_links": {
            "self": {"href": url_for(list_tags.__name__, repository_name=repository_name)},
            "up": {"href": url_for(get_repository.__name__, repository_name=repository_name)},
            "item": [{"href": url_for(get_tag.__name__, repository_name=repository_name, tag_name=tag.name)}
                     for tag in repository.get_all_tags()]
        }
    })


@app.route('/repositories/<path:repository_name>/tags/<string:tag_name>', methods=['GET'])
def get_tag(repository_name: str, tag_name: str):
    repository = Repository(registry, repository_name)
    tag = Tag(repository, tag_name)
    if not tag.exists():
        abort(404)
    return json.jsonify(
            name=tag.name,
            size=tag.get_size(),
            lastModified=tag.get_last_modified().isoformat(),
            _links={
                "self": {"href": url_for(get_tag.__name__, repository_name=repository_name, tag_name=tag_name)},
                "up": {"href": url_for(list_tags.__name__, repository_name=repository_name)}
            }
    )


@app.route('/repositories/<path:repository_name>/tags/<string:tag_name>', methods=['DELETE'])
def delete_tag(repository_name: str, tag_name: str):
    repository = Repository(registry, repository_name)
    tag = Tag(repository, tag_name)
    if not tag.exists():
        abort(404)
    tag.delete()
    return '', 204
