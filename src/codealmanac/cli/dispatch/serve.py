import argparse
from pathlib import Path

from codealmanac.app import CodeAlmanac


def run_serve(app: CodeAlmanac, args: argparse.Namespace) -> int:
    import uvicorn

    from codealmanac.api.app import create_api_app

    api = create_api_app(app, Path.cwd(), args.wiki)
    print(f"codealmanac viewer: http://{args.host}:{args.port}")
    uvicorn.run(api, host=args.host, port=args.port, log_level="warning")
    return 0
