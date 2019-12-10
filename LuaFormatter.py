import os
import sublime, sublime_plugin, sys
import subprocess
import shutil


LUA_STYLE_NAME = "lua_style.lua-format"


def plugin_loaded():
    init_config_file()


def init_config_file():
    package_path = os.path.dirname(os.path.realpath(__file__))
    config_src_path = os.path.join(package_path, LUA_STYLE_NAME)
    config_dst_path = os.path.join(sublime.packages_path(), "User", LUA_STYLE_NAME)
    if not os.path.exists(config_dst_path):
        shutil.copyfile(config_src_path, config_dst_path)


class LuaFormatCommand(sublime_plugin.TextCommand):
    def run(self, edit, error=True, save=True):
        # check whether the lua files
        suffix_setting = self.view.settings().get("syntax")
        file_suffix = suffix_setting.split(".")[0]
        if file_suffix[-3:].lower() != "lua":
            return

        # check whether filename is None
        filename = self.view.file_name()
        if filename is None:
            return

        # run lua-format
        package_path = os.path.split(os.path.dirname(__file__))[1]
        executable_path = os.path.join(
            sublime.packages_path(), package_path, "bin", sys.platform, "lua-format"
        )

        config_path = os.path.join(sublime.packages_path(), "User", LUA_STYLE_NAME)
        process = subprocess.Popen([executable_path, filename, "-c", config_path])


class LuaFormatOnPreSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        s = sublime.load_settings("LuaFormatter.sublime-settings")
        if s.get("auto_format_on_save", False):
            view.run_command("lua_format")
