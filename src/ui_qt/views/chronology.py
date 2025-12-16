"""
Chronology View - PySide6 Version
Timeline of all project activity extracted from RAID item notes.
"""

import re
from datetime import datetime, date
from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QGraphicsDropShadowEffect, QComboBox,
    QLineEdit, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from src.core.models import ProjectData, Item
from src.ui_qt.styles import INDICATOR_COLORS


class ClickableCard(QFrame):
    """QFrame that emits a signal on double-click"""
    double_clicked = Signal(int)

    def __init__(self, item_num: int, parent=None):
        super().__init__(parent)
        self.item_num = item_num
        self.setCursor(Qt.PointingHandCursor)

    def mouseDoubleClickEvent(self, event):
        """Emit signal with item_num on double-click"""
        self.double_clicked.emit(self.item_num)
        super().mouseDoubleClickEvent(event)


class ClickableNoteLabel(QLabel):
    """QLabel that handles link clicks but forwards double-clicks to parent.

    This solves the problem where QLabel with setOpenExternalLinks(True)
    captures all mouse events, preventing double-clicks from reaching
    the parent ClickableCard.
    """
    double_clicked = Signal()

    def mouseDoubleClickEvent(self, event):
        """Forward double-click to signal, allowing parent to handle it"""
        self.double_clicked.emit()
        # Don't call super() - we want to capture the double-click
        # and not have QLabel try to process it as text selection


