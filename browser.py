import curses
import dbLayer as db

class browserWindow:
    hl = 0
    books = []
    topline = 0
    columns = [('Title',20),
               ('Authors',10)]
    mx = my = 0

    def __init__(self,window):
        self.w = window
        self.updateGeometry()
        self.refreshBooks()
        self.sortByColumn('title')

    def refreshBooks(self):
        self.books = db.getBooks()

    def sortByColumn(self, col):
        self.books.sort() # key=dict.get(col))

    def updateGeometry(self):
        (self.my,self.mx)=self.w.getmaxyx()
        # maybe recalculate column widths here.

    def refresh(self):
        self.displayHeader()
        for r in range(0,self.my-2):
            self.displayRow(r)
        self.highlight(self.hl)
        self.w.refresh()

    def displayHeader(self):
        cursor = 0
        for header,width in self.columns:
            self.w.addnstr(0,cursor,header,width)
            self.w.addstr(1,cursor,"-"*width)
            cursor += width+1

    def displayRow(self,row):
        if self.topline+row < len(self.books):
            book = self.books[self.topline+row]
            cursor = 0
            for k,width in self.columns:
                if k.lower() in book:
                    self.w.addnstr(row+2,cursor,book[k.lower()],width)
                cursor += width+1
        else:
            self.w.addstr(row,0," "*self.mx)

    def highlight(self,row):
        self.w.chgat(self.hl+2,0,self.mx,curses.A_NORMAL)
        self.hl=row
        self.w.chgat(self.hl+2,0,self.mx,curses.A_REVERSE)

    def startBrowser(self):
        self.refresh()
        self.w.getch()






