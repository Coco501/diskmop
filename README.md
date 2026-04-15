# diskmop

`diskmop` is a lightweight CLI that scans a directory tree and generates a modern, interactive HTML disk usage report.

It is designed to handle deep and large trees without recursive Python calls. Very large scans can take a long time, which is acceptable by design; the scanner prioritizes correctness, predictable memory usage, and a usable output report.

## Features

- Iterative directory walk for deep trees
- Self-contained HTML report with no external assets
- Largest files and directories tables with search and sorting
- Root-child usage visualization
- Extension breakdown
- Truncation controls so huge trees do not generate unusable HTML

## Install

```bash
python -m pip install .
```

## Usage

```bash
diskmop /path/to/data
diskmop /path/to/data --output report.html
diskmop /path/to/data --max-files 10000 --max-directories 5000
diskmop /path/to/data --flag-files-over 10GB --flag-directories-over 500GB
```

## Notes

- Symlinked directories are not followed.
- Permission errors and broken entries are reported in the generated HTML.
- For very large trees, the report keeps the largest files and directories by default so the HTML remains workable.
