"""ws:int: command line.

    python -m falafelona run --config configs/final.yaml [--out outputs/Falafelona.csv]

Prints aggregates only: label counts, row count, SHA-256. Never raw rows.
Humans run this on real data, not AI agents (CLAUDE.md).
"""

import argparse

from falafelona import pipeline
from falafelona.config import load_config

DEFAULT_OUT = "outputs/Falafelona.csv"


def build_parser():
    parser = argparse.ArgumentParser(prog="falafelona", description="Team Falafelona pipeline")
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("run", help="build the submission CSV from a config")
    run.add_argument("--config", required=True, help="a configs/*.yaml file")
    run.add_argument("--out", default=DEFAULT_OUT, help=f"where to write (default {DEFAULT_OUT})")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "run":
        cfg = load_config(args.config)
        result = pipeline.run(cfg, args.out)
        print(f"wrote   {result['path']}")
        print(f"rows    {result['rows']}")
        for label, count in result["counts"].items():
            print(f"{label:<7} {count:>7}  {100.0 * count / result['rows']:5.1f}%")
        print(f"sha256  {result['sha256']}")
    return 0
