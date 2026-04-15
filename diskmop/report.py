from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from diskmop.scanner import ScanStats


def _fmt_bytes(value: int) -> str:
    suffixes = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(value)
    for suffix in suffixes:
        if size < 1024 or suffix == suffixes[-1]:
            if suffix == "B":
                return f"{int(size)} {suffix}"
            return f"{size:.1f} {suffix}"
        size /= 1024
    return f"{value} B"


def render_report(stats: ScanStats) -> str:
    payload = {
        "meta": {
            "rootPath": stats.root_path,
            "startedAt": stats.started_at,
            "finishedAt": stats.finished_at,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "durationSeconds": stats.duration_seconds,
            "totalSize": stats.total_size,
            "fileCount": stats.file_count,
            "directoryCount": stats.directory_count,
            "retainedFiles": stats.retained_files,
            "retainedDirectories": stats.retained_directories,
            "truncatedFiles": stats.truncated_files,
            "truncatedDirectories": stats.truncated_directories,
            "scannedHidden": stats.scanned_hidden,
            "fileAlertBytes": stats.file_alert_bytes,
            "directoryAlertBytes": stats.directory_alert_bytes,
            "errors": stats.errors,
        },
        "rootChildren": stats.root_children,
        "directories": stats.directories,
        "files": stats.files,
        "extensions": stats.extensions,
    }
    data = json.dumps(payload, separators=(",", ":"))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>diskmop report</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f7fb;
      --panel: rgba(255, 255, 255, 0.88);
      --panel-strong: #ffffff;
      --text: #0f172a;
      --muted: #5b6474;
      --line: rgba(148, 163, 184, 0.22);
      --accent: #1463ff;
      --accent-soft: rgba(20, 99, 255, 0.12);
      --accent-2: #00a67e;
      --danger: #c73b34;
      --shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
      --radius: 20px;
      --radius-sm: 14px;
      --font-ui: "IBM Plex Sans", "Segoe UI", sans-serif;
      --font-mono: "IBM Plex Mono", "SFMono-Regular", monospace;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; min-height: 100%; background:
      radial-gradient(circle at top left, rgba(20,99,255,.10), transparent 28rem),
      radial-gradient(circle at top right, rgba(0,166,126,.10), transparent 24rem),
      var(--bg);
      color: var(--text);
      font-family: var(--font-ui);
    }}
    body {{ padding: 32px 20px 48px; }}
    .shell {{ max-width: 1320px; margin: 0 auto; }}
    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1.6fr) minmax(320px, 1fr);
      gap: 18px;
      margin-bottom: 18px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(14px);
    }}
    .hero-card {{ padding: 28px; }}
    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 7px 12px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .08em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 16px 0 12px;
      font-size: clamp(2rem, 4vw, 3.4rem);
      line-height: .98;
      letter-spacing: -.05em;
    }}
    .subtle {{
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
      max-width: 68ch;
    }}
    .path {{
      margin-top: 18px;
      padding: 14px 16px;
      border-radius: 16px;
      background: rgba(15, 23, 42, 0.04);
      font-family: var(--font-mono);
      font-size: 13px;
      overflow: auto;
      white-space: nowrap;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}
    .stat {{
      padding: 18px;
      border-radius: 18px;
      background: var(--panel-strong);
      border: 1px solid var(--line);
    }}
    .stat .label {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .08em;
      font-weight: 700;
    }}
    .stat .value {{
      margin-top: 8px;
      font-size: clamp(1.35rem, 2vw, 2rem);
      font-weight: 700;
      letter-spacing: -.03em;
    }}
    .meta {{
      margin-top: 14px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.7;
    }}
    .grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
      gap: 18px;
      margin-bottom: 18px;
    }}
    .section {{ padding: 22px; }}
    .section h2 {{
      margin: 0 0 6px;
      font-size: 1.1rem;
      letter-spacing: -.03em;
    }}
    .section p {{
      margin: 0 0 18px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.6;
    }}
    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 16px;
    }}
    .control {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 12px 14px;
      border-radius: 14px;
      background: rgba(15, 23, 42, 0.04);
      border: 1px solid rgba(148, 163, 184, 0.12);
    }}
    input, select {{
      border: 0;
      outline: none;
      background: transparent;
      color: var(--text);
      font: inherit;
      min-width: 0;
    }}
    input[type="search"] {{ width: min(28rem, 58vw); }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      padding: 12px 10px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-size: 12px;
      letter-spacing: .06em;
      text-transform: uppercase;
      cursor: pointer;
      user-select: none;
    }}
    tbody tr:hover {{ background: rgba(20, 99, 255, 0.045); }}
    .name-cell {{
      font-weight: 600;
      line-height: 1.45;
    }}
    .path-cell {{
      color: var(--muted);
      font-size: 12px;
      font-family: var(--font-mono);
      word-break: break-word;
    }}
    .tag {{
      display: inline-flex;
      padding: 4px 8px;
      border-radius: 999px;
      background: rgba(15, 23, 42, 0.05);
      font-size: 12px;
      color: var(--muted);
    }}
    .tag.alert {{
      background: rgba(199, 59, 52, 0.12);
      color: var(--danger);
      font-weight: 700;
    }}
    .bars {{
      display: grid;
      gap: 12px;
    }}
    .bar-row {{ display: grid; gap: 7px; }}
    .bar-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      font-size: 14px;
    }}
    .bar-track {{
      height: 13px;
      background: rgba(148, 163, 184, 0.16);
      border-radius: 999px;
      overflow: hidden;
    }}
    .bar-fill {{
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--accent), #39a0ff);
    }}
    .bar-fill.alert {{
      background: linear-gradient(90deg, #d3532c, #ff8c5a);
    }}
    .ext-list {{
      display: grid;
      gap: 10px;
    }}
    .ext-row {{
      display: grid;
      grid-template-columns: 90px 1fr auto;
      gap: 12px;
      align-items: center;
      font-size: 14px;
    }}
    .ext-label {{
      font-family: var(--font-mono);
      color: var(--muted);
    }}
    .ext-bar {{
      height: 10px;
      border-radius: 999px;
      background: rgba(148, 163, 184, 0.16);
      overflow: hidden;
    }}
    .ext-bar > span {{
      display: block;
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--accent-2), #27d3a3);
    }}
    .notice {{
      margin-top: 16px;
      padding: 14px 16px;
      border-radius: 16px;
      background: rgba(199, 59, 52, 0.08);
      color: var(--danger);
      font-size: 14px;
      line-height: 1.6;
    }}
    .empty {{
      padding: 18px;
      border-radius: 16px;
      background: rgba(15, 23, 42, 0.04);
      color: var(--muted);
      font-size: 14px;
    }}
    @media (max-width: 980px) {{
      .hero, .grid {{ grid-template-columns: 1fr; }}
      .stats {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 700px) {{
      body {{ padding-inline: 14px; }}
      .hero-card, .section {{ padding: 18px; }}
      .stats {{ grid-template-columns: 1fr; }}
      .ext-row {{ grid-template-columns: 1fr; }}
      th:nth-child(4), td:nth-child(4) {{ display: none; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div class="panel hero-card">
        <div class="eyebrow">diskmop report</div>
        <h1>Disk usage, surfaced cleanly.</h1>
        <p class="subtle">This report summarizes one filesystem subtree, keeps the heaviest items visible first, and stays responsive even when the original scan covered a very large directory tree.</p>
        <div class="path" id="root-path"></div>
      </div>
      <div class="panel hero-card">
        <div class="stats" id="stats"></div>
        <div class="meta" id="meta"></div>
      </div>
    </section>

    <section class="grid">
      <div class="panel section">
        <h2>Top-Level Space Map</h2>
        <p>Largest immediate children of the scanned root, useful for deciding where to drill in first.</p>
        <div class="bars" id="root-children"></div>
      </div>
      <div class="panel section">
        <h2>Extension Breakdown</h2>
        <p>Approximate size share by file extension across the scanned tree.</p>
        <div class="ext-list" id="extensions"></div>
      </div>
    </section>

    <section class="panel section" style="margin-bottom: 18px;">
      <h2>Largest Directories</h2>
      <p>These are the heaviest directories retained in the report dataset. Search and sort are client-side.</p>
      <div class="controls">
        <label class="control">
          <span>Search</span>
          <input type="search" id="directory-search" placeholder="Filter by name or path">
        </label>
      </div>
      <div id="directory-table-wrap"></div>
    </section>

    <section class="panel section">
      <h2>Largest Files</h2>
      <p>The file table focuses on the largest files first so the report remains useful for big trees.</p>
      <div class="controls">
        <label class="control">
          <span>Search</span>
          <input type="search" id="file-search" placeholder="Filter by file, extension, or path">
        </label>
      </div>
      <div id="file-table-wrap"></div>
      <div id="notices"></div>
    </section>
  </div>

  <script id="diskmop-data" type="application/json">{data}</script>
  <script>
    const data = JSON.parse(document.getElementById("diskmop-data").textContent);

    const fmtBytes = (value) => {{
      const suffixes = ["B", "KB", "MB", "GB", "TB", "PB"];
      let size = Number(value);
      for (const suffix of suffixes) {{
        if (size < 1024 || suffix === suffixes[suffixes.length - 1]) {{
          return suffix === "B" ? `${{Math.round(size)}} ${{suffix}}` : `${{size.toFixed(1)}} ${{suffix}}`;
        }}
        size /= 1024;
      }}
      return `${{value}} B`;
    }};

    const fmtInt = (value) => new Intl.NumberFormat().format(value);
    const fmtDate = (value) => new Date(value).toLocaleString();
    const byId = (id) => document.getElementById(id);

    byId("root-path").textContent = data.meta.rootPath;

    const stats = [
      ["Total Size", fmtBytes(data.meta.totalSize)],
      ["Files", fmtInt(data.meta.fileCount)],
      ["Directories", fmtInt(data.meta.directoryCount)],
      ["Scan Time", `${{data.meta.durationSeconds.toFixed(2)}}s`],
    ];
    byId("stats").innerHTML = stats.map(([label, value]) => `
      <div class="stat">
        <div class="label">${{label}}</div>
        <div class="value">${{value}}</div>
      </div>
    `).join("");

    byId("meta").innerHTML = `
      <div>Started: ${{fmtDate(data.meta.startedAt)}}</div>
      <div>Finished: ${{fmtDate(data.meta.finishedAt)}}</div>
      <div>Hidden entries included: ${{data.meta.scannedHidden ? "yes" : "no"}}</div>
      <div>File flag threshold: ${{data.meta.fileAlertBytes ? fmtBytes(data.meta.fileAlertBytes) : "off"}}</div>
      <div>Directory flag threshold: ${{data.meta.directoryAlertBytes ? fmtBytes(data.meta.directoryAlertBytes) : "off"}}</div>
    `;

    const rootMax = Math.max(1, ...data.rootChildren.map((row) => row.size));
    byId("root-children").innerHTML = data.rootChildren.length ? data.rootChildren.slice(0, 18).map((row) => `
      <div class="bar-row">
        <div class="bar-head">
          <div>
            <strong>${{row.name}}</strong>
            <span class="tag">${{row.kind}}</span>
            ${{
              row.kind === "file" && data.meta.fileAlertBytes && row.size >= data.meta.fileAlertBytes
                ? `<span class="tag alert">flagged</span>`
                : row.kind === "directory" && data.meta.directoryAlertBytes && row.size >= data.meta.directoryAlertBytes
                  ? `<span class="tag alert">flagged</span>`
                  : ""
            }}
          </div>
          <div>${{fmtBytes(row.size)}}</div>
        </div>
        <div class="bar-track"><div class="bar-fill ${{
          row.kind === "file" && data.meta.fileAlertBytes && row.size >= data.meta.fileAlertBytes
            ? "alert"
            : row.kind === "directory" && data.meta.directoryAlertBytes && row.size >= data.meta.directoryAlertBytes
              ? "alert"
              : ""
        }}" style="width: ${{(row.size / rootMax) * 100}}%"></div></div>
      </div>
    `).join("") : `<div class="empty">No child entries were retained for visualization.</div>`;

    const extMax = Math.max(1, ...data.extensions.map((row) => row.size));
    byId("extensions").innerHTML = data.extensions.length ? data.extensions.slice(0, 14).map((row) => `
      <div class="ext-row">
        <div class="ext-label">${{row.extension}}</div>
        <div class="ext-bar"><span style="width: ${{(row.size / extMax) * 100}}%"></span></div>
        <div>${{fmtBytes(row.size)}}</div>
      </div>
    `).join("") : `<div class="empty">No regular files were found in the scanned subtree.</div>`;

    function buildTable({{ mountId, rows, searchId, defaultSort }}) {{
      let currentSort = defaultSort;
      let currentDir = "desc";

      const render = () => {{
        const search = byId(searchId).value.trim().toLowerCase();
        const filtered = rows.filter((row) => JSON.stringify(row).toLowerCase().includes(search));
        filtered.sort((a, b) => {{
          const left = a[currentSort];
          const right = b[currentSort];
          if (typeof left === "number" && typeof right === "number") {{
            return currentDir === "asc" ? left - right : right - left;
          }}
          return currentDir === "asc"
            ? String(left).localeCompare(String(right))
            : String(right).localeCompare(String(left));
        }});

        const isDirectory = rows === data.directories;
        const table = `
          <table>
            <thead>
              <tr>
                <th data-key="name">Name</th>
                <th data-key="size">Size</th>
                <th data-key="${{isDirectory ? "fileCount" : "extension"}}">${{isDirectory ? "Files" : "Extension"}}</th>
                <th data-key="${{isDirectory ? "directoryCount" : "modifiedAt"}}">${{isDirectory ? "Subdirs" : "Modified"}}</th>
              </tr>
            </thead>
            <tbody>
              ${{
                filtered.length ? filtered.map((row) => {{
                  const flagged = isDirectory
                    ? data.meta.directoryAlertBytes && row.size >= data.meta.directoryAlertBytes
                    : data.meta.fileAlertBytes && row.size >= data.meta.fileAlertBytes;
                  return isDirectory ? `
                  <tr>
                    <td>
                      <div class="name-cell">${{row.name}} ${{flagged ? '<span class="tag alert">flagged</span>' : ""}}</div>
                      <div class="path-cell">${{row.path}}</div>
                    </td>
                    <td>${{fmtBytes(row.size)}}</td>
                    <td>${{fmtInt(row.fileCount)}}</td>
                    <td>${{fmtInt(row.directoryCount)}}</td>
                  </tr>
                ` : `
                  <tr>
                    <td>
                      <div class="name-cell">${{row.name}} ${{flagged ? '<span class="tag alert">flagged</span>' : ""}}</div>
                      <div class="path-cell">${{row.path}}</div>
                    </td>
                    <td>${{fmtBytes(row.size)}}</td>
                    <td><span class="tag">${{row.extension}}</span></td>
                    <td>${{fmtDate(row.modifiedAt * 1000)}}</td>
                  </tr>
                `;
                }}).join("") : `<tr><td colspan="4"><div class="empty">No rows match the current filter.</div></td></tr>`
              }}
            </tbody>
          </table>
        `;
        byId(mountId).innerHTML = table;
        byId(mountId).querySelectorAll("th").forEach((th) => {{
          th.addEventListener("click", () => {{
            const key = th.dataset.key;
            if (currentSort === key) {{
              currentDir = currentDir === "asc" ? "desc" : "asc";
            }} else {{
              currentSort = key;
              currentDir = key === "name" || key === "extension" ? "asc" : "desc";
            }}
            render();
          }});
        }});
      }};

      byId(searchId).addEventListener("input", render);
      render();
    }}

    buildTable({{ mountId: "directory-table-wrap", rows: data.directories, searchId: "directory-search", defaultSort: "size" }});
    buildTable({{ mountId: "file-table-wrap", rows: data.files, searchId: "file-search", defaultSort: "size" }});

    const notices = [];
    if (data.meta.truncatedDirectories > 0) {{
      notices.push(`Directory table truncated. ${{fmtInt(data.meta.truncatedDirectories)}} directories were scanned but not embedded in the HTML.`);
    }}
    if (data.meta.truncatedFiles > 0) {{
      notices.push(`File table truncated. ${{fmtInt(data.meta.truncatedFiles)}} files were scanned but not embedded in the HTML.`);
    }}
    if (data.meta.directoryAlertBytes) {{
      const flaggedDirectories = data.directories.filter((row) => row.size >= data.meta.directoryAlertBytes).length;
      notices.push(`Flagged directories in report dataset: ${{fmtInt(flaggedDirectories)}} at or above ${{fmtBytes(data.meta.directoryAlertBytes)}}.`);
    }}
    if (data.meta.fileAlertBytes) {{
      const flaggedFiles = data.files.filter((row) => row.size >= data.meta.fileAlertBytes).length;
      notices.push(`Flagged files in report dataset: ${{fmtInt(flaggedFiles)}} at or above ${{fmtBytes(data.meta.fileAlertBytes)}}.`);
    }}
    if (data.meta.errors.length > 0) {{
      notices.push(`Encountered ${{fmtInt(data.meta.errors.length)}} filesystem errors. Sample: ${{data.meta.errors.slice(0, 5).join(" | ")}}`);
    }}
    byId("notices").innerHTML = notices.map((text) => `<div class="notice">${{text}}</div>`).join("");
  </script>
</body>
</html>
"""


def write_report(output_path: str | Path, stats: ScanStats) -> Path:
    destination = Path(output_path).expanduser().resolve()
    destination.write_text(render_report(stats), encoding="utf-8")
    return destination
