#!/usr/bin/python
DOCUMENTATION = '''
---
module: copy_remotely
short_description: Copies a file from the remote server to the remote server.
description:
     - Copies a file but, unlike the M(file) module, the copy is performed on the
       remote server.
       The copy is only performed if the source and destination files are different
       (different MD5 sums) or if the destination file does not exist.
       The destination directory is created if missing.
version_added: ""
options:
  src:
    description:
      - Path to the file to copy.
    required: true
    default: null
  dest:
    description:
      - Path to the destination file.
    required: true
    default: null
'''

EXAMPLES = '''
- copy_remotely: src=/tmp/foo.conf dest=/etc/foo.conf
'''

import shutil

def main():
      module = AnsibleModule(
          argument_spec = dict(
              src       = dict(required=True),
              dest      = dict(required=True),
          )
      )

      src = module.params['src']
      dest = module.params['dest']

      if not os.path.exists(src):
          module.fail_json(msg="Source file not found: %s" % src)

      src_md5 = module.md5(src)
      dest_md5 = module.md5(dest)

      changed = False

      # create the target directory if missing
      dest_dir = os.path.dirname(dest)
      if not os.path.isdir(dest_dir):
          os.makedirs(dest_dir)
          changed = True

      # copy the file if newer
      if src_md5 != dest_md5:
          shutil.copyfile(src, dest)
          changed = True

      module.exit_json(changed=changed, src_md5=src_md5, dest_md5=dest_md5)


from ansible.module_utils.basic import *

main()