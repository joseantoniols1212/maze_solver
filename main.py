from collections import defaultdict
from time import sleep
from tkinter import Tk, BOTH, Canvas
import random


ANIMATION_SLEEP_TIME = 0.005


class Window:
    def __init__(self, width, height):
        self.__width = width
        self.__height = height
        self.__root = Tk()
        self.__root.wm_title("Maze Solver")
        self.__canvas = Canvas(
            self.__root, bg="white", height=self.__height, width=self.__width
        )
        self.__canvas.pack(fill=BOTH, expand=1)
        self.__running = False
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()
        print("window closed...")

    def close(self):
        self.__running = False

    def draw_line(self, line, fill_color):
        line.draw(self.__canvas, fill_color)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    def __init__(self, p1, p2):
        self.__p1 = p1
        self.__p2 = p2

    def draw(self, canvas, fill_color, width=2):
        canvas.create_line(
            self.__p1.x,
            self.__p1.y,
            self.__p2.x,
            self.__p2.y,
            fill=fill_color,
            width=width,
        )


class Cell:
    def __init__(self, window=None):
        self.__window = window
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self.__x1 = -1
        self.__x2 = -1
        self.__y1 = -1
        self.__y2 = -1
        self.visited = False

    def draw(self, x1, y1, x2, y2):
        self.__x1 = x1
        self.__x2 = x2
        self.__y1 = y1
        self.__y2 = y2

        if self.__window is None:
            return

        p_ul = Point(x1, y1)
        p_ur = Point(x2, y1)
        p_br = Point(x2, y2)
        p_bl = Point(x1, y2)

        self.__window.draw_line(
            Line(p_bl, p_ul), "black" if self.has_left_wall else "white"
        )
        self.__window.draw_line(
            Line(p_bl, p_br), "black" if self.has_bottom_wall else "white"
        )
        self.__window.draw_line(
            Line(p_br, p_ur), "black" if self.has_right_wall else "white"
        )
        self.__window.draw_line(
            Line(p_ur, p_ul), "black" if self.has_top_wall else "white"
        )

    def draw_move(self, to_cell, undo=False):
        if self.__window is None:
            return

        if not undo:
            color = "red"
        else:
            color = "gray"
        cell1_center_x = self.__x1 + (self.__x2 - self.__x1) / 2
        cell1_center_y = self.__y1 + (self.__y2 - self.__y1) / 2
        cell2_center_x = to_cell.__x1 + (to_cell.__x2 - to_cell.__x1) / 2
        cell2_center_y = to_cell.__y1 + (to_cell.__y2 - to_cell.__y1) / 2

        p1 = Point(cell1_center_x, cell1_center_y)
        p2 = Point(cell2_center_x, cell2_center_y)

        l = Line(p1, p2)

        self.__window.draw_line(l, color)


