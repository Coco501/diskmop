from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import heapq
import os
import stat
import time
from pathlib import Path
from typing import Callable


@dataclass(slots=True)
class ScanOptions:
    max_files: int = 5_000
    max_directories: int = 2_000
    include_hidden: bool = True
    exclude_paths: set[str] = field(default_factory=set)


@dataclass(slots=True)
class FileRecord:
    path: str
    parent: str
    name: str
    size: int
    extension: str
    modified_at: float


@dataclass(slots=True)
class DirectoryRecord:
    path: str
    parent: str | None
    name: str
    depth: int
    total_size: int = 0
    file_count: int = 0
    directory_count: int = 0
    direct_file_size: int = 0
    direct_file_count: int = 0


@dataclass(slots=True)
class ScanStats:
    root_path: str
    started_at: str
    finished_at: str
    duration_seconds: float
    total_size: int
    file_count: int
    directory_count: int
    retained_files: int
    retained_directories: int
    truncated_files: int
    truncated_directories: int
    scanned_hidden: bool
    file_alert_bytes: int | None
    directory_alert_bytes: int | None
    errors: list[str]
    root_children: list[dict[str, object]]
    directories: list[dict[str, object]]
    files: list[dict[str, object]]
    extensions: list[dict[str, object]]


@dataclass(slots=True)
class ScanProgress:
    current_path: str
    files_seen: int
    directories_seen: int
    total_size: int
    errors: int
    depth: int
    done: bool = False


class TopN:
    def __init__(self, limit: int):
        self.limit = limit
        self._heap: list[tuple[int, int, object]] = []
        self._counter = 0
        self.seen = 0

    def add(self, size: int, item: object) -> None:
        self.seen += 1
        if self.limit <= 0:
            heapq.heappush(self._heap, (size, self._counter, item))
            self._counter += 1
            return
        if len(self._heap) < self.limit:
            heapq.heappush(self._heap, (size, self._counter, item))
            self._counter += 1
            return
        if size > self._heap[0][0]:
            heapq.heapreplace(self._heap, (size, self._counter, item))
            self._counter += 1

    def items(self) -> list[object]:
        rows = sorted(self._heap, key=lambda row: (-row[0], row[1]))
        return [row[2] for row in rows]


def _extension_for(name: str) -> str:
    suffix = Path(name).suffix.lower().strip(".")
    return suffix or "(none)"


def _to_posix(path: str) -> str:
    return Path(path).as_posix()


def _child_row(record: DirectoryRecord, size: int, kind: str) -> dict[str, object]:
    return {
        "name": record.name if kind == "directory" else Path(record.path).name,
        "path": record.path,
        "size": size,
        "kind": kind,
    }


def _directory_payload(record: DirectoryRecord) -> dict[str, object]:
    return {
        "path": record.path,
        "parent": record.parent,
        "name": record.name,
        "depth": record.depth,
        "size": record.total_size,
        "fileCount": record.file_count,
        "directoryCount": record.directory_count,
        "directFileSize": record.direct_file_size,
        "directFileCount": record.direct_file_count,
    }


def _file_payload(record: FileRecord) -> dict[str, object]:
    return {
        "path": record.path,
        "parent": record.parent,
        "name": record.name,
        "size": record.size,
        "extension": record.extension,
        "modifiedAt": record.modified_at,
    }


