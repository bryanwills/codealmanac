import argparse
from pathlib import Path

from codealmanac.app import CodeAlmanac


def run_serve(app: CodeAlmanac, args: argparse.Namespace) -> int:
    import uvicorn

    from codealmanac.server.app import create_server_app

    server = create_server_app(app, Path.cwd(), args.wiki)
    print(f"codealmanac viewer: http://{args.host}:{args.port}")
    uvicorn.run(server, host=args.host, port=args.port, log_level="warning")
    return 0
