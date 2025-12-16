"""
Template data for new BRAID Manager projects.
"""

from datetime import date
from .models import ProjectData, ProjectMetadata, Item


def create_new_project(project_name: str = "New Project", client_name: str = None) -> ProjectData:
    """
    Create a new project with default metadata and a starter item.

    Args:
        project_name: Name for the project
        client_name: Optional client name

    Returns:
        ProjectData with default structure
    """
    today = date.today()

    metadata = ProjectMetadata(
        project_name=project_name,
        client_name=client_name,
        next_item_num=2,
        last_updated=today,
        project_start=today,
        project_end=None,
        indicators_updated=today,
        workstreams=["General"]
    )

    # Create a starter item so the project isn't completely empty
    starter_item = Item(
        item_num=1,
        type="Action Item",
        title="Set up project",
        workstream="General",
        description="Initial project setup and configuration",
        assigned_to=None,
        dep_item_num=[],
        start=today,
        finish=None,
        duration=None,
        deadline=None,
        draft=False,
        client_visible=True,
        percent_complete=0,
        rpt_out=[],
        created_date=today,
        last_updated=today,
        notes=None,
        indicator="green",
        priority=None,
        budget_amount=None
    )

    return ProjectData(metadata=metadata, items=[starter_item])


# YAML template as string for reference/manual creation
RAID_LOG_TEMPLATE = """metadata:
  project_name: New Project
  client_name: null
  next_item_num: 2
  last_updated: {today}
  project_start: {today}
  project_end: null
  indicators_updated: {today}
  workstreams:
    - General

items:
  - item_num: 1
    type: Action Item
    workstream: General
    title: Set up project
    description: Initial project setup and configuration
    assigned_to: null
    dep_item_num: []
    start: {today}
    finish: null
    deadline: null
    draft: false
    client_visible: true
    percent_complete: 0
    rpt_out: []
    created_date: {today}
    last_updated: {today}
    notes: null
    indicator: green
"""
