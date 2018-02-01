import subprocess, itertools, numpy
import matplotlib.pyplot as plt

command = 'git log --shortstat --log-size --format=oneline --no-merges'.split()
data = subprocess.check_output(command).split('\n')

def read_groups():
    buf = []
    for line in data:
        buf.append(line)
        if line.find('changed') != -1 and buf:
            yield buf
            buf = []

xs, ys, msgs, commits = [], [], [], []
for group in read_groups():
    if len(group) != 3: continue

    commit = group[0].split()[0]
    log_size = int(group[0].split()[-1])
    msg = group[1]
    change_size = sum(map(int, group[2].split()[3::2]))

    if log_size > 0 and change_size > 0:
        xs.append(change_size)
        ys.append(log_size)
        msgs.append(msg)
        commits.append(commit)

fig, ax = plt.subplots()
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Size of commit (added + deleted lines)')
ax.set_ylabel('Size of commit message')
ax.scatter(xs, ys)

xs_pixels, ys_pixels = ax.transData.transform(numpy.vstack([xs, ys]).T).T
img_height = fig.get_figheight() * fig.dpi

f = open('test.html', 'w')
print >>f, '<img src="test.png" usemap="#points"/>'
print >>f, '<map name="points">'
for x_pixel, y_pixel, msg, commit in zip(xs_pixels, ys_pixels, msgs, commits):
    f.write('<area shape="circle" coords="%d,%d,5" href="https://github.com/spotify/luigi/commit/%s" title="%s">' % (x_pixel, img_height-y_pixel, commit, msg.replace('"', '')))
f.write('</map>')
f.close()

fig.savefig('test.png', dpi=fig.dpi)