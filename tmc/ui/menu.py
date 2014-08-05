import curses
import math
from curses import panel

ret = -1


class Menu:

    """
    A ncurses menu for selecting something.
    """

    def __init__(self, screen, title, items, start):
        self.screen = screen
        self.items = list(items)
        self.title = "┤ {0} (q to cancel) ├".format(title)
        self.window = screen.subwin(0, 0)
        self.window.keypad(1)
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()
        self.position = start
        self.offset = 0
        height = self.window.getmaxyx()[0]
        if self.position + 2 >= height:
            self.offset = (self.position + 2) - height + (height - 3)
        curses.curs_set(0)
        curses.use_default_colors()
        self.display()

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.items):
            self.position = len(self.items) - 1

    def display(self):
        self.panel.top()
        self.panel.show()
        self.window.clear()
        while True:
            self.window.clear()
            self.window.refresh()
            self.window.bkgd(' ')
            self.window.border()
            width = self.window.getmaxyx()[1]
            self.window.addstr(
                0, int((width - len(self.title)) / 2), self.title)
            height = self.window.getmaxyx()[0] - 1
            for index, item in enumerate(self.items):
                pos = index + 2 - self.offset
                if pos < height - 1 and pos >= 2:
                    style = curses.A_NORMAL
                    if index == self.position:
                        style |= curses.A_REVERSE
                    self.window.addstr(2 + index - self.offset,
                                       2,
                                       "{0}".format(item.menuname()),
                                       style)
            scroll = math.floor(
                (self.position / len(self.items)) * (height - 3))
            for i in range(0, height - 3):
                char = "█" if i == scroll else "░"
                self.window.addstr(
                    i + 2, width - 1, char)
            self.window.addstr(1, width - 1, "┴")
            self.window.addstr(height - 1, width - 1, "┬")

            key = self.window.getch()
            if key in [curses.KEY_ENTER, ord('\n')]:
                break
            elif key == curses.KEY_UP:
                self.navigate(-1)
                if self.position - self.offset <= 0 and self.position != 0:
                    self.offset -= 1
            elif key == curses.KEY_DOWN:
                self.navigate(1)
                if self.position + 4 - self.offset >= height:
                    self.offset += 1
            elif key == ord('q'):
                self.position = -1
                break

        global ret
        if self.position >= 0:
            ret = self.items[self.position].tid
        else:
            ret = self.position
        self.window.clear()
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()

    @staticmethod
    def launch(title, items, start):
        if start != 0:
            for index, item in enumerate(items):
                if item.tid == start:
                    start = index
                    break
        curses.wrapper(Menu, title, items, start)
        return ret
