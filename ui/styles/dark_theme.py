"""
JARVIS-inspired dark theme QSS stylesheet for ALFRED GUI.
"""
from .colors import COLORS

DARK_THEME_QSS = f"""
/* ===== Global Styles ===== */
QWidget {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 10pt;
}}

QMainWindow {{
    background-color: {COLORS['bg_primary']};
}}

/* ===== Labels ===== */
QLabel {{
    background-color: transparent;
    color: {COLORS['text_primary']};
}}

QLabel[class="title"] {{
    font-size: 14pt;
    font-weight: bold;
    color: {COLORS['accent_cyan']};
}}

QLabel[class="subtitle"] {{
    font-size: 11pt;
    color: {COLORS['text_secondary']};
}}

/* ===== Push Buttons ===== */
QPushButton {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {COLORS['bg_hover']};
    border-color: {COLORS['border_hover']};
}}

QPushButton:pressed {{
    background-color: {COLORS['bg_pressed']};
    border-color: {COLORS['accent_cyan']};
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_disabled']};
    border-color: {COLORS['border_default']};
}}

QPushButton[class="primary"] {{
    background-color: {COLORS['accent_cyan']};
    color: {COLORS['bg_primary']};
    border: none;
    font-weight: bold;
}}

QPushButton[class="primary"]:hover {{
    background-color: {COLORS['accent_cyan_dim']};
}}

QPushButton[class="icon"] {{
    background-color: transparent;
    border: none;
    padding: 8px;
    border-radius: 20px;
}}

QPushButton[class="icon"]:hover {{
    background-color: {COLORS['bg_tertiary']};
}}

/* ===== Line Edit ===== */
QLineEdit {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 6px;
    padding: 10px 14px;
    selection-background-color: {COLORS['accent_cyan']};
}}

QLineEdit:focus {{
    border-color: {COLORS['accent_cyan']};
}}

QLineEdit:disabled {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_disabled']};
}}

/* ===== Text Edit / Plain Text Edit ===== */
QTextEdit, QPlainTextEdit {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 6px;
    padding: 8px;
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {COLORS['accent_cyan']};
}}

/* ===== Scroll Area ===== */
QScrollArea {{
    background-color: {COLORS['bg_secondary']};
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background-color: {COLORS['bg_secondary']};
}}

/* ===== Scroll Bars ===== */
QScrollBar:vertical {{
    background-color: {COLORS['scrollbar_bg']};
    width: 10px;
    margin: 0;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['scrollbar_handle']};
    min-height: 30px;
    border-radius: 5px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['scrollbar_hover']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
    background: none;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background-color: {COLORS['scrollbar_bg']};
    height: 10px;
    margin: 0;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['scrollbar_handle']};
    min-width: 30px;
    border-radius: 5px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['scrollbar_hover']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
    background: none;
}}

/* ===== Progress Bar ===== */
QProgressBar {{
    background-color: {COLORS['progress_bg']};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {COLORS['progress_chunk']};
    border-radius: 4px;
}}

/* ===== Frames ===== */
QFrame {{
    background-color: transparent;
    border: none;
}}

QFrame[class="panel"] {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 8px;
}}

QFrame[class="card"] {{
    background-color: {COLORS['bg_tertiary']};
    border-radius: 8px;
}}

/* ===== Group Box ===== */
QGroupBox {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {COLORS['accent_cyan']};
    font-weight: bold;
}}

/* ===== Splitter ===== */
QSplitter::handle {{
    background-color: {COLORS['border_default']};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

QSplitter::handle:hover {{
    background-color: {COLORS['accent_cyan']};
}}

/* ===== Tab Widget ===== */
QTabWidget::pane {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 8px;
    border-top-left-radius: 0;
}}

QTabBar::tab {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border_default']};
    border-bottom: none;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['accent_cyan']};
    border-bottom: 2px solid {COLORS['accent_cyan']};
}}

QTabBar::tab:hover:!selected {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

/* ===== Tool Tips ===== */
QToolTip {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 4px;
    padding: 6px;
}}

/* ===== Menu ===== */
QMenu {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 6px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['accent_cyan']};
}}

QMenu::separator {{
    height: 1px;
    background-color: {COLORS['border_default']};
    margin: 4px 8px;
}}

/* ===== Status Bar ===== */
QStatusBar {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    border-top: 1px solid {COLORS['border_default']};
}}

/* ===== Custom Widget Classes ===== */
QWidget[class="chat-bubble-user"] {{
    background-color: {COLORS['bubble_user']};
    border-radius: 16px;
    border-top-right-radius: 4px;
}}

QWidget[class="chat-bubble-alfred"] {{
    background-color: {COLORS['bubble_alfred']};
    border-radius: 16px;
    border-top-left-radius: 4px;
}}

QWidget[class="waveform"] {{
    background-color: {COLORS['waveform_bg']};
    border-radius: 8px;
}}

QWidget[class="action-tile"] {{
    background-color: {COLORS['bg_tertiary']};
    border-radius: 8px;
    border: 2px solid transparent;
}}

QWidget[class="action-tile"]:hover {{
    background-color: {COLORS['bg_hover']};
    border-color: {COLORS['border_hover']};
}}

QWidget[class="dashboard-panel"] {{
    background-color: {COLORS['bg_secondary']};
    border-radius: 8px;
    border: 1px solid {COLORS['border_default']};
}}
"""
