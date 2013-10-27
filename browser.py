import sys
import curses
import db_layer as db
from form import BookForm,CategoryForm

class browserWindow:
    hl=0
    topline = 0
    entries = []
    selected = list()
    commands = [(' /', 'search'), (' n', 'find next'), (' N', 'find previous'), 
            ('F6', 'Sort Column'), (' q', 'quit')]
    cs = []
    # column definitions are in (label, weight, specified width) triples
    columnDefs = [('something',1,None)]
    mx = my = 0
    # for searches
    last_search = ""
    found_index = 0

    def __init__(self,window,helpbar, height=50, width=80):
        self.w = window
        self.hb = helpbar
        self.w.resize(height,width)
        self.updateGeometry()
        self.commands = self.cs+self.commands

    def sortByColumn(self, col):
        self.entries.sort(key=lambda k: k.get(col,"")) # key=dict.get(col))
        self.selected = list(map(lambda x: False, self.selected))


    def updateGeometry(self):
        (self.my,self.mx)=self.w.getmaxyx()
        self.pageSize = self.my-4
        self.calcColWidths()

    def calcColWidths(self):
        total_weights = 0
        available_space = self.mx - len(self.columnDefs) -2
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
                cols.append((label,available_space*weight//total_weights))
        self.columns=cols

    def refresh(self):
        self.hb.commands = self.commands
        self.hb.refresh()
        self.w.box()
        self.displayHeader()
        for r in range(0,self.pageSize):
            self.displayRow(r)
        self.w.refresh()
        self.highlight()

    def clear(self):
        self.w.erase()
        self.w.refresh()

    def centreChild(self,child):
        (y,x) = self.w.getbegyx()
        (r,c) = child.getmaxyx()
        child.mvwin( y+(self.my-r)//2,x+(self.mx-c)//2)


    def displayHeader(self):
        cursor = 2
        for header,width in self.columns:
            self.w.addnstr(1,cursor,header+" "*width,width)
            self.w.addstr(2,cursor,"-"*width)
            cursor += width+1

    def displayRow(self,row):
        if self.topline+row < len(self.entries):
            entry = self.entries[self.topline+row]
            cursor = 2
            self.w.addnstr(row+3, 1, " "*self.mx,self.mx-2)
            if self.selected[self.topline+row]:
                self.w.addstr(row+3, 1, "*")
            else:
                self.w.addstr(row+3, 1, " ")
            for k,width in self.columns:
                if k.lower() in entry:
                    self.w.addnstr(row+3,cursor,str(entry[k.lower()])+" "*width,width)
                cursor += width+1
        else:
            self.w.addstr(row+3,1," "*(self.mx-2))

    def highlight(self):
        row = self.hl-self.topline+3
        if row > 1 and row < self.my:
            self.w.chgat(row,1,self.mx-2,curses.A_REVERSE)

    def unHighlight(self):
        row = self.hl-self.topline+3
        if row > 1 and row < self.my:
            self.w.chgat(row,1,self.mx-2,curses.A_NORMAL)

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
        self.topline = min(self.topline,len(self.entries)-1)
        self.topline = max(self.topline,0)
        self.refresh()

    def search(self, string):
        case_sensitive = not(string.islower())
        #sys.stderr.write(str(case_sensitive)+'\n')
        i = 0
        found = False
        for e in self.entries:
            for k,v in e.items():
                # we or with found to make sure it is never "unfound"
                if case_sensitive:
                    found = str(v).find(string) != -1 or found
                else:
                    found = str(v).lower().find(string) != -1 or found
            if found:
                break
            i += 1;
        if found:
            self.last_search = string
            self.search_index = i
            return i
        else:
            self.search_index = -1
            return -1

    def findNext(self):
        if self.last_search == "" or self.search_index == -1:
            return -1
        found = False
        for i in range(self.hl+1,len(self.entries)-1):
            for k,v in self.entries[i].items():
                if str(v).find(self.last_search) != -1:
                    found = True
            if found:
                break
        if found:
            self.search_index = i
            return i
        else:
            return -1

    def findPrevious(self):
        if self.last_search == "" or self.search_index == -1:
            return -1
        found = False
        for i in range(self.hl-1, 0, -1):
            for k,v in self.entries[i].items():
                if str(v).find(self.last_search) != -1:
                    found = True
            if found:
                break
        if found:
            self.search_index = i
            return i
        else:
            return -1


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
            self.hb.refresh()

    def handleInput(self,ch):
        if ch == curses.KEY_UP or ch == 107 or ch == 16:
            if self.hl == self.topline:
                self.scroll(-self.pageSize//2-1)
            self.mvHighlight(-1)
        elif ch == curses.KEY_DOWN or ch == 106 or ch == 14:
            if self.hl == self.topline+self.pageSize-1:
                self.scroll(+self.pageSize//2+1)
            self.mvHighlight(+1)
        elif ch == curses.KEY_PPAGE:
            self.scroll(-self.pageSize)
            self.mvHighlight(-self.pageSize)
        elif ch == curses.KEY_NPAGE:
            self.scroll(+self.pageSize)
            self.mvHighlight(+self.pageSize)
        elif ch == curses.KEY_HOME:
            self.scroll(-len(self.entries))
            self.mvHighlight(-len(self.entries))
        elif ch == curses.KEY_END:
            self.scroll(len(self.entries))
            self.mvHighlight(len(self.entries))
        elif ch == 47: # forward slash
            string = self.hb.getSearch()
            hl = self.search(string)
            if hl != -1:
                delta = hl - self.hl
                self.scroll(delta)
                self.mvHighlight(delta)
            else:
                self.hb.display(string+' not found')
        elif ch == 110: # n
            hl = self.findNext()
            if hl != -1:
                delta = hl - self.hl
                self.scroll(delta)
                self.mvHighlight(delta)
            else:
                self.hb.display(self.last_search+' not found')
        elif ch == 78: # N
            hl = self.findPrevious()
            if hl != -1:
                delta = hl - self.hl
                self.scroll(delta)
                self.mvHighlight(delta)
            else:
                self.hb.display(self.last_search+' not found')
        elif ch == 270: # F6 Sorts
            w = curses.newwin(1,1)
            cl = columnSelector(w,self.hb,40,20)
            self.centreChild(w)
            col = cl.eventLoop()
            cl.clear()
            self.sortByColumn(col)
            self.clear()
            self.refresh()
        elif ch == 32:
            if len(self.selected)>0:
                self.selected[self.hl] = not self.selected[self.hl]
            self.displayRow(self.hl-self.topline)
            self.highlight()



class trashBrowser(browserWindow):
    columnDefs = [('ID',0,3),
                  ('ISBN',0,13),
                  ('Authors',30,None),
                  ('Title',60,None)]
    
    cs = [(' r', 'restore selected'), (' d', 'delete selected')]
    
    # redefinable functions
    def viewSelection(self,book):
        bookid = book['id']
        w=curses.newwin(1,1)
        bf = BookForm(w, self.hb, book, width=self.mx-10)
        self.centreChild(w)
        bf.caption='Viewing Book '+str(bookid)
        bf.blabel='done'
        bf.event_loop()
        bf.clear()

    def restoreSelected(self):
        books = []
        for sel,book in zip(self.selected, self.entries):
            if sel:
                books.append(book)
        db.restoreBooks(books)

    def delSelected(self):
        books = []
        for sel,book in zip(self.selected, self.entries):
            if sel:
                books.append(book)
        db.deleteBooks(books)

    def refreshBooks(self):
        self.entries = db.getRemovedBooks()
        self.selected = list(map(lambda x:False, self.entries))

    def handleInput(self,ch):
        browserWindow.handleInput(self,ch)
        if ch == 10:
            book = self.entries[self.hl]
            self.viewSelection(book)
            self.refresh()
        if ch==114: #restore books
            count=0
            for s in self.selected[0:self.hl-1]:
                if s:
                    count+=1
            self.restoreSelected()
            self.refreshBooks()
            self.refresh()
            self.scroll(-count)
            self.mvHighlight(-count)
        if ch==100: # delete books
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

class bookBrowser(browserWindow):
    columnDefs = [('ID',0,3),
                  ('ISBN',0,13),
                  ('Authors',30,None),
                  ('Title',60,None)]
    
    cs = [(' u', 'update'), (' d', 'delete selected')]
    
    # redefinable functions
    def updateSelection(self,book):
        bookid = book['id']
        
        w=curses.newwin(1,1)
        bf = BookForm(w,self.hb,book, width=self.mx-20)
        self.centreChild(w)
        bf.caption='Update Book '+str(bookid)
        bf.blabel='update'
        newbook = bf.event_loop()
        if len(newbook)!=0:
            db.updateBook(newbook,bookid)
        bf.clear()

    def viewSelection(self,book):
        bookid = book['id']
        w=curses.newwin(1,1)
        bf = BookForm(w,self.hb,book, width=self.mx-20)
        self.centreChild(w)
        bf.caption='Viewing Book '+str(bookid)
        bf.blabel='done'
        bf.event_loop()
        bf.clear()

    def categorizeSelection(self,book):
        w = curses.newwin(1,1)
        cs = categorySelector(w,self.hb,40,40)
        self.centreChild(w)
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
        self.selected = list(map(lambda x:False, self.entries))

    def refreshBooksInCategory(self,cat):
        self.entries = db.getBooksByCategory(cat)
        self.selected = list(map(lambda x:False, self.entries))

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
    cs = [(' a', 'add category'), (' d', 'delete selected')]


    def refreshCategories(self):
        self.entries = db.getCategories()
        self.sortByColumn('category')
        self.selected = list(map(lambda x:False, self.entries))

    def addCategory(self):
        w = curses.newwin(1,1,10,10)
        cf = CategoryForm(w,self.hb)
        self.centreChild(w)
        cats = cf.event_loop()
        for c in cats:
            db.addCategory(c)
        cf.clear()

    def viewCategory(self):
        w = curses.newwin(20,80,20,20)
        b = bookBrowser(w,self.hb)
        self.centreChild(w)
        b.refreshBooksInCategory(self.entries[self.hl])
        b.eventLoop()
        b.clear()

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
        if ch ==10:
            self.viewCategory()
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
    cs = [(' a', 'add category'), (' c', 'commit')]
    book = {'id':''}
    original=[]


    def refreshCategories(self):
        self.entries = db.getCategories()
        self.sortByColumn('category')
        self.refreshSelected()

    def refreshSelected(self):
        self.original = list(map(lambda x:False, self.entries))
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
        cf = CategoryForm(w,self.hb)
        self.centreChild(w)
        cats = cf.event_loop()
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



class columnSelector(browserWindow):
    columnDefs = [('Column',100,None)]
    entries = [{'column': 'id'}, {'column': 'isbn'}, {'column': 'lccn'},
            {'column': 'title'}, {'column': 'subtitle'}, {'column': 'authors'}, 
            {'column': 'edition'}, {'column': 'publisher'}, 
            {'column': 'publish year'}, {'column': 'publish month'}, 
            {'column': 'publish location'}, {'column': 'pages'}, {'column': 'pagination'}, 
            {'column': 'weight'}, {'column': 'last updated'}]

    def __init__(self,window,helpbar,height=40,width=20):
        self.selected = [False,False,False,False,False,False,False,
                         False,False,False,False,False,False,False,False]
        browserWindow.__init__(self,window,helpbar,height,width)


    def eventLoop(self):
        self.w.keypad(1)
        self.refresh()

        ch = self.w.getch()
        while ch != 27 and ch != 113:
            ch = self.handleInput(ch)
            if ch==10:
                col = self.entries[self.hl]
                return col['column']
            self.w.refresh()
            ch = self.w.getch()
            self.hb.refresh()
    
    def handleInput(self,ch):
        browserWindow.handleInput(self,ch)
        return ch
