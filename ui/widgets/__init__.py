"""ALFRED UI Widgets Package"""
from .chat_widget import ChatWidget, ChatBubble
from .waveform_widget import WaveformWidget
from .quick_actions import QuickActionsWidget
from .system_dashboard import SystemDashboard
from .input_bar import InputBar
from .title_bar import CustomTitleBar
from .sidebar import CollapsibleSidebar
from .status_bar import StatusBar
from .date_separator import DateSeparator
from .settings_panel import SettingsPanel

__all__ = [
    'ChatWidget',
    'ChatBubble',
    'WaveformWidget',
    'QuickActionsWidget',
    'SystemDashboard',
    'InputBar',
    'CustomTitleBar',
    'CollapsibleSidebar',
    'StatusBar',
    'DateSeparator',
    'SettingsPanel',
]
