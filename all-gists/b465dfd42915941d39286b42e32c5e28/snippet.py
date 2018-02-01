#!/usr/bin/env python
'''
Kanban + Pomodoro + Reminder
If you use linux please install sox first (sudo apt-get install sox)
You can use these formats in order to remind you of the tasks:
    * Y:m:d H:M:S
    * Y:m:d H:M
    * everyday H:M[:S]
    * every [monday|tuesday|wednesday|thursday|friday|saturday] H:M[:S]
    * *:m:d H:M[:S]
    * Y:*:d H:M[:S]
    * Y:m:* H:M[:S]
    : *:*:d H:M[:S]
Original source code: https://gist.github.com/goFrendiAsgard/b465dfd42915941d39286b42e32c5e28
'''
import sys, os, json, time, datetime, math, curses, thread

#global variables
KANBAN_FILE = os.path.expanduser("~/.kanban.json")
DEFAULT_KANBAN = {
        "tasks" : [],
        "boards" : ["To do", "Doing", "Done"],
        "work_time" : 25 * 60,
        "rest_time" : 5 * 60
        }
DEFAULT_TASK = {
        "name" : "",
        "board": "",
        "remind_on" : "",
        "remind_for" : 30 * 60
        }
CURRENT_REMINDED_TASKS = []
IS_WORKING = True
IS_PAUSE = False
COUNTER = -1
DAYS = (('mon', 'monday'), ('tue', 'tuesday'), ('wed', 'wednesday'), ('thu', 'thursday'), ('fri', 'friday'), ('sat', 'saturday'), ('sun', 'sunday'))
DATE_SUFFIX = ('', 'st', 'nd', 'rd', 'th')

def _single_beep(frequency, duration):
    try:
        import winsound
        winsound.Beep(frequency, duration)
    except ImportError:
        os.system("play --no-show-progress --null synth %f sine %f vol 1" % (duration, frequency))

def _multi_beep(frequency_list, duration_list):
    for i, frequency in enumerate(frequency_list):
        duration = duration_list[i]
        _single_beep(frequency, duration)

def single_beep(frequency, duration):
    thread.start_new_thread(_single_beep, (frequency, duration))

def multi_beep(frequency_list, duration_list):
    thread.start_new_thread(_multi_beep, (frequency_list, duration_list))

def switch_beep():
    frequency_list = (2093,     0,  2637,     0,  3135)
    duration_list  = ( 0.1,  0.05,   0.1,  0.05,   0.1)
    multi_beep(frequency_list, duration_list)

def alarm_beep():
    frequency_list = (7000,     0,  7000)
    duration_list  = ( 0.2,  0.05,   0.2)
    multi_beep(frequency_list, duration_list)

def parse_str_timestamp_keyword(string, keyword, localtime):
    (year, mon, mday, hour, minute, sec, wday, yday, dst) = localtime
    year = str(year).rjust(4,"0")
    mon = str(mon).rjust(2,"0")
    mday = str(mday).rjust(2,"0")
    if string[:len(keyword)].lower() == keyword.lower():
        string = string.replace(keyword, "%s-%s-%s" % (year, mon, mday))
    return string

def complete_str_timestamp(string):
    localtime = time.localtime()
    (year, mon, mday, hour, minute, sec, wday, yday, dst) = localtime
    year = str(year).rjust(4,"0")
    mon = str(mon).rjust(2,"0")
    mday = str(mday).rjust(2,"0")
    # everyday, daily
    string = parse_str_timestamp_keyword(string, 'everyday', localtime)
    string = parse_str_timestamp_keyword(string, 'daily', localtime)
    # weekly (eg: every thursday, thursday, thu)
    aliases = DAYS[wday]
    for alias in aliases:
        for prefix in ('', 'every '):
            string = parse_str_timestamp_keyword(string, prefix + alias, localtime)
    # monthly (eg: every 1st, 1st, 1)
    alias = str(mday)
    for suffix in DATE_SUFFIX:
        string = parse_str_timestamp_keyword(string, alias+suffix, localtime)
    # stars
    aliases = ("*-*-*",
            "*-*-%s" % (mday),
            "*-%s-*" % (mon),
            "*-%s-%s" % (mon, mday),
            "%s-*-%s" % (year, mday),
            "%s-%s-*" % (year, mon),
            "%s-%s-%s" % (year, mon, mday)
            )
    for alias in aliases:
        string = parse_str_timestamp_keyword(string, alias, localtime)
    # ensure that string is valid date, otherwise make it empty string
    try:
        datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
        return string
    except ValueError:
        try:
            datetime.datetime.strptime(string, "%Y-%m-%d %H:%M")
            return string+":00"
        except ValueError:
            return ""

