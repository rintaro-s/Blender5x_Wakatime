import os
from configparser import ConfigParser
from typing import Any, Callable, Optional, TypeVar

USER_HOME = os.path.expanduser("~")
PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
RESOURCES_DIR = os.path.join(USER_HOME, ".wakatime")
# default wakatime config for legacy python client
FILENAME = os.path.join(USER_HOME, ".wakatime.cfg")
# default section in wakatime config
_section = "settings"

_cfg = ConfigParser()
_cfg.optionxform = str
if not _cfg.has_section(_section):
    _cfg.add_section(_section)
if not _cfg.has_option(_section, "debug"):
    _cfg.set(_section, "debug", str(False))

_loaded = False


def load():
    global _loaded, _cfg
    try:
        if os.path.exists(FILENAME):
            # Create a fresh ConfigParser to avoid stale data
            _cfg = ConfigParser()
            _cfg.optionxform = str  # Preserve case sensitivity
            
            # Read the config file
            files_read = _cfg.read(FILENAME, encoding="utf-8")
            
            if files_read:
                print(f"[Wakatime] [INFO] Successfully loaded config from {FILENAME}")
                
                # Debug: print all sections and options
                print(f"[Wakatime] [DEBUG] Sections found: {_cfg.sections()}")
                
                if _cfg.has_section(_section):
                    print(f"[Wakatime] [DEBUG] Options in [{_section}]: {_cfg.options(_section)}")
                    
                    api_key_loaded = _cfg.get(_section, "api_key", fallback="")
                    if api_key_loaded:
                        print(f"[Wakatime] [INFO] ✓ API Key found: {api_key_loaded[:8]}...")
                    else:
                        print(f"[Wakatime] [WARNING] API Key not found in config")
                    
                    api_url_loaded = _cfg.get(_section, "api_url", fallback="")
                    if api_url_loaded:
                        print(f"[Wakatime] [INFO] ✓ API URL: {api_url_loaded}")
                    else:
                        print(f"[Wakatime] [WARNING] API URL not found in config")
                    
                    rate_limit = _cfg.get(_section, "heartbeat_rate_limit_seconds", fallback="")
                    if rate_limit:
                        print(f"[Wakatime] [INFO] ✓ Heartbeat rate limit: {rate_limit}s")
                    
                    custom_project = _cfg.get(_section, "custom_project_name", fallback="")
                    if custom_project:
                        print(f"[Wakatime] [INFO] ✓ Custom project name: {custom_project}")
                else:
                    print(f"[Wakatime] [WARNING] Section [{_section}] not found in config file")
                    # Add the section for future writes
                    _cfg.add_section(_section)
                
                _loaded = True
            else:
                print(f"[Wakatime] [ERROR] Failed to read config file: {FILENAME}")
                _loaded = False
        else:
            print(f"[Wakatime] [WARNING] Config file not found: {FILENAME}")
            print(f"[Wakatime] [INFO] Using default settings. You can create {FILENAME} manually.")
            _loaded = True
    except Exception as e:
        import traceback
        print(f"[Wakatime] [ERROR] Unable to read {FILENAME}")
        print(f"[Wakatime] [ERROR] {repr(e)}")
        print(traceback.format_exc())
        _loaded = True


def save():
    with open(FILENAME, "w") as out:
        _cfg.write(out)


def set(option: str, value: str) -> None:
    _cfg.set(_section, option, value)
    save()


def get(option: str, default: Any = None) -> str:
    if not _loaded:
        load()
    return _cfg.get(_section, option, fallback=default)


def get_bool(option: str) -> bool:
    return get(option, "").lower() in {"y", "yes", "t", "true", "1"}


_T = TypeVar("_T", bound=Any)


def parse(
    option: str, transform: Callable[[str], _T], default: Optional[_T] = None
) -> Optional[_T]:
    try:
        return transform(get(option))
    except Exception:
        return default


def debug() -> bool:
    return get_bool("debug")


def api_key() -> str:
    return get("api_key", "")


def set_api_key(new_key: str) -> None:
    set("api_key", new_key)


def api_url() -> str:
    return get("api_url", "https://api.wakatime.com/api/v1")


def set_api_url(new_url: str) -> None:
    set("api_url", new_url)


def heartbeat_rate_limit_seconds() -> float:
    return parse("heartbeat_rate_limit_seconds", float, 120.0)
