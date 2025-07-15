from openai import OpenAI
from config import OPENAI_KEY, OPENROUTER_API_KEY
from memory.memory_manager import remember, recall, forget, list_memory, semantic_search_memory
from services.automation import run_command
from service_commands.calendar_commands import handle_calendar_command
from service_commands.weather_commands import handle_weather_command
from service_commands.file_assistant_commands import handle_file_command
from service_commands.system_monitor_commands import handle_system_monitor_command
from service_commands.memory_commands import handle_memory_commands

client = OpenAI(api_key=OPENAI_KEY)


def get_response(text):
    lower = text.lower().strip()

    try:
        # Memory Commands
        response = handle_memory_commands(lower)
        if response:
            return response

        # Service Commands
        response = handle_service_commands(lower)
        if response:
            return response

        # System Level OS Commands
        response = run_command(lower)
        if response:
            print(f"Command executed: {response}")
            return response

        # General GPT Query with LLM fallback
        return query_llm_fallback(lower)

    except Exception as e:
        print(f"Error in get_response: {e}")
        return "Sorry, I encountered an error while processing your request."


def handle_service_commands(text):
    if any(keyword in text for keyword in ["calendar", "schedule", "remind", "event"]):
        return handle_calendar_command(text)

    if any(keyword in text for keyword in ["weather", "forecast", "temperature"]):
        return handle_weather_command(text)

    if any(keyword in text for keyword in ["file", "document", "upload", "download"]):
        return handle_file_command(text)

    if any(keyword in text for keyword in ["system", "monitor", "status"]):
        return handle_system_monitor_command(text)

    return None


def query_llm_fallback(text):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are A.L.F.R.E.D, an All Knowing Logical Facilitator for Reasoned Execution of Duties."},
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content

    except Exception as e:
        print(f"Primary LLM failed: {e}")
        # Fallback to OpenRouter
        try:
            openrouter_client = OpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )
            completion = openrouter_client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=[
                    {"role": "system", "content": "You are A.L.F.R.E.D, an All Knowing Logical Facilitator for Reasoned Execution of Duties."},
                    {"role": "user", "content": text}
                ]
            )
            return completion.choices[0].message.content

        except Exception as fallback_error:
            print(f"Fallback LLM also failed: {fallback_error}")
            return "Sorry, I couldn't process your request with any available models."
