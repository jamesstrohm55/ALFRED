"""
Calendar command handler for parsing and executing calendar-related commands.

Supports natural language commands like:
- "add meeting Team standup tomorrow at 10am for 1 hour"
- "add event Doctor appointment on Friday at 2pm"
- "schedule meeting with John next Monday at 3pm for 30 minutes"
"""
import datetime
import re
from utils.logger import get_logger

logger = get_logger(__name__)

# Try to import dateparser, but handle missing dependency gracefully
try:
    import dateparser
    DATEPARSER_AVAILABLE = True
except ImportError:
    DATEPARSER_AVAILABLE = False
    logger.warning("dateparser not installed - calendar date parsing limited")


def handle_calendar_command(user_input: str) -> str:
    """
    Handle calendar-related commands.

    Args:
        user_input: The user's command string

    Returns:
        Response string or None if not a calendar command
    """
    user_input_lower = user_input.lower()

    # Check if this is a calendar command
    calendar_triggers = ["add meeting", "add event", "schedule meeting", "schedule event", "calendar add"]
    if not any(trigger in user_input_lower for trigger in calendar_triggers):
        return None

    # Check for dateparser availability
    if not DATEPARSER_AVAILABLE:
        return ("I need the 'dateparser' library to handle calendar commands. "
                "Please install it with: pip install dateparser")

    # Parse the command
    parsed = parse_calendar_command(user_input)

    if not parsed.get('title'):
        return ("I need more information to add this event. Please try a command like:\n"
                "\"Add meeting Team standup tomorrow at 10am for 1 hour\"\n"
                "or \"Schedule event Doctor appointment on Friday at 2pm\"")

    if not parsed.get('start_datetime'):
        return (f"I understood you want to add '{parsed['title']}', but I couldn't determine when. "
                "Please include a date and time, like 'tomorrow at 3pm' or 'next Monday at 10am'.")

    # Import calendar service and add the event
    try:
        from services.calendar_service import add_event

        title = parsed['title']
        start = parsed['start_datetime']
        end = start + parsed.get('duration', datetime.timedelta(hours=1))
        description = parsed.get('description', '')

        add_event(title, start, end, description)

        logger.info(f"Added calendar event: {title} at {start}")
        return (f"'{title}' has been added to your calendar for "
                f"{start.strftime('%A, %B %d at %I:%M %p')}.")

    except ImportError as e:
        logger.error(f"Calendar service not available: {e}")
        return "Calendar service is not configured. Please check your Google Calendar setup."
    except Exception as e:
        logger.error(f"Failed to add calendar event: {e}")
        return f"Sorry, I couldn't add that event: {str(e)}"


def parse_calendar_command(text: str) -> dict:
    """
    Parse a natural language calendar command.

    Args:
        text: The command text to parse

    Returns:
        Dictionary with parsed components: title, start_datetime, duration, description
    """
    result = {
        'title': None,
        'start_datetime': None,
        'duration': datetime.timedelta(hours=1),  # Default 1 hour
        'description': ''
    }

    text_lower = text.lower()

    # Remove trigger phrases to get the content
    for trigger in ["add meeting", "add event", "schedule meeting", "schedule event", "calendar add"]:
        if trigger in text_lower:
            text = text[text_lower.find(trigger) + len(trigger):].strip()
            text_lower = text.lower()
            break

    # Extract duration if specified (e.g., "for 1 hour", "for 30 minutes")
    duration_match = re.search(r'for\s+(\d+)\s*(hour|minute|hr|min)s?', text_lower)
    if duration_match:
        amount = int(duration_match.group(1))
        unit = duration_match.group(2)
        if 'hour' in unit or 'hr' in unit:
            result['duration'] = datetime.timedelta(hours=amount)
        else:
            result['duration'] = datetime.timedelta(minutes=amount)
        # Remove duration from text for further parsing
        text = text[:duration_match.start()] + text[duration_match.end():]
        text_lower = text.lower()

    # Try to find date/time expressions
    # Common patterns: "tomorrow at 10am", "next Monday at 3pm", "on Friday at 2pm"
    datetime_patterns = [
        r'(tomorrow|today|tonight)\s+at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?',
        r'(next|this)\s+\w+day\s+at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?',
        r'on\s+\w+day\s+at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?',
        r'at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?',
        r'\d{1,2}(?::\d{2})?\s*(?:am|pm)',
        r'\d{1,2}/\d{1,2}(?:/\d{2,4})?\s+at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?',
    ]

    datetime_text = None
    datetime_start = len(text)
    datetime_end = len(text)

    for pattern in datetime_patterns:
        match = re.search(pattern, text_lower)
        if match and match.start() < datetime_start:
            datetime_text = match.group(0)
            datetime_start = match.start()
            datetime_end = match.end()

    # Parse the datetime using dateparser
    if datetime_text and DATEPARSER_AVAILABLE:
        parsed_dt = dateparser.parse(datetime_text, settings={
            'PREFER_DATES_FROM': 'future',
            'PREFER_DAY_OF_MONTH': 'first'
        })
        if parsed_dt:
            result['start_datetime'] = parsed_dt
            # Extract title from text before the datetime
            title_text = text[:datetime_start].strip()
            # Clean up title
            title_text = re.sub(r'^(called|named|titled)\s+', '', title_text, flags=re.IGNORECASE)
            title_text = title_text.strip(' ,.')
            if title_text:
                result['title'] = title_text.title()

    # If we couldn't find a title but have some text, use it
    if not result['title'] and text.strip():
        # Try to extract just the title if it's before common prepositions
        title_match = re.match(r'^([^@]+?)(?:\s+(?:at|on|tomorrow|today|next|for)\s+)', text, re.IGNORECASE)
        if title_match:
            result['title'] = title_match.group(1).strip().title()
        else:
            # Use the whole text minus any datetime we found
            clean_text = text[:datetime_start].strip() if datetime_start < len(text) else text
            clean_text = clean_text.strip(' ,.')
            if clean_text:
                result['title'] = clean_text.title()

    return result


def parse_duration(text: str) -> datetime.timedelta:
    """
    Parse duration text like '2 hours 30 minutes' into timedelta.

    Args:
        text: Duration string to parse

    Returns:
        timedelta object representing the duration
    """
    text = text.lower()
    minutes = 0

    # Parse hours
    hour_match = re.search(r'(\d+)\s*(?:hour|hr)s?', text)
    if hour_match:
        minutes += int(hour_match.group(1)) * 60

    # Parse minutes
    min_match = re.search(r'(\d+)\s*(?:minute|min)s?', text)
    if min_match:
        minutes += int(min_match.group(1))

    return datetime.timedelta(minutes=minutes or 30)  # Default to 30 mins if unclear
