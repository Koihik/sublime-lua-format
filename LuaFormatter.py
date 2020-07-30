import os
import sublime
import sublime_plugin
import subprocess
import sys


class LuaFormatCommand(sublime_plugin.TextCommand):
    def run(self, edit, error=True, save=True):
        # run lua-format
        package_path = os.path.split(os.path.dirname(__file__))[1]
        executable_path = os.path.join(
            sublime.packages_path(), package_path, "bin", sys.platform, "lua-format"
        )

        contents = self.view.substr(sublime.Region(0, self.view.size()))

        cmd = [executable_path]
        configFile = sublime.load_settings("LuaFormatter.sublime-settings").get("config_file", "")
        if configFile != "":
            cmd.append("-c")
            cmd.append(configFile)

        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.stdin.write(str.encode(contents))
        process.stdin.close()
        output = bytes.decode(process.stdout.read())
        error = bytes.decode(process.stderr.read())
        if error == "":
            self.view.replace(
                edit,
                sublime.Region(0, self.view.size()),
                # ST always uses \n in the text buffer
                output.replace("\r\n", "\n"),
            )
        else:
            sublime.error_message(error)


class LuaFormatOnPreSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        if view.file_name().endswith(".lua"):
            config = sublime.load_settings("LuaFormatter.sublime-settings")
            if config.get("auto_format_on_save", False):
                view.run_command("lua_format")