class Maze:
    def __init__(
        self, x1, y1, num_rows, num_cols, cell_size_x, cell_size_y, win=None, seed=None
    ):
        self.__x1 = x1
        self.__y1 = y1
        self.__num_rows = num_rows
        self.__num_cols = num_cols
        self.__cell_size_x = cell_size_x
        self.__cell_size_y = cell_size_y
        self.__win = win

        self.__cells = []
        self.__create_cells()
        self.__break_entrance_and_exit()

    def __create_cells(self):
        self.__cells = [
            [Cell(self.__win) for _ in range(self.__num_rows)]
            for _ in range(self.__num_cols)
        ]
        for i in range(self.__num_cols):
            for j in range(self.__num_rows):
                self.__draw_cell(i, j)

    def __draw_cell(self, i, j):
        x1 = self.__x1 + i * self.__cell_size_x
        y1 = self.__y1 + j * self.__cell_size_y
        x2 = self.__x1 + (i + 1) * self.__cell_size_x
        y2 = self.__y1 + (j + 1) * self.__cell_size_y
        self.__cells[i][j].draw(x1, y1, x2, y2)

        if self.__win is None:
            return

        self.__animate()

    def __animate(self):
        if self.__win is None:
            return

        self.__win.redraw()
        sleep(ANIMATION_SLEEP_TIME)

    def __break_entrance_and_exit(self):
        self.__cells[0][0].has_top_wall = False
        self.__cells[-1][-1].has_bottom_wall = False
        self.__draw_cell(0, 0)
        self.__draw_cell(self.__num_cols - 1, self.__num_rows - 1)

    def __break_walls_r(self, i, j):
        self.__cells[i][j].visited = True
        while True:
            neighbors_direction = []
            for i_offset, j_offset in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                valid_neighbor = (
                    i + i_offset >= 0
                    and i + i_offset < self.__num_cols
                    and j + j_offset >= 0
                    and j + j_offset < self.__num_rows
                )
                if (
                    valid_neighbor
                    and not self.__cells[i + i_offset][j + j_offset].visited
                ):
                    neighbors_direction.append((i_offset, j_offset))

            if not neighbors_direction:
                self.__draw_cell(i, j)
                return

            dir_rnd_idx = random.randint(0, len(neighbors_direction) - 1)
            i_offset, j_offset = neighbors_direction[dir_rnd_idx]
            n_i = i + i_offset
            n_j = j + j_offset

            if i_offset == 0 and j_offset == 1:  # bottom
                self.__cells[i][j].has_bottom_wall = False
                self.__cells[n_i][n_j].has_top_wall = False
            elif i_offset == 0 and j_offset == -1:  # top
                self.__cells[i][j].has_top_wall = False
                self.__cells[n_i][n_j].has_bottom_wall = False
            elif i_offset == 1 and j_offset == 0:  # right
                self.__cells[i][j].has_right_wall = False
                self.__cells[n_i][n_j].has_left_wall = False
            elif i_offset == -1 and j_offset == 0:  # right
                self.__cells[i][j].has_left_wall = False
                self.__cells[n_i][n_j].has_right_wall = False

            self.__draw_cell(i, j)
            self.__draw_cell(n_i, n_j)

            self.__break_walls_r(n_i, n_j)

    def __reset_visited_cells(self):
        for i in range(self.__num_cols):
            for j in range(self.__num_rows):
                self.__cells[i][j].visited = False

    def __break_walls(self):
        self.__break_walls_r(0, 0)
        self.__reset_visited_cells()

    def __neighbors(self, i, j):
        neighbors = []
        if i + 1 < self.__num_cols:
            right_cell = self.__cells[i + 1][j]
            if not (right_cell.visited or right_cell.has_left_wall):
                neighbors.append((i + 1, j))
        if i - 1 >= 0:
            left_cell = self.__cells[i - 1][j]
            if not (left_cell.visited or left_cell.has_right_wall):
                neighbors.append((i - 1, j))
        if j + 1 < self.__num_rows:
            down_cell = self.__cells[i][j + 1]
            if not (down_cell.visited or down_cell.has_top_wall):
                neighbors.append((i, j + 1))
        if j - 1 >= 0:
            up_cell = self.__cells[i][j - 1]
            if not (up_cell.visited or up_cell.has_bottom_wall):
                neighbors.append((i, j - 1))
        return neighbors

    def __solve_r(self, i, j):
        self.__animate()
        self.__cells[i][j].visited = True
        if i == self.__num_cols - 1 and j == self.__num_rows - 1:
            return True
        neighbors = self.__neighbors(i, j)
        path_to_goal = False
        for neighbor in neighbors:
            self.__cells[i][j].draw_move(self.__cells[neighbor[0]][neighbor[1]])
            res = self.__solve_r(neighbor[0], neighbor[1])
            if not res:
                self.__cells[i][j].draw_move(
                    self.__cells[neighbor[0]][neighbor[1]], undo=True
                )
            path_to_goal = path_to_goal or res
        return path_to_goal

    def solve(self):
        self.__solve_r(0, 0)


def main():
    win = Window(800, 800)
    maze = Maze(50, 50, 10, 10, 50, 50, win)
    maze._Maze__break_walls()
    maze.solve()
    win.wait_for_close()


if __name__ == "__main__":
    main()
