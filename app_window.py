"""Shadow Library - Desktop Application"""

import subprocess
import threading
import time
import sys
import json
import os
import socket
import ctypes


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


def find_edge_path():
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for path in edge_paths:
        if os.path.exists(path):
            return path
    return "msedge"


def run_server():
    """Запускает сервер в отдельном потоке"""
    import uvicorn
    from web_server import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")


def main():
    # Проверка на единственный экземпляр
    if is_already_running():
        print("Application already running!")
        input("Press Enter to exit...")
        return

    # Проверяем, не запущен ли уже сервер на порту 8000
    server_running = is_port_in_use(8000)

    if not server_running:
        # Запускаем сервер в отдельном потоке
        print("Starting server...")
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(2)
    else:
        print("Server already running on port 8000")

    # Проверяем первый запуск и путь к Steam
    first_launch = is_first_launch()
    need_steam_path = not check_steam_path()

    url = "http://127.0.0.1:8000"
    params = []
    if need_steam_path:
        params.append("show_steam_modal=1")
    if first_launch:
        params.append("first_launch=1")

    if params:
        url += "?" + "&".join(params)

    edge_path = find_edge_path()
    print(f"Starting Edge in app mode...\nURL: {url}\nPress Ctrl+C to stop\n{'-' * 50}")

    # Запускаем Edge в режиме приложения
    edge_process = subprocess.Popen([
        edge_path,
        f"--app={url}",
        "--window-size=1200,800",
        "--window-position=100,100",
        "--disable-extensions",
        "--disable-background-networking",
        "--no-first-run",
    ])

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
    print("Done")


if __name__ == "__main__":
    main()
