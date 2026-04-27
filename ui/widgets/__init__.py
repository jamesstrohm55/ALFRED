"""ALFRED UI Widgets Package"""

from .chat_widget import ChatBubble, ChatWidget
from .date_separator import DateSeparator
from .gradient_bar import GradientBar
from .input_zone import InputZone
from .quick_actions import QuickActionsWidget
from .settings_panel import SettingsPanel
from .sidebar import CollapsibleSidebar
from .status_bar import StatusBar
from .system_dashboard import SystemDashboard
from .title_bar import CustomTitleBar

__all__ = [
    "ChatWidget",
    "ChatBubble",
    "GradientBar",
    "InputZone",
    "QuickActionsWidget",
    "SystemDashboard",
    "CustomTitleBar",
    "CollapsibleSidebar",
    "StatusBar",
    "DateSeparator",
    "SettingsPanel",
]
