"""Obsidian write tools — allowlisted, audited captures into the vault."""

from __future__ import annotations

import os
from datetime import datetime, date
from pathlib import Path
from typing import Any

from openjarvis.core.registry import ToolRegistry
from openjarvis.core.types import ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec

_DEFAULT_VAULT = "/mnt/c/Kerja/Project/Personal AI/ODIN"
_ALLOWED_WRITE_DIRS = ("00_INBOX", "01_DAILY", "ODIN")
_BLOCKED = ("password", "secret", "private_key", ".env", "credential")


def _vault() -> Path:
    return Path(os.environ.get("ODIN_VAULT", _DEFAULT_VAULT)).resolve()


def _is_write_allowed(target: Path) -> bool:
    vault = _vault()
    try:
        rel = target.resolve().relative_to(vault)
    except ValueError:
        return False
    if any(b in target.name.lower() for b in _BLOCKED):
        return False
    return bool(rel.parts) and rel.parts[0] in _ALLOWED_WRITE_DIRS


def _audit(tool: str, target: Path, preview: str) -> None:
    vault = _vault()
    log = vault / "ODIN" / "COMMAND_LOG.md"
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rel = target.resolve().relative_to(vault)
        clean = " ".join(preview[:80].splitlines())
        with log.open("a", encoding="utf-8") as f:
            f.write(f"- {ts} | {tool} -> {rel} | {clean}\n")
    except Exception:
        pass


def _today_note() -> Path:
    return _vault() / "01_DAILY" / f"{date.today().isoformat()}.md"


def _append_under_heading(path: Path, heading: str, line: str) -> None:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() \
        else "# Daily Note\n\n## Log\n\n## Tasks\n"
    if f"## {heading}" not in text:
        text = text.rstrip() + f"\n\n## {heading}\n"
    out, inserted = [], False
    for ln in text.splitlines():
        out.append(ln)
        if not inserted and ln.strip() == f"## {heading}":
            out.append(line)
            inserted = True
    if not inserted:
        out += [f"## {heading}", line]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


@ToolRegistry.register("obsidian_capture")
class ObsidianCaptureTool(BaseTool):
    tool_id = "obsidian_capture"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="obsidian_capture",
            description=("Save a note for the user into their Obsidian vault. Appends a "
                         "timestamped line under today's daily-note Log by default; use "
                         "target='inbox' to send it to the inbox instead."),
            parameters={"type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Note text to save."},
                            "target": {"type": "string", "enum": ["daily", "inbox"],
                                       "description": "Where to save (default 'daily')."}},
                        "required": ["text"]},
            category="obsidian",
        )

    def execute(self, **params: Any) -> ToolResult:
        text = (params.get("text") or "").strip()
        if not text:
            return ToolResult(tool_name=self.tool_id, content="Nothing to capture.", success=False)
        ts = datetime.now().strftime("%H:%M")
        if (params.get("target") or "daily").lower() == "inbox":
            path = _vault() / "00_INBOX" / "quick-captures.md"
            if not _is_write_allowed(path):
                return ToolResult(tool_name=self.tool_id, content="Write not allowed.", success=False)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(f"- {date.today().isoformat()} {ts} — {text}\n")
            _audit(self.tool_id, path, text)
            return ToolResult(tool_name=self.tool_id, content=f"Captured to inbox: {text}", success=True)
        path = _today_note()
        if not _is_write_allowed(path):
            return ToolResult(tool_name=self.tool_id, content="Write not allowed.", success=False)
        _append_under_heading(path, "Log", f"- {ts} — {text}")
        _audit(self.tool_id, path, text)
        return ToolResult(tool_name=self.tool_id, content=f"Added to today's note: {text}", success=True)


@ToolRegistry.register("obsidian_add_task")
class ObsidianAddTaskTool(BaseTool):
    tool_id = "obsidian_add_task"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="obsidian_add_task",
            description="Add a to-do as a checkbox under today's daily-note Tasks section.",
            parameters={"type": "object",
                        "properties": {"task": {"type": "string", "description": "The task text."}},
                        "required": ["task"]},
            category="obsidian",
        )

    def execute(self, **params: Any) -> ToolResult:
        task = (params.get("task") or "").strip()
        if not task:
            return ToolResult(tool_name=self.tool_id, content="No task provided.", success=False)
        path = _today_note()
        if not _is_write_allowed(path):
            return ToolResult(tool_name=self.tool_id, content="Write not allowed.", success=False)
        _append_under_heading(path, "Tasks", f"- [ ] {task}")
        _audit(self.tool_id, path, task)
        return ToolResult(tool_name=self.tool_id, content=f"Task added: {task}", success=True)


__all__ = ["ObsidianCaptureTool", "ObsidianAddTaskTool"]
