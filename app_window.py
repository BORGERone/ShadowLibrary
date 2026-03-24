"""Shadow Library - Desktop Application"""

import subprocess
import threading
import time
import sys
import json
import os
import socket
import ctypes
import shutil
import webview


# Глобальная переменная для окна
main_window = None


class WindowAPI:
    """API для управления окном из JavaScript"""
    
    def minimize_window(self):
        """Свернуть окно"""
        if main_window:
            main_window.minimize()
    
    def toggle_maximize_window(self):
        """Развернуть/восстановить окно"""
        if main_window:
            main_window.toggle_fullscreen()
    
    def close_window(self):
        """Закрыть окно"""
        if main_window:
            main_window.destroy()
        os._exit(0)


def get_exe_dir():
    """Получить директорию исполняемого файла"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_path(filename):
    """Получить путь к ресурсу (работает и в exe, и в режиме разработки)"""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


# Папка для данных в %APPDATA%
DATA_DIR = os.path.join(os.environ.get("APPDATA", "."), "ShadowLibrary")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def get_icon_path():
    """Получить путь к иконке приложения"""
    # Сначала ищем рядом с exe (в dist)
    exe_dir = get_exe_dir()
    icon_path = os.path.join(exe_dir, "icon.ico")
    if os.path.exists(icon_path):
        return icon_path
    # Если нет - используем ресурс
    return get_resource_path("icon.ico")


def ensure_icon_exists():
    """Убедиться, что иконка существует в папке данных приложения"""
    icon_in_data = os.path.join(DATA_DIR, "icon.ico")
    if not os.path.exists(icon_in_data):
        # Копируем иконку из ресурсов в папку данных
        source_icon = get_icon_path()
        if os.path.exists(source_icon):
            shutil.copy2(source_icon, icon_in_data)
    return icon_in_data


def get_config_path():
    """Получить путь к конфигу (внешний файл рядом с exe или встроенный)"""
    # Сначала ищем внешний config.json рядом с exe
    exe_dir = get_exe_dir()
    external_config = os.path.join(exe_dir, "config.json")
    if os.path.exists(external_config):
        return external_config
    # Если нет - используем встроенный
    return get_resource_path("config.json")


# Проверка на единственный экземпляр
def is_already_running():
    mutex = ctypes.windll.kernel32.CreateMutexW(None, True, "ShadowLibrary_Mutex")
    if mutex == 0:
        return False
    if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        ctypes.windll.kernel32.CloseHandle(mutex)
        return True
    return False


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


# Путь к конфигу для записи и приоритетного чтения (в %APPDATA%)
APPDATA_CONFIG = os.path.join(os.environ.get("APPDATA", "."), "ShadowLibrary", "config.json")


def check_steam_path():
    # Сначала пробуем читать из APPDATA
    config_file = APPDATA_CONFIG
    if not os.path.exists(config_file):
        # Если нет - читаем из внешнего или встроенного
        config_file = get_config_path()
    if not os.path.exists(config_file):
        return False
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        steam_path = config.get("Custom_Steam_Path", "")
        return bool(steam_path) and os.path.exists(steam_path) and os.path.exists(os.path.join(steam_path, "steam.exe"))
    except:
        return False


def is_first_launch():
    """Проверяет, является ли запуск первым (нет config.json в APPDATA или нет языка)"""
    # Сначала проверяем конфиг в APPDATA
    config_file = APPDATA_CONFIG
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            return "Language" not in config
        except:
            return True
    # Если нет конфига в APPDATA, проверяем внешний/встроенный
    config_file = get_config_path()
    if not os.path.exists(config_file):
        return True
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        return "Language" not in config
    except:
        return True


def run_server():
    """Запускает сервер в отдельном потоке"""
    import uvicorn
    from web_server import app
    uvicorn.run(app, host="127.0.0.1", port=1337, log_level="warning")


def main():
    # Проверка на единственный экземпляр
    if is_already_running():
        print("Application already running!")
        input("Press Enter to exit...")
        return

    # Проверяем, не запущен ли уже сервер на порту 1337
    server_running = is_port_in_use(1337)

    if not server_running:
        # Запускаем сервер в отдельном потоке
        print("Starting server...")
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(2)
    else:
        print("Server already running on port 1337")

    # Проверяем первый запуск и путь к Steam
    first_launch = is_first_launch()
    need_steam_path = not check_steam_path()

    url = "http://127.0.0.1:1337"
    params = []
    if need_steam_path:
        params.append("show_steam_modal=1")
    if first_launch:
        params.append("first_launch=1")

    if params:
        url += "?" + "&".join(params)

    # Получаем путь к иконке
    icon_path = ensure_icon_exists()
    
    print(f"Starting pywebview window...\nURL: {url}\nIcon: {icon_path}\nPress Ctrl+C to stop\n{'-' * 50}")

    # Создаём API для управления окном
    api = WindowAPI()
    
    # Создаём окно с иконкой через pywebview (frameless для кастомной панели)
    window = webview.create_window(
        title="Shadow Library",
        url=url,
        js_api=api,
        width=1200,
        height=800,
        x=100,
        y=100,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600),
        frameless=True,
        transparent=True
    )
    
    # Сохраняем ссылку на окно
    global main_window
    main_window = window

    # Устанавливаем иконку окна после создания
    if os.path.exists(icon_path):
        try:
            window.set_icon(icon_path)
        except:
            pass

    webview.start()


if __name__ == "__main__":
    main()
