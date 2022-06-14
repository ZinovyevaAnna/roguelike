import collections
import random
import unittest

import app


class MazeTest(unittest.TestCase):
    def generate_h_w(self):
        h = 1 + 2 * random.randint(1, 20)
        w = 1 + 2 * random.randint(1, 20)
        return h, w

    def test_maze_walls(self):
        for _ in range(1000):
            h, w = self.generate_h_w()
            maze = app.generate_maze(h, w)
            for i in range(len(maze)):
                self.assertEqual(1, maze[i][0], f'for i = {i}, j = {0}, h = {h}, w = {w}')
                self.assertEqual(1, maze[i][-1], f'for i = {i}, j = {-1}, h = {h}, w = {w}')
            for j in range(len(maze[0])):
                self.assertEqual(1, maze[0][j], f'for i = {0}, j = {j}, h = {h}, w = {w}')
                self.assertEqual(1, maze[-1][j], f'for i = {-1}, j = {j}, h = {h}, w = {w}')

    def test_exit_is_not_in_a_wall(self):
        for _ in range(1000):
            h, w = self.generate_h_w()
            maze = app.generate_maze(h, w)
            exit = app.generate_exit(h, w)
            self.assertEqual(0, maze[exit.x][exit.y])

    def test_path_to_exit_exists(self):
        for _ in range(1000):
            h, w = self.generate_h_w()
            maze = app.generate_maze(h, w)
            exit = app.generate_exit(h, w)

            queue = collections.deque()
            queue.append((1, 1))
            visited = [[False] * w for _ in range(h)]

            def ok(k, h):
                return 0 <= k < len(maze) and 0 <= h < len(maze[0])

            while queue:
                x, y = queue.pop()
                if ok(x - 1, y) and not visited[x - 1][y]:
                    visited[x - 1][y] = True
                    queue.append((x - 1, y))
                if ok(x + 1, y) and not visited[x + 1][y]:
                    visited[x + 1][y] = True
                    queue.append((x + 1, y))
                if ok(x, y - 1) and not visited[x][y - 1]:
                    visited[x][y - 1] = True
                    queue.append((x, y - 1))
                if ok(x, y + 1) and not visited[x][y + 1]:
                    visited[x][y + 1] = True
                    queue.append((x, y + 1))
            self.assertTrue(visited[exit.x][exit.y])


if __name__ == '__main__':
    unittest.main()
