from typing import Optional

import bpy
from bpy.props import BoolProperty, FloatProperty, StringProperty
from bpy.types import PropertyGroup
from . import settings
from .log import ERROR, log
from .utils import u


__all__ = [
    "WakatimeProjectProperties",
    "ReloadConfigOperator",
    "PreferencesDialog",
]


class WakatimeProjectProperties(PropertyGroup):
    _attr = "wakatime_preferences"
    bl_idname = "preferences.wakatime_preferences"
    bl_label = "Wakatime Operator"

    _default_heartbeat_frequency = 2
    _default_always_overwrite_projectname = False
    _default_use_project_folder = False
    _default_chars = "1234567890._"
    _default_prefix = ""
    _default_postfix = ""

    always_overwrite_name: BoolProperty(
        name="Overwrite project-discovery with the name from below",
        default=_default_always_overwrite_projectname,
        description="Wakatime will guess the project-name (e.g. from the git-repo). Checking this box will overwrite "
        "this auto-discovered name (with the name according to the rules below).\n\nHint: when not "
        "working with git, the project's name will always be set according to the rules "
        f"below.",
    )

    use_project_folder: BoolProperty(
        name="Use folder-name as project-name",
        default=_default_use_project_folder,
        description="Will use the name of the folder/directory-name as the project-name.\n\nExample: if selected, "
        "filename 'birthday_project/test_01.blend' will result in project-name "
        "'birthday_project'\n\nHint: if not activated, the blender-filename without the blend-extension "
        f"is used.",
    )

    truncate_trail: StringProperty(
        name="Cut trailing characters",
        default=_default_chars,
        description="With the project-name extracted (from folder- or filename), these trailing characters will be "
        "removed too.\n\nExample: filename 'birthday_01_test_02.blend' will result in project-name "
        "'birthday_01_test'",
    )

    project_prefix: StringProperty(
        name="Project-name prefix",
        default=_default_prefix,
        description="This text will be attached in front of the project-name.",
    )
    project_postfix: StringProperty(
        name="Project-name postfix",
        default=_default_postfix,
        description="This text will be attached at the end of the project-name, after the trailing characters were "
        "removed.",
    )

    heartbeat_frequency: FloatProperty(
        name="Heartbeat Frequency (minutes)",
        default=_default_heartbeat_frequency,
        min=1,
        max=60,
        description="How often the plugin should send heartbeats to Wakatime server",
    )

    @classmethod
    def register(cls):
        setattr(bpy.types.World, cls._attr, bpy.props.PointerProperty(type=cls))

    @classmethod
    def load_defaults(cls):
        annotation = cls.__annotations__["always_overwrite_name"]
        if isinstance(annotation, tuple):
            keywords = annotation[1]
        else:
            keywords = annotation.keywords
        keywords["default"] = settings.get_bool("always_overwrite_project_name")

    @classmethod
    def reload_defaults(cls):
        try:
            bpy.utils.unregister_class(WakatimeProjectProperties)
        except ValueError:
            pass
        cls.load_defaults()
        bpy.utils.register_class(WakatimeProjectProperties)

    @classmethod
    def instance(cls) -> Optional["WakatimeProjectProperties"]:
        try:
            worlds = bpy.context.blend_data.worlds
            first_world = worlds[0]
            return getattr(first_world, cls._attr)
        except (IndexError, AttributeError, TypeError):
            log(ERROR, "Unable to get WakatimeProjectProperties from the First World")
        return None


class ReloadConfigOperator(bpy.types.Operator):
    bl_idname = "ui.wakatime_reload_config"
    bl_label = "Reload Config"
    bl_description = "Reload settings from ~/.wakatime.cfg"

    def execute(self, context):
        # Force reload by resetting the loaded flag
        import importlib
        importlib.reload(settings)
        settings.load()
        
        # Close current dialog and reopen to refresh values
        PreferencesDialog._hide()
        
        # Use a timer to reopen the dialog after a short delay
        def reopen_dialog():
            PreferencesDialog.show()
            return None
        
        bpy.app.timers.register(reopen_dialog, first_interval=0.1)
        
        self.report({'INFO'}, f"Reloaded settings from {settings.FILENAME}")
        return {'FINISHED'}


