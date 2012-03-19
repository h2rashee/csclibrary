import curses
import dbLayer as db

class browserWindow:
    highlight = 0
    books = []

    def refreshBooks(self):
        self.books = db.getBooks()

    def sortByColumn(self, col):
        self.books.sort(key=get(col))

    def refresh(self):
        (my,mx) = w.getmaxyx()
        self.displayHeader()
        for r in range(2,my):
            self.displayRow(my)

    def displayRow(self,row):
        self.w.addstr(row,1,"Row to be updated")





