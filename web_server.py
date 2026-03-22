import uvicorn
import json
import os
import sys
import time
import httpx
import traceback
import vdf
import re
import ctypes
import subprocess
from pathlib import Path
from typing import Tuple, List, Dict
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from common import log, variable
from common.variable import CLIENT, HEADER, REPO_LIST

LOG = log.log("Shadow-Library")
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cracked_games.json")
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# Путь к данным для PyInstaller
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Для Windows - вывод окна на передний план
def bring_window_to_front(window_title_substring):
    """Ищет окно по части заголовка и выводит на передний план"""
    try:
        time.sleep(0.5)
        EnumWindows = ctypes.windll.user32.EnumWindows
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow
        ShowWindow = ctypes.windll.user32.ShowWindow
        SW_RESTORE = 9

        hwnd_to_use = None

        def callback(hwnd, lparam):
            nonlocal hwnd_to_use
            if not ctypes.windll.user32.IsWindowVisible(hwnd):
                return True
            length = GetWindowTextLength(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buffer, length + 1)
                if window_title_substring.lower() in buffer.value.lower():
                    hwnd_to_use = hwnd
                    return False
            return True

        for _ in range(5):
            EnumWindows(EnumWindowsProc(callback), 0)
            if hwnd_to_use:
                ShowWindow(hwnd_to_use, SW_RESTORE)
                time.sleep(0.1)
                SetForegroundWindow(hwnd_to_use)
                return True
            time.sleep(0.2)
        return False
    except:
        return False


def open_file_with_app(file_path):
    """Открывает файл в приложении по умолчанию и возвращает процесс"""
    try:
        if file_path.endswith('.vdf') or file_path.endswith('.txt') or file_path.endswith('.lua'):
            return subprocess.Popen(['notepad.exe', file_path])
        else:
            os.startfile(file_path)
            return None
    except:
        os.startfile(file_path)
        return None


app = FastAPI(title="Shadow Library - Web Interface")

# === НАСТРОЙКИ ===
MANIFEST_DIR = "manifests"

if not os.path.exists(MANIFEST_DIR):
    os.makedirs(MANIFEST_DIR)

app.mount("/files", StaticFiles(directory=MANIFEST_DIR), name="manifests")


# === РАБОТА С ФАЙЛАМИ ===
def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_config(key: str, default=""):
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get(key, default)
        except:
            pass
    return default


def get_steam_path():
    return get_config("Custom_Steam_Path", "")


def get_language():
    return get_config("Language", "ru")


def set_language(lang: str) -> bool:
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
        except:
            pass
    config["Language"] = lang
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False


LOCALES_DIR = os.path.join(BASE_DIR, "locales")
LOCALES_CACHE = {}

def get_available_languages() -> List[str]:
    if not os.path.exists(LOCALES_DIR):
        return ["en", "ru"]
    languages = [f[:-5] for f in os.listdir(LOCALES_DIR) if f.endswith(".json")]
    return languages if languages else ["en", "ru"]


def load_locale(lang: str) -> Dict[str, str]:
    if lang in LOCALES_CACHE:
        return LOCALES_CACHE[lang]
    locale_path = os.path.join(LOCALES_DIR, f"{lang}.json")
    if not os.path.exists(locale_path):
        locale_path = os.path.join(LOCALES_DIR, "en.json")
        if not os.path.exists(locale_path):
            return {}
    
    try:
        with open(locale_path, "r", encoding="utf-8") as f:
            locale_data = json.load(f)
            LOCALES_CACHE[lang] = locale_data
            return locale_data
    except:
        return {}


def get_all_locales() -> Dict[str, Dict[str, str]]:
    """Загружает все доступные локализации"""
    locales = {}
    for lang in get_available_languages():
        locales[lang] = load_locale(lang)
    return locales


# === API МОДЕЛИ ===
class GameRequest(BaseModel):
    app_id: str
    use_steamtools: bool = True
    use_autocrack: bool = True  # True = SteamAutoCrack, False = ManifestHub


