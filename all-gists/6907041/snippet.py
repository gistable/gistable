import sqlite3

def get_chrome_cookies():
    conn = sqlite3.connect('/home/<username>/.config/chromium/Default/Cookies')
    query = 'select name, value, path from cookies where host_key=".livejournal.com";'
    return [{"name": r[0], "value": r[1], "path": r[2]} for r in conn.execute(query)]