import os, time, random
from collections import defaultdict
from System import Console, ConsoleColor, ConsoleKey
from System.Threading import Thread, ThreadStart

class Screen(object):
    red = ConsoleColor.Red; green = ConsoleColor.Green; blue = ConsoleColor.Blue;black = ConsoleColor.Black
    dimension = (21,39)
    def __update_input(self):
        mapping = defaultdict(lambda: None, 
                              {ConsoleKey.A:Snake.left,ConsoleKey.J:Snake.left, ConsoleKey.LeftArrow:Snake.left,
                               ConsoleKey.D:Snake.right,ConsoleKey.L:Snake.right,ConsoleKey.RightArrow:Snake.right,
                               ConsoleKey.W:Snake.up,ConsoleKey.I:Snake.up,ConsoleKey.UpArrow:Snake.up,
                               ConsoleKey.S:Snake.down,ConsoleKey.K:Snake.down,ConsoleKey.DownArrow:Snake.down})
        while True: self.last_input = mapping[Console.ReadKey(True).Key]
    def __init__(self):
        self.last_input = None; self.__input_update_thread = Thread(ThreadStart(self.__update_input)); self.__input_update_thread.Start()
        os.system("cls") # os.system("clear")
        Console.Title = "Snake by LuYU426"
        # The next line needed to be commented out on Unix-like systems. However before running, the console needs to be adjusted accordingly 
        Console.CursorVisible = False; Console.WindowWidth = 80; Console.WindowHeight = 25;Console.BufferHeight = Console.WindowHeight; Console.BufferWidth = Console.WindowWidth
        for i in range(0,24):
            for j in range(0, 80):
                if i == 0 or j == 0: self.__show(j, i, Screen.black, "#")
                elif i == 22 or j == 79: self.__show(j, i, Screen.black,"#")
                else: self.__show(j, i, Screen.black," ")
    def __show(self,left,top,color,content): Console.CursorLeft = left; Console.CursorTop = top; Console.BackgroundColor = color; Console.Write(content)
    def show_score(self,score): self.__show(3,23,Screen.black,"Score:  {0}".format(score))
    def color(self, position, width, height, color):
        for row in range(position[0], position[0] + height):
            for col in range(position[1], position[1] + width):
                self.__show(col * 2 + 1,row + 1,color,"  ")

class GameLogic(object):
    def update(self, screen, snake, fruit, stats):
        stats.increase_score()
        screen.show_score(stats.current_score) 
        update_result = snake.update(screen.last_input,fruit.current_position)
        if update_result[0] == False: return True
        if update_result[1] == True: return False
        if update_result[2][0] < 0 or update_result[2][1] < 0: return False
        if update_result[2][0] >= Screen.dimension[0] or update_result[2][1] >= Screen.dimension[1]: return False
        screen.color(update_result[2],1,1,screen.green)
        if update_result[3] is None:
            fruit.reset_position()
            while snake.position_in_buffer(fruit.current_position): fruit.reset_position()
            screen.color(fruit.current_position,1,1,screen.red)
            stats.increase_level()
        else: screen.color(update_result[3],1,1,screen.black)
        return True
    def end(self): screen.color((0,0),39,21,Screen.blue)

class Snake(object):
    up = 0x00; down = 0x01; left = 0x10; right = 0x11
    def __init__(self): 
        self.__buffer = list(); self.__current_time_slice = 0
        self.__buffer = [[Screen.dimension[0]/2 + 1,Screen.dimension[1]/2 + 1]]
        self.__current_direction = Snake.up
    def __current_speed(self):
        _s = 8 - len(self.__buffer)/2
        return 1 if _s < 1 else _s
    def position_in_buffer(self, fruit_pos): 
        for item in self.__buffer:
            if item == fruit_pos:
                return True
        return False
    # returns [whether_need_update_screen(bool), whether_fail(bool), head_pos_to_draw(x,y), tail_pos_to_remove(x,y)]
    def update(self, direction, fruit_pos): 
        self.__current_time_slice += 1
        self.__current_time_slice %= self.__current_speed()
        if self.__current_time_slice != 0: return [False, False]
        if direction is None: direction = self.__current_direction
        if direction ^ self.__current_direction == 0x01: direction = self.__current_direction
        self.__current_direction = direction; candidate = [0, 0]; head = self.__buffer[len(self.__buffer) - 1]
        candidate[0] = head[0] + 1 if self.__current_direction == Snake.down else head[0] - 1 if self.__current_direction == Snake.up else head[0]
        candidate[1] = head[1] + 1 if self.__current_direction == Snake.right else head[1] - 1 if self.__current_direction == Snake.left else head[1]
        if self.position_in_buffer(candidate): return [True, True]
        if candidate == fruit_pos: self.__buffer.append(candidate); return [True, False, candidate, None]
        else:
            self.__buffer.append(candidate); tail = self.__buffer[0]; self.__buffer.remove(tail)
            return [True, False, candidate, tail]

class Fruit(object):
    def __init__(self): self.reset_position()
    @property
    def current_position(self): return self.__position
    def reset_position(self): self.__position = [random.randint(0,Screen.dimension[0]-1),random.randint(0,Screen.dimension[1]-1)]

class Stastics(object):
    def __init__(self): self.current_score = 0; self.__level = 0
    def increase_score(self): self.current_score += 1
    def increase_level(self): self.__level += 1; self.current_score += pow(2,self.__level-1)

if __name__ == "__main__":
    screen = Screen(); logic = GameLogic(); stats = Stastics(); fruit = Fruit(); snake = Snake()
    while snake.position_in_buffer(fruit.current_position): fruit.reset_position()
    screen.color(fruit.current_position,1,1,screen.red)
    while logic.update(screen, snake, fruit, stats): time.sleep(0.05)
    logic.end()