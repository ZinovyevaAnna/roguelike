import curses
import json
import os.path
import random
import unittest

import app


class MovesTest(unittest.TestCase):
    def setUp(self):
        if os.path.isfile('../.saved_version'):
            os.remove('../.saved_version')
        app.App.display = lambda *arg: None
        app.App.instance = None

    def choose_in_menu(self, win: app.App, param):
        win.act(27, None)  # esc
        self.assertTrue(isinstance(win.get_state(), app.Menu))
        win.get_state().selected = app.menu_options.index(param)
        win.act(10, None)  # enter

    def make_random_move(self, win: app.App):
        moves = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]
        for _ in range(100):
            random_move = moves[random.randint(0, len(moves) - 1)]
            win.act(random_move, None)

    def test_menu(self):
        win = app.get()
        self.choose_in_menu(win, 'continue')
        self.assertTrue(isinstance(win.get_state(), app.Game))
        self.choose_in_menu(win, 'new game')
        self.assertTrue(isinstance(win.get_state(), app.Game))

    def test_moves_throw_wall(self):
        win = app.get()
        self.choose_in_menu(win, 'new game')

        for _ in range(10000):
            self.make_random_move(win)
            me = win.get_state().me
            maze = win.get_state().maze
            self.assertEqual(0, maze[me.x][me.y])

    def test_maze_saved_version(self):
        win = app.get()
        self.choose_in_menu(win, 'new game')

        for _ in range(100):
            self.make_random_move(win)

        old_maze = json.dumps(win.get_state().maze)
        old_me = json.dumps(win.get_state().me.__dict__)
        win.act(27, None)  # esc

        app.App.instance = None
        win = app.get()
        self.choose_in_menu(win, 'continue')
        self.assertEqual(json.dumps(win.get_state().maze), old_maze)
        self.assertEqual(json.dumps(win.get_state().me.__dict__), old_me)

    def test_new_map_when_exit_found(self):
        win = app.get()
        self.choose_in_menu(win, 'new game')
        old_map = json.dumps(win.get_state().maze)
        win.get_state().exit.x = 1
        win.get_state().exit.y = 1
        win.act(10, None)  # enter
        self.assertNotEqual(json.dumps(win.get_state().maze), old_map)


if __name__ == '__main__':
    unittest.main()
