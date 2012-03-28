import sys
import curses
import dbLayer as db
from form import bookForm,categoryForm

class browserWindow:
    hl=0
    topline = 0
    entries = []
    selected = []
    commands = [(' q', 'quit')]
    # column definitions are in (label, weight, specified width) triples
    columnDefs = [('something',1,None)]
    mx = my = 0


    def clear(self):
        self.w.erase()
        self.w.refresh()

    def __init__(self,window,helpbar):
        self.w = window
        self.hb = helpbar
        self.updateGeometry()

    def sortByColumn(self, col):
        self.entries.sort(key=lambda k: k.get(col)) # key=dict.get(col))
        self.selected = map(lambda x: False, self.selected)

    def updateGeometry(self):
        (self.my,self.mx)=self.w.getmaxyx()
        self.pageSize = self.my-3
        self.calcColWidths()

    def calcColWidths(self):
        total_weights = 0
        available_space = self.mx - len(self.columnDefs)
        cols = []
        for label,weight,value in self.columnDefs:
            if value!=None:
                available_space -= value
            else:
                total_weights+=weight

        for label,weight,value in self.columnDefs:
            if value!=None:
                cols.append((label,value))
            else:
                cols.append((label,available_space*weight/total_weights))
        self.columns=cols

    def refresh(self):
        self.hb.commands = self.commands
        self.hb.refresh()
        self.displayHeader()
        for r in range(0,self.pageSize):
            self.displayRow(r)
        self.w.refresh()
        self.highlight()

    def displayHeader(self):
        cursor = 1
        for header,width in self.columns:
            self.w.addnstr(0,cursor,header+" "*width,width)
            self.w.addstr(1,cursor,"-"*width)
            cursor += width+1

    def displayRow(self,row):
        if self.topline+row < len(self.entries):
            entry = self.entries[self.topline+row]
            cursor = 1
            if self.selected[self.topline+row]:
                self.w.addstr(row+2, 0, "*")
            else:
                self.w.addstr(row+2, 0, " ")
            for k,width in self.columns:
                if k.lower() in entry:
                    self.w.addnstr(row+2,cursor,str(entry[k.lower()])+" "*width,width)
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
        new = min(new,len(self.entries)-1)
        self.unHighlight()
        self.hl = new
        self.highlight()
    
    def scroll(self,delta):
        self.unHighlight()
        self.topline += delta
        self.topline = max(self.topline,0)
        self.topline = min(self.topline,len(self.entries)-1)
        self.refresh()

    def eventLoop(self):
        self.w.keypad(1)
        self.refresh()

        ch = self.w.getch()
        while ch != 27 and ch != 113:
            ch = self.handleInput(ch)
            if ch==113:
                return {}
            self.w.refresh()
            ch = self.w.getch()

    def handleInput(self,ch):
        if ch == curses.KEY_UP or ch == 107 or ch == 16:
            if self.hl == self.topline:
                self.scroll(-self.pageSize/2-1)
            self.mvHighlight(-1)
        elif ch == curses.KEY_DOWN or ch == 106 or ch == 14:
            if self.hl == self.topline+self.pageSize-1:
                self.scroll(+self.pageSize/2+1)
            self.mvHighlight(+1)
        elif ch == curses.KEY_PPAGE:
            self.scroll(-self.pageSize)
            self.mvHighlight(-self.pageSize)
        elif ch == curses.KEY_NPAGE:
            self.scroll(+self.pageSize)
            self.mvHighlight(+self.pageSize)
        elif ch == 32:
            self.selected[self.hl] = not self.selected[self.hl]
            self.displayRow(self.hl-self.topline)
            self.highlight()



