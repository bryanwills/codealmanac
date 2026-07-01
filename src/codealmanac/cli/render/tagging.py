from codealmanac.services.tagging.models import TaggingResult


def render_tagging(
    changed_label: str,
    unchanged_label: str,
    result: TaggingResult,
) -> None:
    if result.changed_topics:
        print(f"{result.slug}: {changed_label} {', '.join(result.changed_topics)}")
        return
    unchanged = ", ".join(result.requested_topics)
    print(f"{result.slug}: {unchanged_label} {unchanged}")
