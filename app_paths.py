"""
Утилита для определения правильных путей к данным приложения.
Обеспечивает работу как в режиме разработки, так и после установки.
"""
import os
import sys
from pathlib import Path


def get_app_data_dir():
    """
    Возвращает путь к директории данных приложения.
    
    Если приложение запущено из установленной версии (в Program Files),
    использует AppData\Local\ChatList.
    Иначе использует текущую директорию (режим разработки).
    """
    # Определяем, запущено ли приложение из установленной версии
    if getattr(sys, 'frozen', False):
        # Приложение упаковано в exe
        exe_path = Path(sys.executable)
        
        # Проверяем, находится ли exe в Program Files
        program_files = Path(os.environ.get('ProgramFiles', 'C:\\Program Files'))
        program_files_x86 = Path(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'))
        
        if (program_files in exe_path.parents or 
            program_files_x86 in exe_path.parents or
            'Program Files' in str(exe_path)):
            # Установленная версия - используем AppData
            appdata_local = Path(os.environ.get('LOCALAPPDATA', 
                                                Path.home() / 'AppData' / 'Local'))
            app_data_dir = appdata_local / 'ChatList'
            app_data_dir.mkdir(parents=True, exist_ok=True)
            return str(app_data_dir)
    
    # Режим разработки - используем текущую директорию
    return os.getcwd()


def get_db_path():
    """Возвращает путь к файлу базы данных."""
    app_data_dir = get_app_data_dir()
    return os.path.join(app_data_dir, 'chatlist.db')


def get_logs_dir():
    """Возвращает путь к директории логов."""
    app_data_dir = get_app_data_dir()
    logs_dir = os.path.join(app_data_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


def get_env_path():
    """Возвращает путь к файлу .env."""
    app_data_dir = get_app_data_dir()
    return os.path.join(app_data_dir, '.env')

