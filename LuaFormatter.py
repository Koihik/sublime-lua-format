import os
import subprocess
import sys

import sublime
import sublime_plugin


def get_st_project_path():
    """Get the active Sublime Text project path.
    Original: https://gist.github.com/astronaughts/9678368
    :rtype: object
    :return: The active Sublime Text project path.
    """
    window = sublime.active_window()
    folders = window.folders()
    if len(folders) == 1:
        return folders[0]
    else:
        active_view = window.active_view()
        if active_view:
            active_file_name = active_view.file_name()
        else:
            active_file_name = None
        if not active_file_name:
            return folders[0] if len(folders) else os.path.expanduser("~")
        for folder in folders:
            if active_file_name.startswith(folder):
                return folder
        return os.path.dirname(active_file_name)


def get_file_abs_dir(filepath):
    return os.path.abspath(os.path.dirname(filepath))


def find_config(start_dir, alt_dirs=None):
    config_file = ".lua-format"
    target = os.path.join(start_dir, config_file)
    if os.path.exists(target):
        return target
    return None


class LuaFormatCommand(sublime_plugin.TextCommand):
    def try_find_config(self, view):
        project_file_dir = get_st_project_path()

        # 1. Attempt to automatically resolve:
        resolved_config = find_config(project_file_dir)
        if resolved_config and os.path.exists(resolved_config):
            return resolved_config

        return None

    def run(self, edit, error=True, save=True):
        # run lua-format
        package_path = os.path.split(os.path.dirname(__file__))[1]
        executable_path = os.path.join(
            sublime.packages_path(), package_path, "bin", sys.platform, "lua-format"
        )

        contents = self.view.substr(sublime.Region(0, self.view.size()))

        cmd = [executable_path]
        config_file_settings = sublime.load_settings(
            "LuaFormatter.sublime-settings"
        ).get("config_file", "")
        config_file_project = self.try_find_config(self.view)
        config_file = config_file_settings

        if config_file_project:
            config_file = config_file_project

        if config_file != "":
            cmd.append("-c")
            cmd.append(config_file)

        process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        process.stdin.write(str.encode(contents))
        process.stdin.close()
        output = bytes.decode(process.stdout.read())
        error = bytes.decode(process.stderr.read())
        if error == "":
            self.view.replace(edit, sublime.Region(0, self.view.size()), output)
        else:
            sublime.error_message(error)


class LuaFormatOnPreSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        if view.file_name().endswith(".lua"):
            config = sublime.load_settings("LuaFormatter.sublime-settings")
            if config.get("auto_format_on_save", False):
                view.run_command("lua_format")