class PreferencesDialog(bpy.types.Operator):
    bl_idname = "ui.wakatime_blender_preferences"
    bl_label = "Wakatime Preferences"
    bl_description = "Configure wakatime plugin for blender"

    api_key: StringProperty(
        name="API Key",
        default="",
        description="Wakatime API key from your account",
    )

    api_url: StringProperty(
        name="API URL",
        default="https://api.wakatime.com/api/v1",
        description="Wakatime API URL (leave default unless using custom server)",
    )

    custom_project_name: StringProperty(
        name="Custom Project Name",
        default="",
        description="Optional: Set a custom project name to always use for this blend file. Leave empty to use auto-detection.",
    )

    config_status: StringProperty(
        name="Config Status",
        default="",
        description="Status of config file loading",
    )

    heartbeat_rate_display: StringProperty(
        name="Heartbeat Rate Limit",
        default="",
        description="Current heartbeat rate limit from config (seconds)",
    )

    always_overwrite_name_default: BoolProperty(
        name="Overwrite project-discovery by default",
        default=False,
        description="Wakatime will guess the project-name (e.g. from the git-repo). "
        "Checking this box will overwrite this auto-discovered name "
        "for new blend files by default.",
    )

    is_shown = False

    @classmethod
    def show(cls):
        if not cls.is_shown:
            cls.is_shown = True
            bpy.ops.ui.wakatime_blender_preferences("INVOKE_DEFAULT")

    @classmethod
    def _hide(cls):
        cls.is_shown = False

    def execute(self, _context):
        settings.set_api_key(u(self.api_key))
        settings.set_api_url(u(self.api_url))
        settings.set(
            "always_overwrite_project_name", f"{self.always_overwrite_name_default}"
        )
        if self.custom_project_name:
            settings.set("custom_project_name", u(self.custom_project_name))
        else:
            settings.set("custom_project_name", "")
        WakatimeProjectProperties.reload_defaults()
        self._hide()
        return {"FINISHED"}

    def invoke(self, context, _event):
        import os
        
        print("[Wakatime] [DEBUG] PreferencesDialog.invoke() called")
        
        # Force reload settings
        settings.load()
        
        # Load values with debug output
        api_key_value = settings.api_key()
        print(f"[Wakatime] [DEBUG] api_key() returned: '{api_key_value}'")
        self.api_key = api_key_value
        
        api_url_value = settings.api_url()
        print(f"[Wakatime] [DEBUG] api_url() returned: '{api_url_value}'")
        self.api_url = api_url_value
        
        custom_name_value = settings.get("custom_project_name", "")
        print(f"[Wakatime] [DEBUG] custom_project_name: '{custom_name_value}'")
        self.custom_project_name = custom_name_value
        
        always_overwrite_value = settings.get_bool("always_overwrite_project_name")
        print(f"[Wakatime] [DEBUG] always_overwrite_project_name: {always_overwrite_value}")
        self.always_overwrite_name_default = always_overwrite_value
        
        config_path = settings.FILENAME
        if os.path.exists(config_path):
            self.config_status = f"✓ Loaded from: {config_path}"
            print(f"[Wakatime] [DEBUG] Config file exists at: {config_path}")
        else:
            self.config_status = f"⚠ Config not found: {config_path}"
            print(f"[Wakatime] [WARNING] Config file not found at: {config_path}")
        
        rate_limit = settings.heartbeat_rate_limit_seconds()
        print(f"[Wakatime] [DEBUG] heartbeat_rate_limit_seconds: {rate_limit}")
        self.heartbeat_rate_display = f"{rate_limit:.0f} seconds"
        
        print(f"[Wakatime] [DEBUG] Dialog fields set - api_key: '{self.api_key}', api_url: '{self.api_url}'")
        
        return context.window_manager.invoke_props_dialog(self, width=600)

    def draw(self, _context):
        props = WakatimeProjectProperties.instance()
        if props is None:
            return
        layout = self.layout
        
        box = layout.box()
        box.label(text=self.config_status, icon='INFO' if '✓' in self.config_status else 'ERROR')
        row = box.row()
        row.operator("ui.wakatime_reload_config", text="Reload Config", icon='FILE_REFRESH')
        
        layout.separator()
        
        box = layout.box()
        box.label(text="API Settings", icon='NETWORK_DRIVE')
        col = box.column()
        col.prop(self, "api_key", text="API Key")
        col.prop(self, "api_url", text="API URL")
        col.label(text=f"Rate Limit: {self.heartbeat_rate_display}", icon='TIME')
        
        layout.separator()
        
        box = layout.box()
        box.label(text="Project Name Settings", icon='FILE_FOLDER')
        col = box.column()
        col.prop(self, "custom_project_name", text="Custom Name (Override All)")
        col.separator(factor=0.5)
        col.prop(self, "always_overwrite_name_default", text="Always Override by Default")
        col.prop(props, "always_overwrite_name", text="Override for Current File")
        
        layout.separator()
        
        box = layout.box()
        box.label(text="Auto-Detection Rules", icon='SETTINGS')
        col = box.column()
        col.prop(props, "use_project_folder", text="Use Folder Name")
        col.prop(props, "project_prefix", text="Prefix")
        col.prop(props, "project_postfix", text="Postfix")
        col.prop(props, "truncate_trail", text="Trim Trailing Chars")
        
        layout.separator()
        
        box = layout.box()
        box.label(text="Heartbeat Settings", icon='HEART')
        col = box.column()
        col.prop(props, "heartbeat_frequency", text="Frequency (minutes)")
