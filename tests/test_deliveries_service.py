from pathlib import Path

from codealmanac.app import create_app
from codealmanac.core.models import AppConfig
from codealmanac.services.control.models import ControlDeliveryMode
from codealmanac.services.control.requests import (
    CreateControlRunRequest,
    SetBranchPolicyRequest,
    UpsertRepositoryRequest,
)
from codealmanac.services.deliveries.models import DeliveryStatus
from codealmanac.services.deliveries.requests import (
    CreateDeliveryRequest,
    ReadDeliveryRequest,
    UpdateDeliveryRequest,
)


def test_delivery_ledger_creates_and_updates_delivery(
    tmp_path: Path,
    isolated_home: Path,
):
    app = create_app(
        AppConfig(
            registry_path=isolated_home / ".codealmanac/registry.json",
            control_db_path=isolated_home / ".codealmanac/control.sqlite",
        )
    )
    repository = app.control.upsert_repository(
        UpsertRepositoryRequest(
            provider="github",
            owner_login="AlmanacCode",
            name="codealmanac",
            full_name="AlmanacCode/codealmanac",
            almanac_root=Path("almanac"),
            local_root_path=tmp_path / "repo",
        )
    )
    branch = app.control.set_branch_policy(
        SetBranchPolicyRequest(repository_id=repository.id, name="dev")
    )
    run = app.control.create_run(
        CreateControlRunRequest(
            repository_id=repository.id,
            branch_id=branch.id,
            expected_head_sha="head-1",
        )
    )

    delivery = app.deliveries.create(
        CreateDeliveryRequest(
            run_id=run.id,
            mode=ControlDeliveryMode.COMMIT,
            target_ref="dev",
            expected_head_sha="head-1",
        )
    )
    updated = app.deliveries.update(
        UpdateDeliveryRequest(
            delivery_id=delivery.id,
            status=DeliveryStatus.SUCCEEDED,
            delivered_head_sha="head-2",
            commit_sha="head-2",
            summary="updated wiki",
        )
    )
    reloaded = app.deliveries.read(ReadDeliveryRequest(delivery_id=delivery.id))

    assert delivery.status is DeliveryStatus.PENDING
    assert delivery.run_id == run.id
    assert updated.status is DeliveryStatus.SUCCEEDED
    assert updated.finished_at is not None
    assert reloaded == updated
