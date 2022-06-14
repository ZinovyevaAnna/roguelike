import curses
from curses import wrapper
import app


def init_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)


def main(stdscr):
    init_colors()
    stdscr.clear()
    stdscr.addstr(app.INSTRUCTION)
    win = app.get()
    while True:
        key = stdscr.getch()
        continued = win.act(key, stdscr)
        if not continued:
            break


curses.use_env(True)
wrapper(main)
