import curses
import math
from curses import panel

from tmc import conf

use_unicode = conf.use_unicode_characters


class Menu:

    """
    A ncurses menu for selecting something.
    """

    def __init__(self, screen, title, items, selected, resp):
        self.resp = resp
        self.screen = screen
        self.items = list(items)
        self.position = 0
        if selected:
            for index, item in enumerate(self.items):
                if item.tid == selected.tid:
                    self.position = index
                    break
        self.offset = 0
        self.window = screen.subwin(0, 0)
        self.height = height = self.window.getmaxyx()[0]
        if self.position + 2 >= height:
            self.offset = self.position - 1

        if use_unicode:
            self.title = "┤ {0} (q to cancel) ├".format(title)
        else:
            self.title = "| {0} (q to cancel) |".format(title)

        self.window.keypad(1)
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()
        try:
            curses.curs_set(0)
            curses.use_default_colors()
        except curses.error:
            pass
        self.start()

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.items):
            self.position = len(self.items) - 1

    def draw(self):
        self.window.clear()
        self.window.refresh()
        self.window.bkgd(' ')
        if use_unicode:
            self.window.border()
        else:
            self.window.border("|", "|", "-", "-", "+", "+", "+", "+")
        width = self.window.getmaxyx()[1]
        self.window.addstr(0, int((width - len(self.title)) / 2), self.title)
        height = self.window.getmaxyx()[0] - 1
        for index, item in enumerate(self.items):
            pos = index + 2 - self.offset
            if height - 1 > pos >= 2:
                style = curses.A_NORMAL
                if index == self.position:
                    style |= curses.A_REVERSE
                self.window.addstr(2 + index - self.offset, 2,
                                   "{0}".format(item.menuname()), style)
        scroll = math.floor((self.position / len(self.items)) * (height - 3))
        for i in range(0, height - 3):
            if i == scroll:
                char = "█" if use_unicode else "#"
            else:
                char = "░" if use_unicode else "-"
            self.window.addstr(
                i + 2, width - 1, char)
        if use_unicode:
            self.window.addstr(1, width - 1, "┴")
            self.window.addstr(height - 1, width - 1, "┬")

    def wait_for_input(self):
        key = self.window.getch()
        if key in [curses.KEY_ENTER, ord('\n')]:
            return False
        elif key == curses.KEY_UP:
            self.navigate(-1)
            if self.position - self.offset <= 0 and self.position != 0:
                self.offset -= 1
        elif key == curses.KEY_DOWN:
            self.navigate(1)
            if self.position + 4 - self.offset >= self.height:
                self.offset += 1
        elif key == ord('q'):
            self.resp["done"] = True
            return False
        return True

    def start(self):
        self.panel.top()
        self.panel.show()
        self.window.clear()
        while True:
            self.draw()
            if self.wait_for_input() is False:
                break

        if not self.resp["done"]:
            self.resp["code"] = self.items[self.position].tid
            self.resp["item"] = self.items[self.position]

        self.window.clear()
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()

    @staticmethod
    def launch(title, items, selected=None):
        """
        Launches a new menu. Wraps curses nicely so exceptions won't screw with
        the terminal too much.
        """
        resp = {"code": -1, "done": False}
        curses.wrapper(Menu, title, items, selected, resp)
        return resp