class bookBrowser(browserWindow):
    columnDefs = [('ID',0,3),
                  ('ISBN',0,13),
                  ('Authors',30,None),
                  ('Title',60,None)]
    
    commands = [(' u', 'update'), (' d', 'delete selected'), (' q', 'quit')]
    
    # redefinable functions
    def updateSelection(self,book):
        bookid = book['id']
        
        w=curses.newwin(1,1,20,20)
        bf=bookForm(w,self.hb,book)
        bf.caption='Update Book '+str(bookid)
        bf.blabel='update'
        newbook = bf.eventLoop()
        if len(newbook)!=0:
            db.updateBook(newbook,bookid)
        bf.clear()

    def viewSelection(self,book):
        bookid = book['id']
        w=curses.newwin(1,1,20,20)
        bf = bookForm(w,self.hb,book)
        bf.caption='Viewing Book '+str(bookid)
        bf.blabel='done'
        bf.eventLoop()
        bf.clear()

    def categorizeSelection(self,book):
        w = curses.newwin(40,20,20,20)
        cs = categorySelector(w,self.hb)
        cs.book = book
        cs.refreshCategories()
        cs.eventLoop()
        cs.clear()
    
    def delSelected(self):
        books = []
        for sel,book in zip(self.selected, self.entries):
            if sel:
                books.append(book)
        db.removeBooks(books)

    def refreshBooks(self):
        self.entries = db.getBooks()
        self.selected = map(lambda x:False, self.entries)

    def handleInput(self,ch):
        browserWindow.handleInput(self,ch)
        if ch == 117: #update on 'u'
            book = self.entries[self.hl]
            self.updateSelection(book)
            self.entries[self.hl]=db.getBookByID(book['id'])
            self.refresh()
        elif ch == 10:
            book = self.entries[self.hl]
            self.viewSelection(book)
            self.refresh()
        elif ch == 99:
            book = self.entries[self.hl]
            self.categorizeSelection(book)
            self.refresh()
        if ch==100:
            count=0
            for s in self.selected[0:self.hl-1]:
                if s:
                    count+=1
            self.delSelected()
            self.refreshBooks()
            self.refresh()
            self.scroll(-count)
            self.mvHighlight(-count)
        return ch

class categoryBrowser(browserWindow):
    columnDefs = [('Category',100,None)]
    commands = [(' a', 'add category'), (' d', 'delete selected'), (' q', 'quit')]


    def refreshCategories(self):
        self.entries = db.getCategories()
        self.sortByColumn('category')
        self.selected = map(lambda x:False, self.entries)

    def addCategory(self):
        w = curses.newwin(1,1,10,10)
        cf = categoryForm(w,self.hb)
        cats = cf.eventLoop()
        for c in cats:
            db.addCategory(c)
        cf.clear()

    def delSelected(self):
        categories = []
        for sel,cat in zip(self.selected, self.entries):
            if sel:
                categories.append(cat)
        db.deleteCategories(categories)

    def handleInput(self,ch):
        browserWindow.handleInput(self,ch)
        if ch==97:
            self.addCategory()
            self.refreshCategories()
            self.refresh()
        if ch==100:
            count=0
            for s in self.selected[0:self.hl-1]:
                if s:
                    count+=1
            self.delSelected()
            self.refreshCategories()
            self.refresh()
            self.scroll(-count)
            self.mvHighlight(-count)
        return ch

class categorySelector(browserWindow):
    columnDefs = [('Category',100,None)]
    commands = [(' a', 'add category'), (' c', 'commit'), (' q', 'quit')]
    book = {'id':''}
    original=[]


    def refreshCategories(self):
        self.entries = db.getCategories()
        self.sortByColumn('category')
        self.refreshSelected()

    def refreshSelected(self):
        self.original = map(lambda x:False, self.entries)
        cats = db.getBookCategories(self.book)
        cats.sort()
        cats.sort(key=lambda k: k.get('category')) # key=dict.get(col))
        i = 0
        j = 0
        for cat in self.entries:
            if i == len(cats):
                break
            if cat['id']==cats[i]['cat_id']:
                self.original[j] = True;
                i+=1
            j+=1
        self.selected = self.original[:]


    def addCategory(self):
        w = curses.newwin(1,1,10,10)
        cf = categoryForm(w,self.hb)
        cats = cf.eventLoop()
        for c in cats:
            db.addCategory(c)
        cf.clear()

    def updateCategories(self):
        # first removed the deselected ones
        uncats = []
        cats = []
        for old, new, category in zip(self.original, self.selected, self.entries):
            if old and (not new):
                uncats.append(category)
            if (not old) and new:
                cats.append(category)
        db.uncategorizeBook(self.book, uncats)
        # add the newly selected categories
        db.categorizeBook(self.book, cats)


    def handleInput(self,ch):
        browserWindow.handleInput(self,ch)
        if ch==97:
            self.addCategory()
            self.refreshCategories()
            self.refresh()
        if ch==99:
            self.updateCategories()
            return 113

