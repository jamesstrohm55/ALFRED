"""
File assistant service for finding, opening, and managing files.
"""
import os
import subprocess
import platform
import threading
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

# Directories to skip during file search (common system/cache directories)
EXCLUDED_DIRS = {
    # Windows
    '$Recycle.Bin', 'Windows', 'ProgramData', 'AppData',
    'node_modules', '.git', '__pycache__', '.venv', 'venv',
    'System Volume Information', 'Recovery',
    # Cross-platform
    '.cache', '.npm', '.yarn', 'site-packages',
}

# Maximum search results to prevent memory issues
DEFAULT_MAX_RESULTS = 100

# Search cancellation support
_search_cancelled = threading.Event()


def cancel_search():
    """Cancel any ongoing file search."""
    _search_cancelled.set()
    logger.info("File search cancelled")


def _reset_search():
    """Reset search cancellation flag."""
    _search_cancelled.clear()


def is_safe_path(path: str) -> bool:
    """
    Validate that a path is safe to operate on.

    Args:
        path: Path to validate

    Returns:
        True if path is safe, False otherwise
    """
    if not path:
        return False

    try:
        # Resolve the path to catch path traversal attempts
        resolved = Path(path).resolve()

        # Check for obvious dangerous paths
        path_lower = str(resolved).lower()
        dangerous_patterns = [
            'windows\\system32',
            'windows\\syswow64',
            'program files',
            '\\system volume information',
        ]

        for pattern in dangerous_patterns:
            if pattern in path_lower:
                logger.warning(f"Blocked operation on system path: {path}")
                return False

        return True

    except (ValueError, OSError) as e:
        logger.warning(f"Invalid path '{path}': {e}")
        return False


def find_file(filename: str, search_path: str = None, max_results: int = DEFAULT_MAX_RESULTS) -> list:
    """
    Find files matching the given filename.

    Args:
        filename: Name or partial name to search for
        search_path: Directory to search in (defaults to user's home directory)
        max_results: Maximum number of results to return

    Returns:
        List of matching file paths
    """
    _reset_search()

    # Default to user's home directory instead of C:\
    if search_path is None:
        search_path = str(Path.home())

    if not os.path.isdir(search_path):
        logger.warning(f"Search path does not exist: {search_path}")
        return []

    matches = []
    filename_lower = filename.lower()
    files_scanned = 0

    logger.info(f"Searching for '{filename}' in {search_path}")

    try:
        for root, dirs, files in os.walk(search_path):
            # Check for cancellation
            if _search_cancelled.is_set():
                logger.info(f"Search cancelled after scanning {files_scanned} files")
                break

            # Skip excluded directories (modify dirs in-place to prevent descent)
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith('.')]

            for name in files:
                files_scanned += 1

                if filename_lower in name.lower():
                    full_path = os.path.join(root, name)
                    matches.append(full_path)

                    if len(matches) >= max_results:
                        logger.info(f"Search stopped: reached {max_results} results")
                        return matches

    except PermissionError as e:
        logger.debug(f"Permission denied during search: {e}")
    except Exception as e:
        logger.error(f"Error during file search: {e}")

    logger.info(f"Search complete: found {len(matches)} matches after scanning {files_scanned} files")
    return matches


def open_file_or_folder(path: str) -> str:
    """
    Open a file or folder with the system's default application.

    Args:
        path: Path to the file or folder

    Returns:
        Success or error message
    """
    if not is_safe_path(path):
        return "Cannot open this path for security reasons."

    if not os.path.exists(path):
        return f"Path does not exist: {path}"

    try:
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', path])
        else:  # Linux and others
            subprocess.call(['xdg-open', path])

        logger.info(f"Opened: {path}")
        return f"Opened: {path}"

    except Exception as e:
        logger.error(f"Error opening '{path}': {e}")
        return f"Error opening file: {str(e)}"


def delete_file(path: str, confirm: bool = True) -> str:
    """
    Delete a file safely.

    Args:
        path: Path to the file to delete
        confirm: If True, requires the path to be validated (safety check)

    Returns:
        Success or error message
    """
    if not is_safe_path(path):
        return "Cannot delete this path for security reasons."

    if not os.path.exists(path):
        return f"File does not exist: {path}"

    if os.path.isdir(path):
        return "Cannot delete directories with this command. Use a file manager for directories."

    try:
        os.remove(path)
        logger.info(f"Deleted file: {path}")
        return f"File deleted successfully: {path}"
    except PermissionError:
        return f"Permission denied: cannot delete {path}"
    except Exception as e:
        logger.error(f"Error deleting '{path}': {e}")
        return f"Error deleting file: {str(e)}"


def list_files_in_folder(folder_path: str) -> list:
    """
    List files in a folder.

    Args:
        folder_path: Path to the folder

    Returns:
        List of filenames or error message string
    """
    if not is_safe_path(folder_path):
        return "Cannot list this path for security reasons."

    if not os.path.isdir(folder_path):
        return f"Not a valid directory: {folder_path}"

    try:
        files = os.listdir(folder_path)
        logger.debug(f"Listed {len(files)} items in {folder_path}")
        return files
    except PermissionError:
        return f"Permission denied: cannot list {folder_path}"
    except Exception as e:
        logger.error(f"Error listing '{folder_path}': {e}")
        return f"Error listing files in folder: {str(e)}"
