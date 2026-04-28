from __future__ import annotations

import contextlib
import io
import json
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlparse

from novel_pipeline.ledger import RunLedger
from novel_pipeline.pipeline import inspect_block_command, status_run
from novel_pipeline.reports import (
    build_checkpoint_report,
    build_cleanliness_report,
    build_glossary_audit_report,
    build_glossary_conflicts_report,
    build_glossary_decisions_report,
    build_glossary_guard_report,
    build_provider_usage_report,
)
from novel_pipeline.types import AppConfig


def _latest_run_id(config: AppConfig) -> str | None:
    ledger = RunLedger(config.ledger_path)
    last_run_id: str | None = None
    for record in ledger.iter_records():
        last_run_id = record.run_id
    return last_run_id


def _list_run_ids(config: AppConfig) -> list[str]:
    ledger = RunLedger(config.ledger_path)
    run_ids: list[str] = []
    seen: set[str] = set()
    for record in ledger.iter_records():
        if record.run_id not in seen:
            seen.add(record.run_id)
            run_ids.append(record.run_id)
    return run_ids


def _quiet_status_run(config: AppConfig, run_id: str | None) -> dict[str, Any]:
    with contextlib.redirect_stdout(io.StringIO()):
        return status_run(config=config, run_id=run_id)


def _quiet_inspect_block(config: AppConfig, run_id: str, block_id: str) -> dict[str, Any]:
    with contextlib.redirect_stdout(io.StringIO()):
        return inspect_block_command(config=config, run_id=run_id, block_id=block_id)