def scan_directory(
    root: str | os.PathLike[str],
    options: ScanOptions | None = None,
    progress_callback: Callable[[ScanProgress], None] | None = None,
) -> ScanStats:
    scan_options = options or ScanOptions()
    root_path = Path(root).expanduser().resolve()
    if not root_path.exists():
        raise FileNotFoundError(f"Path does not exist: {root_path}")
    if not root_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root_path}")

    started_wall = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat()

    root_str = _to_posix(str(root_path))
    file_top = TopN(scan_options.max_files)
    directory_top = TopN(scan_options.max_directories)
    extension_sizes: dict[str, int] = {}
    errors: list[str] = []
    root_children: list[dict[str, object]] = []
    progress_total_size = 0
    progress_directories_seen = 0
    progress_last_emit = started_wall

    @dataclass(slots=True)
    class Frame:
        path: Path
        parent: str | None
        name: str
        depth: int
        iterator: object | None = None
        total_size: int = 0
        file_count: int = 0
        directory_count: int = 0
        direct_file_size: int = 0
        direct_file_count: int = 0

    stack: list[Frame] = [Frame(path=root_path, parent=None, name=root_path.name or root_str, depth=0)]
    root_record: DirectoryRecord | None = None

    while stack:
        frame = stack[-1]
        frame_str = _to_posix(str(frame.path))

        if frame.iterator is None:
            progress_directories_seen += 1
            try:
                frame.iterator = os.scandir(frame.path)
            except OSError as exc:
                errors.append(f"{frame_str}: {exc.strerror or exc}")
                frame.iterator = iter(())

        try:
            entry = next(frame.iterator)
        except OSError as exc:
            errors.append(f"{frame_str}: {exc.strerror or exc}")
            if hasattr(frame.iterator, "close"):
                frame.iterator.close()
            frame.iterator = iter(())
            continue
        except StopIteration:
            if hasattr(frame.iterator, "close"):
                frame.iterator.close()
            record = DirectoryRecord(
                path=frame_str,
                parent=frame.parent,
                name=frame.name,
                depth=frame.depth,
                total_size=frame.total_size + frame.direct_file_size,
                file_count=frame.file_count + frame.direct_file_count,
                directory_count=frame.directory_count,
                direct_file_size=frame.direct_file_size,
                direct_file_count=frame.direct_file_count,
            )
            stack.pop()
            directory_top.add(record.total_size, record)

            if stack:
                parent = stack[-1]
                parent.total_size += record.total_size
                parent.file_count += record.file_count
                parent.directory_count += 1 + record.directory_count
                if parent.depth == 0:
                    root_children.append(_child_row(record, record.total_size, "directory"))
            else:
                root_record = record
            continue

        name = entry.name
        if not scan_options.include_hidden and name.startswith("."):
            continue

        entry_path = Path(entry.path)
        entry_str = _to_posix(str(entry_path))
        if entry_str in scan_options.exclude_paths:
            continue
        try:
            if entry.is_symlink():
                continue
            if entry.is_dir(follow_symlinks=False):
                stack.append(
                    Frame(
                        path=entry_path,
                        parent=frame_str,
                        name=name,
                        depth=frame.depth + 1,
                    )
                )
                continue
            if not entry.is_file(follow_symlinks=False):
                continue

            entry_stat = entry.stat(follow_symlinks=False)
            if not stat.S_ISREG(entry_stat.st_mode):
                continue

            size = entry_stat.st_blocks * 512
            progress_total_size += size
            frame.direct_file_size += size
            frame.direct_file_count += 1
            extension = _extension_for(name)
            extension_sizes[extension] = extension_sizes.get(extension, 0) + size
            file_top.add(
                size,
                FileRecord(
                    path=entry_str,
                    parent=frame_str,
                    name=name,
                    size=size,
                    extension=extension,
                    modified_at=entry_stat.st_mtime,
                ),
            )
            if frame.depth == 0:
                root_children.append(
                    {
                        "name": name,
                        "path": entry_str,
                        "size": size,
                        "kind": "file",
                    }
                )
        except OSError as exc:
            errors.append(f"{entry_str}: {exc.strerror or exc}")

        if progress_callback is not None:
            now = time.perf_counter()
            if now - progress_last_emit >= 0.12:
                progress_callback(
                    ScanProgress(
                        current_path=frame_str,
                        files_seen=file_top.seen,
                        directories_seen=progress_directories_seen,
                        total_size=progress_total_size,
                        errors=len(errors),
                        depth=frame.depth,
                    )
                )
                progress_last_emit = now

    if root_record is None:
        raise RuntimeError(f"Failed to scan directory: {root_str}")

    root_children.sort(key=lambda row: (-int(row["size"]), str(row["name"])))

    extension_rows = [
        {"extension": extension, "size": size}
        for extension, size in sorted(extension_sizes.items(), key=lambda item: (-item[1], item[0]))
    ]

    retained_files = file_top.items()
    retained_directories = directory_top.items()

    finished_at = datetime.now(timezone.utc).isoformat()
    duration = time.perf_counter() - started_wall
    if progress_callback is not None:
        progress_callback(
            ScanProgress(
                current_path=root_str,
                files_seen=file_top.seen,
                directories_seen=progress_directories_seen,
                total_size=progress_total_size,
                errors=len(errors),
                depth=0,
                done=True,
            )
        )
    return ScanStats(
        root_path=root_str,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration,
        total_size=root_record.total_size,
        file_count=root_record.file_count,
        directory_count=root_record.directory_count,
        retained_files=len(retained_files),
        retained_directories=len(retained_directories),
        truncated_files=max(0, file_top.seen - len(retained_files)),
        truncated_directories=max(0, directory_top.seen - len(retained_directories)),
        scanned_hidden=scan_options.include_hidden,
        file_alert_bytes=None,
        directory_alert_bytes=None,
        errors=errors,
        root_children=root_children[:200],
        directories=[_directory_payload(record) for record in retained_directories],
        files=[_file_payload(record) for record in retained_files],
        extensions=extension_rows[:50],
    )
