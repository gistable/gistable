from deluge._libtorrent import lt
from deluge.core.torrentmanager import TorrentManagerState
from shutil import copy, _samefile
import cPickle
import os

class Transplant(object):
    def __init__(self, config_dir="", torrent_ids=None, torrents=None):
        self.state_dir = ""
        self.torrents = {}
        if config_dir:
            config_dir = os.path.expanduser(config_dir)
            config_dir = os.path.normpath(config_dir)
            self.state_dir = os.path.join(config_dir, "state")
            state_file = open(os.path.join(self.state_dir, "torrents.state"), "rb")
            resume_file = open(os.path.join(self.state_dir, "torrents.fastresume"), "rb")
            self._update(state_file, resume_file)
            self._link()
        if torrent_ids:
            for torrent_id in torrent_ids:
                state_file = open(torrent_id+".state", "rb")
                resume_file = open(torrent_id+".fastresume", "rb")
                self._update(state_file, resume_file)
            self._link()
        if torrents:
            self.torrents.update(torrents)

    def _update(self, state_file, resume_file):
        state_data = cPickle.load(state_file)
        resume_data = lt.bdecode(resume_file.read())
        state_file.close()
        resume_file.close()
        for torrent_state in state_data.torrents:
            torrent_id = torrent_state.torrent_id
            self.torrents.setdefault(torrent_id, {})["state"] = torrent_state
            self.torrents[torrent_id]["resume"] = resume_data.get(torrent_id)

    def _link(self):
        for torrent_id in self.torrents:
            filename = os.path.join(self.state_dir, torrent_id+".torrent")
            if os.path.isfile(filename):
                self.torrents[torrent_id]["filename"] = filename
            else:
                raise IOError, "Missing torrent file: %s" % filename

    def __iter__(self):
        return iter(self.torrents)

    def __contains__(self, torrent_id):
        return torrent_id in self.torrents

    def __getitem__(self, torrent_id):
        return self.torrents[torrent_id]

    def filter(self, torrent_ids=None):
        if torrent_ids:
            torrent_ids = set(torrent_ids) & self.torrents.viewkeys()
        else:
            torrent_ids = self.torrents.viewkeys()
        return torrent_ids

    def combine(self, other):
        self.torrents.update(other.torrents)

    def separate(self, torrent_ids=None):
        torrents = {torrent_id: self.torrents[torrent_id] for torrent_id in self.filter(torrent_ids)}
        return Transplant(torrents=torrents)

    def rebase(self, save_path=None, completed_path=None):
        for torrent_id in self.torrents:
            if save_path:
                self.torrents[torrent_id]["state"].save_path = save_path
            if completed_path:
                self.torrents[torrent_id]["state"].move_completed_path = completed_path

    def save(self):
        if self.state_dir:
            state_filename = os.path.join(self.state_dir, "torrents.state")
            resume_filename = os.path.join(self.state_dir, "torrents.fastresume")
            self.__write(self.torrents.keys(), state_filename, resume_filename)
        else:
            for torrent_id in self.torrents:
                state_filename = torrent_id+".state"
                resume_filename = torrent_id+".fastresume"
                self.__write([torrent_id], state_filename, resume_filename)
        for torrent_id in self.torrents:
            new_filename = os.path.join(self.state_dir, torrent_id+".torrent")
            if not _samefile(self.torrents[torrent_id]["filename"], new_filename):
                copy(self.torrents[torrent_id]["filename"], new_filename)

    def __write(self, torrent_ids, state_filename, resume_filename):
        state_file = open(state_filename+".new", "wb")
        resume_file = open(resume_filename+".new", "wb")
        state_data = TorrentManagerState()
        state_data.torrents = [self.torrents[torrent_id]["state"] for torrent_id in torrent_ids]
        resume_data = {torrent_id: self.torrents[torrent_id]["resume"] for torrent_id in torrent_ids}
        cPickle.dump(state_data, state_file, cPickle.HIGHEST_PROTOCOL)
        resume_file.write(lt.bencode(resume_data))
        state_file.flush()
        resume_file.flush()
        os.fsync(state_file.fileno())
        os.fsync(resume_file.fileno())
        state_file.close()
        resume_file.close()
        os.rename(state_filename+".new", state_filename)
        os.rename(resume_filename+".new", resume_filename)

if __name__ == "__main__":
    import argparse

    def list_cmd(args):
        t = Transplant(args.config)
        print "Available torrents:"
        for torrent_id in t.filter(args.torrent_ids):
            print "%s - %s" % (torrent_id, t[torrent_id]["state"].filename)

    def import_cmd(args):
        t1 = Transplant(args.config)
        t2 = Transplant(torrent_ids=args.torrent_ids)
        if args.save_path or args.completed_path:
            t2.rebase(args.save_path, args.completed_path)
        t1.combine(t2)
        t1.save()
        print "Successfully imported:"
        for torrent_id in t2:
            print "%s - %s" % (torrent_id, t1[torrent_id]["state"].filename)

    def export_cmd(args):
        t1 = Transplant(args.config)
        t2 = t1.separate(args.torrent_ids)
        if args.save_path or args.completed_path:
            t2.rebase(args.save_path, args.completed_path)
        t2.save()
        print "Successfully exported:"
        for torrent_id in t2:
            print "%s - %s" % (torrent_id, t2[torrent_id]["state"].filename)

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="~/.config/deluge")
    subparsers = parser.add_subparsers(title="commands", description="available commands")
    parser_list = subparsers.add_parser("list")
    parser_list.set_defaults(cmd=list_cmd)
    parser_list.add_argument("torrent_ids", nargs='*')
    parser_import = subparsers.add_parser("import")
    parser_import.set_defaults(cmd=import_cmd)
    parser_import.add_argument("torrent_ids", nargs='+')
    parser_import.add_argument("-sp", "--save-path")
    parser_import.add_argument("-cp", "--completed-path")
    parser_export = subparsers.add_parser("export")
    parser_export.set_defaults(cmd=export_cmd)
    parser_export.add_argument("torrent_ids", nargs='*')
    parser_export.add_argument("-sp", "--save-path")
    parser_export.add_argument("-cp", "--completed-path")
    args = parser.parse_args()
    args.cmd(args)