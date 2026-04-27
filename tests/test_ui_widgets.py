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


class TestInputZone:
    def test_initial_state_is_idle(self, qapp):
        from ui.widgets.input_zone import InputZone

        zone = InputZone()
        assert zone.state == InputZone.IDLE

    def test_set_state_listening(self, qapp):
        from ui.widgets.input_zone import InputZone

        zone = InputZone()
        zone.set_state(InputZone.LISTENING)
        assert zone.state == InputZone.LISTENING

    def test_set_state_speaking(self, qapp):
        from ui.widgets.input_zone import InputZone

        zone = InputZone()
        zone.set_state(InputZone.SPEAKING)
        assert zone.state == InputZone.SPEAKING

    def test_set_state_idle_from_listening(self, qapp):
        from ui.widgets.input_zone import InputZone

        zone = InputZone()
        zone.set_state(InputZone.LISTENING)
        zone.set_state(InputZone.IDLE)
        assert zone.state == InputZone.IDLE

    def test_same_state_is_noop(self, qapp):
        from ui.widgets.input_zone import InputZone

        zone = InputZone()
        zone.set_state(InputZone.IDLE)
        assert zone.state == InputZone.IDLE

    def test_text_submitted_signal(self, qapp):
        from ui.widgets.input_zone import InputZone

        zone = InputZone()
        received = []
        zone.text_submitted.connect(received.append)
        zone._text_input.setText("hello")
        zone._on_send_clicked()
        assert received == ["hello"]

    def test_on_listening_state_changed_true(self, qapp):
        from ui.widgets.input_zone import InputZone

        zone = InputZone()
        zone.on_listening_state_changed(True)
        assert zone.state == InputZone.LISTENING

    def test_on_listening_state_changed_false(self, qapp):
        from ui.widgets.input_zone import InputZone

        zone = InputZone()
        zone.set_state(InputZone.LISTENING)
        zone.on_listening_state_changed(False)
        assert zone.state == InputZone.IDLE
