"""
File assistant command handler for A.L.F.R.E.D - processes file operations.
"""
from __future__ import annotations

import os
from typing import Optional, Union

from services.file_assistant import find_file, open_file_or_folder, delete_file, list_files_in_folder
from core.voice import speak


def handle_file_command(user_input: str) -> Optional[Union[str, list[str]]]:
    """
    Handle file-related commands (find, open, delete, list).

    Args:
        user_input: The user's command text

    Returns:
        Response string, list of file paths, or None if not a file command
    """
    user_input = user_input.lower()

    if user_input.startswith("find "):
        filename: str = user_input.replace("find ", "").strip()
        results: list[str] = find_file(filename)
        if results:
            speak(f"I found {len(results)} result(s).")
            return results[:5]  # Return only the first 5 results for brevity
        else:
            return "No files found."

    elif user_input.startswith("open "):
        target: str = user_input.replace("open ", "").strip()
        if os.path.exists(target):
            open_file_or_folder(target)
            return "File found and opened"
        else:
            matches: list[str] = find_file(target)
            if matches:
                open_file_or_folder(matches[0])
                return "File found and opened"
            else:
                return "File not found."

    elif user_input.startswith("delete "):
        filename = user_input.replace("delete ", "").strip()
        matches = find_file(filename)

        if matches:
            file_to_delete: str = matches[0]
            speak("Are you sure you want to delete this file?")
            confirm: str = input("Type yes to confirm or no to cancel: ").strip().lower()
            if confirm == "yes":
                return delete_file(file_to_delete)
            else:
                return "Delete operation canceled."
        else:
            return "File not found."

    elif user_input.startswith("list files in "):
        folder: str = user_input.replace("list files in ", "").strip()
        if os.path.exists(folder):
            files: list[str] = list_files_in_folder(folder)
            if files:
                return f"Files in {folder}:\n" + "\n".join(files)
            else:
                return f"No files found in {folder}."
        else:
            return "Folder not found."

    return None