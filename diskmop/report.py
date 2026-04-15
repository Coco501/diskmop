from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import quote

from diskmop.scanner import ScanStats


def _favicon_href() -> str:
    svg = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <defs>
    <radialGradient id="disk" cx="34%" cy="28%" r="78%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="38%" stop-color="#d8dde5"/>
      <stop offset="72%" stop-color="#98a1ad"/>
      <stop offset="100%" stop-color="#6e7783"/>
    </radialGradient>
    <linearGradient id="handle" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4f5561"/>
      <stop offset="100%" stop-color="#242935"/>
    </linearGradient>
  </defs>
  <circle cx="26" cy="32" r="19" fill="url(#disk)" stroke="#2a3140" stroke-width="2.5"/>
  <circle cx="26" cy="32" r="8" fill="none" stroke="#eef2f7" stroke-width="2"/>
  <path d="M18 20h4v4h-4zm4-4h4v4h-4zm4 4h4v4h-4z" fill="#ffffff" opacity=".92"/>
  <path d="M36 13l4 1.2-8.7 28.7-4-1.2z" fill="url(#handle)" stroke="#2a3140" stroke-width="1.1"/>
  <path d="M35 40l15 4.7-2.7 8.5-15-4.6z" fill="#c9ced6" stroke="#2a3140" stroke-width="1.3"/>
  <path d="M34.7 48.1l2.8 7.2m4.3-5.8l2.3 6.3m4.5-5.5l1.9 5.9" stroke="#2a3140" stroke-width="1.5" stroke-linecap="round"/>