def _safe_workspace_path(config: AppConfig, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = (config.workspace.root / raw_path).resolve()
    else:
        candidate = candidate.resolve()
    workspace_root = config.workspace.root.resolve()
    try:
        candidate.relative_to(workspace_root)
    except ValueError as exc:
        raise ValueError("Path is outside the workspace root.") from exc
    if candidate.suffix.lower() not in {".md", ".json", ".txt", ".yaml", ".yml"}:
        raise ValueError("Unsupported file type for operator viewer.")
    if not candidate.exists():
        raise ValueError("Requested file does not exist.")
    return candidate


def generate_operator_report(
    *,
    config: AppConfig,
    run_id: str,
    kind: str,
    chapter_ids: list[str] | None = None,
) -> dict[str, Any]:
    if kind == "checkpoint":
        return build_checkpoint_report(config=config, run_id=run_id)
    if kind == "cleanliness":
        return build_cleanliness_report(config=config, run_id=run_id, chapter_ids=chapter_ids or None)
    if kind == "provider-usage":
        return build_provider_usage_report(config=config, run_id=run_id)
    if kind == "glossary-decisions":
        return build_glossary_decisions_report(config=config, run_id=run_id)
    if kind == "glossary-conflicts":
        return build_glossary_conflicts_report(config=config, run_id=run_id)
    if kind == "glossary-audit":
        return build_glossary_audit_report(config=config, run_id=run_id)
    if kind == "glossary-guard":
        return build_glossary_guard_report(config=config, run_id=run_id)
    raise ValueError(f"Unsupported report kind: {kind}")


def build_operator_snapshot(config: AppConfig, run_id: str | None = None) -> dict[str, Any]:
    resolved_run_id = run_id or _latest_run_id(config)
    status = _quiet_status_run(config, resolved_run_id) if resolved_run_id else {"runs": []}
    return {
        "run_id": resolved_run_id,
        "available_run_ids": _list_run_ids(config),
        "status": status,
    }


def _render_operator_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Novel Operator</title>
  <style>
    :root {
      --bg: #f4f5f7;
      --surface: #ffffff;
      --surface-alt: #eef1f5;
      --text: #16181d;
      --muted: #5f6673;
      --border: #d9dee8;
      --accent: #0f62fe;
      --danger: #c0362c;
      --ok: #1f8f50;
      --shadow: 0 1px 2px rgba(16,24,40,.04), 0 8px 24px rgba(16,24,40,.06);
      --radius: 8px;
      font-family: "Segoe UI", Tahoma, sans-serif;
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--text); }
    .shell {
      min-height: 100svh;
      display: grid;
      grid-template-columns: 280px minmax(0, 1fr);
    }
    .nav {
      background: #111827;
      color: #f9fafb;
      padding: 20px 18px;
      border-right: 1px solid rgba(255,255,255,.08);
    }
    .nav h1 {
      margin: 0 0 6px;
      font-size: 18px;
      font-weight: 700;
    }
    .nav p {
      margin: 0 0 18px;
      color: #c7ced9;
      font-size: 13px;
      line-height: 1.4;
    }
    .nav section { margin-bottom: 20px; }
    .nav label, .panel label {
      display: block;
      margin-bottom: 6px;
      font-size: 12px;
      font-weight: 600;
      color: inherit;
    }
    .nav input, .panel input, .panel select {
      width: 100%;
      height: 38px;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 0 10px;
      background: white;
      color: var(--text);
    }
    .nav input { background: rgba(255,255,255,.98); }
    .btn-row, .grid-btns {
      display: grid;
      gap: 8px;
    }
    .grid-btns { grid-template-columns: 1fr 1fr; }
    button {
      height: 36px;
      border: 1px solid transparent;
      border-radius: 6px;
      padding: 0 12px;
      font-weight: 600;
      cursor: pointer;
      background: var(--surface-alt);
      color: var(--text);
    }
    button.primary {
      background: var(--accent);
      color: white;
    }
    button.ghost-dark {
      background: rgba(255,255,255,.08);
      color: #f9fafb;
      border-color: rgba(255,255,255,.12);
    }
    .main {
      padding: 20px;
      display: grid;
      gap: 18px;
      align-content: start;
    }
    .topbar {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 12px;
    }
    .topbar h2 {
      margin: 0;
      font-size: 24px;
    }
    .topbar p {
      margin: 4px 0 0;
      color: var(--muted);
      font-size: 13px;
    }
    .metrics {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }
    .metric, .panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }
    .metric {
      padding: 14px 16px;
      min-height: 94px;
    }
    .metric .label {
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 8px;
    }
    .metric .value {
      font-size: 24px;
      font-weight: 700;
    }
    .metric .sub {
      margin-top: 6px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
      word-break: break-word;
    }
    .layout {
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(320px, .7fr);
      gap: 18px;
    }
    .panel {
      padding: 16px;
    }
    .panel h3 {
      margin: 0 0 6px;
      font-size: 16px;
    }
    .panel p.meta {
      margin: 0 0 14px;
      font-size: 12px;
      color: var(--muted);
    }
    .table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    .table th, .table td {
      text-align: left;
      padding: 10px 8px;
      border-top: 1px solid var(--border);
      vertical-align: top;
    }
    .table th {
      color: var(--muted);
      font-size: 12px;
      font-weight: 600;
    }
    .stack { display: grid; gap: 14px; }
    .pill {
      display: inline-block;
      border-radius: 999px;
      padding: 4px 8px;
      font-size: 11px;
      font-weight: 700;
      background: var(--surface-alt);
      color: var(--text);
    }
    .pill.ok { background: #e7f7ee; color: var(--ok); }
    .pill.danger { background: #fdeceb; color: var(--danger); }
    .mono {
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
      font-size: 12px;
    }
    .actions-list, .artifact-list, .issues-list {
      display: grid;
      gap: 8px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .artifact-list a, .report-link {
      color: var(--accent);
      text-decoration: none;
      word-break: break-all;
    }
    .report-link:hover, .artifact-list a:hover { text-decoration: underline; }
    .inspect-grid {
      display: grid;
      grid-template-columns: 1fr 1fr auto;
      gap: 8px;
      margin-bottom: 12px;
    }
    .empty {
      color: var(--muted);
      font-size: 13px;
    }
    .footer-note {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
    }
    @media (max-width: 1080px) {
      .shell { grid-template-columns: 1fr; }
      .metrics, .layout { grid-template-columns: 1fr; }
      .inspect-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside class="nav">
      <h1>Novel Operator</h1>
      <p>Local control surface for status, inspection, and reports.</p>

      <section>
        <label for="runIdInput">Run ID</label>
        <input id="runIdInput" placeholder="batch-ch019-ch023-v1">
        <div class="btn-row" style="margin-top: 10px;">
          <button class="primary" id="loadRunBtn">Load Run</button>
          <button class="ghost-dark" id="refreshBtn">Refresh</button>
        </div>
      </section>

      <section>
        <label>Reports</label>
        <div class="grid-btns">
          <button class="ghost-dark" data-report="checkpoint">Checkpoint</button>
          <button class="ghost-dark" data-report="cleanliness">Cleanliness</button>
          <button class="ghost-dark" data-report="provider-usage">Provider</button>
          <button class="ghost-dark" data-report="glossary-decisions">Decisions</button>
          <button class="ghost-dark" data-report="glossary-conflicts">Conflicts</button>
          <button class="ghost-dark" data-report="glossary-audit">Audit</button>
          <button class="ghost-dark" data-report="glossary-guard">Guard</button>
        </div>
      </section>

      <section>
        <div class="footer-note">
          This slice is intentionally read-only and control-light. It surfaces status, inspection, and reports without adding new state-changing paths.
        </div>
      </section>
    </aside>

    <main class="main">
      <div class="topbar">
        <div>
          <h2 id="runTitle">No run loaded</h2>
          <p id="runSubtitle">Load a run to inspect current status, blocker, and artifacts.</p>
        </div>
      </div>

      <section class="metrics" id="metrics"></section>

      <div class="layout">
        <section class="panel">
          <h3>Chapter Status</h3>
          <p class="meta">Current chapter progress and next pending stages.</p>
          <div id="chapterTableWrap" class="empty">No run loaded.</div>
        </section>

        <div class="stack">
          <section class="panel">
            <h3>Safe Next Action</h3>
            <p class="meta">Directly from the current verified run state.</p>
            <div id="nextAction" class="mono empty">No run loaded.</div>
          </section>

          <section class="panel">
            <h3>Manual Actions</h3>
            <p class="meta">Outstanding operator actions from `status`.</p>
            <ul id="manualActions" class="actions-list"></ul>
          </section>

          <section class="panel">
            <h3>Recent Report Output</h3>
            <p class="meta">Generated by the existing CLI report layer.</p>
            <div id="reportResult" class="empty">No report generated yet.</div>
          </section>
        </div>
      </div>

      <section class="panel">
        <h3>Block Inspection</h3>
        <p class="meta">Read-only artifact and validation view for one block.</p>
        <div class="inspect-grid">
          <input id="inspectRunId" placeholder="Run ID">
          <input id="inspectBlockId" placeholder="Block ID e.g. ch019-block-002">
          <button class="primary" id="inspectBtn">Inspect</button>
        </div>
        <div id="inspectResult" class="empty">No block inspected.</div>
      </section>
    </main>
  </div>

  <script>
    const state = {
      runId: "",
      snapshot: null,
    };

    const runIdInput = document.getElementById("runIdInput");
    const inspectRunId = document.getElementById("inspectRunId");
    const inspectBlockId = document.getElementById("inspectBlockId");

    function setRunId(runId) {
      state.runId = runId || "";
      runIdInput.value = state.runId;
      if (!inspectRunId.value) {
        inspectRunId.value = state.runId;
      }
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }

    function fileLink(path, label) {
      const href = "/api/file?path=" + encodeURIComponent(path);
      return `<a class="report-link" href="${href}" target="_blank" rel="noreferrer">${escapeHtml(label || path)}</a>`;
    }

    function renderMetrics(snapshot) {
      const metrics = document.getElementById("metrics");
      const status = snapshot?.status || {};
      const completedCount = Array.isArray(status.completed_blocks) ? status.completed_blocks.length : 0;
      const failedCount = Array.isArray(status.current_failed_blocks) ? status.current_failed_blocks.length : 0;
      const records = status.total_records ?? 0;
      const chapterCount = Array.isArray(status.chapter_ids) ? status.chapter_ids.length : 0;
      metrics.innerHTML = `
        <div class="metric">
          <div class="label">Completed Blocks</div>
          <div class="value">${completedCount}</div>
          <div class="sub">${chapterCount} chapters in run scope</div>
        </div>
        <div class="metric">
          <div class="label">Current Failed Blocks</div>
          <div class="value">${failedCount}</div>
          <div class="sub">${status.historical_failed_records ?? 0} historical failed records</div>
        </div>
        <div class="metric">
          <div class="label">Ledger Records</div>
          <div class="value">${records}</div>
          <div class="sub">${escapeHtml(status.run_id || "no run")}</div>
        </div>
        <div class="metric">
          <div class="label">Next Effective Action</div>
          <div class="value" style="font-size:16px; line-height:1.35;">${escapeHtml(status.next_effective_action || "none")}</div>
          <div class="sub">Manual actions needed: ${(status.manual_actions || []).length}</div>
        </div>
      `;
    }

    function renderChapterTable(snapshot) {
      const wrap = document.getElementById("chapterTableWrap");
      const summary = snapshot?.status?.chapter_summary || {};
      const chapterIds = snapshot?.status?.chapter_ids || [];
      if (!chapterIds.length) {
        wrap.className = "empty";
        wrap.textContent = "No chapter summary available.";
        return;
      }
      const rows = chapterIds.map((chapterId) => {
        const item = summary[chapterId] || {};
        const pending = (item.pending_blocks || []).map((blockId) => `${blockId} (${item.pending_stages?.[blockId] || "?"})`).join(", ") || "none";
        const failed = (item.failed_blocks || []).join(", ") || "none";
        const output = item.output_exists ? fileLink(item.output_path, "open output") : "missing";
        return `
          <tr>
            <td class="mono">${escapeHtml(chapterId)}</td>
            <td>${item.completed_blocks ?? 0}/${item.expected_blocks ?? 0}</td>
            <td>${escapeHtml(pending)}</td>
            <td>${escapeHtml(failed)}</td>
            <td>${output}</td>
          </tr>
        `;
      }).join("");
      wrap.className = "";
      wrap.innerHTML = `
        <table class="table">
          <thead>
            <tr>
              <th>Chapter</th>
              <th>Progress</th>
              <th>Pending</th>
              <th>Failed</th>
              <th>Output</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    }

    function renderManualActions(snapshot) {
      const list = document.getElementById("manualActions");
      const actions = snapshot?.status?.manual_actions || [];
      list.innerHTML = "";
      if (!actions.length) {
        list.innerHTML = `<li class="empty">No manual actions.</li>`;
        return;
      }
      for (const action of actions) {
        const li = document.createElement("li");
        li.className = "mono";
        li.textContent = action;
        list.appendChild(li);
      }
    }

    function renderSnapshot(snapshot) {
      state.snapshot = snapshot;
      const runId = snapshot?.run_id || "";
      setRunId(runId);
      document.getElementById("runTitle").textContent = runId || "No run loaded";
      document.getElementById("runSubtitle").textContent = snapshot?.available_run_ids?.length
        ? `${snapshot.available_run_ids.length} known run IDs in ledger.`
        : "No runs recorded.";
      document.getElementById("nextAction").textContent = snapshot?.status?.next_effective_action || "none";
      renderMetrics(snapshot);
      renderChapterTable(snapshot);
      renderManualActions(snapshot);
    }

    async function loadSnapshot(runId = "") {
      const query = runId ? `?run_id=${encodeURIComponent(runId)}` : "";
      const response = await fetch(`/api/bootstrap${query}`);
      const data = await response.json();
      renderSnapshot(data);
    }

    async function inspectBlock() {
      const runId = inspectRunId.value.trim() || state.runId;
      const blockId = inspectBlockId.value.trim();
      if (!runId || !blockId) {
        document.getElementById("inspectResult").innerHTML = `<div class="empty">Run ID and block ID are required.</div>`;
        return;
      }
      const response = await fetch(`/api/inspect-block?run_id=${encodeURIComponent(runId)}&block_id=${encodeURIComponent(blockId)}`);
      const data = await response.json();
      if (!response.ok) {
        document.getElementById("inspectResult").innerHTML = `<div class="empty">${escapeHtml(data.error || "Inspect failed.")}</div>`;
        return;
      }
      const artifactEntries = Object.entries(data.artifact_paths || {}).map(([stage, path]) => {
        const exists = data.artifact_exists?.[stage];
        const label = `${stage} (${exists ? "exists" : "missing"})`;
        return `<li>${exists ? fileLink(path, label) : escapeHtml(label + ": " + path)}</li>`;
      }).join("");
      const issues = (data.formatted_validation_issues || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
      document.getElementById("inspectResult").innerHTML = `
        <div class="stack">
          <div><span class="pill ${data.next_pending_stage ? "danger" : "ok"}">${data.next_pending_stage ? "pending " + escapeHtml(data.next_pending_stage) : "complete"}</span></div>
          <div class="mono">chapter: ${escapeHtml(data.chapter_id)}</div>
          <div>
            <strong>Artifacts</strong>
            <ul class="artifact-list">${artifactEntries}</ul>
          </div>
          <div>
            <strong>Formatted validation issues</strong>
            ${issues ? `<ul class="issues-list">${issues}</ul>` : `<div class="empty">none</div>`}
          </div>
          <div class="mono">ledger records: ${(data.records || []).length}</div>
        </div>
      `;
    }

    async function generateReport(kind) {
      const runId = state.runId || runIdInput.value.trim();
      if (!runId) {
        document.getElementById("reportResult").innerHTML = `<div class="empty">Run ID is required.</div>`;
        return;
      }
      const response = await fetch("/api/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: runId, kind }),
      });
      const data = await response.json();
      if (!response.ok) {
        document.getElementById("reportResult").innerHTML = `<div class="empty">${escapeHtml(data.error || "Report generation failed.")}</div>`;
        return;
      }
      document.getElementById("reportResult").innerHTML = `
        <div class="stack">
          <div><span class="pill ${data.actionable_failure ? "danger" : "ok"}">${data.actionable_failure ? "actionable" : "ok"}</span></div>
          <div>${fileLink(data.path, data.path)}</div>
        </div>
      `;
    }

    document.getElementById("loadRunBtn").addEventListener("click", () => loadSnapshot(runIdInput.value.trim()));
    document.getElementById("refreshBtn").addEventListener("click", () => loadSnapshot(state.runId || runIdInput.value.trim()));
    document.getElementById("inspectBtn").addEventListener("click", inspectBlock);
    document.querySelectorAll("[data-report]").forEach((button) => {
      button.addEventListener("click", () => generateReport(button.dataset.report));
    });

    loadSnapshot("");
  </script>
</body>
</html>
"""


class _OperatorHandler(BaseHTTPRequestHandler):
    config: AppConfig
    default_run_id: str | None

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _send_json(self, payload: dict[str, Any], *, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, *, content_type: str = "text/plain; charset=utf-8", status: int = 200) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        if parsed.path == "/":
            self._send_text(_render_operator_html(), content_type="text/html; charset=utf-8")
            return
        if parsed.path == "/api/bootstrap":
            run_id = (params.get("run_id") or [self.default_run_id or ""])[0] or None
            try:
                payload = build_operator_snapshot(self.config, run_id=run_id)
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
            return
        if parsed.path == "/api/inspect-block":
            run_id = (params.get("run_id") or [""])[0]
            block_id = (params.get("block_id") or [""])[0]
            if not run_id or not block_id:
                self._send_json({"error": "run_id and block_id are required."}, status=400)
                return
            try:
                payload = _quiet_inspect_block(self.config, run_id, block_id)
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
            return
        if parsed.path == "/api/file":
            raw_path = (params.get("path") or [""])[0]
            if not raw_path:
                self._send_text("Missing path.", status=400)
                return
            try:
                safe_path = _safe_workspace_path(self.config, unquote(raw_path))
                text = safe_path.read_text(encoding="utf-8")
                title = quote(str(safe_path))
                html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{safe_path.name}</title>
                <style>body{{margin:0;background:#f5f6f8;color:#111827;font-family:Segoe UI,Tahoma,sans-serif}}
                header{{padding:14px 18px;border-bottom:1px solid #d7dce5;background:#fff}}
                main{{padding:18px}} pre{{white-space:pre-wrap;word-break:break-word;background:#fff;border:1px solid #d7dce5;border-radius:8px;padding:16px}}</style>
                </head><body><header><strong>{safe_path}</strong></header><main><pre>{text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</pre></main></body></html>"""
                self._send_text(html, content_type="text/html; charset=utf-8")
            except Exception as exc:
                self._send_text(str(exc), status=400)
            return
        self._send_json({"error": "Not found."}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/report":
            self._send_json({"error": "Not found."}, status=404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            payload = json.loads(raw)
            run_id = str(payload.get("run_id") or "").strip()
            kind = str(payload.get("kind") or "").strip()
            chapter_ids = payload.get("chapter_ids")
            if not run_id or not kind:
                self._send_json({"error": "run_id and kind are required."}, status=400)
                return
            result = generate_operator_report(
                config=self.config,
                run_id=run_id,
                kind=kind,
                chapter_ids=chapter_ids if isinstance(chapter_ids, list) else None,
            )
            self._send_json(
                {
                    "path": str(result["path"]),
                    "actionable_failure": bool(result.get("actionable_failure")),
                }
            )
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)


def serve_operator_ui(
    *,
    config: AppConfig,
    host: str = "127.0.0.1",
    port: int = 8765,
    run_id: str | None = None,
    open_browser: bool = False,
) -> ThreadingHTTPServer:
    handler = type(
        "OperatorHandler",
        (_OperatorHandler,),
        {"config": config, "default_run_id": run_id},
    )
    server = ThreadingHTTPServer((host, port), handler)
    if open_browser:
        url = f"http://{host}:{port}/"
        threading.Timer(0.3, lambda: webbrowser.open(url)).start()
    return server


__all__ = [
    "build_operator_snapshot",
    "generate_operator_report",
    "serve_operator_ui",
]
