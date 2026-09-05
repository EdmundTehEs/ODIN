"""Obsidian read-only tools — let ODIN see his vault (plain markdown)."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from typing import Any

from openjarvis.core.registry import ToolRegistry
from openjarvis.core.types import ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec

_DEFAULT_VAULT = "/mnt/c/Kerja/Project/Personal AI/ODIN"
_BLOCKED = ("password", "secret", "private_key", ".env", "credential")
_MAX_BYTES = 1_048_576


def _vault() -> Path:
    return Path(os.environ.get("ODIN_VAULT", _DEFAULT_VAULT)).resolve()


def _safe_target(rel: str):
    vault = _vault()
    target = (vault / rel).resolve()
    if not (target == vault or target.is_relative_to(vault)):
        return None
    if any(b in target.name.lower() for b in _BLOCKED):
        return None
    return target


@ToolRegistry.register("obsidian_read_note")
class ObsidianReadNoteTool(BaseTool):
    tool_id = "obsidian_read_note"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="obsidian_read_note",
            description=("Read one note from the user's Obsidian vault. Provide a "
                         "vault-relative path like 'ODIN/USER_PROFILE.md'. Read-only."),
            parameters={"type": "object",
                        "properties": {"path": {"type": "string",
                                                "description": "Vault-relative .md path."}},
                        "required": ["path"]},
            category="obsidian",
        )

    def execute(self, **params: Any) -> ToolResult:
        rel = (params.get("path") or "").strip()
        if not rel:
            return ToolResult(tool_name=self.tool_id, content="No path provided.", success=False)
        target = _safe_target(rel)
        if target is None:
            return ToolResult(tool_name=self.tool_id, content=f"Access denied: {rel}", success=False)
        if not target.is_file():
            return ToolResult(tool_name=self.tool_id, content=f"Note not found: {rel}", success=False)
        try:
            if target.stat().st_size > _MAX_BYTES:
                return ToolResult(tool_name=self.tool_id, content="Note too large.", success=False)
            text = target.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            return ToolResult(tool_name=self.tool_id, content=f"Read error: {exc}", success=False)
        return ToolResult(tool_name=self.tool_id, content=text, success=True,
                          metadata={"path": str(target)})


@ToolRegistry.register("obsidian_today")
class ObsidianTodayTool(BaseTool):
    tool_id = "obsidian_today"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="obsidian_today",
            description="Read today's daily note from the Obsidian vault. Read-only. No parameters.",
            parameters={"type": "object", "properties": {}},
            category="obsidian",
        )

    def execute(self, **params: Any) -> ToolResult:
        rel = f"01_DAILY/{date.today().isoformat()}.md"
        target = _safe_target(rel)
        if target is None or not target.is_file():
            return ToolResult(tool_name=self.tool_id,
                              content=f"No daily note for today ({rel}).", success=False)
        text = target.read_text(encoding="utf-8", errors="replace")
        return ToolResult(tool_name=self.tool_id, content=text, success=True,
                          metadata={"path": str(target)})


@ToolRegistry.register("obsidian_search")
class ObsidianSearchTool(BaseTool):
    tool_id = "obsidian_search"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="obsidian_search",
            description=("Search the Obsidian vault for a text query. Returns matching "
                         "notes with the lines that matched. Read-only."),
            parameters={"type": "object",
                        "properties": {"query": {"type": "string", "description": "Text to find."},
                                       "limit": {"type": "integer",
                                                 "description": "Max notes (default 10)."}},
                        "required": ["query"]},
            category="obsidian",
        )

    def execute(self, **params: Any) -> ToolResult:
        query = (params.get("query") or "").strip()
        if not query:
            return ToolResult(tool_name=self.tool_id, content="No query provided.", success=False)
        limit = int(params.get("limit") or 10)
        vault = _vault()
        if not vault.is_dir():
            return ToolResult(tool_name=self.tool_id, content=f"Vault not found at {vault}.", success=False)
        q = query.lower()
        hits = []
        for md in sorted(vault.rglob("*.md")):
            if any(b in md.name.lower() for b in _BLOCKED):
                continue
            try:
                lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                continue
            matched = [ln.strip() for ln in lines if q in ln.lower()]
            if matched:
                snippet = "\n".join(f"    {m}" for m in matched[:3])
                hits.append(f"{md.relative_to(vault)}:\n{snippet}")
                if len(hits) >= limit:
                    break
        if not hits:
            return ToolResult(tool_name=self.tool_id, content=f"No notes matched '{query}'.", success=True)
        return ToolResult(tool_name=self.tool_id, content="\n\n".join(hits), success=True,
                          metadata={"matches": len(hits)})


__all__ = ["ObsidianReadNoteTool", "ObsidianTodayTool", "ObsidianSearchTool"]
