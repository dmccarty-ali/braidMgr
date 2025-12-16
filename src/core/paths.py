"""
Platform-aware path handling for BRAID Manager.
Provides consistent data directory locations across macOS and Windows.
"""

import sys
from pathlib import Path


# Application identity
APP_NAME = "BRAID Manager"
APP_AUTHOR = "Centric Consulting"


def get_app_data_dir() -> Path:
    """
    Get the platform-appropriate application data directory.

    Returns:
        macOS:   ~/Library/Application Support/BRAID Manager/
        Windows: %APPDATA%/BRAID Manager/  (typically C:/Users/<user>/AppData/Roaming/)
        Linux:   ~/.local/share/BRAID Manager/
    """
    if sys.platform == "darwin":
        # macOS
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":
        # Windows - use APPDATA environment variable
        import os
        appdata = os.environ.get("APPDATA")
        if appdata:
            base = Path(appdata)
        else:
            # Fallback if APPDATA not set
            base = Path.home() / "AppData" / "Roaming"
    else:
        # Linux/other Unix
        base = Path.home() / ".local" / "share"

    return base / APP_NAME


def get_default_project_dir() -> Path:
    """Get the default project data directory (inside app data dir)."""
    return get_app_data_dir() / "projects" / "default"


def ensure_app_directories() -> Path:
    """
    Ensure application directories exist. Creates them if needed.
    Returns the app data directory path.
    """
    app_dir = get_app_data_dir()
    app_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (app_dir / "projects").mkdir(exist_ok=True)
    (app_dir / "projects" / "default").mkdir(exist_ok=True)

    return app_dir


def is_first_run() -> bool:
    """Check if this is the first time the app is running."""
    app_dir = get_app_data_dir()
    return not app_dir.exists()


def get_project_data_path() -> Path:
    """
    Get the path to the current project's data directory.
    For now, returns the default project. Future: support multiple projects.
    """
    return get_default_project_dir()
