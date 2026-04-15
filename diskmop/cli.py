from __future__ import annotations

import argparse
from pathlib import Path
import sys

from diskmop.report import write_report
from diskmop.scanner import ScanOptions, scan_directory


SIZE_SUFFIXES = [
    ("pb", 1024**5),
    ("tb", 1024**4),
    ("gb", 1024**3),
    ("mb", 1024**2),
    ("kb", 1024),
    ("b", 1),
]


def parse_size(value: str) -> int:
    raw = value.strip().lower()
    if not raw:
        raise argparse.ArgumentTypeError("size value cannot be empty")

    number = raw
    multiplier = 1
    for suffix, suffix_multiplier in SIZE_SUFFIXES:
        if raw.endswith(suffix):
            number = raw[: -len(suffix)].strip()
            multiplier = suffix_multiplier
            break

    try:
        size = float(number)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid size '{value}'. Use values like 10GB, 750MB, or 1048576."
        ) from exc

    if size < 0:
        raise argparse.ArgumentTypeError("size value cannot be negative")
    return int(size * multiplier)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="diskmop",
        description="Scan a directory tree and generate an interactive HTML disk usage report.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Directory to scan. Defaults to the current directory.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="diskmop-report.html",
        help="HTML report destination. Defaults to ./diskmop-report.html",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=5_000,
        help="Maximum number of files to embed in the report. Defaults to 5000.",
    )
    parser.add_argument(
        "--max-directories",
        type=int,
        default=2_000,
        help="Maximum number of directories to embed in the report. Defaults to 2000.",
    )
    parser.add_argument(
        "--hide-hidden",
        action="store_true",
        help="Skip filesystem entries whose names start with a dot.",
    )
    parser.add_argument(
        "--flag-files-over",
        type=parse_size,
        help="Mark files larger than this size in the HTML report, for example 10GB.",
    )
    parser.add_argument(
        "--flag-directories-over",
        type=parse_size,
        help="Mark directories larger than this size in the HTML report, for example 500GB.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        output_path_arg = Path(args.output).expanduser().resolve()
        stats = scan_directory(
            args.path,
            ScanOptions(
                max_files=args.max_files,
                max_directories=args.max_directories,
                include_hidden=not args.hide_hidden,
                exclude_paths={output_path_arg.as_posix()},
            ),
        )
        stats.file_alert_bytes = args.flag_files_over
        stats.directory_alert_bytes = args.flag_directories_over
        output_path = write_report(output_path_arg, stats)
    except (FileNotFoundError, NotADirectoryError, PermissionError, OSError) as exc:
        print(f"diskmop: {exc}", file=sys.stderr)
        return 1

    target = Path(args.path).expanduser().resolve()
    print(f"Scanned {target}")
    print(f"Report written to {output_path}")
    print(
        f"Total: {stats.total_size} bytes across {stats.file_count} files and {stats.directory_count} directories"
    )
    if stats.truncated_files or stats.truncated_directories:
        print(
            "Report dataset truncated "
            f"({stats.truncated_files} files, {stats.truncated_directories} directories omitted from HTML)"
        )
    if stats.errors:
        print(f"Encountered {len(stats.errors)} filesystem errors during the scan")
    return 0
