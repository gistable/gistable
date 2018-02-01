import logging
import subprocess
import time
import sys
import win32con
import win32gui_struct
import os
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui

from ctypes.wintypes import WinDLL, BOOL, DWORD
_kernel32 = WinDLL("kernel32")

SetProcessShutdownParameters = _kernel32.SetProcessShutdownParameters
SetProcessShutdownParameters.restype = BOOL
SetProcessShutdownParameters.argtypes = [DWORD, DWORD]

class Enum(object):
    def __init__(self, labels):
        self.values = {k: v for v, k in labels.items()}
        self.labels = labels

    def __getattr__(self, name):
        return self.labels[name]

    def __getitem__(self, value):
        return self.values[value]

    def __str__(self):
        return "Enum(labels: %r)" % self.labels
    __repr__ = __str__

try:
    import vboxapi
    VBM = vboxapi.VirtualBoxManager()
    VB = VBM.getVirtualBox()
    MachineState = Enum(VBM.constants.all_values('MachineState'))
    AutostopType = Enum(VBM.constants.all_values('AutostopType'))
    LockType = Enum(VBM.constants.all_values('LockType'))
    OffMachineStates = (
        MachineState.PoweredOff,
        MachineState.Saved,
        MachineState.Teleported,
        MachineState.Aborted,
    )
except ImportError:
    vboxapi = None
    class VB:
        class Machine:
            name = 'Missing `vboxapi` python package !!'
            state = 0
        machines = Machine,
    MachineState = {0: '?'}


class VirtualBoxAutoShutdownTray(object):
    CLASS_NAME = 'VirtualBoxAutoShutdownTray'
    HOVER_TEXT = 'VirtualBox automatic shutdown cleaner'
    def __init__(self):
        self.window_class = win32gui.WNDCLASS()
        self.hinstance = self.window_class.hInstance = win32gui.GetModuleHandle(None)
        self.window_class.lpszClassName = self.CLASS_NAME
        self.window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        self.window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        self.window_class.hbrBackground = win32con.COLOR_WINDOW
        self.window_class.lpfnWndProc = self.dispatch
        self.class_atom = win32gui.RegisterClass(self.window_class)
        self.hwnd = win32gui.CreateWindow(
            self.class_atom,
            self.CLASS_NAME,
            win32con.WS_OVERLAPPED | win32con.WS_SYSMENU,
            0,
            0,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            0,
            0,
            self.hinstance,
            None
        )
        win32gui.UpdateWindow(self.hwnd)
        self.set_icon()

    @property
    def dispatch(self):
        return {
            win32gui.RegisterWindowMessage("TaskbarCreated"): self.set_icon,
            win32con.WM_CLOSE: self.on_close,
            win32con.WM_QUIT: self.on_close,
            win32con.WM_QUERYENDSESSION: self.on_close,
            win32con.WM_ENDSESSION: self.on_close,
            win32con.WM_COMMAND: self.on_command,
            win32con.WM_USER+20: self.on_notify,
        }

    def set_icon(self, *_args):
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, (
            self.hwnd,
            0,
            win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
            win32con.WM_USER+20,
            win32gui.LoadIcon(self.hinstance, 1),
            self.HOVER_TEXT
        ))

    def on_command(self, hwnd, msg, wparam, lparam):
        print 'on_command', hwnd, msg, wparam, lparam
        command_id = win32gui.LOWORD(wparam)
        if command_id == 0:
            self.quit()
        else:
            raise RuntimeError("Unknown command_id %r" % command_id)

    def on_close(self, *args):
        self.shutdown_machines()
        self.quit()

    def on_notify(self, hwnd, msg, wparam, lparam):
        print 'on_notify', hwnd, msg, wparam, lparam
        if lparam == win32con.WM_LBUTTONDBLCLK:
            pass
        elif lparam == win32con.WM_RBUTTONUP:
            self.show_menu()
        elif lparam == win32con.WM_LBUTTONUP:
            pass
        return True

    def quit(self, *args):
        win32gui.DestroyWindow(self.hwnd)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (self.hwnd, 0))
        win32gui.PostQuitMessage(0)

    @property
    def menu_entries(self):
        for i, machine in enumerate(VB.machines):
            yield "[%s] %s" % (
                MachineState[machine.state], machine.name
            ), i

    def shutdown_machines(self):
        if vboxapi:
            for machine in VB.machines:
                logging.info("Checking for machine `%s` (state: %s)", machine.name, MachineState[machine.state])
                logging.error("Attempting ACPI shutdown for `%s`.", machine.name)
                sess = None
                try:
                    sess = VBM.getSessionObject(VB)
                    machine.lockMachine(sess, LockType.Shared)

                    for i in range(10):
                        logging.info("Machine `%s` is in state: %s", machine.name, MachineState[machine.state])
                        if machine.state == MachineState.Paused:
                            sess.console.resume()
                        elif machine.state in OffMachineStates:
                            break
                            logging.info("Machine `%s` is in state: %s. Were done !", machine.name, MachineState[machine.state])
                        else:
                            sess.console.PowerButton()
                        time.sleep(1)
                except Exception as exc:
                    logging.error("Failed to ACPI shutdown `%s`: %s", machine.name, exc)
                finally:
                    if sess:
                        try:
                            sess.unlockMachine()
                        except Exception as exc:
                            logging.debug("Failed to unlock session: %s", exc)

                if machine.state not in OffMachineStates:
                    logging.critical("Saving machine `%s` ... ", machine.name)
                    sess = None
                    try:
                        sess = VBM.getSessionObject(VB)
                        machine.lockMachine(sess, LockType.Shared)
                        sess.console.saveState()

                        for i in range(20):
                            time.sleep(1)
                            logging.info("Machine `%s` is in state: %s", machine.name, MachineState[machine.state])
                            if machine.state == MachineState.Saved:
                                break
                        else:
                            logging.error("Failed to save `%s`: Took too much time to save !", machine.name)
                    except Exception as exc:
                        logging.error("Failed to save `%s`: %s", machine.name, exc)
                    finally:
                        if sess:
                            try:
                                sess.unlockMachine()
                            except Exception as exc:
                                logging.debug("Failed to unlock session: %s", exc)


    def show_menu(self):
        menu = win32gui.CreatePopupMenu()
        count = 0

        for count, (option_text, option_id) in enumerate(self.menu_entries):
            win32gui.AppendMenu(
                menu,
                win32con.MF_STRING|win32con.MF_GRAYED|win32con.MF_DISABLED,
                option_id,
                option_text
            )

        win32gui.InsertMenu(
            menu, count+1, win32con.MF_BYPOSITION, win32con.MF_SEPARATOR, None
        )
        win32gui.InsertMenuItem(
            menu, count+2, 1, win32gui_struct.PackMENUITEMINFO(
                text="Quit",
                wID=0,
                hbmpItem=win32con.HBMMENU_MBAR_CLOSE
            )[0]
        )

        pos = win32gui.GetCursorPos()
        # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(
            menu,
            win32con.TPM_LEFTALIGN,
            pos[0],
            pos[1],
            0,
            self.hwnd,
            None
        )
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)

    def run(self):
        SetProcessShutdownParameters(0x3FF, 0) # so we get shutdown first
        win32gui.PumpMessages()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename='vbox-shutdown.log' if len(sys.argv) < 2 else sys.argv[1])
    if 'pythonw.exe' in sys.executable:
        app = VirtualBoxAutoShutdownTray()
        app.run()
    else:
        subprocess.Popen([sys.executable.replace('python.exe', 'pythonw.exe'), __file__] + sys.argv[1:])
