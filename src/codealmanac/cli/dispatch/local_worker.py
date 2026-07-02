import argparse
import json

from codealmanac.app import CodeAlmanac
from codealmanac.services.harnesses.models import HarnessKind
from codealmanac.workflows.local_worker.requests import RunNextLocalWorkerRequest


def dispatch_run_local_worker(args: argparse.Namespace, app: CodeAlmanac) -> int:
    result = app.workflows.local_worker.run_next(
        RunNextLocalWorkerRequest(
            repository_id=args.repository_id,
            branch_id=args.branch_id,
            operation=args.operation,
            harness=HarnessKind(args.using),
            title=args.title,
        )
    )
    if args.json:
        print(json.dumps(result.model_dump(mode="json")))
    return 0
