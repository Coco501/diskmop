# PYTHON_ARGCOMPLETE_OK
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import time
import webbrowser

import argcomplete

from diskmop.report import write_report
from diskmop.scanner import ScanOptions, ScanProgress, scan_directory


SIZE_SUFFIXES = [
    ("pb", 1024**5),
    ("tb", 1024**4),
    ("t", 1024**4),
    ("gb", 1024**3),
    ("g", 1024**3),
    ("mb", 1024**2),
    ("m", 1024**2),
    ("kb", 1024),
    ("k", 1024),
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


def format_bytes(value: int) -> str:
    suffixes = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(value)
    for suffix in suffixes:
        if size < 1024 or suffix == suffixes[-1]:
            return f"{int(size)} {suffix}" if suffix == "B" else f"{size:.1f} {suffix}"
        size /= 1024
    return f"{value} B"


def choose_output_path(path: Path) -> tuple[Path, Path | None]:
    if not path.exists():
        return path, None

    stem = path.stem
    suffix = path.suffix or ".html"
    parent = path.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate, path
        counter += 1


class ProgressReporter:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        self._frames = [
            "====................",
            ".====...............",
            "..====..............",
            "...====.............",
            "....====............",
            ".....====...........",
            "......====..........",
            ".......====.........",
            "........====........",
            ".........====.......",
            "..........====......",
            "...........====.....",
            "............====....",
            ".............====...",
            "..............====..",
            "...............====.",
        ]
        self._tick = 0
        self._last_line_time = 0.0

    def update(self, progress: ScanProgress) -> None:
        if not self.enabled:
            return
        current_name = Path(progress.current_path).name or progress.current_path
        n = len(self._frames)
        period = 2 * (n - 1)
        pos = self._tick % period
        frame = self._frames[pos if pos < n else period - pos]
        message = (
            f"Scanning [{frame}] "
            f"{format_bytes(progress.total_size)}  "
            f"{progress.files_seen} files  "
            f"{progress.directories_seen} dirs  "
            f"errors {progress.errors}  "
            f"now {current_name}"
        )
        self._tick += 1
        if sys.stderr.isatty():
            width = os.get_terminal_size(sys.stderr.fileno()).columns
            sys.stderr.write("\r" + message[:width].ljust(width))
            sys.stderr.flush()
            if progress.done:
                sys.stderr.write("\n")
        else:
            now = time.time()
            if progress.done or now - self._last_line_time >= 5:
                sys.stderr.write(message + "\n")
                sys.stderr.flush()
                self._last_line_time = now


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
        "-H", "--hide-hidden",
        action="store_true",
        help="Skip filesystem entries whose names start with a dot.",
    )
    parser.add_argument(
        "-f", "--flag",
        type=parse_size,
        metavar="SIZE",
        help=(
            "Mark files and directories larger than this size in the HTML report. "
            "Accepts units: kb/k, mb/m, gb/g, tb/t (case-insensitive). "
            "Example: 10gb, 500M, 2T."
        ),
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open the report in a browser after generation.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args(argv)

    try:
        requested_output = Path(args.output).expanduser().resolve()
        output_path_arg, replaced_path = choose_output_path(requested_output)
        if replaced_path is not None:
            print(
                f"diskmop: warning: {replaced_path} already exists; writing new report to {output_path_arg}",
                file=sys.stderr,
            )
        progress = ProgressReporter(enabled=True)
        stats = scan_directory(
            args.path,
            ScanOptions(
                max_files=args.max_files,
                max_directories=args.max_directories,
                include_hidden=not args.hide_hidden,
                exclude_paths={output_path_arg.as_posix()},
            ),
            progress_callback=progress.update,
        )
        stats.file_alert_bytes = args.flag
        stats.directory_alert_bytes = args.flag
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
    if not args.no_open:
        webbrowser.open(output_path.as_uri())
    return 0