class SteamPathRequest(BaseModel):
    steam_path: str


class OpenRequest(BaseModel):
    target: str


# === API ОТКРЫТИЯ ПАПОК ===
@app.post("/open_local")
async def open_local_path(req: OpenRequest):
    steam_path = get_steam_path()
    if not steam_path or not os.path.exists(steam_path):
        return JSONResponse({"error": "Путь к Steam не настроен"}, status_code=400)

    path_to_open = steam_path

    if req.target == "config_folder":
        path_to_open = os.path.join(steam_path, "config")
    elif req.target == "config_file":
        path_to_open = os.path.join(steam_path, "config", "config.vdf")
    elif req.target == "depot":
        path_to_open = os.path.join(steam_path, "depotcache")
    elif req.target == "stplug":
        path_to_open = os.path.join(steam_path, "config", "stplug-in")
    elif req.target == "applist":
        path_to_open = os.path.join(steam_path, "AppList")
    elif req.target == "manifests_folder":
        path_to_open = os.path.abspath(MANIFEST_DIR)

    try:
        if req.target in ["config_file", "stplug", "applist"]:
            if os.path.isdir(path_to_open):
                os.startfile(path_to_open)
                bring_window_to_front(os.path.basename(path_to_open))
            else:
                process = open_file_with_app(path_to_open)
                if process:
                    time.sleep(0.3)
                    bring_window_to_front(os.path.basename(path_to_open))
                    bring_window_to_front("Блокнот")
                    bring_window_to_front("Notepad")
        else:
            os.startfile(path_to_open)
            bring_window_to_front(os.path.basename(path_to_open))

        return {"status": "ok", "opened": path_to_open}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/get_steam_path")
async def api_get_steam_path():
    steam_path = get_steam_path()
    LOG.debug(f"Get steam path: {steam_path} from {CONFIG_FILE}")
    return {"steam_path": steam_path}


@app.get("/check_steam_path")
async def api_check_steam_path():
    steam_path = get_steam_path()
    valid = bool(steam_path) and os.path.exists(steam_path) and os.path.exists(os.path.join(steam_path, "steam.exe"))
    return {"valid": valid, "steam_path": steam_path}


@app.post("/set_steam_path")
async def api_set_steam_path(req: SteamPathRequest):
    path = req.steam_path.strip()
    if not os.path.exists(path):
        return JSONResponse({"error": "Указанный путь не существует"}, status_code=400)
    if not os.path.exists(os.path.join(path, "steam.exe")):
        return JSONResponse({"error": "В указанной папке не найден steam.exe"}, status_code=400)

    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
        except:
            pass
    config["Custom_Steam_Path"] = path
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    LOG.info(f"Steam path saved: {path} to {CONFIG_FILE}")
    return {"status": "ok", "steam_path": path}


class LanguageRequest(BaseModel):
    language: str


@app.get("/api/get_language")
async def api_get_language():
    return {"language": get_language()}


@app.get("/api/get_locales")
async def api_get_locales():
    return get_all_locales()


@app.get("/api/get_available_languages")
async def api_get_available_languages():
    return {"languages": get_available_languages()}


@app.post("/api/set_language")
async def api_set_language(req: LanguageRequest):
    lang = req.language.strip()
    valid_languages = get_available_languages()
    if lang not in valid_languages:
        return JSONResponse({"error": f"Недопустимый язык. Доступные: {', '.join(valid_languages)}"}, status_code=400)

    if set_language(lang):
        return {"status": "ok", "language": lang}
    else:
        return JSONResponse({"error": "Ошибка сохранения языка"}, status_code=500)


async def CheckCN() -> bool:
    try:
        req = await CLIENT.get("https://mips.kugou.com/check/iscn?&format=json")
        body = req.json()
        scn = bool(body["flag"])
        variable.IS_CN = scn
        return scn
    except:
        variable.IS_CN = True
        return True


