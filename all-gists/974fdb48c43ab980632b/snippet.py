
import datetime, webbrowser

def main():
    today = datetime.datetime.today().weekday()

    if today == 0 or today == 2 or today == 4:
        webbrowser.open("http://xkcd.com")

if __name__ == "__main__":
    main()
