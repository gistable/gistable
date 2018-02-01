def progress_bar(iteration, total, barLength=50):
    percent = int(round((iteration / total) * 100))
    nb_bar_fill = int(round((barLength * percent) / 100))
    bar_fill = '#' * nb_bar_fill
    bar_empty = ' ' * (barLength - nb_bar_fill)
    sys.stdout.write("\r  [{0}] {1}%".format(str(bar_fill + bar_empty), percent))
    sys.stdout.flush()
    
def bar_example():
    for i in range(20):
        time.sleep(0.5)
        progress_bar(i, 99, 200)
        
if __name__ == '__main__':
    bar_example()