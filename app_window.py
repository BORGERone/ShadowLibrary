"""Shadow Library - Desktop Application"""

import threading
import time
import sys
import json
import os
import socket
import ctypes
import shutil
import webview
from ctypes import wintypes


# Глобальная переменная для окна
main_window = None

# Константы Windows для изменения размера окна
HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17

# Глобальная переменная для хранения HWND
window_hwnd = None

# Глобальные переменные для ручного resize
resize_state = {
    'is_resizing': False,
    'zone': None,
    'start_x': 0,
    'start_y': 0,
    'start_width': 0,
    'start_height': 0,
    'start_left': 0,
    'start_top': 0
}


class WindowAPI:
    """API для управления окном из JavaScript"""

    def __init__(self):
        self.resize_handler = None

    def set_window(self, window):
        """Установить ссылку на окно и инициализировать resize handler"""
        global main_window, window_hwnd
        main_window = window
        
        # Создаём ResizeHandler после создания окна
        self.resize_handler = ResizeHandler(window)

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

    def start_resize(self, zone):
        """
        Начать изменение размера окна.
        zone: 'top', 'bottom', 'left', 'right', 'top-left', 'top-right', 'bottom-left', 'bottom-right'
        """
        global window_hwnd, resize_state

        # Получаем HWND если ещё не получен
        if self.resize_handler:
            window_hwnd = self.resize_handler.get_hwnd()

        if not window_hwnd:
            return

        # Получаем текущую позицию мыши и окна
        point = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))

        rect = wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(window_hwnd, ctypes.byref(rect))

        # Сохраняем состояние для ручного resize
        resize_state['is_resizing'] = True
        resize_state['zone'] = zone
        resize_state['start_x'] = point.x
        resize_state['start_y'] = point.y
        resize_state['start_width'] = rect.right - rect.left
        resize_state['start_height'] = rect.bottom - rect.top
        resize_state['start_left'] = rect.left
        resize_state['start_top'] = rect.top
        resize_state['hwnd'] = window_hwnd

        # Устанавливаем capture на окно
        ctypes.windll.user32.SetCapture(window_hwnd)

        # Запускаем поток для отслеживания мыши
        resize_state['thread'] = threading.Thread(target=self._resize_loop, daemon=False)
        resize_state['thread'].start()

    def _resize_loop(self):
        """Цикл отслеживания мыши для resize"""
        global resize_state

        # Первый цикл - сразу начинаем resize
        point = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        self.resize_window(point.x, point.y, resize_state['zone'])

        # Ждём пока кнопка не будет отпущена
        while True:
            time.sleep(0.05)

            # GetAsyncKeyState возвращает SHORT, старший бит = состояние кнопки СЕЙЧАС
            lbutton_state = ctypes.windll.user32.GetAsyncKeyState(0x01)
            lbutton_down = (lbutton_state & 0x8000) != 0

            if not lbutton_down:
                # Кнопка отпущена - завершаем resize
                break

            # Получаем текущую позицию мыши
            point = wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(point))

            # Вызываем resize с текущей зоной
            self.resize_window(point.x, point.y, resize_state['zone'])

        # Освобождаем capture
        resize_state['is_resizing'] = False
        if resize_state.get('hwnd'):
            ctypes.windll.user32.ReleaseCapture()

    def resize_window(self, current_x, current_y, zone):
        """
        Обновить размер окна во время resize.
        zone: зона для resize (передаётся явно)
        """
        global resize_state
        if not resize_state['is_resizing']:
            return
        
        if not resize_state.get('hwnd'):
            return

        hwnd = resize_state['hwnd']
        
        # Вычисляем дельту
        dx = current_x - resize_state['start_x']
        dy = current_y - resize_state['start_y']
        
        # Новые параметры - начинаем с исходных
        new_left = resize_state['start_left']
        new_top = resize_state['start_top']
        new_width = resize_state['start_width']
        new_height = resize_state['start_height']
        
        # Минимальные размеры
        min_width, min_height = 800, 600
        
        # Применяем изменения ТОЛЬКО в направлении указанной зоны
        if zone == 'left':
            new_left = resize_state['start_left'] + dx
            new_width = resize_state['start_width'] - dx
            if new_width < min_width:
                new_left = resize_state['start_left'] + (resize_state['start_width'] - min_width)
                new_width = min_width
        elif zone == 'right':
            new_width = resize_state['start_width'] + dx
            if new_width < min_width:
                new_width = min_width
        elif zone == 'top':
            new_top = resize_state['start_top'] + dy
            new_height = resize_state['start_height'] - dy
            if new_height < min_height:
                new_top = resize_state['start_top'] + (resize_state['start_height'] - min_height)
                new_height = min_height
        elif zone == 'bottom':
            new_height = resize_state['start_height'] + dy
            if new_height < min_height:
                new_height = min_height
        elif zone == 'top-left':
            new_left = resize_state['start_left'] + dx
            new_top = resize_state['start_top'] + dy
            new_width = resize_state['start_width'] - dx
            new_height = resize_state['start_height'] - dy
            if new_width < min_width:
                new_left = resize_state['start_left'] + (resize_state['start_width'] - min_width)
                new_width = min_width
            if new_height < min_height:
                new_top = resize_state['start_top'] + (resize_state['start_height'] - min_height)
                new_height = min_height
        elif zone == 'top-right':
            new_top = resize_state['start_top'] + dy
            new_width = resize_state['start_width'] + dx
            new_height = resize_state['start_height'] - dy
            if new_width < min_width:
                new_width = min_width
            if new_height < min_height:
                new_top = resize_state['start_top'] + (resize_state['start_height'] - min_height)
                new_height = min_height
        elif zone == 'bottom-left':
            new_left = resize_state['start_left'] + dx
            new_width = resize_state['start_width'] - dx
            new_height = resize_state['start_height'] + dy
            if new_width < min_width:
                new_left = resize_state['start_left'] + (resize_state['start_width'] - min_width)
                new_width = min_width
            if new_height < min_height:
                new_height = min_height
        elif zone == 'bottom-right':
            new_width = resize_state['start_width'] + dx
            new_height = resize_state['start_height'] + dy
            if new_width < min_width:
                new_width = min_width
            if new_height < min_height:
                new_height = min_height
        
        # Устанавливаем новый размер и позицию
        SWP_NOZORDER = 0x0004
        SWP_NOACTIVATE = 0x0010
        ctypes.windll.user32.SetWindowPos(
            hwnd, 0,
            int(new_left), int(new_top),
            int(new_width), int(new_height),
            SWP_NOZORDER | SWP_NOACTIVATE
        )

    def end_resize(self):
        """Завершить resize операцию"""
        global resize_state
        print(f"RESIZE: END")
        resize_state['is_resizing'] = False
        resize_state['zone'] = None
        ctypes.windll.user32.ReleaseCapture()


