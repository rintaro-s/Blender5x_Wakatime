import bpy
from bpy.app.handlers import persistent

try:
    from .wakatime_blender import settings
    from .wakatime_blender.heartbeat_queue import HeartbeatQueue
    from .wakatime_blender.log import ERROR, INFO, log
    from .wakatime_blender.preferences import (
        PreferencesDialog,
        ReloadConfigOperator,
        WakatimeProjectProperties,
    )
    from .wakatime_blender.wakatime_downloader import WakatimeDownloader
except ImportError as e:
    import traceback
    print(f"[Wakatime] [ERROR] Failed to import modules: {e}")
    print(traceback.format_exc())
    raise


bl_info = {
    "name": "WakaTime",
    "category": "Development",
    "author": "Allis Tauri <allista@gmail.com>",
    "version": (3, 0, 0),
    "blender": (5, 0, 0),
    "description": "Submits your working stats to the Wakatime time tracking service.",
    "tracker_url": "https://github.com/wakatime/blender-wakatime/issues",
}

__version__ = ".".join((f"{n}" for n in bl_info["version"]))

heartbeat_queue: HeartbeatQueue

REGISTERED = False


def handle_activity(is_write=False):
    if not REGISTERED:
        return
    heartbeat_queue.enqueue(bpy.data.filepath, is_write)
    if not settings.api_key():
        PreferencesDialog.show()


@persistent
def load_handler(_):
    handle_activity()


@persistent
def save_handler(_):
    handle_activity(is_write=True)


@persistent
def activity_handler(_):
    handle_activity()


def menu(self, _context):
    self.layout.operator(PreferencesDialog.bl_idname)


def register():
    global REGISTERED, heartbeat_queue
    if REGISTERED:
        return
    try:
        log(INFO, "Initializing Wakatime plugin v{}", __version__)
        
        try:
            settings.load()
        except Exception as e:
            log(ERROR, "Failed to load settings: {}", e)
        
        try:
            WakatimeProjectProperties.load_defaults()
        except Exception as e:
            log(ERROR, "Failed to load defaults: {}", e)
        
        try:
            bpy.utils.register_class(WakatimeProjectProperties)
        except Exception as e:
            log(ERROR, "Failed to register WakatimeProjectProperties: {}", e)
        
        try:
            bpy.utils.register_class(ReloadConfigOperator)
        except Exception as e:
            log(ERROR, "Failed to register ReloadConfigOperator: {}", e)
        
        try:
            bpy.utils.register_class(PreferencesDialog)
        except Exception as e:
            log(ERROR, "Failed to register PreferencesDialog: {}", e)
        
        try:
            bpy.types.TOPBAR_MT_blender_system.append(menu)
        except Exception as e:
            log(ERROR, "Failed to append menu: {}", e)
        
        try:
            bpy.app.handlers.load_post.append(load_handler)
            bpy.app.handlers.save_post.append(save_handler)
            bpy.app.handlers.depsgraph_update_pre.append(activity_handler)
        except Exception as e:
            log(ERROR, "Failed to register handlers: {}", e)
        
        try:
            downloader = WakatimeDownloader()
            heartbeat_queue = HeartbeatQueue(__version__)
            downloader.start()
            heartbeat_queue.start()
        except Exception as e:
            log(ERROR, "Unable to start worker threads: {}", e)
    except Exception as e:
        log(ERROR, "Critical error during registration: {}", e)
        import traceback
        print(traceback.format_exc())
    finally:
        REGISTERED = True


def unregister():
    global REGISTERED
    if not REGISTERED:
        return
    try:
        log(INFO, "Unregistering Wakatime plugin v{}", __version__)
        
        try:
            bpy.types.TOPBAR_MT_blender_system.remove(menu)
        except Exception as e:
            log(ERROR, "Failed to remove menu: {}", e)
        
        try:
            bpy.app.handlers.load_post.remove(load_handler)
            bpy.app.handlers.save_post.remove(save_handler)
            bpy.app.handlers.depsgraph_update_pre.remove(activity_handler)
        except Exception as e:
            log(ERROR, "Failed to remove handlers: {}", e)
        
        try:
            bpy.utils.unregister_class(PreferencesDialog)
        except Exception as e:
            log(ERROR, "Failed to unregister PreferencesDialog: {}", e)
        
        try:
            bpy.utils.unregister_class(ReloadConfigOperator)
        except Exception as e:
            log(ERROR, "Failed to unregister ReloadConfigOperator: {}", e)
        
        try:
            if 'heartbeat_queue' in globals():
                heartbeat_queue.shutdown()
                heartbeat_queue.join(heartbeat_queue.POLL_INTERVAL * 3)
        except Exception as e:
            log(ERROR, "Failed to shutdown heartbeat queue: {}", e)
        
        try:
            bpy.utils.unregister_class(WakatimeProjectProperties)
        except Exception as e:
            log(ERROR, "Failed to unregister WakatimeProjectProperties: {}", e)
    except Exception as e:
        log(ERROR, "Critical error during unregistration: {}", e)
    finally:
        REGISTERED = False
