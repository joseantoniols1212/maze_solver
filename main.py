from tkinter import Tk, BOTH, Canvas


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


def main():
    win = Window(800, 600)
    point1 = Point(0, 0)
    point2 = Point(800, 600)
    line = Line(point1, point2)
    win.draw_line(line, "black")
    win.wait_for_close()


if __name__ == "__main__":
    main()