class ResizeHandler:
    """Обработчик для получения HWND окна."""

    def __init__(self, window):
        self.window = window

    def get_hwnd(self):
        """Получаем HWND окна pywebview через поиск по заголовку"""
        global window_hwnd

        if window_hwnd:
            return window_hwnd

        try:
            # Ждём пока окно создастся
            for _ in range(10):
                time.sleep(0.1)

                def callback(hwnd, lparam):
                    global window_hwnd
                    try:
                        if ctypes.windll.user32.IsWindowVisible(hwnd):
                            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                            if length > 0:
                                buffer = ctypes.create_unicode_buffer(length + 1)
                                ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
                                if buffer.value == "Shadow Library":
                                    window_hwnd = hwnd
                                    return False
                    except:
                        pass
                    return True

                callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
                cb = callback_type(callback)
                ctypes.windll.user32.EnumWindows(cb, 0)

                if window_hwnd:
                    break

        except Exception as e:
            print(f"Could not get HWND: {e}")

        return window_hwnd


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


def get_system_language():
    """
    Определить язык системы.
    Возвращает код языка из доступных в программе, или 'en' по умолчанию.

    Доступные языки: en, ru, de, es, fr, hi, it, ja, ko, pl, pt, zh
    """
    try:
        # Получаем язык системы через Windows API
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()

        # Извлекаем первичный код языка (низшие 10 бит)
        primary_lang = lang_id & 0x3FF

        # Маппинг LANGID Windows к кодам языков программы
        lang_map = {
            1: 'en',    # LANG_ENGLISH
            4: 'zh',    # LANG_CHINESE
            7: 'de',    # LANG_GERMAN
            10: 'es',   # LANG_SPANISH
            12: 'fr',   # LANG_FRENCH
            19: 'it',   # LANG_ITALIAN
            25: 'ru',   # LANG_RUSSIAN
            28: 'pl',   # LANG_POLISH
            31: 'pt',   # LANG_PORTUGUESE
            18: 'ko',   # LANG_KOREAN
            57: 'hi',   # LANG_HINDI
            110: 'ja',  # LANG_JAPANESE
        }

        # Получаем код языка или 'en' если не найден
        return lang_map.get(primary_lang, 'en')

    except Exception as e:
        print(f"Error detecting system language: {e}")
        return 'en'  # По умолчанию английский