</svg>
""".strip()
    return f"data:image/svg+xml,{quote(svg)}"


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
    favicon = _favicon_href()
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>diskmop report</title>
  <link rel="icon" href="{favicon}">
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
      --font-ui: "IBM Plex Sans", "Segoe UI", sans-serif;
      --font-mono: "IBM Plex Mono", "SFMono-Regular", monospace;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{
      margin: 0;
      min-height: 100%;
      background:
        radial-gradient(circle at top left, rgba(20,99,255,.10), transparent 28rem),
        radial-gradient(circle at top right, rgba(0,166,126,.10), transparent 24rem),
        var(--bg);
      color: var(--text);
      font-family: var(--font-ui);
    }}
    body {{ padding: 32px 20px 48px; }}
    button, input, select {{ font: inherit; color: inherit; }}
    .shell {{ max-width: 1320px; margin: 0 auto; }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 18px;
      margin-bottom: 18px;
    }}
    .settings-anchor {{ position: relative; flex: 0 0 auto; }}
    .settings-toggle {{
      width: 48px;
      height: 48px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: var(--panel);
      box-shadow: var(--shadow);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      backdrop-filter: blur(14px);
    }}
    .settings-toggle svg {{ width: 22px; height: 22px; stroke: var(--muted); }}
    .settings-panel {{
      position: absolute;
      top: calc(100% + 10px);
      right: 0;
      width: min(300px, 86vw);
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--panel-strong);
      box-shadow: var(--shadow);
      display: none;
      z-index: 20;
    }}
    .settings-panel.open {{ display: block; }}
    .settings-panel h3 {{
      margin: 0 0 8px;
      font-size: 1rem;
      letter-spacing: -.03em;
    }}
    .settings-panel p {{
      margin: 0 0 14px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.55;
    }}
    .picker-grid {{
      display: grid;
      gap: 12px;
    }}
    .picker {{
      display: grid;
      gap: 6px;
      font-size: 13px;
      color: var(--muted);
    }}
    .picker input {{
      width: 100%;
      min-height: 42px;
      border: 1px solid var(--line);
      background: #fff;
      border-radius: 12px;
      padding: 4px;
    }}
    .settings-actions {{
      display: flex;
      justify-content: space-between;
      gap: 10px;
      margin-top: 14px;
    }}
    .mini-btn {{
      border: 1px solid var(--line);
      background: var(--panel);
      padding: 10px 12px;
      border-radius: 12px;
      cursor: pointer;
    }}
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
    .report-for {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 600;
      letter-spacing: .04em;
      text-transform: uppercase;
    }}
    .path {{
      margin-top: 10px;
      padding: 18px 20px;
      border-radius: 16px;
      background:
        linear-gradient(135deg, rgba(20, 99, 255, 0.12), rgba(255, 255, 255, 0.96)),
        rgba(15, 23, 42, 0.04);
      border: 1px solid rgba(20, 99, 255, 0.18);
      box-shadow: inset 0 1px 0 rgba(255,255,255,.8);
      font-family: var(--font-mono);
      font-size: 14px;
      color: #0b214f;
      font-weight: 600;
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
    .section {{
      padding: 22px;
    }}
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
    .bars, .ext-list, .notice-stack {{
      display: grid;
      gap: 12px;
    }}
    .bar-row {{
      display: grid;
      gap: 7px;
    }}
    .bar-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      font-size: 14px;
      align-items: center;
    }}
    .bar-left {{
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
      flex-wrap: wrap;
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
      background: linear-gradient(90deg, var(--accent), color-mix(in srgb, var(--accent), white 30%));
    }}
    .bar-fill.alert {{
      background: linear-gradient(90deg, #d3532c, #ff8c5a);
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
      background: linear-gradient(90deg, var(--accent-2), color-mix(in srgb, var(--accent-2), white 30%));
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
    .section-card {{
      margin-bottom: 18px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: hidden;
    }}
    .section-header {{
      display: flex;
      justify-content: flex-start;
      gap: 12px;
      align-items: center;
      padding: 20px 22px;
    }}
    .section-card.is-open .section-header {{
      border-bottom: 1px solid var(--line);
    }}
    .summary-copy h2 {{
      margin: 0 0 4px;
      font-size: 1.12rem;
      letter-spacing: -.03em;
    }}
    .summary-copy p {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.55;
    }}
    .collapse-btn {{
      border: 1px solid var(--line);
      background: var(--panel-strong);
      border-radius: 12px;
      width: 42px;
      height: 42px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      flex: 0 0 auto;
    }}
    .collapse-btn svg {{
      width: 20px;
      height: 20px;
      stroke: var(--muted);
      fill: none;
      stroke-width: 2.2;
      stroke-linecap: round;
      stroke-linejoin: round;
      transition: transform .16s ease;
    }}
    .collapse-btn[aria-expanded="false"] svg {{
      transform: rotate(-90deg);
    }}
    .section-body {{
      padding: 18px 22px 22px;
    }}
    .section-body[hidden] {{
      display: none;
    }}
    .controls {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 14px;
    }}
    .control-group {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      width: 100%;
    }}
    .search-control {{
      flex: 1 1 420px;
      display: grid;
      grid-template-columns: auto minmax(0, 1fr);
      align-items: center;
      gap: 12px;
      padding: 0;
      border-radius: 0;
      background: transparent;
      border: 0;
      box-shadow: none;
    }}
    .search-control span {{
      font-size: 15px;
      font-weight: 500;
      color: var(--text);
    }}
    .search-input-wrap {{
      position: relative;
    }}
    .search-input-wrap input {{
      width: 100%;
      border: 1px solid rgba(148, 163, 184, 0.45);
      background: #fff;
      border-radius: 14px;
      padding: 11px 14px;
      outline: none;
      transition: border-color .15s ease, box-shadow .15s ease;
    }}
    .search-input-wrap input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent), white 84%);
    }}
    .rows-control {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 0;
      border-radius: 0;
      background: transparent;
      border: 0;
      box-shadow: none;
      white-space: nowrap;
    }}
    .rows-control select {{
      border: 1px solid rgba(148, 163, 184, 0.45);
      background: #fff;
      border-radius: 12px;
      padding: 8px 10px;
      outline: none;
    }}
    .table-meta {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 12px;
      color: var(--muted);
      font-size: 13px;
    }}
    .table-shell {{
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--panel-strong);
    }}
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
    tbody tr:hover {{
      background: color-mix(in srgb, var(--accent), white 94%);
    }}
    .name-cell {{
      font-weight: 600;
      line-height: 1.45;
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .path-cell {{
      color: var(--muted);
      font-size: 12px;
      font-family: var(--font-mono);
      word-break: break-word;
      margin-top: 4px;
    }}
    .pager {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 14px;
    }}
    .pager-controls {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .pager-btn {{
      border: 1px solid var(--line);
      background: var(--panel-strong);
      padding: 10px 12px;
      border-radius: 12px;
      cursor: pointer;
    }}
    .pager-btn[disabled] {{
      opacity: .45;
      cursor: default;
    }}
    .notice {{
      padding: 14px 16px;
      border-radius: 16px;
      background: rgba(199, 59, 52, 0.08);
      color: var(--danger);
      font-size: 14px;
      line-height: 1.55;
      border: 1px solid rgba(199, 59, 52, 0.12);
    }}
    .empty {{
      padding: 18px;
      border-radius: 16px;
      background: rgba(15, 23, 42, 0.04);
      color: var(--muted);
      font-size: 14px;
    }}
    .notes-list {{
      display: grid;
      gap: 12px;
    }}
    .note-item {{
      padding: 16px 18px;
      border-radius: 16px;
      background: var(--panel-strong);
      border: 1px solid var(--line);
      color: var(--text);
    }}
    .note-item.alert {{
      background: rgba(199, 59, 52, 0.08);
      color: var(--danger);
      border-color: rgba(199, 59, 52, 0.12);
    }}
    .note-item strong {{
      display: block;
      margin-bottom: 6px;
      font-size: 14px;
    }}
    .note-item p {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.6;
    }}
    @media (max-width: 980px) {{
      .hero, .grid {{
        grid-template-columns: 1fr;
      }}
      .stats {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}
    @media (max-width: 700px) {{
      body {{
        padding-inline: 14px;
      }}
      .stats {{
        grid-template-columns: 1fr;
      }}
      .grid {{
        grid-template-columns: 1fr;
      }}
      .ext-row {{
        grid-template-columns: 1fr;
      }}
      .search-control {{
        grid-template-columns: 1fr;
        align-items: stretch;
      }}
      th:nth-child(4), td:nth-child(4) {{
        display: none;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <div class="topbar">
      <div></div>
      <div class="settings-anchor">
        <button class="settings-toggle" id="settings-toggle" type="button" aria-label="Highlight colors">
          <svg viewBox="0 0 24 24" fill="none" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="3.25"></circle>
            <path d="m4.9 4.9 1.5 1.5"></path>
            <path d="m17.6 17.6 1.5 1.5"></path>
            <path d="m19.1 4.9-1.5 1.5"></path>
            <path d="m6.4 17.6-1.5 1.5"></path>
            <path d="M12 2.7v2"></path>
            <path d="M12 19.3v2"></path>
            <path d="M2.7 12h2"></path>
            <path d="M19.3 12h2"></path>
            <path d="M8.1 3.8h7.8l.7 2.1 2 .8 2-1 3.3 3.3-1 2 .8 2.1 2.1.7v4.4l-2.1.7-.8 2.1 1 2-3.3 3.3-2-1-2 .8-.7 2.1H8.1l-.7-2.1-2-.8-2 1-3.3-3.3 1-2-.8-2.1-2.1-.7v-4.4l2.1-.7.8-2.1-1-2 3.3-3.3 2 1 2-.8.7-2.1Z"></path>
          </svg>
        </button>
        <div class="settings-panel" id="settings-panel">
          <h3>Highlight Colors</h3>
          <p>Adjust the blue and green report accents.</p>
          <div class="picker-grid">
            <label class="picker">Blue bars<input type="color" id="picker-accent"></label>
            <label class="picker">Green bars<input type="color" id="picker-accent-2"></label>
          </div>
          <div class="settings-actions">
            <button class="mini-btn" id="reset-theme" type="button">Reset</button>
            <button class="mini-btn" id="close-settings" type="button">Close</button>
          </div>
        </div>
      </div>
    </div>

    <section class="hero">
      <div class="panel hero-card">
        <div class="eyebrow">diskmop report</div>
        <h1>diskmop</h1>
        <div class="report-for">report generated for:</div>
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
        <p>Largest immediate children of the scanned root.</p>
        <div class="bars" id="root-children"></div>
      </div>
      <div class="panel section">
        <h2>Extension Breakdown</h2>
        <p>Approximate size share by file extension.</p>
        <div class="ext-list" id="extensions"></div>
      </div>
    </section>

    <section class="section-card is-open" id="directories-section">
      <div class="section-header">
        <div class="summary-copy">
          <h2>Largest Directories</h2>
        </div>
      </div>
      <div class="section-body" id="directory-section-body">
        <div class="controls">
          <div class="control-group">
            <label class="search-control">
              <span>Search</span>
              <span class="search-input-wrap"><input type="search" id="directory-search" placeholder="Filter by name or path"></span>
            </label>
            <label class="rows-control">Rows
              <select id="directory-page-size">
                <option>25</option>
                <option selected>50</option>
                <option>100</option>
                <option>250</option>
              </select>
            </label>
          </div>
        </div>
        <div class="table-meta" id="directory-table-meta"></div>
        <div class="table-shell" id="directory-table-wrap"></div>
        <div class="pager" id="directory-pager"></div>
      </div>
    </section>

    <section class="section-card" id="files-section">
      <div class="section-header">
        <div class="summary-copy">
          <h2>Largest Files</h2>
        </div>
      </div>
      <div class="section-body" id="file-section-body">
        <div class="controls">
          <div class="control-group">
            <label class="search-control">
              <span>Search</span>
              <span class="search-input-wrap"><input type="search" id="file-search" placeholder="Filter by file, extension, or path"></span>
            </label>
            <label class="rows-control">Rows
              <select id="file-page-size">
                <option>25</option>
                <option selected>50</option>
                <option>100</option>
                <option>250</option>
              </select>
            </label>
          </div>
        </div>
        <div class="table-meta" id="file-table-meta"></div>
        <div class="table-shell" id="file-table-wrap"></div>
        <div class="pager" id="file-pager"></div>
      </div>
    </section>

    <section class="section-card is-open" id="scan-notes-section">
      <div class="section-header">
        <button class="collapse-btn" type="button" id="scan-notes-collapse" aria-expanded="true" aria-controls="scan-notes-body" aria-label="Collapse scan notes">
          <svg viewBox="0 0 20 20" aria-hidden="true">
            <path d="m4 12 6-6 6 6"></path>
          </svg>
        </button>
        <div class="summary-copy">
          <h2>Scan Notes</h2>
          <p>Retention limits, scan behavior, and any filesystem issues found during collection.</p>
        </div>
      </div>
      <div class="section-body" id="scan-notes-body">
        <div class="notes-list" id="notices"></div>
      </div>
    </section>
  </div>

  <script id="diskmop-data" type="application/json">{data}</script>
  <script>
    const data = JSON.parse(document.getElementById("diskmop-data").textContent);
    const byId = (id) => document.getElementById(id);
    const storageKey = "diskmop-highlight-theme-v1";
    const defaultTheme = {{
      accent: "#1463ff",
      accent2: "#00a67e",
    }};

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

    function hexToRgb(hex) {{
      const clean = hex.replace("#", "");
      const bigint = Number.parseInt(clean, 16);
      return {{
        r: (bigint >> 16) & 255,
        g: (bigint >> 8) & 255,
        b: bigint & 255,
      }};
    }}

    function applyTheme(theme) {{
      const root = document.documentElement;
      root.style.setProperty("--accent", theme.accent);
      root.style.setProperty("--accent-2", theme.accent2);
      const accent = hexToRgb(theme.accent);
      root.style.setProperty("--accent-soft", `rgba(${{accent.r}}, ${{accent.g}}, ${{accent.b}}, 0.12)`);
      localStorage.setItem(storageKey, JSON.stringify(theme));
      byId("picker-accent").value = theme.accent;
      byId("picker-accent-2").value = theme.accent2;
    }}

    function setupThemeControls() {{
      const stored = localStorage.getItem(storageKey);
      const initial = stored ? JSON.parse(stored) : defaultTheme;
      applyTheme(initial);

      byId("picker-accent").addEventListener("input", () => {{
        applyTheme({{
          accent: byId("picker-accent").value,
          accent2: byId("picker-accent-2").value,
        }});
      }});
      byId("picker-accent-2").addEventListener("input", () => {{
        applyTheme({{
          accent: byId("picker-accent").value,
          accent2: byId("picker-accent-2").value,
        }});
      }});
      byId("reset-theme").addEventListener("click", () => applyTheme(defaultTheme));
      byId("settings-toggle").addEventListener("click", () => {{
        byId("settings-panel").classList.toggle("open");
      }});
      byId("close-settings").addEventListener("click", () => {{
        byId("settings-panel").classList.remove("open");
      }});
      document.addEventListener("click", (event) => {{
        const anchor = document.querySelector(".settings-anchor");
        if (!anchor.contains(event.target)) {{
          byId("settings-panel").classList.remove("open");
        }}
      }});
    }}

    function setupSectionToggle(sectionId, buttonId, bodyId) {{
      const section = byId(sectionId);
      const button = byId(buttonId);
      const body = byId(bodyId);

      button.addEventListener("click", () => {{
        const isOpen = !body.hidden;
        body.hidden = isOpen;
        section.classList.toggle("is-open", !isOpen);
        button.setAttribute("aria-expanded", String(!isOpen));
        button.setAttribute("aria-label", `${{isOpen ? "Expand" : "Collapse"}} scan notes`);
      }});
    }}

    function entryFlagged(row, type) {{
      if (type === "directory") {{
        return data.meta.directoryAlertBytes && row.size >= data.meta.directoryAlertBytes;
      }}
      return data.meta.fileAlertBytes && row.size >= data.meta.fileAlertBytes;
    }}

    byId("root-path").textContent = data.meta.rootPath;
    byId("stats").innerHTML = [
      ["Total Size", fmtBytes(data.meta.totalSize)],
      ["Files", fmtInt(data.meta.fileCount)],
      ["Directories", fmtInt(data.meta.directoryCount)],
      ["Scan Time", `${{data.meta.durationSeconds.toFixed(2)}}s`],
    ].map(([label, value]) => `
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
          <div class="bar-left">
            <strong>${{row.name}}</strong>
            <span class="tag">${{row.kind}}</span>
            ${{entryFlagged(row, row.kind) ? '<span class="tag alert">flagged</span>' : ""}}
          </div>
          <div>${{fmtBytes(row.size)}}</div>
        </div>
        <div class="bar-track"><div class="bar-fill ${{entryFlagged(row, row.kind) ? "alert" : ""}}" style="width:${{(row.size / rootMax) * 100}}%"></div></div>
      </div>
    `).join("") : `<div class="empty">No child entries were retained for visualization.</div>`;

    const extMax = Math.max(1, ...data.extensions.map((row) => row.size));
    byId("extensions").innerHTML = data.extensions.length ? data.extensions.slice(0, 14).map((row) => `
      <div class="ext-row">
        <div class="ext-label">${{row.extension}}</div>
        <div class="ext-bar"><span style="width:${{(row.size / extMax) * 100}}%"></span></div>
        <div>${{fmtBytes(row.size)}}</div>
      </div>
    `).join("") : `<div class="empty">No regular files were found in the scanned subtree.</div>`;

    const notices = [];
    if (data.meta.truncatedDirectories > 0) {{
      notices.push({{
        title: "Directory retention limit reached",
        body: `The directory table excludes ${{fmtInt(data.meta.truncatedDirectories)}} additional rows so the report stays responsive.`,
        tone: "alert",
      }});
    }}
    if (data.meta.truncatedFiles > 0) {{
      notices.push({{
        title: "File retention limit reached",
        body: `The file table excludes ${{fmtInt(data.meta.truncatedFiles)}} additional rows so the report stays responsive.`,
        tone: "alert",
      }});
    }}
    notices.push({{
      title: "Scan configuration",
      body: `Hidden entries were ${{data.meta.scannedHidden ? "included" : "excluded"}}. File flag threshold is ${{data.meta.fileAlertBytes ? fmtBytes(data.meta.fileAlertBytes) : "off"}}. Directory flag threshold is ${{data.meta.directoryAlertBytes ? fmtBytes(data.meta.directoryAlertBytes) : "off"}}.`,
      tone: "neutral",
    }});
    if (data.meta.errors.length > 0) {{
      notices.push({{
        title: "Filesystem errors encountered",
        body: `Observed ${{fmtInt(data.meta.errors.length)}} filesystem errors while scanning. Sample: ${{data.meta.errors.slice(0, 4).join(" | ")}}`,
        tone: "alert",
      }});
    }}
    byId("notices").innerHTML = notices.length
      ? notices.map((note) => `
          <div class="note-item ${{note.tone === "alert" ? "alert" : ""}}">
            <strong>${{note.title}}</strong>
            <p>${{note.body}}</p>
          </div>
        `).join("")
      : `<div class="empty">No retention limits or scan issues were recorded for this run.</div>`;

    function buildTable(config) {{
      const state = {{
        sortKey: config.defaultSort,
        sortDir: config.defaultSort === "name" ? "asc" : "desc",
        page: 1,
        pageSize: Number(byId(config.pageSizeId).value),
      }};

      function filteredRows() {{
        const term = byId(config.searchId).value.trim().toLowerCase();
        const rows = config.rows.filter((row) => {{
          if (!term) return true;
          return JSON.stringify(row).toLowerCase().includes(term);
        }});
        rows.sort((left, right) => {{
          const a = left[state.sortKey];
          const b = right[state.sortKey];
          if (typeof a === "number" && typeof b === "number") {{
            return state.sortDir === "asc" ? a - b : b - a;
          }}
          return state.sortDir === "asc"
            ? String(a).localeCompare(String(b))
            : String(b).localeCompare(String(a));
        }});
        return rows;
      }}

      function render() {{
        state.pageSize = Number(byId(config.pageSizeId).value);
        const rows = filteredRows();
        const totalPages = Math.max(1, Math.ceil(rows.length / state.pageSize));
        state.page = Math.min(state.page, totalPages);
        const start = (state.page - 1) * state.pageSize;
        const pageRows = rows.slice(start, start + state.pageSize);

        byId(config.metaId).innerHTML = `
          <div>Showing <strong>${{pageRows.length ? fmtInt(start + 1) : "0"}}-${{fmtInt(start + pageRows.length)}}</strong> of <strong>${{fmtInt(rows.length)}}</strong> retained rows</div>
        `;
        if (!pageRows.length) {{
          byId(config.mountId).innerHTML = `<div class="empty">No rows match the current filter.</div>`;
        }} else {{
          byId(config.mountId).innerHTML = `
            <table>
              <thead>
                <tr>
                  ${{config.columns.map((col) => `<th data-key="${{col.key}}">${{col.label}}</th>`).join("")}}
                </tr>
              </thead>
              <tbody>
                ${{pageRows.map((row) => config.rowRenderer(row)).join("")}}
              </tbody>
            </table>
          `;
          byId(config.mountId).querySelectorAll("th").forEach((th) => {{
            th.addEventListener("click", () => {{
              const key = th.dataset.key;
              if (state.sortKey === key) {{
                state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
              }} else {{
                state.sortKey = key;
                state.sortDir = key === "name" || key === "extension" ? "asc" : "desc";
              }}
              render();
            }});
          }});
        }}

        byId(config.pagerId).innerHTML = `
          <div>Page <strong>${{fmtInt(state.page)}}</strong> of <strong>${{fmtInt(totalPages)}}</strong></div>
          <div class="pager-controls">
            <button class="pager-btn" type="button" data-action="prev" ${{state.page <= 1 ? "disabled" : ""}}>Previous</button>
            <button class="pager-btn" type="button" data-action="next" ${{state.page >= totalPages ? "disabled" : ""}}>Next</button>
          </div>
        `;
        byId(config.pagerId).querySelectorAll("[data-action]").forEach((button) => {{
          button.addEventListener("click", () => {{
            if (button.dataset.action === "prev" && state.page > 1) state.page -= 1;
            if (button.dataset.action === "next" && state.page < totalPages) state.page += 1;
            render();
          }});
        }});
      }}

      byId(config.searchId).addEventListener("input", () => {{
        state.page = 1;
        render();
      }});
      byId(config.pageSizeId).addEventListener("change", () => {{
        state.page = 1;
        render();
      }});
      render();
    }}

    buildTable({{
      rows: data.directories,
      defaultSort: "size",
      mountId: "directory-table-wrap",
      metaId: "directory-table-meta",
      pagerId: "directory-pager",
      searchId: "directory-search",
      pageSizeId: "directory-page-size",
      columns: [
        {{ key: "name", label: "Name" }},
        {{ key: "size", label: "Size" }},
        {{ key: "fileCount", label: "Files" }},
        {{ key: "directoryCount", label: "Subdirs" }},
      ],
      rowRenderer: (row) => `
        <tr>
          <td>
            <div class="name-cell">${{row.name}} ${{entryFlagged(row, "directory") ? '<span class="tag alert">flagged</span>' : ""}}</div>
            <div class="path-cell">${{row.path}}</div>
          </td>
          <td>${{fmtBytes(row.size)}}</td>
          <td>${{fmtInt(row.fileCount)}}</td>
          <td>${{fmtInt(row.directoryCount)}}</td>
        </tr>
      `,
    }});

    buildTable({{
      rows: data.files,
      defaultSort: "size",
      mountId: "file-table-wrap",
      metaId: "file-table-meta",
      pagerId: "file-pager",
      searchId: "file-search",
      pageSizeId: "file-page-size",
      columns: [
        {{ key: "name", label: "Name" }},
        {{ key: "size", label: "Size" }},
        {{ key: "extension", label: "Extension" }},
        {{ key: "modifiedAt", label: "Modified" }},
      ],
      rowRenderer: (row) => `
        <tr>
          <td>
            <div class="name-cell">${{row.name}} ${{entryFlagged(row, "file") ? '<span class="tag alert">flagged</span>' : ""}}</div>
            <div class="path-cell">${{row.path}}</div>
          </td>
          <td>${{fmtBytes(row.size)}}</td>
          <td><span class="tag">${{row.extension}}</span></td>
          <td>${{fmtDate(row.modifiedAt * 1000)}}</td>
        </tr>
      `,
    }});

    setupThemeControls();
    setupSectionToggle("scan-notes-section", "scan-notes-collapse", "scan-notes-body");
  </script>
</body>
</html>
"""


def write_report(output_path: str | Path, stats: ScanStats) -> Path:
    destination = Path(output_path).expanduser().resolve()
    destination.write_text(render_report(stats), encoding="utf-8")
    return destination
