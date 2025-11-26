from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import IO

from devtool.software_list import Package, list_go_packages, list_rpms


def main():
    parser = make_parser()
    args = vars(parser.parse_args())
    cmd = args.pop("__cmd__")
    cmd(**args)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Helper tool for development in this project")
    subcommands = parser.add_subparsers(title="subcommands", required=True)

    ls_parser = subcommands.add_parser("ls", help="List software to be installed in the image")
    ls_parser.add_argument("-f", "--format", choices=["txt", "json", "md"], default="txt")
    ls_parser.add_argument("-o", "--output-file", type=Path)
    ls_parser.set_defaults(__cmd__=list_software)

    return parser


def list_software(format: str, output_file: Path | None) -> None:
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    project_root = Path(proc.stdout.strip())

    go_packages = list_go_packages(project_root)
    rpms = list_rpms(project_root)
    packages = sorted(go_packages + rpms, key=lambda p: p.name)

    if output_file:
        with output_file.open("w") as outfile:
            _print_packages(format, packages, outfile)
    else:
        _print_packages(format, packages, sys.stdout)


def _print_packages(format: str, packages: list[Package], outfile: IO[str]) -> None:
    match format:
        case "txt":
            for package in packages:
                print(package.name, package.version, file=outfile)
        case "json":
            print(json.dumps([p.asdict() for p in packages], indent=2), file=outfile)
        case "md":
            print("# Installed Software", end="\n\n", file=outfile)
            _print_markdown_table(packages, outfile)
        case _:
            raise RuntimeError(f"Invalid format passed from CLI: {format}")


def _print_markdown_table(packages: list[Package], outfile: IO[str]) -> None:
    columns: list[list[str]] = []
    columns.append(["Name", *(p.name for p in packages)])
    columns.append(["Version", *(p.version for p in packages)])
    columns.append(
        [
            "Install Method",
            *("`go install`" if p.installed_with == "go" else "RPM" for p in packages),
        ]
    )
    # Hardcoded to generate smaller diffs. Increase if any package name is longer than this.
    column_width = 30

    for column in columns:
        column.insert(1, "-" * column_width)

    transposed: list[tuple[str, ...]] = list(zip(*columns))
    for row in transposed:
        for value in row:
            outfile.write("| ")
            outfile.write(value.ljust(column_width))
            outfile.write(" ")
        outfile.write("|\n")


if __name__ == "__main__":
    main()
