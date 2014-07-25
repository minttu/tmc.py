import curses
from curses import panel

ret = -1


class Menu:

    """
    A ncurses menu for selecting something.
    """

    def __init__(self, screen, title, items, start):
        self.screen = screen
        self.items = list(items)
        self.title = "{0} (q to cancel)".format(title)
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
            self.window.addstr(0, 1, self.title, curses.A_NORMAL)
            height = self.window.getmaxyx()[0]
            for index, item in enumerate(self.items):
                pos = index + 2 - self.offset
                if pos < height and pos >= 2:
                    self.window.addstr(2 + index - self.offset,
                                       1,
                                       "{0}".format(item.name),
                                       curses.A_REVERSE if index == self.position else curses.A_NORMAL)

            key = self.window.getch()
            if key in [curses.KEY_ENTER, ord('\n')]:
                break
            elif key == curses.KEY_UP:
                self.navigate(-1)
                if self.position + 2 - self.offset <= 2 and self.position != 0:
                    self.offset -= 1
            elif key == curses.KEY_DOWN:
                self.navigate(1)
                if self.position + 3 - self.offset >= height:
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


def launch(title, items, start):
    if start != 0:
        for index, item in enumerate(items):
            if item.tid == start:
                start = index
                break
    curses.wrapper(Menu, title, items, start)
    return ret
