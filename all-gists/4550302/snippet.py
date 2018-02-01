from PIL import Image, ImageDraw
import sqlite3
from grapefruit import Color

c1 = Color.NewFromHtml('#ffffff')
c2 = Color.NewFromHtml('#660000')

conn = sqlite3.connect('zon-tags-2.db')
im = Image.new('RGBA', (20 * 52 + 60, (2012 - 1946) * 20 + 40))

sql = "SELECT substr(id, 0, 5) year, substr(id, 6, 2) issue, count(*) from articles group by year, issue
 order by year, issue"

draw = ImageDraw.Draw(im)

for y in range(1946, 2013):
    draw.text((5, 32 + (y - 1946) * 20), str(y), fill='black')

for i in range(1, 53):
    draw.text((36 + (i) * 20, 10), str(i), fill='black')

for res in conn.execute(sql):
    year, issue, count = map(int, res)
    y = 30 + (year - 1946) * 20
    x = 30 + issue * 20
    col = c2.Blend(c1, percent=count / 561.0)
    draw.rectangle((x, y, x + 19, y + 19), fill=col.html)

im.save('heatmap-part.png', 'PNG')