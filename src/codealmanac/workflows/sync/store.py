from datetime import UTC, datetime
from pathlib import Path

from codealmanac.core.paths import normalize_path
from codealmanac.database.local import connect_local_database
from codealmanac.workflows.sync.models import SyncState

SYNC_STATE_KEY = "sync"


class SyncStateStore:
    def __init__(self, database_path: Path):
        self.database_path = normalize_path(database_path)

    def read(self) -> SyncState:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT last_completed_at
                FROM sync_state
                WHERE name = ?
                """,
                (SYNC_STATE_KEY,),
            ).fetchone()
        if row is None or row["last_completed_at"] is None:
            return SyncState()
        return SyncState(
            last_completed_at=datetime.fromisoformat(
                str(row["last_completed_at"])
            ).astimezone(UTC)
        )

    def record_completed(self, completed_at: datetime) -> SyncState:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO sync_state (name, last_completed_at)
                VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    last_completed_at = excluded.last_completed_at
                """,
                (SYNC_STATE_KEY, completed_at.astimezone(UTC).isoformat()),
            )
            connection.commit()
        return SyncState(last_completed_at=completed_at.astimezone(UTC))

    def connect(self):
        return connect_local_database(self.database_path)
