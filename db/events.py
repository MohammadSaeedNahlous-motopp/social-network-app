from pathlib import Path

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session


def delete_file(path: str):
    Path(path).unlink(missing_ok=True)


@event.listens_for(Session, "after_flush")
def collect_deleted_files(session, flush_context):
    # Check all objects that SQLAlchemy considers "dirty",
    # meaning their database values have been changed.
    for obj in session.dirty:
        mapper = inspect(obj).mapper

        for column in mapper.columns:
            # Only handle columns explicitly marked as file fields.
            if not getattr(column, "info", {}).get("file_field"):
                continue

            # Get the change history for this specific column.
            # This tells us what value the column had before the change.
            history = inspect(obj).attrs[column.key].history

            # Nothing changed in this column, so there is nothing to do.
            if not history.has_changes():
                continue

            # We want to delete "images/old.jpg", but only after
            # the database transaction successfully commits.
            for old_value in history.deleted:
                if old_value and old_value != getattr(obj, column.key):
                    # Store the old file path in the current SQLAlchemy
                    # session so we can delete it after commit.
                    #
                    # A set is used to avoid deleting the same file
                    # multiple times if it appears more than once.
                    session.info.setdefault("files_to_delete", set()).add(old_value)


@event.listens_for(Session, "after_commit")
def delete_old_files(session):
    # The database transaction has successfully committed -> remove file
    # pop() also removes the files from session.info after retrieving them.
    files = session.info.pop("files_to_delete", set())

    for path in files:
        delete_file(path)


@event.listens_for(Session, "after_rollback")
def clear_deleted_files(session):
    # The database transaction failed or was explicitly rolled back.
    #
    # In this case, the old files are still referenced by the database,
    # so they must NOT be deleted.
    #
    # We only need to forget the files that were scheduled for deletion.
    session.info.pop("files_to_delete", None)
