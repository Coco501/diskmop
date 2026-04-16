# diskmop

`diskmop` is a lightweight CLI tool that recursively scans a directory and generates an interactive HTML disk usage report.

It is designed to handle deep and large trees without recursive Python calls. Very large scans can take a long time; the scanner prioritizes correctness, predictable memory usage, and a usable output report.

## Features

- Self-contained HTML report with no external assets
- "Largest Files" and "Largest Directories" tables with search and sorting features
- Breakdown of file extension statistics

## Notes

- Symlinked directories are not followed.
- Permission errors and broken entries are reported in the generated HTML.
- For very large trees, the report keeps the largest files and directories by default so the HTML remains workable.

## Install

```bash
pipx install .
```

For development:

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
| `-H`, `--hide-hidden` | off | Skip entries whose names start with a dot |
| `-f`, `--flag SIZE` | off | Mark files and directories larger than this size in the report |
| `--no-open` | off | Do not open the report in a browser after generation |
| `--max-files N` | 5000 | Maximum files to embed in the report |
| `--max-directories N` | 2000 | Maximum directories to embed in the report |

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
diskmop
diskmop /path/to/data -o report.html
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

## AI Disclaimer
Please consider that this project was almost entirely written by a combination of Claude Code and Codex. Take it with a grain of salt.
