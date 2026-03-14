"""ALFRED UI Widgets Package"""

from .chat_widget import ChatBubble, ChatWidget
from .date_separator import DateSeparator
from .input_bar import InputBar
from .quick_actions import QuickActionsWidget
from .settings_panel import SettingsPanel
from .sidebar import CollapsibleSidebar
from .status_bar import StatusBar
from .system_dashboard import SystemDashboard
from .title_bar import CustomTitleBar
from .waveform_widget import WaveformWidget

__all__ = [
    "ChatWidget",
    "ChatBubble",
    "WaveformWidget",
    "QuickActionsWidget",
    "SystemDashboard",
    "InputBar",
    "CustomTitleBar",
    "CollapsibleSidebar",
    "StatusBar",
    "DateSeparator",
    "SettingsPanel",
]
