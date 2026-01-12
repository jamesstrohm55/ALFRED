"""
ALFRED GUI Application Entry Point.

Usage:
    python -m ui.app

Or from the main directory:
    python ui/app.py
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main entry point for the ALFRED GUI application."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("A.L.F.R.E.D")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("ALFRED")

    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Import and create main window
    from ui.main_window import MainWindow
    window = MainWindow()

    # Optional: Play startup announcement
    try:
        from core.voice import speak
        speak("Graphical interface loaded, sir.")
    except ImportError as e:
        logger.warning(f"Voice module not available: {e}")
    except (OSError, RuntimeError) as e:
        logger.warning(f"Voice playback failed: {e}")

    # Show window
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
