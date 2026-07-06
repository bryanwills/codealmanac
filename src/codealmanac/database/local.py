from pathlib import Path

from codealmanac.database.sqlite import SQLiteConnection, connect_sqlite

LOCAL_DATABASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS repositories (
    repository_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    root_path TEXT NOT NULL UNIQUE,
    almanac_root TEXT NOT NULL,
    registered_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    repository_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    title TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    record_json TEXT NOT NULL,
    spec_json TEXT,
    FOREIGN KEY (repository_id) REFERENCES repositories(repository_id)
);

CREATE INDEX IF NOT EXISTS runs_repository_created_idx
    ON runs(repository_id, created_at);

CREATE INDEX IF NOT EXISTS runs_status_created_idx
    ON runs(status, created_at);

CREATE TABLE IF NOT EXISTS run_events (
    run_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    event_json TEXT NOT NULL,
    PRIMARY KEY (run_id, sequence),
    FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS worker_locks (
    name TEXT PRIMARY KEY,
    owner_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sync_state (
    name TEXT PRIMARY KEY,
    last_completed_at TEXT
);
"""


def connect_local_database(path: Path) -> SQLiteConnection:
    connection = connect_sqlite(path)
    connection.executescript(LOCAL_DATABASE_SCHEMA)
    connection.commit()
    return connection
