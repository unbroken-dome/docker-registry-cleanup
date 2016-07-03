import logging

from typing import List, Set
from datetime import datetime, timedelta
from .CleanupInfo import CleanupInfo
from ..model import Repository, Tag


logger = logging.getLogger(__name__)


class RepositoryPurge:
    def __init__(self, min_tags: int = None, max_tags: int = None, max_age_in_days: int = None):
        self.min_tags = min_tags if min_tags is not None else 0
        self.max_tags = max_tags
        self.max_age = timedelta(days=max_age_in_days) if max_age_in_days is not None else None

    def purge_repository(self, repository: Repository) -> CleanupInfo:
        if not repository.exists():
            return CleanupInfo()

        # Get all tags and sort them by age
        tags = sorted(
                list(repository.get_all_tags()), reverse=True,
                key=lambda tag: tag.get_last_modified())

        tags_to_delete = self._find_tags_to_delete(tags,
                                                   self.max_tags if self.max_tags is not None else len(tags))

        cleanup_info = CleanupInfo(num_removed=len(tags_to_delete),
                                   space_freed=sum([tag.get_size() for tag in tags_to_delete]))
        for tag in tags_to_delete:
            logger.info('Deleting: %s', tag)
            tag.delete()

        return cleanup_info

    def _find_tags_to_delete(self, tags: List[Tag], max_tags: int) -> Set[Tag]:
        # chop off tags beyond the maximum number
        tags_to_delete = set(tag for tag in tags[max_tags:])

        threshold_date = (datetime.now() - self.max_age) if self.max_age is not None else None

        for i in range(0, min(max_tags, len(tags))):
            tag = tags[i]
            # Keep this tag if it's either among the youngest min_tags tags, or younger than max_age
            should_keep_this_tag = (i + 1 <= self.min_tags) \
                                   or threshold_date is None \
                                   or tag.get_last_modified() >= threshold_date
            if not should_keep_this_tag:
                tags_to_delete.add(tag)

        return tags_to_delete
