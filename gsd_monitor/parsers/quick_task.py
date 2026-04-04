"""Quick tasks under .planning/quick/."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from pydantic import BaseModel


class QuickTaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class QuickTask(BaseModel):
    title: str = ""
    status: QuickTaskStatus = QuickTaskStatus.OPEN
    created: datetime | None = None
    last_updated: datetime | None = None
    file_path: str = ""


_STATUS_FM = re.compile(r"^status:\s*([^\r\n]+)", re.MULTILINE)
_CHECKBOX = re.compile(r"^-\s*\[(x| )]", re.MULTILINE | re.IGNORECASE)
_HEADING = re.compile(r"^#\s+([^\r\n]+)", re.MULTILINE)


class QuickTaskParser:
    @staticmethod
    def parse(planning_dir: str) -> list[QuickTask]:
        try:
            quick = Path(planning_dir) / "quick"
            if not quick.is_dir():
                return []
            out: list[QuickTask] = []
            for fp in quick.rglob("*.md"):
                try:
                    content = fp.read_text(encoding="utf-8", errors="replace")
                    stem = fp.stem
                    title = QuickTaskParser._extract_title(content, stem)
                    st = QuickTaskParser._detect_status(fp.name, content)
                    st_ct = datetime.fromtimestamp(fp.stat().st_ctime, tz=timezone.utc)
                    st_mt = datetime.fromtimestamp(fp.stat().st_mtime, tz=timezone.utc)
                    out.append(
                        QuickTask(
                            title=title,
                            status=st,
                            created=st_ct,
                            last_updated=st_mt,
                            file_path=str(fp.resolve()),
                        )
                    )
                except Exception:
                    continue
            return out
        except Exception:
            return []

    @staticmethod
    def _extract_title(content: str, file_stem: str) -> str:
        m = _HEADING.search(content)
        if m:
            return m.group(1).strip()
        return file_stem

    @staticmethod
    def _detect_status(file_name: str, content: str) -> QuickTaskStatus:
        sm = _STATUS_FM.search(content)
        if sm:
            v = sm.group(1).strip().lower()
            if "complete" in v:
                return QuickTaskStatus.COMPLETE
            if "progress" in v or "in_progress" in v:
                return QuickTaskStatus.IN_PROGRESS
        cm = _CHECKBOX.search(content)
        if cm and cm.group(1).lower() == "x":
            return QuickTaskStatus.COMPLETE
        return QuickTaskStatus.OPEN
