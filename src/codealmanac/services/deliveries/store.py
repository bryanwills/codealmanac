from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from codealmanac.core.errors import NotFoundError
from codealmanac.database import SQLiteConnection
from codealmanac.services.control.schema import connect_control
from codealmanac.services.deliveries.models import DeliveryRecord, DeliveryStatus
from codealmanac.services.deliveries.requests import (
    CreateDeliveryRequest,
    ReadDeliveryRequest,
    UpdateDeliveryRequest,
)


class DeliveriesStore:
    def __init__(self, control_db_path: Path):
        self.control_db_path = control_db_path

    def create(self, request: CreateDeliveryRequest) -> DeliveryRecord:
        delivery_id = f"delivery_{uuid4().hex}"
        now = current_timestamp()
        with connect_control(self.control_db_path) as connection:
            self.ensure_run_exists(connection, request.run_id)
            connection.execute(
                """
                INSERT INTO deliveries (
                  id,
                  run_id,
                  mode,
                  status,
                  target_ref,
                  expected_head_sha,
                  created_at,
                  updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    delivery_id,
                    request.run_id,
                    request.mode.value,
                    DeliveryStatus.PENDING.value,
                    request.target_ref,
                    request.expected_head_sha,
                    now,
                    now,
                ),
            )
            return self.delivery_by_id(connection, delivery_id)

    def read(self, request: ReadDeliveryRequest) -> DeliveryRecord:
        with connect_control(self.control_db_path) as connection:
            return self.delivery_by_id(connection, request.delivery_id)

    def update(self, request: UpdateDeliveryRequest) -> DeliveryRecord:
        now = current_timestamp()
        finished_at = now if request.status is not DeliveryStatus.PENDING else None
        with connect_control(self.control_db_path) as connection:
            self.delivery_by_id(connection, request.delivery_id)
            connection.execute(
                """
                UPDATE deliveries
                SET status = ?,
                    delivered_head_sha = COALESCE(?, delivered_head_sha),
                    commit_sha = COALESCE(?, commit_sha),
                    pr_url = COALESCE(?, pr_url),
                    summary = COALESCE(?, summary),
                    error = COALESCE(?, error),
                    finished_at = COALESCE(finished_at, ?),
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    request.status.value,
                    request.delivered_head_sha,
                    request.commit_sha,
                    request.pr_url,
                    request.summary,
                    request.error,
                    finished_at,
                    now,
                    request.delivery_id,
                ),
            )
            return self.delivery_by_id(connection, request.delivery_id)

    def ensure_run_exists(self, connection: SQLiteConnection, run_id: str) -> None:
        row = connection.execute(
            """
            SELECT id
            FROM runs
            WHERE id = ?
            """,
            (run_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError("run", run_id)

    def delivery_by_id(
        self,
        connection: SQLiteConnection,
        delivery_id: str,
    ) -> DeliveryRecord:
        row = connection.execute(
            "SELECT * FROM deliveries WHERE id = ?",
            (delivery_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError("delivery", delivery_id)
        return DeliveryRecord.model_validate(dict(row))


def current_timestamp() -> str:
    return datetime.now(UTC).isoformat()
