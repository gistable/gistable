
# coroutine example

def look_for(pattern):
    while True:
        temp = yield
        if pattern in temp:
            print("I found {} in {}!".format(pattern, temp))
        else:
            print("No {} in {}.".format(pattern, temp))
        if pattern == 'break':
            break

if __name__ == "__main__":
    c = look_for('ed')
    c.send(None)  # prime the "coroutine"
    c.send('education')
    c.send('fundamental')
    c.send('ed was here!')
    c.send('something else')
    c.send('break')