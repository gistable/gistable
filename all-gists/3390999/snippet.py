import sublime, sublime_plugin, subprocess

class TidyXmlCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    if self.view.sel()[0].size() > 0:
      self.cursor = None
      for region in self.view.sel():
        self.format(edit, region)
    else:
      self.cursor = self.view.sel()[0]
      region = sublime.Region(0, self.view.size())
      self.format(edit, region)
    
  def clear(self):
    self.view.erase_status('tidyxml')

  def format(self, edit, region):
    command = 'tidy -xml -i -utf8 -w -q'
    p = subprocess.Popen(command, bufsize=-1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    result, err = p.communicate(self.view.substr(region).encode('utf-8'))
    
    if err != "":
      self.view.set_status('tidyxml', "tidyxml: "+err)
      sublime.set_timeout(self.clear,10000)
    else:
      self.view.replace(edit, self.view.line(region), result.decode('utf-8').replace('\r\n', '\n'))
      sublime.set_timeout(self.clear,0)
      sublime.set_timeout(self.move_cursor,1) # minor delay necessary, not sure why

  def move_cursor(self):
    if self.cursor != None:
      self.view.sel().clear()
      self.view.sel().add(self.cursor)
      self.view.show(self.cursor)