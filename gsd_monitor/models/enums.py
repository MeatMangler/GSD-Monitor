from enum import Enum


class PhaseStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    NEEDS_VERIFICATION = "needs_verification"


class DriftIndicator(str, Enum):
    NONE = "none"
    MINOR = "minor"
    MAJOR = "major"
    DEFERRED = "deferred"


class ResearchCoverage(str, Enum):
    NONE = "none"
    PARTIAL = "partial"
    COMPLETE = "complete"


class MilestoneStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"


class GsdVersion(str, Enum):
    V1 = "gsd1"
    CORE = "gsd-core"


class AppTheme(str, Enum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


class GitAvailability(str, Enum):
    AVAILABLE = "available"
    NOT_A_GIT_REPO = "not_a_git_repo"
    GIT_NOT_INSTALLED = "git_not_installed"
    LIBRARY_ERROR = "library_error"