class CollapsibleMonthSection(QWidget):
    """A collapsible section for a month's entries"""

    def __init__(self, month_name: str, expanded: bool = True, parent=None):
        super().__init__(parent)
        self.month_name = month_name
        self._expanded = expanded

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Clickable header
        self.header = QLabel()
        self._update_header_text()
        self.header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1a1a2e;
            background: transparent;
            padding: 16px 0 8px 0;
            border-bottom: 2px solid #e0e0e0;
        """)
        self.header.setCursor(Qt.PointingHandCursor)
        self.header.mousePressEvent = self._toggle
        layout.addWidget(self.header)

        # Container for entries
        self.entries_widget = QWidget()
        self.entries_widget.setStyleSheet("background: transparent;")
        self.entries_layout = QVBoxLayout(self.entries_widget)
        self.entries_layout.setContentsMargins(0, 8, 0, 0)
        self.entries_layout.setSpacing(12)
        layout.addWidget(self.entries_widget)

        # Set initial state
        self.entries_widget.setVisible(self._expanded)

    def _update_header_text(self):
        """Update header with expand/collapse indicator"""
        arrow = "▼" if self._expanded else "▶"
        self.header.setText(f"{arrow}  {self.month_name}")

    def _toggle(self, event=None):
        """Toggle expanded state"""
        self._expanded = not self._expanded
        self.entries_widget.setVisible(self._expanded)
        self._update_header_text()

    def set_expanded(self, expanded: bool):
        """Set expanded state"""
        self._expanded = expanded
        self.entries_widget.setVisible(self._expanded)
        self._update_header_text()

    def is_expanded(self) -> bool:
        """Return current expanded state"""
        return self._expanded

    def add_entry(self, widget: QWidget):
        """Add an entry widget to this month section"""
        self.entries_layout.addWidget(widget)


def add_shadow(widget, blur=15, offset=2, color=QColor(0, 0, 0, 25)):
    """Add drop shadow to a widget"""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, offset)
    shadow.setColor(color)
    widget.setGraphicsEffect(shadow)


def urls_to_links(text: str) -> str:
    """Convert bare URLs in text to HTML hyperlinks with domain name as display text."""
    from urllib.parse import urlparse, unquote

    def make_link(match):
        url = match.group(0)
        # Add https:// if no protocol specified
        href = url if url.startswith(('http://', 'https://')) else f'https://{url}'

        # Extract domain using proper URL parsing
        try:
            # Decode any URL-encoded characters first
            decoded_url = unquote(href)
            parsed = urlparse(decoded_url)
            domain = parsed.netloc or parsed.path.split('/')[0]
        except Exception:
            # Fallback: simple extraction
            domain_part = re.sub(r'^https?://', '', url)
            domain = domain_part.split('/')[0].split('%')[0]

        # Use domain as display text (e.g., "teams.microsoft.com", "sharepoint.com")
        return f'<a href="{href}" style="color: #0d6efd;">{domain}</a>'

    # Match URLs with protocol OR common domain patterns without protocol
    url_pattern = r'https?://[^\s<>\[\]]+|(?:[a-zA-Z0-9-]+\.)+(?:com|org|net|edu|gov|io|co|app|dev|sharepoint)[^\s<>\[\]]*'
    return re.sub(url_pattern, make_link, text)


# =============================================================================
# Note Parsing - extracts dated entries from item notes
# =============================================================================

def parse_notes(notes_text: str) -> List[dict]:
    """
    Parse notes field and extract dated entries.

    Supports two date formats:
    - Legacy: "> MM/DD/YY - Author - Note text..."
    - Current: "> YYYY-MM-DD - Author - Note text..."

    Returns list of dicts with 'date', 'author', 'text' keys.
    """
    if not notes_text:
        return []

    entries = []

    # Combined pattern for both date formats
    date_pattern = r'(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2})'
    pattern = rf'>\s*{date_pattern}\s*-?\s*([^-\n]*?)\s*-\s*(.+?)(?=(?:>\s*(?:\d{{4}}-\d{{2}}-\d{{2}}|\d{{1,2}}/\d{{1,2}}/\d{{2}}))|$)'

    matches = re.findall(pattern, notes_text, re.DOTALL)

    for match in matches:
        date_str, author, text = match

        # Parse date - try both formats
        parsed_date = None
        if '-' in date_str:
            try:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        else:
            try:
                parsed_date = datetime.strptime(date_str, "%m/%d/%y").date()
            except ValueError:
                pass

        if not parsed_date:
            continue

        # Clean up author and text
        author = author.strip()
        text = ' '.join(text.split())  # Normalize whitespace

        entries.append({
            'date': parsed_date,
            'date_str': date_str,
            'author': author if author else 'Unknown',
            'text': text
        })

    return entries


def extract_chronology(project_data: ProjectData) -> List[dict]:
    """
    Extract all dated notes from all items, with denormalized task data.
    Returns list of entries sorted by date descending (most recent first).
    """
    chronology = []

    for item in project_data.items:
        notes = item.notes or ''
        entries = parse_notes(notes)

        for entry in entries:
            chronology.append({
                'date': entry['date'],
                'author': entry['author'],
                'note_text': entry['text'],
                # Task context
                'item_num': item.item_num,
                'type': item.type or 'Plan Item',
                'workstream': item.workstream or '',
                'title': item.title or 'Untitled',
                'assigned_to': item.assigned_to or '',
                'indicator': item.indicator or 'Not Started',
                'percent_complete': item.percent_complete or 0,
            })

    # Sort by date descending (most recent first)
    chronology.sort(key=lambda x: x['date'], reverse=True)

    return chronology


# =============================================================================
# Chronology View Widget
# =============================================================================

class ChronologyView(QScrollArea):
    """Chronology view showing all project activity in date order"""

    # Signal emitted when item is double-clicked (item_num)
    item_clicked = Signal(int)

    def __init__(self, project_data: Optional[ProjectData], parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.all_entries = []
        self.filtered_entries = []

        # Filter state
        self.filter_type = ""
        self.search_text = ""

        # Track month sections for expand/collapse
        self.month_sections = []

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet("QScrollArea { border: none; background: #f5f5f5; }")

        # Container
        self.container = QWidget()
        self.container.setStyleSheet("background: #f5f5f5;")
        self.setWidget(self.container)

        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(16)

        # Extract chronology data
        if self.project_data:
            self.all_entries = extract_chronology(self.project_data)
            self.filtered_entries = self.all_entries.copy()

        self._build_ui()

    def _build_ui(self):
        """Build the UI"""
        # Title
        self.title_label = QLabel(f"Chronology ({len(self.filtered_entries)} entries)")
        self.title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #1a1a2e; background: transparent;")
        self.main_layout.addWidget(self.title_label)

        # Filter controls card
        filter_card = QFrame()
        filter_card.setStyleSheet("QFrame { background: white; border-radius: 8px; padding: 8px; }")
        add_shadow(filter_card, blur=10, offset=1)

        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(24)

        # Build filter options from data
        types = self._get_filter_options()

        # Type filter
        type_layout = QHBoxLayout()
        type_layout.setSpacing(8)
        type_lbl = QLabel("Type:")
        type_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #1a1a2e; background: transparent;")
        type_layout.addWidget(type_lbl)
        self.type_combo = QComboBox()
        self.type_combo.addItem("All", "")
        for t in types:
            self.type_combo.addItem(t, t)
        self.type_combo.setStyleSheet("font-size: 12px; min-width: 100px;")
        self.type_combo.currentIndexChanged.connect(self._on_filter_changed)
        type_layout.addWidget(self.type_combo)
        filter_layout.addLayout(type_layout)

        # Search box
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        search_lbl = QLabel("Search:")
        search_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #1a1a2e; background: transparent;")
        search_layout.addWidget(search_lbl)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search notes...")
        self.search_box.setStyleSheet("font-size: 12px; min-width: 200px; padding: 4px 8px;")
        self.search_box.textChanged.connect(self._on_filter_changed)
        search_layout.addWidget(self.search_box)
        filter_layout.addLayout(search_layout)

        filter_layout.addStretch()

        # Expand/Collapse buttons
        expand_btn = QPushButton("Expand All")
        expand_btn.setStyleSheet("""
            QPushButton {
                background: #f5f5f5;
                color: #333333;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #e9ecef;
            }
        """)
        expand_btn.setCursor(Qt.PointingHandCursor)
        expand_btn.clicked.connect(self._expand_all)
        filter_layout.addWidget(expand_btn)

        collapse_btn = QPushButton("Collapse All")
        collapse_btn.setStyleSheet("""
            QPushButton {
                background: #f5f5f5;
                color: #333333;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #e9ecef;
            }
        """)
        collapse_btn.setCursor(Qt.PointingHandCursor)
        collapse_btn.clicked.connect(self._collapse_all)
        filter_layout.addWidget(collapse_btn)

        self.main_layout.addWidget(filter_card)

        # Entries container - will be rebuilt on filter changes
        self.entries_container = QWidget()
        self.entries_container.setStyleSheet("background: transparent;")
        self.entries_layout = QVBoxLayout(self.entries_container)
        self.entries_layout.setContentsMargins(0, 0, 0, 0)
        self.entries_layout.setSpacing(12)

        self._render_entries()

        self.main_layout.addWidget(self.entries_container)
        self.main_layout.addStretch()

    def _get_filter_options(self):
        """Get unique values for filter dropdowns"""
        types = set()

        for entry in self.all_entries:
            if entry['type']:
                types.add(entry['type'])

        return sorted(types)

    def _on_filter_changed(self):
        """Handle filter changes"""
        self.filter_type = self.type_combo.currentData() or ""
        self.search_text = self.search_box.text().lower().strip()

        self._apply_filters()
        self._render_entries()

    def _apply_filters(self):
        """Apply current filters to entries"""
        self.filtered_entries = []

        for entry in self.all_entries:
            # Type filter
            if self.filter_type and entry['type'] != self.filter_type:
                continue

            # Search filter - search in note text and title
            if self.search_text:
                searchable = f"{entry['note_text']} {entry['title']}".lower()
                if self.search_text not in searchable:
                    continue

            self.filtered_entries.append(entry)

        self.title_label.setText(f"Chronology ({len(self.filtered_entries)} entries)")

    def _render_entries(self):
        """Render the filtered entries with collapsible month sections"""
        # Clear existing entries and month sections
        self.month_sections = []
        while self.entries_layout.count():
            child = self.entries_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.filtered_entries:
            no_data = QLabel("No entries match the current filters")
            no_data.setStyleSheet("font-size: 14px; color: #666; padding: 40px; background: transparent;")
            no_data.setAlignment(Qt.AlignCenter)
            self.entries_layout.addWidget(no_data)
            return

        # Group by month using collapsible sections
        current_month = None
        current_section = None
        is_first_month = True

        for entry in self.filtered_entries:
            entry_month = entry['date'].strftime('%B %Y')

            # Create new month section if changed
            if entry_month != current_month:
                current_month = entry_month
                # First month expanded, others collapsed
                current_section = CollapsibleMonthSection(entry_month, expanded=is_first_month)
                self.month_sections.append(current_section)
                self.entries_layout.addWidget(current_section)
                is_first_month = False

            # Create entry card and add to current section
            card = self._create_entry_card(entry)
            current_section.add_entry(card)

    def _create_entry_card(self, entry: dict):
        """Create a card for a single chronology entry"""
        card = ClickableCard(entry['item_num'])
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border-left: 4px solid #3b82f6;
            }
        """)
        add_shadow(card, blur=8, offset=1)

        # Connect double-click signal to emit item_clicked
        card.double_clicked.connect(self.item_clicked.emit)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Header row: date and item info
        header = QHBoxLayout()
        header.setSpacing(12)

        # Date
        date_str = entry['date'].strftime('%m/%d/%y')
        date_label = QLabel(date_str)
        date_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #1a1a2e; background: transparent;")
        date_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        header.addWidget(date_label)

        header.addStretch()

        # Item badge
        item_type = entry['type']
        type_colors = {
            "Risk": "#dc3545",
            "Issue": "#fd7e14",
            "Action Item": "#0d6efd",
            "Decision": "#6f42c1",
            "Deliverable": "#28a745",
            "Budget": "#20c997",
            "Plan Item": "#6c757d"
        }
        type_color = type_colors.get(item_type, "#6c757d")

        item_badge = QLabel(f"#{entry['item_num']} {item_type}")
        item_badge.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {type_color};
            background: transparent;
            padding: 2px 8px;
            border: 1px solid {type_color};
            border-radius: 10px;
        """)
        item_badge.setAttribute(Qt.WA_TransparentForMouseEvents)
        header.addWidget(item_badge)

        layout.addLayout(header)

        # Item title
        title_label = QLabel(entry['title'])
        title_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #1a1a2e; background: transparent;")
        title_label.setWordWrap(True)
        title_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(title_label)

        # Note text - convert URLs to clickable links
        # Uses ClickableNoteLabel to allow both link clicks AND double-click to edit
        note_text = entry['note_text']
        if len(note_text) > 500:
            note_text = note_text[:497] + "..."

        note_html = urls_to_links(note_text)
        note_label = ClickableNoteLabel(note_html)
        note_label.setStyleSheet("font-size: 13px; color: #333; background: transparent; line-height: 1.4;")
        note_label.setWordWrap(True)
        note_label.setTextFormat(Qt.RichText)
        note_label.setOpenExternalLinks(True)
        # Connect note label double-click to card's signal
        note_label.double_clicked.connect(lambda: card.double_clicked.emit(entry['item_num']))
        layout.addWidget(note_label)

        # Footer: workstream, assigned, status
        footer = QHBoxLayout()
        footer.setSpacing(16)

        if entry['workstream']:
            ws_label = QLabel(f"Workstream: {entry['workstream']}")
            ws_label.setStyleSheet("font-size: 11px; color: #888; background: transparent;")
            ws_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            footer.addWidget(ws_label)

        if entry['assigned_to']:
            assigned_label = QLabel(f"Assigned: {entry['assigned_to']}")
            assigned_label.setStyleSheet("font-size: 11px; color: #888; background: transparent;")
            assigned_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            footer.addWidget(assigned_label)

        # Status indicator
        indicator = entry['indicator']
        indicator_color = INDICATOR_COLORS.get(indicator, "#6c757d")
        status_label = QLabel(f"● {indicator}")
        status_label.setStyleSheet(f"font-size: 11px; color: {indicator_color}; background: transparent;")
        status_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        footer.addWidget(status_label)

        footer.addStretch()

        layout.addLayout(footer)

        return card

    def _expand_all(self):
        """Expand all month sections"""
        for section in self.month_sections:
            section.set_expanded(True)

    def _collapse_all(self):
        """Collapse all month sections"""
        for section in self.month_sections:
            section.set_expanded(False)

    def refresh(self, project_data, budget):
        """Refresh with new data"""
        self.project_data = project_data

        # Re-extract chronology
        if self.project_data:
            self.all_entries = extract_chronology(self.project_data)
        else:
            self.all_entries = []

        # Reapply filters
        self._apply_filters()

        # Clear and rebuild
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

        self._build_ui()

    def _clear_layout(self, layout):
        """Recursively clear a layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())
