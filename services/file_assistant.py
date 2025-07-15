import os
import subprocess
import platform

def find_file(filename, search_path='C:\\'):
    matches = []
    for root, dirs, files in os.walk(search_path):
        for name in files:
            if filename.lower() in name.lower():
                matches.append(os.path.join(root, name))
    return matches

def open_file_or_folder(path):
    if platform.system() == 'Windows':
        os.startfile(path)
    elif platform.system() == 'Darwin':  # macOS
        subprocess.call(['open', path])
    elif platform.system() == 'Linux':
        subprocess.call(['xdg-open', path])
    else:
        subprocess.call(['xdg-open', path])  # Fallback for unknown systems

def delete_file(path):
    try:
        os.remove(path)
        return f"File deleted successfully."
    except Exception as e:
        return f"Error deleting file: {str(e)}"
    
def list_files_in_folder(folder_path):
    try:
        return os.listdir(folder_path)
    except Exception as e:
        return f"Error listing files in folder: {str(e)}"