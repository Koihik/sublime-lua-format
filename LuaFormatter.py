import os.path
import sublime, sublime_plugin, sys
import subprocess

class LuaFormatCommand(sublime_plugin.TextCommand):
  def run(self, edit, error=True, save=True):
    self.filename = self.view.file_name()
    self.fname = os.path.basename(self.filename)
    region = sublime.Region(0, self.view.size())

    settings = sublime.load_settings('LuaFormatter.sublime-settings')
    config = settings.get('config_file')

    src = self.view.substr(region)
    command = os.path.join(sublime.packages_path(), 'LuaFormatter', 'bin', sys.platform, 'lua-format')
    command = "'" + command + "' -si '" + self.filename + "'"
    if config:
        command = command + " -c " + config

    process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out = process.communicate(src.encode("utf-8"))
    if out[0]:
    	self.view.replace(edit, region, out[0].decode('utf8'))
    if out[1]:
    	msg = "Run lua-format error: \n" + out[1].decode('utf8')
    	sublime.error_message(msg)
