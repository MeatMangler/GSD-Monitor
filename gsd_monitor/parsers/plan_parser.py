"""PLAN.md — extract title and GitHub-style task list items."""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, Field

from gsd_monitor.models.core import ParseResult, TodoItem


class PlanParseResult(BaseModel):
    title: str = ""
    todos: list[TodoItem] = Field(default_factory=list)


# - [ ] or - [x] task text
_TASK_LINE = re.compile(r"^-\s*\[(x| )\]\s*(.*)$", re.MULTILINE | re.IGNORECASE)

# <task id="N.N" status="done">Task text</task>  (gsd-core XML format)
# Also handles multi-line: <task ...>\ntext\n</task>
_XML_TASK = re.compile(
    r'<task[^>]*\bstatus=["\']?([^"\'>\s]+)["\']?[^>]*>\s*(.*?)\s*</task>',
    re.DOTALL | re.IGNORECASE,
)

_H1 = re.compile(r"^#\s+(.+)$", re.MULTILINE)


class PlanParser:
    @staticmethod
    def parse(file_path: str) -> ParseResult:
        try:
            p = Path(file_path)
            if not p.is_file():
                return ParseResult.err(f"Plan file not found: {file_path}")
            text = p.read_text(encoding="utf-8", errors="replace")
            h1 = _H1.search(text)
            title = h1.group(1).strip() if h1 else ""
            todos: list[TodoItem] = []
            for m in _TASK_LINE.finditer(text):
                checked = m.group(1).lower() == "x"
                rest = m.group(2).strip()
                todos.append(TodoItem(is_checked=checked, text=rest))
            for m in _XML_TASK.finditer(text):
                status_val = m.group(1).lower()
                checked = status_val in ("done", "complete", "completed", "x")
                task_text = m.group(2).strip()
                if task_text:
                    todos.append(TodoItem(is_checked=checked, text=task_text))
            return ParseResult.ok(PlanParseResult(title=title, todos=todos))
        except Exception as ex:
            return ParseResult.err(f"Failed to parse plan file: {ex}")
