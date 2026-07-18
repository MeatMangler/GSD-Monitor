from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gsd_monitor.models.enums import (
    DriftIndicator,
    GsdVersion,
    MilestoneStatus,
    PhaseStatus,
    ResearchCoverage,
)


class TodoItem(BaseModel):
    is_checked: bool = False
    text: str = ""


class DecisionEntry(BaseModel):
    id: str = ""
    text: str = ""
    is_covered: bool = False


class PhaseEntry(BaseModel):
    number: int = 0
    title: str = ""
    status: PhaseStatus = PhaseStatus.NOT_STARTED
    drift: DriftIndicator = DriftIndicator.NONE
    goal: str | None = None
    plan_content: str | None = None
    todos: list[TodoItem] = Field(default_factory=list)
    artifact_paths: list[str] = Field(default_factory=list)
    last_updated: datetime | None = None
    plan_write_time: datetime | None = None
    has_context: bool = False
    has_research: bool = False
    has_plan: bool = False
    has_validation: bool = False
    nyquist_compliant: bool | None = None
    research_coverage: ResearchCoverage = ResearchCoverage.NONE
    research_content: str | None = None
    validation_content: str | None = None
    is_archived: bool = False
    archive_milestone: str | None = None
    archive_root: str | None = None
    code: str | None = None
    risk_tag: str | None = None
    depends_on: list[str] = Field(default_factory=list)
    has_uat: bool = False
    has_ui_spec: bool = False
    has_ui_review: bool = False
    has_summary: bool = False
    has_requirements: bool = False
    decisions: list["DecisionEntry"] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class Milestone(BaseModel):
    title: str = ""
    number: int = 0
    status: MilestoneStatus = MilestoneStatus.PLANNED
    progress: int = 0
    phases: list[PhaseEntry] = Field(default_factory=list)
    code: str | None = None
    vision: str | None = None
    is_archived: bool = False
    completion_date: str | None = None


class GsdProject(BaseModel):
    name: str = ""
    path: str = ""
    description: str | None = None
    last_updated: datetime | None = None
    milestones: list[Milestone] = Field(default_factory=list)
    version: GsdVersion = GsdVersion.V1
    handoff_info: dict | None = None
    continue_here: bool = False
    config_info: dict | None = None
    progress_percent: int = 0
    completed_phases: int = 0
    total_phases: int = 0
    has_requirements: bool = False
    requirements: list[Any] = Field(default_factory=list)


class AppSettings(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scan_roots: list[str] = Field(default_factory=list, alias="ScanRoots")
    theme: str = Field(
        default="system",
        alias="Theme",
        validation_alias="Theme",
    )
    claude_cli_path: str | None = Field(default=None, alias="ClaudeCliPath")
    terminal_path: str | None = Field(default=None, alias="TerminalPath")
    notify_on_drift: bool = Field(default=True, alias="NotifyOnDrift")
    notify_on_phase_completion: bool = Field(default=True, alias="NotifyOnPhaseCompletion")
    notify_on_verification_failure: bool = Field(
        default=True, alias="NotifyOnVerificationFailure"
    )


class StateInfo(BaseModel):
    current_phase: str = ""
    status: str = ""
    last_activity: datetime | None = None
    active_milestone: str | None = None
    active_slice: str | None = None
    active_task: str | None = None
    workflow_phase: str | None = None
    total_phases: int = 0
    completed_phases: int = 0
    progress_percent: int = 0


class ParseResult(BaseModel):
    is_success: bool
    value: Any = None
    error_message: str | None = None

    @classmethod
    def ok(cls, value: Any) -> ParseResult:
        return cls(is_success=True, value=value, error_message=None)

    @classmethod
    def err(cls, msg: str) -> ParseResult:
        return cls(is_success=False, value=None, error_message=msg)
