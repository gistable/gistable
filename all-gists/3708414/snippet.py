from fnmatch import fnmatch

def check_pdb(ui, repo, hooktype, node=None, source=None, **kwargs):
    for file in [f for f in repo[node].files() if fnmatch(f, '*.py')]:
        # ファイルごとにチェック
