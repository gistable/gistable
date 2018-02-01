import tarfile
import time
from io import BytesIO

admin_password = 'xxxxx'

#write password to file
pw_tarstream = BytesIO()
pw_tar = tarfile.TarFile(fileobj=pw_tarstream, mode='w')
file_data = admin_password.encode('utf8')
tarinfo = tarfile.TarInfo(name='pw.txt')
tarinfo.size = len(file_data)
tarinfo.mtime = time.time()
#tarinfo.mode = 0600
pw_tar.addfile(tarinfo, BytesIO(file_data))
pw_tar.close()


container = docker_client.create_container(
    **container_options
)

pw_tarstream.seek(0)
pr = docker_client.put_archive(
    container=container['Id'],
    path='/tmp',
    data=pw_tarstream
)