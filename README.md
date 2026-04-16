# diskmop

`diskmop` is a lightweight CLI that scans a directory tree and generates a modern, interactive HTML disk usage report.

It is designed to handle deep and large trees without recursive Python calls. Very large scans can take a long time, which is acceptable by design; the scanner prioritizes correctness, predictable memory usage, and a usable output report.

## Features

- Iterative directory walk for deep trees
- Self-contained HTML report with no external assets
- Largest files and directories tables with search, pagination, and collapsible sections
- Root-child usage visualization
- Extension breakdown
- Saved theme palette controls directly in the report UI
- Collision-safe output naming when a report file already exists
- Live CLI progress feedback during long scans
- Truncation controls so huge trees do not generate unusable HTML

## Install

```bash
pipx install .
```

For development:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

## Usage

```
diskmop [path] [options]
```

`path` defaults to the current directory.

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `-h`, `--help` | | Show help and exit |
| `-o`, `--output PATH` | `diskmop-report.html` | HTML report destination |
| `--max-files N` | 5000 | Maximum files to embed in the report |
| `--max-directories N` | 2000 | Maximum directories to embed in the report |
| `-H`, `--hide-hidden` | off | Skip entries whose names start with a dot |
| `-f`, `--flag SIZE` | off | Mark files and directories larger than this size in the report |

### `--flag` / `-f` size format

Accepts a number followed by a unit suffix (case-insensitive):

| Suffix | Unit |
|--------|------|
| `kb` or `k` | Kibibytes (1024 B) |
| `mb` or `m` | Mebibytes (1024 KB) |
| `gb` or `g` | Gibibytes (1024 MB) |
| `tb` or `t` | Tebibytes (1024 GB) |

Bare `b` (bytes) is not accepted. A bare number (no suffix) is interpreted as bytes.

### Examples

```bash
diskmop /path/to/data
diskmop /path/to/data -o report.html
diskmop /path/to/data --max-files 10000 --max-directories 5000
diskmop /path/to/data -f 10gb
diskmop /path/to/data -f 500M
diskmop /path/to/data -f 2T -H
```

## Shell completion

`diskmop` supports tab completion in bash, zsh, and fish via [`argcomplete`](https://github.com/kislyuk/argcomplete).

### Bash

Add to `~/.bashrc`:

```bash
eval "$(register-python-argcomplete diskmop)"
```

### Zsh

Add to `~/.zshrc`:

```zsh
autoload -U bashcompinit && bashcompinit
eval "$(register-python-argcomplete diskmop)"
```

### Fish

```fish
register-python-argcomplete --shell fish diskmop | source
```

Or, to enable completion for all `argcomplete`-enabled tools at once, run once:

```bash
activate-global-python-argcomplete
```

## Notes

- Symlinked directories are not followed.
- Permission errors and broken entries are reported in the generated HTML.
- For very large trees, the report keeps the largest files and directories by default so the HTML remains workable.