async def CheckLimit(headers):
    try:
        r = await CLIENT.get("https://api.github.com/rate_limit", headers=headers)
        if r.status_code == 200:
            return r.json().get("rate", {}).get("remaining", 0)
    except:
        pass
    return 0


async def GetLatestRepoInfo(repos: list, app_id: str, headers, use_autocrack: bool = True):
    if use_autocrack:
        filtered_repos = [r for r in repos if "SteamAutoCrack" in r or "ManifestHub" in r]
    else:
        filtered_repos = [r for r in repos if "Auiowu" in r or "tymolu233" in r]
    if not filtered_repos:
        filtered_repos = repos

    latest_date = None
    selected_repo = None
    for repo in filtered_repos:
        url = f"https://api.github.com/repos/{repo}/branches/{app_id}"
        r = await CLIENT.get(url, headers=headers)
        r_json = r.json()
        if r_json and "commit" in r_json:
            date = r_json["commit"]["commit"]["author"]["date"]
            if (latest_date is None) or (date > latest_date):
                latest_date = str(date)
                selected_repo = str(repo)
    return selected_repo, latest_date


async def FetchFiles(sha: str, path: str, repo: str):
    if variable.IS_CN:
        url_list = [
            f"https://cdn.jsdmirror.com/gh/{repo}@{sha}/{path}",
            f"https://raw.gitmirror.com/{repo}/{sha}/{path}",
            f"https://raw.dgithub.xyz/{repo}/{sha}/{path}",
            f"https://gh.akass.cn/{repo}/{sha}/{path}",
        ]
    else:
        url_list = [f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"]

    retry = 3
    while retry > 0:
        for url in url_list:
            try:
                r = await CLIENT.get(url, headers=HEADER, timeout=30)
                if r.status_code == 200:
                    return r.read()
                else:
                    LOG.error(f"Failed: {path} - Status: {r.status_code}")
            except:
                pass
        retry -= 1
        LOG.warning(f"Retry: {retry} - {path}")
    raise Exception(f"Download failed: {path}")


def ParseKey(content: bytes) -> List[Tuple[str, str]]:
    try:
        depots = vdf.loads(content.decode("utf-8"))["depots"]
        return [(d_id, d_info["DecryptionKey"]) for d_id, d_info in depots.items()]
    except:
        return []


async def HandleDepotFiles(repos: List, app_id: str, steam_path: Path, use_autocrack: bool = True):
    collected = []
    depot_map = {}
    try:
        selected_repo, latest_date = await GetLatestRepoInfo(repos, app_id, headers=HEADER, use_autocrack=use_autocrack)
        if not selected_repo:
            LOG.error(f"No repo for App ID {app_id}")
            return collected, depot_map

        branch_url = f"https://api.github.com/repos/{selected_repo}/branches/{app_id}"
        branch_res = await CLIENT.get(branch_url, headers=HEADER)
        branch_res.raise_for_status()

        tree_url = branch_res.json()["commit"]["commit"]["tree"]["url"]
        tree_res = await CLIENT.get(tree_url)
        tree_res.raise_for_status()

        depot_cache = Path(f"{steam_path}/depotcache")
        depot_cache.mkdir(exist_ok=True)

        LOG.info(f"Repo: https://github.com/{selected_repo}")
        LOG.info(f"Updated: {latest_date}")

        for item in tree_res.json()["tree"]:
            file_path = str(item["path"])
            if file_path.endswith(".manifest"):
                save_path = depot_cache / file_path
                if save_path.exists():
                    LOG.warning(f"Exists: {save_path}")
                    continue
                content = await FetchFiles(branch_res.json()["commit"]["sha"], file_path, selected_repo)
                LOG.info(f"Downloaded: {file_path}")
                with open(save_path, "wb") as f:
                    f.write(content)
            elif "key.vdf" in file_path.lower():
                key_content = await FetchFiles(branch_res.json()["commit"]["sha"], file_path, selected_repo)
                collected.extend(ParseKey(key_content))

        for item in tree_res.json()["tree"]:
            if not item["path"].endswith(".manifest"):
                continue
            filename = Path(item["path"]).stem
            if "_" not in filename:
                continue
            depot_id, manifest_id = filename.replace(".manifest", "").split("_", 1)
            if not (depot_id.isdigit() and manifest_id.isdigit()):
                continue
            depot_map.setdefault(depot_id, []).append(manifest_id)

        for depot_id in depot_map:
            depot_map[depot_id].sort(key=lambda x: int(x), reverse=True)
    except Exception as e:
        LOG.error(f"Error: {str(e)}")
    return collected, depot_map


def SetupUnlock(depot_data, app_id, tool_choice, depot_map, version_lock=False):
    if tool_choice == 1:
        return SetupTools(depot_data, app_id, depot_map, version_lock)
    elif tool_choice == 2:
        return SetupGreenLuma(depot_data)
    return False


def SetupTools(depot_data, app_id, depot_map, version_lock=False):
    steam_path = get_steam_path()
    st_path = Path(f"{steam_path}/config/stplug-in")
    st_path.mkdir(exist_ok=True)
    lua_content = f'addappid({app_id}, 1, "None")\n'
    for d_id, d_key in depot_data:
        if version_lock:
            for manifest_id in depot_map[d_id]:
                lua_content += f'addappid({d_id}, 1, "{d_key}")\nsetManifestid({d_id},"{manifest_id}")\n'
        else:
            lua_content += f'addappid({d_id}, 1, "{d_key}")\n'
    with open(st_path / f"{app_id}.lua", "w", encoding="utf-8") as f:
        f.write(lua_content)
    return True


def SetupGreenLuma(depot_data):
    steam_path = get_steam_path()
    applist_dir = Path(f"{steam_path}/AppList")
    applist_dir.mkdir(exist_ok=True)
    for f in applist_dir.glob("*.txt"):
        f.unlink()
    for idx, (d_id, _) in enumerate(depot_data, 1):
        (applist_dir / f"{idx}.txt").write_text(str(d_id))
    config_path = Path(f"{steam_path}/config/config.vdf")
    with open(config_path, "r+", encoding="utf-8") as f:
        content = vdf.loads(f.read())
        content.setdefault("depots", {}).update({d_id: {"DecryptionKey": d_key} for d_id, d_key in depot_data})
        f.seek(0)
        f.write(vdf.dumps(content))
    return True


def RemoveUnlock(app_id, tool):
    try:
        steam_path = get_steam_path()
        if tool == "SteamTools":
            lua_file = Path(f"{steam_path}/config/stplug-in/{app_id}.lua")
            if lua_file.exists():
                lua_file.unlink()
                LOG.info(f"Removed: {lua_file}")
                return True
            LOG.warning(f"Not found: {lua_file}")
            return False
        elif tool == "GreenLuma":
            applist_dir = Path(f"{steam_path}/AppList")
            if applist_dir.exists():
                for f in applist_dir.glob("*.txt"):
                    f.unlink()
                LOG.info("Cleared AppList")
            config_path = Path(f"{steam_path}/config/config.vdf")
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    content = vdf.loads(f.read())
                if "depots" in content:
                    for depot_id in list(content["depots"].keys()):
                        del content["depots"][depot_id]
                    with open(config_path, "w", encoding="utf-8") as f:
                        f.write(vdf.dumps(content))
                    LOG.info("Removed depots from config.vdf")
                    return True
            return False
        else:
            LOG.error(f"Unknown tool: {tool}")
            return False
    except Exception as e:
        LOG.error(f"Remove error: {e}")
        return False


async def get_game_name(app_id: str) -> str:
    try:
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
        response = await CLIENT.get(url, timeout=10)
        data = response.json()
        if data.get(str(app_id), {}).get("success"):
            return data[str(app_id)]["data"].get("name", "Unknown")
        return "Unknown"
    except Exception as e:
        LOG.warning(f"Get game name error: {e}")
        return "Unknown"


async def get_game_icon(app_id: str) -> str:
    try:
        url = f"https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/{app_id}/{app_id}.jpg"
        response = await CLIENT.head(url, timeout=5)
        if response.status_code == 200:
            return url
        api_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
        response = await CLIENT.get(api_url, timeout=10)
        data = response.json()
        if data.get(str(app_id), {}).get("success"):
            game_data = data[str(app_id)]["data"]
            if "header_image" in game_data:
                return game_data["header_image"]
            if "capsule_image" in game_data:
                return game_data["capsule_image"]
        return ""
    except Exception as e:
        LOG.warning(f"Get game icon error: {e}")
        return ""


def extract_app_id_from_input(input_str: str):
    input_str = input_str.strip()
    if input_str.isdigit():
        return input_str
    match = re.search(r'store\.steampowered\.com/app/(\d+)', input_str)
    if match:
        return match.group(1)
    digits = ''.join(filter(str.isdigit, input_str))
    return digits if digits else None


async def process_game(app_id: str, use_steamtools: bool, use_autocrack: bool, version_lock: bool = False) -> dict:
    result = {"success": False, "message": "", "depot_count": 0, "selected_repo": "", "game_name": "", "game_icon": ""}
    try:
        extracted_app_id = extract_app_id_from_input(app_id)
        if not extracted_app_id:
            result["message"] = "Неверный App ID"
            return result
        app_id = extracted_app_id
        steam_path = get_steam_path()
        await CheckCN()
        depot_data, depot_map = await HandleDepotFiles(REPO_LIST, app_id, Path(steam_path), use_autocrack=use_autocrack)
        if not depot_data or not depot_map:
            result["message_key"] = "manifestNotFound"
            result["message"] = "Манифесты не найдены"
            return result
        tool_choice = 1 if use_steamtools else 2
        if SetupUnlock(depot_data, app_id, tool_choice, depot_map, version_lock):
            result["success"] = True
            result["message_key"] = "configSuccess"
            result["message"] = "Настройка успешна! Перезапустите Steam."
            result["depot_count"] = len(depot_data)
            selected_repo, _ = await GetLatestRepoInfo(REPO_LIST, app_id, headers=HEADER, use_autocrack=use_autocrack)
            result["selected_repo"] = selected_repo or "Unknown"
            result["game_name"] = await get_game_name(app_id)
            result["game_icon"] = await get_game_icon(app_id)
            db = load_db()
            game_entry = {"app_id": app_id, "game_name": result["game_name"], "game_icon": result["game_icon"],
                "depot_count": len(depot_data), "tool": "SteamTools" if use_steamtools else "GreenLuma",
                "source": "SteamAutoCrack" if use_autocrack else "ManifestAutoUpdate",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
            existing = next((g for g in db if g["app_id"] == app_id), None)
            if existing:
                db.remove(existing)
            db.insert(0, game_entry)
            save_db(db)
        else:
            result["message"] = "Ошибка настройки"
    except Exception as e:
        result["message"] = f"Ошибка: {str(e)}"
        LOG.error(f"Error: {traceback.format_exc()}")
    return result


def load_html_template() -> str:
    template_path = os.path.join(BASE_DIR, "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/", response_class=HTMLResponse)
async def get_index():
    content = load_html_template()
    return Response(
        content=content,
        media_type="text/html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.post("/api/unlock")
async def api_unlock(request: GameRequest):
    result = await process_game(request.app_id, request.use_steamtools, request.use_autocrack, version_lock=False)
    return result


@app.get("/api/games")
async def api_get_games():
    return load_db()


@app.delete("/api/games/{app_id}")
async def api_delete_game(app_id: str):
    db = load_db()
    game = next((g for g in db if g["app_id"] == app_id), None)
    if game:
        tool = game.get("tool", "SteamTools")
        RemoveUnlock(app_id, tool)
        LOG.info(f"Removed: {app_id} ({tool})")
    db = [g for g in db if g["app_id"] != app_id]
    save_db(db)
    return {"status": "ok", "deleted": app_id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