def str_to_timestamp(string):
    string = complete_str_timestamp(string)
    if string != "":
        return time.mktime(datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S").timetuple())

def timestamp_to_str(timestamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

def menu():
    print("(p) Pomodoro       (a) Add Task   (d) Delete Task")
    print("(c) Configuration  (e) Edit Task  (q) Quit Program")

def type_match(value_1, value_2):
    # string
    string_type = (str, unicode)
    if type(value_1) in string_type and type(value_2) in string_type:
        return True
    # number
    number_type = (float, int)
    if type(value_1) in string_type and type(value_2) in string_type:
        return True
    # other type
    if type(value_1) == type(value_2):
        return True
    return False

def load_kanban():
    if os.path.exists(KANBAN_FILE):
        with open(KANBAN_FILE, "r") as infile:
            kanban = json.load(infile)
            default_board = kanban["boards"][0] if len(kanban["boards"])>0 else ""
            # completing kanban
            for key, value in DEFAULT_KANBAN.items():
                if key not in kanban.keys():
                    kanban[key] = value
                if not type_match(kanban[key], DEFAULT_KANBAN[key]):
                    kanban[key] = value
            # completing task
            for i, task in enumerate(kanban["tasks"]):
                for key, value in DEFAULT_TASK.items():
                    if key not in task.keys():
                        kanban["tasks"][i][key] = value
                    if not type_match(kanban["tasks"][i][key], DEFAULT_TASK[key]):
                        kanban["tasks"][i][key] = value
                # No empty board
                if task["board"] == "":
                    kanban["tasks"][i]["board"] = default_board
            return kanban
    return DEFAULT_KANBAN

def save_kanban(kanban):
    with open(KANBAN_FILE, "w+") as outfile:
        json.dump(kanban, outfile)

def change_configuration(kanban):
    # prompt and save work time
    work_time = raw_input("Work time in minutes (previous value: %d) : " % (int(kanban["work_time"])/60))
    if work_time.strip().isdigit():
        work_time = int(work_time)
        kanban["work_time"] = work_time * 60
    # prompt and save rest time
    rest_time = raw_input("Rest time in minutes (previous value: %d) : " % (int(kanban["rest_time"])/60))
    if rest_time.strip().isdigit():
        rest_time = int(rest_time)
        kanban["rest_time"] = rest_time * 60
    # prompt and save boards
    boards = raw_input("Boards, separated by '|' (previous value: '%s') : " % (" | ".join(kanban["boards"])))
    if boards.strip() != "":
        boards = boards.split("|")
        for i,board in enumerate(boards):
            boards[i] = board.strip()
        kanban["boards"] = boards
    # return the modified kanban
    return kanban

def get_available_board_option(kanban):
    boards = list(kanban["boards"])
    for i, board in enumerate(boards):
        boards[i] = "'" + board + "'"
    return ", ".join(kanban["boards"])

def normalize_board(board_name, kanban):
    boards = kanban["boards"]
    for board in boards:
        if board.replace(" ", "").lower() == board_name.replace(" ", "").lower():
            return board
    return board_name.strip()

def add_task(kanban):
    # task name
    task_name = raw_input("Task name : ")
    # board
    default_board = kanban["boards"][0] if len(kanban["boards"])>0 else ""
    board = raw_input("Board name, (default : '%s') : " %(default_board))
    board = normalize_board(board, kanban)
    if board == "":
        board = default_board
    elif board not in kanban["boards"]:
        kanban["boards"].append(board)
    # remind_on
    remind_on = raw_input("Remind on (format : Y-m-d H:M:S), (default : '') : ")
    # remind_for
    remind_for = raw_input("Reminder duration in minutes, (default : 30) : ")
    if remind_for.strip() == "":
        remind_for = 30 * 60
    # add to kanban
    new_task = {
            "name" : task_name,
            "board" : board,
            "remind_on" : remind_on,
            "remind_for" : remind_for
            }
    kanban["tasks"].append(new_task)
    return kanban

def delete_task(kanban):
    task_id = raw_input("Task id : ")
    if task_id.isdigit():
        kanban["tasks"].pop(int(task_id)-1)
    return kanban

def edit_task(kanban):
    task_id = raw_input("Task id : ")
    if task_id.isdigit():
        task_id = int(task_id) - 1
        task = kanban["tasks"][task_id]
        # task name
        default_task_name = task["name"]
        task_name = raw_input("Task name (previous value : %s) : " % (default_task_name))
        if task_name.strip() != "":
            task["name"] = task_name
        # board
        default_board = task["board"]
        board = raw_input("Board name, (previous value : '%s') : " %(default_board))
        board = normalize_board(board, kanban)
        if board.strip() != "":
            if board not in kanban["boards"]:
                kanban["boards"].append(board)
            task["board"] = board
        # remind_on
        default_remind_on = task["remind_on"]
        remind_on = raw_input("Remind on (format : yyyy-mm-dd H:M:S), (previous value : '%s') : " % (default_remind_on))
        if remind_on.strip() != "":
            task["remind_on"] = remind_on
        elif default_remind_on.strip() != "":
            keep_value = raw_input("Do you want to keep the previous value '%s' (y/n)" % (default_remind_on))
            if keep_value.lower() == "n":
                task["remind_on"] = ""
        # remind for
        default_remind_for = task["remind_for"]
        remind_for = raw_input("Reminder duration in minutes, (default : %d) : " % (default_remind_for/60.0))
        if remind_for.strip() != "":
            task["remind_for"] = remind_for
    return kanban

def format_seconds(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)

def get_reminded_tasks(kanban):
    tasks = kanban["tasks"]
    current_time = time.time()
    reminded_tasks = []
    for i, task in enumerate(tasks):
        if complete_str_timestamp(task["remind_on"].strip()) != "":
            time_start = str_to_timestamp(task["remind_on"])
            time_stop = time_start + float(task["remind_for"])
            if time_start < current_time and time_stop > current_time:
                reminded_tasks.append(str(i+1) + " . " + task["name"])
    return reminded_tasks

def reminder_display(kanban):
    current_time = time.time()
    reminded_tasks = get_reminded_tasks(kanban)
    display = ""
    if len(reminded_tasks) > 0:
        display += "REMINDER :\n"
    for task in reminded_tasks:
        display += "[*] %s\n" %(task)
    return display

def kanban_display(kanban):
    boards = kanban["boards"]
    tasks = kanban["tasks"]
    board_section = {}
    board_width = {}
    max_card_count = 0
    current_time = time.time()
    # get board_width and board_section
    for board in boards:
        # get board_task
        board_task = []
        for i, card in enumerate(tasks):
            if card["board"] == board:
                card["id"] = str(i+1)
                board_task.append(card)
        # get max_card_count
        if len(board_task) > max_card_count:
            max_card_count = len(board_task)
        # get max_width
        max_width = len(board)
        for i, card in enumerate(board_task):
            title_width = len(card["id"]) + 3 + len(card["name"])
            remind_on_width = len(card["remind_on"])
            width = max(title_width, remind_on_width)
            if width > max_width:
                max_width = width
        board_section[board] = board_task
        board_width[board] = max_width
    # prepare kanban
    first_line = []
    card_title_list = []
    card_remind_on_list = []
    for board in boards:
        width = board_width[board]
        board_title = board.ljust(width, " ")
        first_line.append(board_title)
    for i in range(max_card_count):
        card_title = []
        card_remind_on = []
        for board in boards:
            width = board_width[board]
            if i>=len(board_section[board]):
                card_title.append("".ljust(width, " "))
                card_remind_on.append("".rjust(width, " "))
            else:
                card = board_section[board][i]
                title = card["id"] + " . " + card["name"]
                card_title.append(title.ljust(width, " "))
                card_remind_on.append(card["remind_on"].rjust(width, " "))
        card_title_list.append(card_title)
        card_remind_on_list.append(card_remind_on)
    # draw kanban
    # the kanban
    first_line = " | ".join(first_line)
    display = first_line + "\n" # board title
    display +=  "=" * len(first_line) + "\n" # the separator
    for i in range(max_card_count):
        card_title = " | ".join(card_title_list[i])
        card_remind_on = " | ".join(card_remind_on_list[i])
        display += card_title + "\n"
        display += card_remind_on + "\n"
        display +=  "-" * len(first_line) + "\n" # the separator
    return display

def display_pomodoro(stdscr, counter, is_working, is_pause, kanban):
    formatted_counter = format_seconds(counter)
    counter_status = "PAUSED" if is_pause else "      "
    working_status = "WORKING" if is_working else "REST   "
    command_bar_1 = "(w) Work Mode  (r) Rest Mode     (space) Pause/Resume"
    command_bar_2 = "(s) Stop Alarm (x) Exit Pomodoro (q) Quit Program"
    # clear the screen and redraw
    try:
        reminder_view = reminder_display(kanban)
        kanban_view = kanban_display(kanban)
        reminder_line_count = len(reminder_view.split("\n"))
        stdscr.addstr(0,0, "%s | %s %s" %(working_status, formatted_counter, counter_status), curses.A_BOLD)
        stdscr.addstr(1,0, command_bar_1)
        stdscr.addstr(2,0, command_bar_2)
        stdscr.addstr(4,0, reminder_view, curses.A_BOLD)
        stdscr.addstr(4+reminder_line_count,0, kanban_view)
        stdscr.refresh()
    except curses.error:
        pass

def pomodoro(kanban):
    quit = False
    # some variables
    global COUNTER
    global IS_WORKING
    global IS_PAUSE
    global CURRENT_REMINDED_TASKS
    COUNTER = int(kanban["work_time"]) if COUNTER == -1 else COUNTER
    initial_time = math.ceil(time.time())
    # create stdscr object, make getch non-blocking
    stdscr = curses.initscr()
    stdscr.nodelay(1)
    # turn off echo, hide cursor
    curses.noecho()
    curses.curs_set(0)
    curses.use_default_colors()
    while True:
        # the process: calculate COUNTER
        current_time = math.floor(time.time())
        if current_time - initial_time >=1:
            initial_time = current_time
            if not IS_PAUSE: # if IS_PAUSE, don't reduce the COUNTER
                stdscr.clear()
                COUNTER -= 1
                for task in get_reminded_tasks(kanban):
                    if task not in CURRENT_REMINDED_TASKS:
                        alarm_beep()
                        break
        # the display
        display_pomodoro(stdscr, COUNTER, IS_WORKING, IS_PAUSE, kanban)
        # the process: calculate IS_WORKING
        if COUNTER <= 0:
            COUNTER = int(kanban["rest_time"]) if IS_WORKING else int(kanban["work_time"])
            IS_WORKING = not IS_WORKING
            switch_beep()
        # the command
        command = stdscr.getch()
        if command == ord("x") or command == ord("X"): # exit
            break
        elif command == ord(" "): # pause/resume
            IS_PAUSE = not IS_PAUSE
        elif not IS_WORKING and (command == ord("w") or command == ord("W")): # work
            IS_WORKING = True
            COUNTER = int(kanban["work_time"])
            switch_beep()
        elif IS_WORKING and (command == ord("r") or command == ord("R")): # resume
            IS_WORKING = False
            COUNTER = int(kanban["rest_time"])
            switch_beep()
        elif command == ord("s") or command == ord("S"):
            CURRENT_REMINDED_TASKS = get_reminded_tasks(kanban)
        elif command == ord("q") or command == ord("Q"): #quit
            quit = True
            break
    curses.endwin()
    return quit

def main(args):
    # load kanban
    kanban = load_kanban()
    choice = "p"
    while True:
        if choice == "p" or choice == "P": # user choose "pomodoro & kanban"
            quit = pomodoro(kanban)
            if quit:
                break
        elif choice == "c" or choice == "C": # user choose "configuration"
            kanban = change_configuration(kanban)
        elif choice == "a" or choice == "A": # user choose "add task"
            kanban = add_task(kanban)
        elif choice == "e" or choice == "E": # user choose "edit task"
            kanban = edit_task(kanban)
        elif choice == "d" or choice == "D": # user choose "delete task"
            kanban = delete_task(kanban)
        elif choice == "q" or choice == "Q": # user choose "exit"
            break
        else:
            print("Invalid command")
        # save kanban and show pomodoro
        save_kanban(kanban)
        kanban = load_kanban()
        os.system('cls||clear')
        print(reminder_display(kanban))
        print(kanban_display(kanban))
        menu() # show the menu and read the user"s choice
        choice = raw_input("Your choice : ")

if __name__ == "__main__":
   curses.wrapper(main)