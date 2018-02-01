import curses, os, traceback

class CursedMenu(object):
    '''A class which abstracts the horrors of building a curses-based menu system'''

    def __init__(self):
        '''Initialization'''
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        self.screen.keypad(1)

        # Highlighted and Normal line definitions
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.highlighted = curses.color_pair(1)
        self.normal = curses.A_NORMAL


    def show(self, options, title="Title", subtitle="Subtitle"):
        '''Draws a menu with the given parameters'''
        self.set_options(options)
        self.title = title
        self.subtitle = subtitle
        self.selected = 0
        self.draw_menu()


    def set_options(self, options):
        '''Validates that the last option is "Exit"'''
        if options[-1] is not 'Exit':
            options.append('Exit')
        self.options = options


    def draw_menu(self):
        '''Actually draws the menu and handles branching'''
        request = ""
        try:
            while request is not "Exit":
                self.draw()
                request = self.get_user_input()
                self.handle_request(request)
            self.__exit__()

        # Also calls __exit__, but adds traceback after
        except Exception as exception:
            self.__exit__()
            traceback.print_exc()


    def draw(self):
        '''Draw the menu and lines'''
        self.screen.border(0)
        self.screen.addstr(2,2, self.title, curses.A_STANDOUT) # Title for this menu
        self.screen.addstr(4,2, self.subtitle, curses.A_BOLD) #Subtitle for this menu

        # Display all the menu items, showing the 'pos' item highlighted
        for index in range(len(self.options)):
            textstyle = self.normal
            if index == self.selected:
                textstyle = self.highlighted
            self.screen.addstr(5+index,4, "%d - %s" % (index+1, self.options[index]), textstyle)

        self.screen.refresh()


    def get_user_input(self):
        '''Gets the user's input and acts appropriately'''
        user_in = self.screen.getch() # Gets user input

        '''Enter and Exit Keys are special cases'''
        if user_in == 10:
            return self.options[self.selected]
        if user_in == 27:
            return self.options[-1]

        # This is a number; check to see if we can set it
        if user_in >= ord('1') and user_in <= ord(str(min(9,len(self.options)+1))):
            self.selected = user_in - ord('0') - 1 # convert keypress back to a number, then subtract 1 to get index
            return

        # Increment or Decrement
        if user_in == curses.KEY_DOWN: # down arrow
            self.selected += 1
        if user_in == curses.KEY_UP: # up arrow
            self.selected -=1
        self.selected = self.selected % len(self.options)
        return


    def handle_request(self, request):
        '''This is where you do things with the request'''
        if request is None: return


    def __exit__(self):
        curses.endwin()
        os.system('clear')


'''demo'''
cm = CursedMenu()
cm.show(['First','2nd','#3'], title='Demo Menu', subtitle='Options')