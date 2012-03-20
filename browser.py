import curses
import dbLayer as db
from bookForm import bookForm

class browserWindow:
    hl=0
    books = []
    topline = 0
    columns = [('ID',3),
               ('Title',30),
               ('Authors',20),
               ('ISBN',13)]
    mx = my = 0

    # redefinable functions
    def updateSelection(self,book):
        bookid = book['id']
        
        w=curses.newwin(1,1,20,20)
        bf=bookForm(w)
        bf.caption='Update Book '+str(bookid)
        bf.blabel='update'
        bf.updateEntries(book)
        newbook = bf.eventLoop()
        if len(newbook)!=0:
            db.updateBook(newbook,bookid)
        bf.clear()

    def viewSelection(self,book):
        bookid = book['id']
        w=curses.newwin(1,1,20,20)
        bf = bookForm(w)
        bf.caption='Viewing Book '+str(bookid)
        bf.blabel='done'
        bf.updateEntries(book)
        bf.eventLoop()
        bf.clear()

    def clear(self):
        self.w.erase()
        self.w.refresh()


    def __init__(self,window):
        self.w = window
        self.updateGeometry()
        self.refreshBooks()

    def refreshBooks(self):
        self.books = db.getBooks()

    def sortByColumn(self, col):
        self.books.sort() # key=dict.get(col))

    def updateGeometry(self):
        (self.my,self.mx)=self.w.getmaxyx()
        self.pageSize = self.my-3
        # maybe recalculate column widths here.

    def refresh(self):
        self.displayHeader()
        for r in range(0,self.pageSize):
            self.displayRow(r)
        self.w.refresh()
        self.highlight()

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
                    self.w.addnstr(row+2,cursor,str(book[k.lower()])+" "*width,width)
                cursor += width+1
        else:
            self.w.addstr(row+2,0," "*self.mx)

    def highlight(self):
        row = self.hl-self.topline+2
        if row > 1 and row < self.my:
            self.w.chgat(row,0,self.mx,curses.A_REVERSE)

    def unHighlight(self):
        row = self.hl-self.topline+2
        if row > 1 and row < self.my:
            self.w.chgat(row,0,self.mx,curses.A_NORMAL)

    def mvHighlight(self,delta):
        new = self.hl+delta
        new = max(new,0)
        new = min(new,len(self.books)-1)
        self.unHighlight()
        self.hl = new
        self.highlight()
    
    def scroll(self,delta):
        self.unHighlight()
        self.topline += delta
        self.topline = max(self.topline,0)
        self.topline = min(self.topline,len(self.books)-1)
        self.refresh()

    def startBrowser(self):
        self.w.keypad(1)
        self.refresh()

        ch = self.w.getch()
        while ch != 27 and ch != 113:
            if ch == curses.KEY_UP:
                if self.hl == self.topline:
                    self.scroll(-self.pageSize/2-1)
                self.mvHighlight(-1)
            elif ch == curses.KEY_DOWN:
                if self.hl == self.topline+self.pageSize-1:
                    self.scroll(+self.pageSize/2+1)
                self.mvHighlight(+1)
            elif ch == curses.KEY_PPAGE:
                self.scroll(-self.pageSize)
                self.mvHighlight(-self.pageSize)
            elif ch == curses.KEY_NPAGE:
                self.scroll(+self.pageSize)
                self.mvHighlight(+self.pageSize)
            
            elif ch == 117:
                book = self.books[self.hl]
                self.updateSelection(book)
                self.books[self.hl]=db.getBookByID(book['id'])
                self.refresh()

            elif ch == 10:
                book = self.books[self.hl]
                self.viewSelection(book)
                self.refresh()
                

            self.w.refresh()
            ch = self.w.getch()






