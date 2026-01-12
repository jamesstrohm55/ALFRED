"""ALFRED UI Widgets Package"""
from .chat_widget import ChatWidget, ChatBubble
from .waveform_widget import WaveformWidget
from .quick_actions import QuickActionsWidget
from .system_dashboard import SystemDashboard
from .input_bar import InputBar

__all__ = [
    'ChatWidget',
    'ChatBubble',
    'WaveformWidget',
    'QuickActionsWidget',
    'SystemDashboard',
    'InputBar'
]
