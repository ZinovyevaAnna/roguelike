import curses
import functools
import json
import os.path
import random
from abc import ABCMeta, abstractmethod
from curses import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT

INSTRUCTION = '\n' \
              '    To move use arrows\n' \
              '    To choose press Enter\n' \
              '    To exit press Esc\n' \
              '\n' \
              '    Now press any key\n'


def get():
    return App.get()


class State(metaclass=ABCMeta):
    @abstractmethod
    def act_on_down(self):
        raise NotImplementedError()

    @abstractmethod
    def act_on_up(self):
        raise NotImplementedError()

    @abstractmethod
    def act_on_left(self):
        raise NotImplementedError()

    @abstractmethod
    def act_on_right(self):
        raise NotImplementedError()

    @abstractmethod
    def act_on_enter(self):
        raise NotImplementedError()

    @abstractmethod
    def act_on_esc(self):
        raise NotImplementedError()

    @abstractmethod
    def display(self, stdscr):
        raise NotImplementedError()


menu_options = ('continue',
                'new game',
                'exit')


class Menu(State):
    def __init__(self):
        self.selected = 0

    def act_on_down(self):
        self.selected = (self.selected + 1) % len(menu_options)

    def act_on_up(self):
        self.selected = (self.selected - 1) % len(menu_options)

    def act_on_left(self):
        pass

    def act_on_right(self):
        pass

    def act_on_enter(self):
        if menu_options[self.selected] == 'exit':
            return False
        if menu_options[self.selected] == 'new game':
            get().switch_state()
            get().get_state().new_game()
        if menu_options[self.selected] == 'continue':
            get().switch_state()
            get().get_state().load()
        return True

    def act_on_esc(self):
        pass

    def display(self, stdscr):
        safe(stdscr.clear)()
        for i in range(len(menu_options)):
            safe(stdscr.addstr)(i + 1, 1, ('> ' if self.selected == i else '') + menu_options[i])


class Element:
    def __init__(self, x, y, sym, col):
        self.x = x
        self.y = y
        self.symbol = sym
        self.color = col

    def draw(self, stdscr):
        safe(stdscr.addstr)(self.x, self.y, self.symbol, curses.color_pair(self.color))


class Game(State):
    def __init__(self):
        self.level = None
        self.maze = None
        self.new_game()

    def generate_next_level(self):
        self.level += 1
        self.h += 2
        self.w += 4
        self.maze = generate_maze(self.h, self.w)
        self.me = Element(1, 1, '©', 1)
        self.exit = generate_exit(self.h, self.w)

    def new_game(self):
        self.level = 0
        self.h = 5
        self.w = 9
        self.generate_next_level()

    def act_on_down(self):
        if self.me.x + 1 == self.h \
                or self.maze[self.me.x + 1][self.me.y]:
            return
        self.me.x += 1

    def act_on_up(self):
        if self.me.x == 0 \
                or self.maze[self.me.x - 1][self.me.y]:
            return
        self.me.x -= 1

    def act_on_left(self):
        if self.me.y == 0 \
                or self.maze[self.me.x][self.me.y - 1]:
            return
        self.me.y -= 1

    def act_on_right(self):
        if self.me.y + 1 == self.w \
                or self.maze[self.me.x][self.me.y + 1]:
            return
        self.me.y += 1

    def act_on_enter(self):
        if self.me.x == self.exit.x and self.me.y == self.exit.y:
            get().get_state().generate_next_level()
        return True

    def act_on_esc(self):
        get().get_state().save()
        get().switch_state()

    def is_visible(self, i, j):
        return abs(self.me.x - i) + abs(self.me.y - j) < 6

    def display(self, stdscr):
        stdscr.clear()
        for i in range(self.h):
            for j in range(self.w):
                if self.is_visible(i, j):
                    if self.maze[i][j] == 0:
                        safe(stdscr.addstr)(i, j, ' ', curses.color_pair(3))
                    else:
                        safe(stdscr.addstr)(i, j, ' ', curses.color_pair(2))
                else:
                    safe(stdscr.addstr)(i, j, '.')
        self.me.draw(stdscr)
        if self.is_visible(self.exit.x, self.exit.y):
            self.exit.draw(stdscr)
        safe(stdscr.move)(self.h, 0)
        safe(stdscr.refresh)()

    def save(self):
        with open('.saved_version', 'w') as file:
            packed = {'level': self.level,
                      'me': self.me.__dict__,
                      'exit': self.exit.__dict__,
                      'h': self.h, 'w': self.w,
                      'maze': self.maze}
            json.dump(packed, file)

    def load(self):
        if not os.path.isfile('.saved_version'):
            self.new_game()
            return
        with open('.saved_version', 'r') as file:
            packed = json.load(file)
            self.level = packed['level']
            e = packed['me']
            self.me = Element(e['x'], e['y'], e['symbol'], e['color'])
            e = packed['exit']
            self.exit = Element(e['x'], e['y'], e['symbol'], e['color'])
            self.h, self.w = packed['h'], packed['w']
            self.maze = packed['maze']


class App:
    instance = None
    MENU = 0
    GAME = 1

    def __init__(self):
        self.menu = Menu()
        self.game = Game()
        self.state = App.MENU

    def get_state(self):
        if self.state == App.MENU:
            return self.menu
        return self.game

    def switch_state(self):
        self.state = 1 - self.state

    def act(self, key, stdscr):
        result = True
        if key == KEY_LEFT:
            self.get_state().act_on_left()
        if key == KEY_RIGHT:
            self.get_state().act_on_right()
        if key == KEY_UP:
            self.get_state().act_on_up()
        if key == KEY_DOWN:
            self.get_state().act_on_down()
        if key == 10:  # enter
            result = self.get_state().act_on_enter()
        if key == 27:  # esc
            self.get_state().act_on_esc()
        self.get_state().display(stdscr)
        return result

    @staticmethod
    def get():
        if App.instance is None:
            App.instance = App()
        return App.instance


def generate_exit(h, w):
    x = random.randint(h // 2, h - 1)
    y = random.randint(w // 2, w - 1)
    if not x % 2:
        x -= 1
    if not y % 2:
        y -= 1
    return Element(x, y, 'E', 4)


def generate_maze(h, w):
    maze = [[1] * w for _ in range(h)]
    dfs(maze, 1, 1)
    for _ in range(h + w):
        maze[random.randint(0, h - 1)][random.randint(0, w - 1)] = 0
    return maze


def dfs(f, i, j):
    def ok(k, h):
        return 0 <= k < len(f) and 0 <= h < len(f[0])

    f[i][j] = 0
    while True:
        unvisited = []
        if ok(i - 2, j) and f[i - 2][j] == 1:
            unvisited.append((i - 2, j))
        if ok(i, j - 2) and f[i][j - 2] == 1:
            unvisited.append((i, j - 2))
        if ok(i + 2, j) and f[i + 2][j] == 1:
            unvisited.append((i + 2, j))
        if ok(i, j + 2) and f[i][j + 2] == 1:
            unvisited.append((i, j + 2))
        if not unvisited:
            break
        i2, j2 = unvisited[random.randint(0, len(unvisited) - 1)]
        f[(i + i2) // 2][(j + j2) // 2] = 0
        dfs(f, i2, j2)


def safe(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except curses.error:
            pass

    return inner
