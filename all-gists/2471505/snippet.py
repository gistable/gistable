import win32clipboard, win32con


def get_pattern():
    text = str(eval(raw_input("Pattern:\n")))

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text)
    win32clipboard.CloseClipboard()


def main():
    while True:
        get_pattern()

if __name__ == "__main__":
    main()
