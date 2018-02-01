import os
import i3
import sys
import pickle

def showHelp():
    print(sys.argv[0] + " <save|restore>")

def get_visible_workspace():
    for workspace in i3.get_workspaces():
        if workspace['visible']:
            return workspace['name']

if __name__ == '__main__':
    if len(sys.argv) < 2:
        showHelp()
        sys.exit(1)

    if sys.argv[1] == 'save':
        print("Storing...")
        workspace_mapping = {}
        for workspace in i3.get_workspaces():
            workspace_mapping[workspace['name']] = workspace['output']
        pickle.dump(workspace_mapping, open("%s/.i3/workspace_mapping" % os.path.expanduser("~"), "wb"))
    elif sys.argv[1] == 'restore':
        print("Restoring")
        try:
            workspace_mapping = pickle.load(open("%s/.i3/workspace_mapping" % os.path.expanduser("~"), "rb"))
        except Exception:
            print("Can't find existing mappings...")
            sys.exit(1)
        current_workspace = get_visible_workspace()
        for workspace in i3.get_workspaces():
            if workspace['name'] in workspace_mapping:
                i3.msg('command', 'workspace %s' % workspace['name'])
                i3.msg('command', 'move workspace to output %s' % workspace_mapping[workspace['name']])
        i3.msg('command', 'workspace %s' % current_workspace)
    else:
        showHelp()
        sys.exit(1)
