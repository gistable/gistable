import sys
from subprocess import Popen
from Tkinter import Tk, StringVar
import ttk

START, STOP = "start", "stop"

# just some arbitrary command for demonstration
cmd = [sys.executable, '-c', """import sys, time
print("!")
sys.stdout.flush()
for i in range(30):
    sys.stdout.write("%d " % i)
    sys.stdout.flush()
    time.sleep(.05)
"""]


class App(object):
    def __init__(self, parent):
        self.process = None
        self.after = parent.after
        self.command = START
        self.button_text = None
        self.progressbar = None
        self.make_widgets(parent)

    def make_widgets(self, parent):
        parent = ttk.Frame(parent, padding="3 3 3 3")
        parent.pack()
        self.progressbar = ttk.Progressbar(parent, length=200,
                                           mode='indeterminate')
        self.progressbar.pack()
        self.button_text = StringVar()
        self.button_text.set(self.command)
        button = ttk.Button(parent, textvariable=self.button_text,
                            command=self.toggle)
        button.pack()
        button.focus()

    def toggle(self, event_unused=None):
        if self.command is START:
            self.progressbar.start()
            try:
                self.start_process()
            except:
                self.progressbar.stop()
                raise
            self.command = STOP
            self.button_text.set(self.command)
        else:
            assert self.command is STOP
            self.stop_process()

    def stop(self):
        self.progressbar.stop()
        self.command = START
        self.button_text.set(self.command)

    def start_process(self):
        self.stop_process()
        self.process = Popen(cmd)

        def poller():
            if self.process is not None and self.process.poll() is None:
                # process is still running
                self.after(delay, poller)  # continue polling
            else:
                self.stop()
        delay = 100  # milliseconds
        self.after(delay, poller)

    def stop_process(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            # kill process in a couple of seconds if it is not terminated
            self.after(2000, kill_process, self.process)
        self.process = None


def kill_process(process):
    if process is not None and process.poll() is None:
        process.kill()
        process.wait()


if __name__ == "__main__":
    root = Tk()
    app = App(root)

    def shutdown():
        app.stop_process()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", shutdown)
    root.bind('<Return>', app.toggle)
    root.mainloop()