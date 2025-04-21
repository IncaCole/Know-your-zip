import os
import shutil
import sys

def clean_python():
    """Clean Python-specific files and directories."""
    # Files and directories to clean
    items_to_clean = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.pytest_cache',
        '.coverage',
        'htmlcov',
        '*.egg-info',
        'build',
        'dist'
    ]
    
    # Current directory
    current_dir = os.getcwd()
    
    # Walk through the directory
    for root, dirs, files in os.walk(current_dir):
        # Clean directories
        for dir_name in dirs:
            if dir_name in ['__pycache__', 'build', 'dist', '.pytest_cache', 'htmlcov']:
                dir_path = os.path.join(root, dir_name)
                print(f"Removing directory: {dir_path}")
                shutil.rmtree(dir_path, ignore_errors=True)
        
        # Clean files
        for file_name in files:
            if file_name.endswith(('.pyc', '.pyo', '.pyd')) or file_name == '.coverage':
                file_path = os.path.join(root, file_name)
                print(f"Removing file: {file_path}")
                try:
                    os.remove(file_path)
                except OSError:
                    pass

if __name__ == "__main__":
    print("Starting Python cleanup...")
    clean_python()
    print("Python cleanup completed!") 