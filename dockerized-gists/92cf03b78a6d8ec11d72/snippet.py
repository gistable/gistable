def copy_into(directory, target_dir):
    with directory.relpath():
        for pth in path('./').walk():
            tgt = target_dir.joinpath(*pth.splitpath())
            if pth.isdir():
                tgt.makedirs_p()
                continue

            if pth.islink():
                link = pth.realpath().relpath()
                new_tgt = target_dir.joinpath(*link.splitpath())
                if not new_tgt.exists():
                    link.copyfile(new_tgt)

                with tgt.parent:
                    new_tgt = new_tgt.relpath()
                    new_tgt.symlink(tgt.relpath())
                    continue
            else:
                pth.copyfile(tgt)