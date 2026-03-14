"""
Utility functions for ALFRED UI - icon loading and helpers.
"""

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

ICONS_DIR = os.path.join(os.path.dirname(__file__), "resources", "icons")


def load_svg_icon(name: str, size: int = 24, color: str = None) -> QIcon:
    """
    Load an SVG icon by name from the icons directory.

    Args:
        name: Icon filename without extension (e.g., 'system')
        size: Icon size in pixels
        color: Optional override color (not used for pre-colored SVGs)

    Returns:
        QIcon loaded from SVG, or empty QIcon if not found
    """
    pixmap = load_svg_pixmap(name, size)
    if pixmap.isNull():
        return QIcon()
    return QIcon(pixmap)


def load_svg_pixmap(name: str, size: int = 24) -> QPixmap:
    """
    Load an SVG as a QPixmap by name.

    Args:
        name: Icon filename without extension
        size: Target size in pixels

    Returns:
        QPixmap rendered from SVG, or null QPixmap if not found
    """
    path = os.path.join(ICONS_DIR, f"{name}.svg")
    if not os.path.exists(path):
        return QPixmap()

    renderer = QSvgRenderer(path)
    if not renderer.isValid():
        return QPixmap()

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def get_icon_path(name: str) -> str:
    """Get the full path to an icon file."""
    return os.path.join(ICONS_DIR, f"{name}.svg")
