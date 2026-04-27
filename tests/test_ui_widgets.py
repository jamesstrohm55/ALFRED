"""
Smoke tests for refactored UI widgets.
Skipped in CI environments without a display.
"""

import os
import sys

import pytest

pytestmark = pytest.mark.skipif("CI" in os.environ, reason="UI tests require display")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


class TestGradientBar:
    def test_initial_value_is_zero(self, qapp):
        from ui.widgets.gradient_bar import GradientBar
        bar = GradientBar("#00d4ff", "#0088bb")
        assert bar._value == 0

    def test_set_value_clamps_to_range(self, qapp):
        from ui.widgets.gradient_bar import GradientBar
        bar = GradientBar("#00d4ff", "#0088bb")
        bar.set_value(150)
        assert bar._value == 100
        bar.set_value(-10)
        assert bar._value == 0

    def test_set_value_normal(self, qapp):
        from ui.widgets.gradient_bar import GradientBar
        bar = GradientBar("#00d4ff", "#0088bb")
        bar.set_value(45)
        assert bar._value == 45