def save_window_state(window):
    """Сохранить позицию и размер окна в config.json"""
    try:
        # Читаем текущий конфиг
        config = {}
        if os.path.exists(APPDATA_CONFIG):
            try:
                with open(APPDATA_CONFIG, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except:
                pass

        # Получаем позицию и размер окна
        rect = wintypes.RECT()
        if window_hwnd:
            ctypes.windll.user32.GetWindowRect(window_hwnd, ctypes.byref(rect))
            config['Window_X'] = rect.left
            config['Window_Y'] = rect.top
            config['Window_Width'] = rect.right - rect.left
            config['Window_Height'] = rect.bottom - rect.top

            # Записываем в APPDATA
            with open(APPDATA_CONFIG, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving window state: {e}")


def load_window_state():
    """Загрузить позицию и размер окна из config.json"""
    state = {
        'x': None,
        'y': None,
        'width': None,
        'height': None
    }

    try:
        if os.path.exists(APPDATA_CONFIG):
            with open(APPDATA_CONFIG, "r", encoding="utf-8") as f:
                config = json.load(f)

            state['x'] = config.get('Window_X')
            state['y'] = config.get('Window_Y')
            state['width'] = config.get('Window_Width')
            state['height'] = config.get('Window_Height')
    except Exception as e:
        print(f"Error loading window state: {e}")

    return state


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
    """
    Проверяет, является ли запуск первым (нет config.json в APPDATA или нет языка).
    Если язык не настроен - устанавливаем язык системы.
    """
    # Сначала проверяем конфиг в APPDATA
    config_file = APPDATA_CONFIG
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Если язык уже есть - это не первый запуск
            if "Language" in config:
                return False

            # Языка нет - устанавливаем системный
            system_lang = get_system_language()
            config["Language"] = system_lang

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error reading config: {e}")
            return True

    # Если нет конфига в APPDATA, проверяем внешний/встроенный
    config_file = get_config_path()
    if not os.path.exists(config_file):
        # Конфига нет вообще - это первый запуск, создаём с системным языком
        system_lang = get_system_language()
        config = {"Language": system_lang}

        # Создаём директорию APPDATA если нет
        appdata_dir = os.path.dirname(APPDATA_CONFIG)
        if not os.path.exists(appdata_dir):
            os.makedirs(appdata_dir)

        try:
            with open(APPDATA_CONFIG, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except:
            pass

        return True

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Если язык есть - не первый запуск
        if "Language" in config:
            return False

        # Языка нет - устанавливаем системный
        system_lang = get_system_language()
        config["Language"] = system_lang

        # Сохраняем в APPDATA
        appdata_dir = os.path.dirname(APPDATA_CONFIG)
        if not os.path.exists(appdata_dir):
            os.makedirs(appdata_dir)

        with open(APPDATA_CONFIG, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        return True

    except Exception as e:
        print(f"Error: {e}")
        return True


def run_server():
    """Запускает сервер в отдельном потоке"""
    import uvicorn
    from web_server import app
    uvicorn.run(app, host="127.0.0.1", port=1337, log_level="warning")


def main():
    # Проверка на единственный экземпляр
    if is_already_running():
        return

    # Загружаем сохранённую позицию и размер окна
    window_state = load_window_state()

    # Проверяем, не запущен ли уже сервер на порту 1337
    server_running = is_port_in_use(1337)

    if not server_running:
        # Запускаем сервер в отдельном потоке
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(2)

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

    # Создаём API для управления окном
    api = WindowAPI()

    # Параметры окна
    window_kwargs = {
        'title': "Shadow Library",
        'url': url,
        'js_api': api,
        'width': window_state['width'] if window_state['width'] else 1200,
        'height': window_state['height'] if window_state['height'] else 800,
        'x': window_state['x'] if window_state['x'] else 100,
        'y': window_state['y'] if window_state['y'] else 100,
        'resizable': True,
        'fullscreen': False,
        'min_size': (800, 600),
        'frameless': True,
        'transparent': True
    }

    # Создаём окно
    window = webview.create_window(**window_kwargs)

    # Инициализируем API с окном
    api.set_window(window)

    # Обработчик закрытия окна - сохраняем позицию и размер
    def on_closing():
        save_window_state(window)

    try:
        window.events.closing += on_closing
    except:
        pass

    # Устанавливаем иконку
    if os.path.exists(icon_path):
        try:
            window.set_icon(icon_path)
        except:
            pass

    webview.start()

    # Сохраняем состояние окна при выходе
    save_window_state(window)


if __name__ == "__main__":
    main()
