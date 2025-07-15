from services.file_assistant import find_file, open_file_or_folder, delete_file, list_files_in_folder
from core.voice import speak
import os

def handle_file_command(user_input):
    user_input = user_input.lower()

    if user_input.startswith("find "):
        filename = user_input.replace("find ", "").strip()
        results = find_file(filename)
        if results:
            speak(f"I found {len(results)} result(s).")
            return results[:5]  # Return only the first 5 results for brevity
        else:
            return "No files found."
        
    elif user_input.startswith("open "):
        target = user_input.replace("open ", "").strip()
        if os.path.exists(target):
            open_file_or_folder(target)
            return f"File found and opened"
        else:
            matches = find_file(target)
            if matches:
                open_file_or_folder(matches[0])
                return f"File found and opened"
            else:
                return "File not found."
        
    elif user_input.startswith("delete "):
        filename = user_input.replace("delete ", "").strip()
        matches = find_file(filename)
        
        if matches:
            file_to_delete = matches[0]
            speak(f"Are you sure you want to delete this file?")
            confirm = input("Type yes to confirm or no to cancel: ").strip().lower()
            if confirm == "yes":
                return delete_file(file_to_delete)
            else:
                return "Delete operation canceled."
        else:
            return "File not found."
        
    elif user_input.startswith("list files in "):
        folder = user_input.replace("list files in ", "").strip()
        if os.path.exists(folder):
            files = list_files_in_folder(folder)
            if files:
                return f"Files in {folder}:\n" + "\n".join(files)
            else:
                return f"No files found in {folder}."
        else:
            return "Folder not found."
        
    return None