#!/usr/bin/env python3
#
# Simple encrypted backup
#
# Copyright 2011 Thomas Jost
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

# {{{ Imports
import gzip
import optparse
import os
import os.path
import pickle
import subprocess
import sys
import time
# }}}

# {{{ Constants
FILES_PER_PACK = 250
# }}}

# {{{ Packs management
class PacksManager:
    # {{{ Init and internal stuff
    def __init__(self, dbpath, src, dst):
        self._src = src
        self._dst = dst

        # Load the pickled database if it exists
        self._dbpath = dbpath
        self._db_dirty = False
        if os.path.isfile(dbpath):
            with gzip.open(dbpath, "rb") as f:
                print("Loading DB...")
                self._db = pickle.load(f)
        else:
            self._db = {}
            self._db_dirty = True

        self._packs = {}
        self._new_packs = set()
        self._modified_packs = set()
        self._deleted_packs = set()

        # Prepare a list of packs
        for fn in self._db:
            pack = self._db[fn][0]
            if pack in self._packs:
                self._packs[pack].append(fn)
            else:
                self._packs[pack] = [fn]

        # Stuff needed to create new pack names
        self._n = 1
        self._packname = "pack_{0}_{1}".format(time.strftime("%Y%m%d-%H%M%S"), "{0:06d}")

    # Dump the DB to disk
    def dump_db(self):
        with gzip.open(self._dbpath, "wb") as f:
            pickle.dump(self._db, f, protocol=pickle.HIGHEST_PROTOCOL)

    # Iterate on keys
    def __iter__(self):
        return iter(self._db)

    # Read the mtime of a file from the DB
    def __getitem__(self, fn):
        return self._db[fn][1]

    # Test if a file is in the DB
    def __contains__(self, fn):
        return fn in self._db
    # }}}

    # {{{ Packs management
    # Add a new pack to the DB
    def new_pack(self):
        pack = self._packname.format(self._n)
        self._n += 1
        self._packs[pack] = []
        self._new_packs.add(pack)
        return pack

    # Create a pack
    def make_pack(self, pack):
        files = self._packs[pack]
        pack_file = os.path.join(self._dst, pack)

        tarcmd = ["tar", "-C", self._src, "-c"]
        tarcmd.extend(files)
        gpgcmd = ["gpg", "-e", "-o", pack_file, "--batch"]
        
        tar = subprocess.Popen(tarcmd, stdout=subprocess.PIPE)
        gpg = subprocess.Popen(gpgcmd, stdin=tar.stdout)
        tar.stdout.close()
        gpg.communicate()

        # If this failed, fail miserably :)
        if gpg.returncode != 0:
            try:
                os.remove(pack_file)
            except:
                pass
            raise Exception("GnuPG ended with code {}.".format(gpg.returncode))

    # Apply the requested modifications
    def sync(self):
        # New packs
        tot = len(self._new_packs)
        if tot == 0:
            print("No new pack.")
        else:
            n = 1
            for pack in self._new_packs:
                print("\rNew packs: {0}/{1}...".format(n, tot), end="")
                self.make_pack(pack)
                n += 1
            print(" done.")

        # Updated packs
        tot = len(self._modified_packs)
        if tot == 0:
            print("No updated pack.")
        else:
            n = 1
            for pack in self._modified_packs:
                print("\rModified packs: {0}/{1}...".format(n, tot), end="")

                # Prepare a new pack, delete the old one
                new_pack = self.new_pack()
                self._packs[new_pack] = self._packs[pack]
                del self._packs[pack]
                self._deleted_packs.add(pack)

                # And move data from the old one to the new one in the DB too
                for fn in self._packs[new_pack]:
                    mtime = self._db[fn][1]
                    self._db[fn] = (new_pack, mtime)
                
                self.make_pack(new_pack)
                n += 1
            print(" done.")

        # Deleted packs
        tot = len(self._deleted_packs)
        if tot == 0:
            print("No deleted pack.")
        else:
            n = 1
            for pack in self._deleted_packs:
                print("\rDeleted packs: {0}/{1}...".format(n, tot), end="")
                pack_file = os.path.join(self._dst, pack)
                try:
                    os.remove(pack_file)
                except:
                    print(" {0} was not removed :/".format(pack))
                n += 1
            print(" done.")

        if self._db_dirty:
            print("Saving the database...")
            self.dump_db()

        print("Done.")
    # }}}

    # {{{ File operations
    # Add a new file to the DB
    def add_file(self, fn, mtime):
        # Find if there is an incomplete pack
        cur_pack = None
        for pack in self._packs:
            fns = self._packs[pack]
            if len(fns) < FILES_PER_PACK:
                cur_pack = pack
                if cur_pack not in self._new_packs:
                    self._modified_packs.add(cur_pack)
                break

        # Create a new pack if all the others are full
        if cur_pack is None:
            cur_pack = self.new_pack()

        # Now add the file to the DB
        self._db[fn] = (cur_pack, mtime)
        self._packs[cur_pack].append(fn)
        self._db_dirty = True

    # Delete a file from the DB
    def del_file(self, fn):
        pack = self._db[fn][0]
        del self._db[fn]
        self._packs[pack].remove(fn)
        self._db_dirty = True

        # Is the pack now empty?
        if len(self._packs[pack]) == 0:
            del self._packs[pack]
            self._modified_packs.discard(pack)
            self._deleted_packs.add(pack)
        else:
            self._modified_packs.add(pack)

    # Signal that a file was modified (and needs to be repacked)
    def update_file(self, fn, new_mtime):
        pack, mtime = self._db[fn]
        self._db[fn] = (pack, new_mtime)
        self._modified_packs.add(pack)
        self._db_dirty = True
    # }}}
# }}}

# {{{ Tree walking
def new_files(pm, path, exclude):
    for root, dirs, files in os.walk(path):
        root2 = os.path.relpath(root, path)

        # Excluded dir?
        basedir = root2.split(os.sep)[0]
        if basedir in exclude:
            continue
        
        for f in files:
            p = os.path.join(root2, f)
            pp = os.path.join(root, f)
            if p not in pm:
                mtime = int(os.path.getmtime(pp))
                yield (p, mtime)

def deleted_files(pm, path):
    for f in pm:
        p = os.path.join(path, f)
        if not os.path.isfile(p):
            yield f

def modified_files(pm, path):
    for f in pm:
        p = os.path.join(path, f)
        if os.path.isfile(p):
            mtime = pm[f]
            new_mtime = int(os.path.getmtime(p))
            if mtime != new_mtime:
                yield (f, new_mtime)
# }}}

# {{{ Script run
if __name__ == "__main__":
    # Parse command line
    usage="Usage: %prog [options] src_dir dst_dir"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-d", "--db", metavar="DB",
                      action="store", dest="db", default="packs.db",
                      help="path to the internal database; default: %default")
    parser.add_option("-e", "--exclude", metavar="DIRNAME",
                      action="append", dest="exclude", default=[],
                      help="don't search for new files in the DIRNAME directory; may be used several times")
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("2 arguments are needed")
    
    src, dst = args

    pm = PacksManager(options.db, src, dst)

    # New files, modified files, deleted files
    print("Looking for changes...")
    nf = list(new_files(pm, src, options.exclude))
    mf = list(modified_files(pm, src))
    df = list(deleted_files(pm, src))

    for fn, mtime in nf:
        pm.add_file(fn, mtime)
    for fn, mtime in mf:
        pm.update_file(fn, mtime)
    for fn in df:
        pm.del_file(fn)

    pm.sync()
# }}}
