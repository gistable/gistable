import sublime_plugin, os
 
class RemoteEdit(sublime_plugin.EventListener):
    def on_post_save(self, view):
        remote = { "/local/path/to/project": "/usr/bin/scp '$1' username@remote_host:'/remote/path/to/project$2'" }
 
        for dirname, target in remote.iteritems():
            if view.file_name().startswith( dirname ):
                target = target.replace( "$1", view.file_name() )
                target = target.replace( "$2", view.file_name()[len(dirname):] )
 
                fname = view.file_name().replace(dirname, '')
                os.system( target + " &" )
                os.system( "/usr/local/bin/growlnotify -m 'Copied %s'" % fname )