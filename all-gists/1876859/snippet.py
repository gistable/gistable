#variation of http://urbangiraffe.com/2011/08/13/remote-editing-with-sublime-text-2/ that adds creating new folders remotely.

import sublime_plugin, os

class RemoteEdit(sublime_plugin.EventListener):
  def on_post_save(self, view):
    remote = { "/Users/leto/work/project": ["/usr/bin/scp", None, "user@server", "root_remote_path_like ~/project/", None] }

    for dirname, target in remote.iteritems():
      if view.file_name().startswith( dirname ):
        if self.copy_file(view, target, dirname) == 256:
          path = target[3] + os.path.dirname(target[4])
          create_target = "ssh %s '[ -d %s  || mkdir -p %s ]'" % (target[2], path, path)
          if os.system( create_target ) == 0:
            self.copy_file(view, target, dirname)


  def copy_file(self, view, target, dirname):
    target[1] = view.file_name()
    target[4] = view.file_name()[len(dirname):]
    print "%s %s %s:%s%s" % tuple(target)
    return os.system( "%s %s %s:%s%s" % tuple(target) )